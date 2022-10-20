import GetAnglesFromPoints2D as geom
from GetAnglesMath3D import get_angles_math_3d

from AsyncWorkerBase import log_safe

def gen_dict(joints, angles):
    return {x: y for x, y in zip(joints, angles)}


class BaseMpPoseProcessor:

    def get_pose_dict(self, landmarks):
        if len(landmarks):
            angles = geom.get_angles_from_results_2d(landmarks)
            joint_dict = gen_dict(geom.names, angles)
            return joint_dict
        return {}


class MpPoseProcessorMath3D(BaseMpPoseProcessor):
    def __init__(self, num_frames_to_avg=3):
        self.num_frames_to_avg = max(num_frames_to_avg, 1)
        self.join_dict_acum = {}
        self.current_joint_dict = {}

    def update_joint_angle(self, name, angle):
        idx, summed, angles = self.join_dict_acum.setdefault(name, [0, 0.0, []])

        if len(angles) < self.num_frames_to_avg:
            angles.append(angle)
        else:
            summed -= angles[idx]
            angles[idx] = angle
            idx = (idx + 1) % self.num_frames_to_avg

        summed += angle
        self.join_dict_acum[name] = idx, summed, angles
        self.current_joint_dict[name] = summed / len(angles)
        # log_safe(f'updated joint angle {name}={angles}')

    def get_pose_dict(self, landmarks):
        if len(landmarks):
            joint_dict = get_angles_math_3d(landmarks)
            for joint, angle in joint_dict.items():
                self.update_joint_angle(joint, angle)
            return self.current_joint_dict
        return {}
