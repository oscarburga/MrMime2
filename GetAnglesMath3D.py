import numpy as np

from Vec3D import Vec3
import math

from AsyncWorkerBase import log_safe

pi_half = math.pi * 0.5


# RShoulder, RElbow, RWrist, LShoulder, LElbow, LWrist, RHip, LHip
mppose_idxes = [12, 14, 16, 11, 13, 15, 24, 23]

names = ['HeadPitch',
         'HeadYaw',
         'RElbowRoll',
         'RShoulderRoll',
         'LElbowRoll',
         'LShoulderRoll',
         'RElbowYaw',
         'LElbowYaw'
         ]

idx_of = {
    'Nose': 0,
    'LEye': 2,
    'LEar': 7,
    'REye': 5,
    'REar': 8,
    'LMouth': 9,
    'RMouth': 10,
    'RShoulder': 12,
    'RElbow': 14,
    'RWrist': 16,
    'LShoulder': 11,
    'LElbow': 13,
    'LWrist': 15,
    'RHip': 24,
    'LHip': 23
}

bounds_of = {
    'HeadYaw': (-2.0857, 2.0857),
    'HeadPitch': (-0.6720, 0.5149),

    'RShoulderPitch': (-2.0857, 2.0857),
    'RShoulderRoll': (-1.3265, 0.3142),
    'RElbowYaw': (-2.0857, 2.0857),
    'RElbowRoll': (0.0349, 1.5446),
    'RWristYaw': (-1.8238, 1.8238),

    'LShoulderPitch': (-2.0857, 2.0857),
    'LShoulderRoll': (-0.3142, 1.3265),
    'LElbowYaw': (-2.0857, 2.0857),
    'LElbowRoll': (-1.5446, -0.0349),
    'LWristYaw': (-1.8238, 1.8238)
}


def get_head_angles(get_as_vec, torso_front, torso_up) -> (float, float):
    """

    Args:
        get_as_vec: get_as_vec function to obtain face landmark coordinates
        torso_front: torso front vector
        torso_up: torso up vector

    Returns:
        Estimation of head (yaw, pitch) angles

    """
    nose = get_as_vec('Nose')

    l_ear = get_as_vec('LEar')
    r_ear = get_as_vec('REar')

    l_eye = get_as_vec('LEye')
    r_eye = get_as_vec('REye')

    l_mouth = get_as_vec('LMouth')
    r_mouth = get_as_vec('RMouth')

    # Get eyes and nose normal
    l_unit = (l_eye - nose).get_normal()
    r_unit = (r_eye - nose).get_normal()
    eyes_normal = (l_unit % r_unit).get_normal()

    # Get nose and mouth normal
    l_unit = (l_mouth - nose).get_normal()
    r_unit = (r_mouth - nose).get_normal()
    mouth_normal = (l_unit % r_unit).get_normal()

    # Get face front vector
    face_front = ((eyes_normal + mouth_normal) * 0.5).get_normal()

    # Get face right vector
    face_right = (r_ear - l_ear).get_normal()
    face_right += (r_mouth - l_mouth).get_normal()
    face_right += (r_eye - l_eye).get_normal()
    face_right = (face_right / 3).get_normal()

    face_front_side_proj = face_front.project_onto_plane(face_right).get_normal()
    torso_front_side_proj = torso_front.project_onto_plane(face_right).get_normal()

    # negative on face right to use face_left instead.
    pitch = Vec3.signed_angle(torso_front_side_proj, face_front_side_proj, -face_right)

    # for yaw, get angle of face front with torso front
    torso_front_proj = torso_front.project_onto_plane(torso_up)
    face_front_proj = face_front.project_onto_plane(torso_up)
    yaw = Vec3.signed_angle(torso_front_proj, face_front_proj, torso_up)

    # print(f'Pitch = {pitch}')
    return pitch, yaw


def get_arm_angles(get_as_vec, front_vector, right_vector):
    shoulder = get_as_vec('RShoulder')
    elbow = get_as_vec('RElbow')
    wrist = get_as_vec('RWrist')

    min_sp, max_sp = bounds_of['RShoulderPitch']
    angle_candidates = np.arange(min_sp, max_sp, (max_sp - min_sp) / 80)

    best_angle_set = {}
    min_total_dist_squared = math.inf
    print('-shoulder loop-')
    for shoulder_pitch in angle_candidates:
        rot_by_pitch = front_vector.rotate_around_vector(right_vector, shoulder_pitch)
        arm_plane_normal = right_vector % rot_by_pitch.get_normal()
        arm_plane_normal = arm_plane_normal.get_normal()

        shoulder_to_elbow = elbow - shoulder
        arm_vec_proj = shoulder_to_elbow.project_onto_plane(arm_plane_normal)
        shoulder_roll = Vec3.signed_angle(rot_by_pitch, arm_vec_proj, arm_plane_normal)

        rot_by_both = rot_by_pitch.rotate_around_vector(arm_plane_normal, shoulder_roll)
        rot_by_both *= shoulder_to_elbow.size()

        shoulder_dist_sq = (rot_by_both - shoulder_to_elbow).size2()
        if shoulder_dist_sq < min_total_dist_squared:
            min_total_dist_squared = shoulder_dist_sq
            best_angle_set = {'pitch': shoulder_pitch, 'roll': shoulder_roll}
            print('new min: ', min_total_dist_squared, best_angle_set)

    return best_angle_set['pitch'], best_angle_set['roll']


def get_shoulder_angles(front_vector, arm_vec, side_axis_ref) -> (float, float):
    """
    Estimates shoulder roll and pitch.
    Args:
        front_vector: Torso front vector
        arm_vec: Shoulder-to-elbow vector
        side_axis_ref: Reference axis for this side (right or left vector)
    Returns:
        Tuple of floats (roll, pitch) corresponding to the shoulder angles.
    """
    # shoulder roll: project onto torso plane and get angle.
    # Angle is measured starting from the side_axis_ref. This way we do
    # not depend on torso_down for the angle
    # arm_tp = arm_vec.project_onto_plane(front_vector).get_normal()
    # shoulder_roll = Vec3.signed_angle(side_axis_ref, arm_tp, front_vector)

    # shoulder pitch: project onto the side plane and get angle with torso
    arm_sp = arm_vec.project_onto_plane(side_axis_ref).get_normal()
    front_sp = front_vector.project_onto_plane(side_axis_ref).get_normal()
    shoulder_pitch = Vec3.signed_angle(-front_sp, arm_sp, -side_axis_ref)

    arm_plane_normal = -(side_axis_ref % arm_sp).get_normal()
    arm_projected = arm_vec.get_normal().project_onto_plane(arm_plane_normal).get_normal()
    shoulder_roll = Vec3.signed_angle(side_axis_ref, arm_projected, arm_plane_normal)

    return shoulder_roll, shoulder_pitch


def get_elbow_angles(shoulder, elbow, wrist) -> (float, float):
    """
    Estimates elbow roll and yaw. TODO: Actually calculate elbow yaw
    Args:
        shoulder: shoulder joint location
        elbow: elbow joint location
        wrist: wrist joint location
    Returns:
        Tuple of floats (roll, yaw) corresponding to the elbow angles
    """
    elbow_to_shoulder = (shoulder - elbow).get_normal()
    elbow_to_wrist = (wrist - elbow).get_normal()
    cross = (elbow_to_wrist % elbow_to_shoulder).get_normal()
    elbow_roll = Vec3.signed_angle(elbow_to_wrist, elbow_to_shoulder, cross)
    # since elbow roll is measured from a straight-arm position, take it as 180 - angle
    elbow_roll = math.pi - elbow_roll
    return elbow_roll, 0


def get_angles_math_3d(landmark_tuples):

    if not landmark_tuples or len(landmark_tuples) != 33:
        return [None] * len(names)

    def get_as_vec(name):
        return Vec3(*landmark_tuples[idx_of[name]])

    def clamp_angle(name, x):
        _min, _max = bounds_of[name]
        out = min(x, _max)
        out = max(out, _min)
        if out != x:
            log_safe(f'{name}: clamped from {x} to {out}')
        return out

    l_shoulder = get_as_vec('LShoulder')
    l_elbow = get_as_vec('LElbow')
    l_hip = get_as_vec('LHip')
    l_wrist = get_as_vec('LWrist')
    r_shoulder = get_as_vec('RShoulder')
    r_elbow = get_as_vec('RElbow')
    r_hip = get_as_vec('RHip')
    r_wrist = get_as_vec('RWrist')

    # Get a frontal vector as the mean of the 4 normal vectors
    # formed by the shoulder and hip joints
    torso = [l_shoulder, l_hip, r_hip, r_shoulder]
    front_vector = Vec3()
    for i in range(4):
        left = torso[(i-1) % 4]
        mid = torso[i]
        right = torso[(i+1) % 4]
        cross = (right - mid) % (left - mid)
        front_vector += cross.get_normal()
    front_vector /= 4.0
    front_vector = front_vector.get_normal()

    # Get a right vector as the straight line between the shoulders
    right_vector = (r_shoulder - l_shoulder).get_normal()

    # Get up vector as the cross of front and right
    up_vector = (right_vector % front_vector).get_normal()

    # Correct the right vector
    # right_vector = front_vector % up_vector

    # Get left shoulder angles
    left_axis_arm_ref = (-right_vector).project_onto_plane(front_vector).get_normal()
    l_arm = (l_elbow - l_shoulder).get_normal()

    l_shoulder_roll, l_shoulder_pitch = get_shoulder_angles(front_vector,
                                                            l_arm,
                                                            left_axis_arm_ref)

    # l_shoulder_roll = pi_half - l_shoulder_roll
    l_shoulder_roll += pi_half
    l_shoulder_pitch *= -1.0

    # Get right shoulder angles
    right_axis_arm_ref = right_vector.project_onto_plane(front_vector).get_normal()
    r_arm = (r_elbow - r_shoulder).get_normal()

    r_shoulder_roll, r_shoulder_pitch = get_shoulder_angles(front_vector,
                                                            r_arm,
                                                            right_axis_arm_ref)

    r_shoulder_roll += pi_half
    r_shoulder_roll *= -1.0

    # left elbow angle
    l_elbow_roll, l_elbow_yaw = get_elbow_angles(l_shoulder,
                                                 l_elbow,
                                                 l_wrist)
    # multiply by minus 1 to adjust for NAO asymmetric angle axes...
    l_elbow_roll *= -1.0

    #right elbow angle
    r_elbow_roll, r_elbow_yaw = get_elbow_angles(r_shoulder,
                                                 r_elbow,
                                                 r_wrist)

    # head angles
    head_pitch, head_yaw = get_head_angles(get_as_vec, front_vector, up_vector)

    # r shoulder test angles
    # r_shoulder_pitch, r_shoulder_roll = get_arm_angles(get_as_vec, front_vector, right_vector)

    out_dic = {
        # 'HeadPitch': head_pitch
        'HeadYaw': head_yaw,
        'RShoulderRoll': r_shoulder_roll,
        'RShoulderPitch': r_shoulder_pitch,
        # 'RElbowYaw': r_elbow_yaw,
        # 'RElbowRoll': r_elbow_roll,
        'LShoulderRoll': l_shoulder_roll,
        'LShoulderPitch': l_shoulder_pitch
        # 'LElbowYaw': l_elbow_yaw,
        # 'LElbowRoll': l_elbow_roll
    }

    for name, angle in out_dic.items():
        out_dic[name] = clamp_angle(name, angle)

    return out_dic
