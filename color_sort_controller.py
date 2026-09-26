from controller import Robot
import math
import numpy as np

from arm_ik import ArmIK   # <-- use the numeric IK class

TIME_STEP = 32
robot = Robot()

arm_ik = ArmIK()

# ---- DEVICE LIST DEBUGGER ----
print("\n=== DEVICE LIST START ===")
for i in range(robot.getNumberOfDevices()):
    dev = robot.getDeviceByIndex(i)
    try:
        print(i, dev.getName(), type(dev).__name__)
    except:
        print(i, "<unnamed>", type(dev).__name__)
print("=== DEVICE LIST END ===\n")
# ---- END DEBUGGER ----

# ---- STATES ----
WAITING, ANALYZING, MOVING_DROP, RELEASING, MOVING_HOME = range(5)

counter = 0
state = WAITING

# ---- CARTESIAN DROP POSES (TUNE THESE NUMBERS) ----
# These are *guesses* for world-frame TCP poses above each crate.
# You may need to tweak x,y,z slightly so the wrist ends up above each box.
GREEN_DROP_POSE = {
    "position": [0.55,  0.00, 0.30],      # center crate
    "rpy":      [0.0, math.pi, 0.0],      # wrist mostly down
}

RED_DROP_POSE = {
    "position": [0.55, -0.25, 0.30],      # right crate (neg Y)
    "rpy":      [0.0, math.pi, 0.0],
}

BLUE_DROP_POSE = {
    "position": [0.55,  0.25, 0.30],      # left crate (pos Y)
    "rpy":      [0.0, math.pi, 0.0],
}

# how long to wait for motions (in controller steps)
MOVE_TO_DROP_STEPS = 60    # ~2 seconds
MOVE_HOME_STEPS    = 60
OPEN_CLOSE_STEPS   = 20

speed = 1.0

# ----- devices -----

# Gripper internal motors
hand_motors = [
    robot.getDevice("finger_1_joint_1"),
    robot.getDevice("finger_2_joint_1"),
    robot.getDevice("finger_middle_joint_1"),
]

for m in hand_motors:
    m.setVelocity(2.0)

# Use actual joint limits to avoid warnings
GRIPPER_OPEN  = hand_motors[0].getMinPosition()   # ≈ 0.0495
GRIPPER_CLOSE = hand_motors[0].getMaxPosition()   # ≈ 0.85

# UR5e joints (6 DoF)
arm_joint_names = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

arm_motors = []
arm_sensors = []

for name in arm_joint_names:
    m = robot.getDevice(name)
    arm_motors.append(m)
    m.setVelocity(speed)
    ps = m.getPositionSensor()
    ps.enable(TIME_STEP)
    arm_sensors.append(ps)

# Camera
camera = robot.getDevice("camera")
camera.enable(2 * TIME_STEP)

# Distance sensor
distance_sensor = robot.getDevice("distance sensor")
distance_sensor.enable(TIME_STEP)

# Position sensor on wrist_1 (for "home" detection; home ≈ 0)
position_sensor = robot.getDevice("wrist_1_joint_sensor")
position_sensor.enable(TIME_STEP)

# Snapshot the initial joint config as "home" for going back later
# (We do this after one step, but initial is usually fine.)
HOME_Q = None

# Color reference values
RED_COLOR =   {'r': 0.904295, 'g': 0.243366, 'b': 0.14963}
BLUE_COLOR =  {'r': 0.037842, 'g': 0.03833,  'b': 0.904295}
GREEN_COLOR = {'r': 0.398413, 'g': 0.85156,  'b': 0.270146}

detected_color = None
last_block_present = False      # edge detect on distance sensor


# ---------- COLOR DETECTION ----------

def get_dominant_color(camera):
    """Analyze camera image and return 'red' / 'blue' / 'green'."""
    img = camera.getImage()
    if img is None:
        return None

    width = camera.getWidth()
    height = camera.getHeight()

    r_sum = g_sum = b_sum = 0.0
    samples = 0

    for y in range(height // 3, 2 * height // 3):
        for x in range(width // 3, 2 * width // 3):
            r = camera.imageGetRed(img, width, x, y) / 255.0
            g = camera.imageGetGreen(img, width, x, y) / 255.0
            b = camera.imageGetBlue(img, width, x, y) / 255.0
            r_sum += r
            g_sum += g
            b_sum += b
            samples += 1

    if samples == 0:
        return None

    avg_r = r_sum / samples
    avg_g = g_sum / samples
    avg_b = b_sum / samples

    def color_distance(c1, c2):
        return math.sqrt(
            (c1['r'] - c2['r'])**2 +
            (c1['g'] - c2['g'])**2 +
            (c1['b'] - c2['b'])**2
        )

    current = {'r': avg_r, 'g': avg_g, 'b': avg_b}

    red_dist   = color_distance(current, RED_COLOR)
    blue_dist  = color_distance(current, BLUE_COLOR)
    green_dist = color_distance(current, GREEN_COLOR)

    m = min(red_dist, blue_dist, green_dist)
    if m == red_dist:
        return 'red'
    elif m == blue_dist:
        return 'blue'
    else:
        return 'green'


# ---------- IK HELPERS ----------

def rpy_to_matrix(roll, pitch, yaw):
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)

    # R = Rz(yaw) * Ry(pitch) * Rx(roll)
    R = np.array([
        [cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr],
        [sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr],
        [  -sp,            cp*sr,            cp*cr]
    ])
    return R


def make_pose_matrix(position, rpy):
    x, y, z = position
    roll, pitch, yaw = rpy
    R = rpy_to_matrix(roll, pitch, yaw)
    T = np.eye(4)
    T[0:3, 0:3] = R
    T[0:3, 3]   = [x, y, z]
    return T


def goto_pose_with_ik(position, rpy):
    """Compute IK for a pose and send all 6 joint commands."""
    T = make_pose_matrix(position, rpy)

    # read current q from sensors
    q_current = [ps.getValue() for ps in arm_sensors]

    # run IK with initial guess
    q_sol = arm_ik.computeInverseKinematics(T, q_current)

    # send to motors
    for i, m in enumerate(arm_motors):
        m.setPosition(float(q_sol[i]))


# ----- MAIN LOOP -----
first_step = True

while robot.step(TIME_STEP) != -1:

    # On first iteration, store HOME_Q as whatever pose the arm starts in
    if first_step:
        HOME_Q = [ps.getValue() for ps in arm_sensors]
        first_step = False

    if counter <= 0:
        if state == WAITING:
            d = distance_sensor.getValue()
            wrist_angle = position_sensor.getValue()
            print(f"WAITING, d = {d}, wrist = {wrist_angle}")

            # Keep gripper open while idle
            for m in hand_motors:
                m.setPosition(GRIPPER_OPEN)

            block_present = (d < 500)
            at_home = abs(wrist_angle) < 0.1

            # Only trigger when a NEW block arrives while arm is at home
            if block_present and at_home and not last_block_present:
                print("NEW block under gripper → CLOSE + ANALYZE")

                # Close immediately while block is still under gripper
                for m in hand_motors:
                    m.setPosition(GRIPPER_CLOSE)

                state = ANALYZING
                counter = OPEN_CLOSE_STEPS  # give time for fingers to close

            last_block_present = block_present

        elif state == ANALYZING:
            color = get_dominant_color(camera)
            if color is None:
                print("Color detection failed, default to GREEN")
                detected_color = 'green'
            else:
                detected_color = color
            print(f"Color detected: {detected_color}")

            # choose drop pose based on color
            if detected_color == 'red':
                pose = RED_DROP_POSE
                print("Moving to RED crate (IK)")
            elif detected_color == 'blue':
                pose = BLUE_DROP_POSE
                print("Moving to BLUE crate (IK)")
            else:
                pose = GREEN_DROP_POSE
                print("Moving to GREEN crate (IK)")

            # IK → joint commands
            goto_pose_with_ik(pose["position"], pose["rpy"])

            state = MOVING_DROP
            counter = MOVE_TO_DROP_STEPS

        elif state == MOVING_DROP:
            # done waiting for move → release
            print("Releasing crate")
            for m in hand_motors:
                m.setPosition(GRIPPER_OPEN)

            state = RELEASING
            counter = OPEN_CLOSE_STEPS

        elif state == RELEASING:
            # send arm back to home joint configuration
            print("Rotating arm back to home")
            for i, m in enumerate(arm_motors):
                m.setPosition(HOME_Q[i])

            state = MOVING_HOME
            counter = MOVE_HOME_STEPS

        elif state == MOVING_HOME:
            # after going home, reset state
            print("Ready for next crate\n")
            state = WAITING
            detected_color = None
            counter = 0  # just in case

    counter -= 1
