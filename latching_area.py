
import cv2 as cv
from pupil_apriltags import Detector
import numpy as np
import csv
import os

# ==========================================
# 1. EXPERIMENT & HARDWARE CONFIGURATION
# ==========================================
TOTAL_EDGE_OFFSET = 0.11  # 11 cm total offset

# FIXED ROBOT q2 COORDINATES FROM CAMERA (meters)
FIXED_X, FIXED_Y, FIXED_Z = 0.03, 0.12, 0.20  

CSV_FILENAME = "experiment_data.csv"
TEST_NUMBER = input("Enter Test Number for this run: ").strip()

# Camera Intrinsics & Tag Setup
CAMERA_PARAMS = [580.0, 580.0, 960.0, 540.0]
TAG_SIZE = 0.059  # 5.9 cm tag size

detector = Detector(families='tag36h11')

cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

# ==========================================
# 2. VIDEO RECORDING SETUP (TOGGLEABLE)
# ==========================================
RECORD_VIDEO = False
out_video = None
video_filename = f"test_{TEST_NUMBER}.mp4"

if RECORD_VIDEO:
    frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv.CAP_PROP_FPS)) or 30
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    out_video = cv.VideoWriter(video_filename, fourcc, fps, (frame_width, frame_height))

print(f"--- Running Test #{TEST_NUMBER} ---")
print("Waiting for initial AprilTag detection...")

latest_cam_coords = None
latest_rel_coords = None
latest_angle_deg = None
latest_distance_cm = None
printed_initial_readout = False

# ==========================================
# 3. DETECTION LOOP
# ==========================================
while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        break

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    results = detector.detect(gray, estimate_tag_pose=True, camera_params=CAMERA_PARAMS, tag_size=TAG_SIZE)
    
    for r in results:
        # q1 = Moving Robot center coordinates from camera
        q1_x = float(r.pose_t[0][0])
        q1_y = float(r.pose_t[1][0])
        q1_z = float(r.pose_t[2][0])

        # q2 = Fixed Robot coordinates
        q2_x, q2_y, q2_z = FIXED_X, FIXED_Y, FIXED_Z

        # Relative vector between q1 (moving) and q2 (fixed)
        dx = q2_x - q1_x
        dy = q2_y - q1_y
        dz = q2_z - q1_z

        # Center-to-center distance
        center_distance = np.sqrt(dx**2 + dy**2 + dz**2)
        raw_edge_distance = center_distance - TOTAL_EDGE_OFFSET

        # Zero-threshold for touching edges (< 0.5 cm)
        if raw_edge_distance < 0.005:
            edge_distance_cm = 0.0
            angle_deg = 0.0
            rel_x, rel_y, rel_z = 0.0, 0.0, 0.0
        else:
            edge_distance_m = float(raw_edge_distance)
            edge_distance_cm = edge_distance_m * 100.0
            
            # Scale relative vector to match edge distance
            scale = edge_distance_m / center_distance if center_distance > 0 else 0
            rel_x = dx * scale
            rel_y = dy * scale
            rel_z = dz * scale

            # Angle between line q1->q2 and horizontal +X line at q1
            angle_rad = np.arctan2(dy, dx)
            angle_deg = abs(float(np.degrees(angle_rad)))

        # Format current frame strings
        curr_cam_coords = f"({q1_x:.2f}, {q1_y:.2f}, {q1_z:.2f})"
        curr_rel_coords = f"({rel_x:.2f}, {rel_y:.2f}, {rel_z:.2f})"
        curr_angle_deg = f"{angle_deg:.1f}"
        curr_distance_cm = f"{edge_distance_cm:.1f}"

        # LOCK IN VALUES ON FIRST DETECTION SO TERMINAL & CSV ARE 100% IDENTICAL
        if not printed_initial_readout:
            latest_cam_coords = curr_cam_coords
            latest_rel_coords = curr_rel_coords
            latest_angle_deg = curr_angle_deg
            latest_distance_cm = curr_distance_cm

            print("\n=== INITIAL EDGE-TO-EDGE STARTING POINT ===")
            print(f"Cam Tag Center (q1): {latest_cam_coords}")
            print(f"Edge Rel Pos:        {latest_rel_coords}")
            print(f"Edge Distance:       {latest_distance_cm} cm")
            print(f"Angle (q1 -> q2):    {latest_angle_deg}°")
            print("===========================================")
            print("Press 'q' in camera window when finished.\n")
            printed_initial_readout = True

        # Draw overlays on video feed
        ptA, ptB, ptC, ptD = [tuple(map(int, pt)) for pt in r.corners]
        cv.line(frame, ptA, ptB, (0, 255, 0), 2)
        cv.line(frame, ptB, ptC, (0, 255, 0), 2)
        cv.line(frame, ptC, ptD, (0, 255, 0), 2)
        cv.line(frame, ptD, ptA, (0, 255, 0), 2)

        text = f"Dist: {curr_distance_cm}cm, Ang: {curr_angle_deg}deg"
        cv.putText(frame, text, ptA, cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv.LINE_AA)

    if RECORD_VIDEO and out_video is not None:
        out_video.write(frame)

    cv.imshow('AprilTag Tracker', frame)
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
if RECORD_VIDEO and out_video is not None:
    out_video.release()
cv.destroyAllWindows()

# ==========================================
# 4. CSV SAVE LOGIC
# ==========================================
headers = ["test_id", "cam_p_m", "rel_p_m", "theta_deg", "dist_cm"]
rows = []

if os.path.exists(CSV_FILENAME):
    with open(CSV_FILENAME, mode='r', newline='') as f:
        file_lines = list(csv.reader(f))
        if len(file_lines) > 2:
            for line in file_lines[2:]:
                if line and line[0] != str(TEST_NUMBER):
                    rows.append(line)

if latest_cam_coords is not None:
    new_row = [
        str(TEST_NUMBER),
        latest_cam_coords,
        latest_rel_coords,
        latest_angle_deg,
        latest_distance_cm
    ]
    rows.append(new_row)
    rows.sort(key=lambda r: int(r[0]) if r[0].isdigit() else r[0])

with open(CSV_FILENAME, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([f"# Ref Fixed Robot Pose (m): x_f={FIXED_X}, y_f={FIXED_Y}, z_f={FIXED_Z} | Edge Offset={TOTAL_EDGE_OFFSET}m"])
    writer.writerow(headers)
    writer.writerows(rows)

print(f"Data successfully saved to {CSV_FILENAME}")
