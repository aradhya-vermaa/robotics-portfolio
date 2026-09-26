# arm_ik.py
import numpy as np
import kinematic_helpers as kh

class ArmIK:
    def __init__(self):
        pass

    # -------- forward kinematics using your T01..T56 --------
    def forward_kinematics(self, q):
        """
        q: 6-element joint array [q1..q6]
        returns 4x4 transform T06
        """
        T = np.eye(4)
        T = T @ kh.T01(q[0])
        T = T @ kh.T12(q[1])
        T = T @ kh.T23(q[2])
        T = T @ kh.T34(q[3])
        T = T @ kh.T45(q[4])
        T = T @ kh.T56(q[5])
        return T

    # -------- numeric IK (Jacobian transpose, position only) --------
    def compute_inverse_kinematics(self,
                                   target_T,
                                   q_init,
                                   max_iters=80,
                                   alpha=0.4,
                                   pos_tol=1e-3):
        """
        Basic numeric IK using Jacobian transpose on position only.

        target_T: 4x4 desired end-effector transform
        q_init:   6-element initial guess
        returns:  6-element joint array
        """
        q = np.array(q_init, dtype=float)

        for _ in range(max_iters):
            # current end-effector pose
            T = self.forward_kinematics(q)
            p = T[:3, 3]
            p_target = target_T[:3, 3]

            # position error
            e = p_target - p

            # stop if close enough
            if np.linalg.norm(e) < pos_tol:
                break

            # finite-difference Jacobian (position part only)
            J = np.zeros((3, 6))
            h = 1e-4
            for i in range(6):
                q_perturb = q.copy()
                q_perturb[i] += h
                Tp = self.forward_kinematics(q_perturb)
                pp = Tp[:3, 3]
                J[:, i] = (pp - p) / h

            # gradient-like update using Jacobian transpose
            dq = alpha * (J.T @ e)
            q += dq

        return q

    # CamelCase wrapper so your controller can call
    # arm_ik.computeInverseKinematics(T, q_current)
    def computeInverseKinematics(self,
                                 target_T,
                                 q_init,
                                 max_iters=80,
                                 alpha=0.4,
                                 pos_tol=1e-3):
        return self.compute_inverse_kinematics(
            target_T,
            q_init,
            max_iters=max_iters,
            alpha=alpha,
            pos_tol=pos_tol,
        )
