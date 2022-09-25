import GetAnglesFromPoints2D as geom
from GetAnglesMath3D import get_angles_math_3d


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

    def get_pose_dict(self, landmarks):
        if len(landmarks):
            joint_dict = get_angles_math_3d(landmarks)
            return joint_dict
        return {}
