from django.conf import settings

import json
import requests
from urllib.parse import urljoin


def detect_face_emotion(face_array):
    """
    face emotion detection api consumption wrapper

    Args:
        face_array (ndarray): extracted face area in numpy array format

    Returns:
        tuple: all emotion and top most emotion
    """
    data = {'face': face_array.tolist()}

    EMOTIONS_API_URL = urljoin(
        settings.EMOTION_DETECTION_BASE_API_URL,
        '/detect-emotions'
    )

    response = requests.post(
        EMOTIONS_API_URL, json=data
    )

    if response.status_code == 200:
        parsed_response = response.json()

        # parsed_response
        all_emotions = parsed_response['all_emotions']
        topmost_emotion = parsed_response['topmost_emotion']

        return (all_emotions, topmost_emotion)
    else:
        return ([], [])


def verify_genuine(face_array):
    """
    verify genuine face

    Args:
        face_array (ndarray): extarcted face in numpy array format

    Returns:
        dict: dictionary containing face anti spoofing result
    """
    data = {'face': face_array.tolist()}

    FAKE_DETECTION_API_URL = urljoin(settings.FAKE_DETECTION_BASE_API_URL, '/verify-genuine')

    response = requests.post(
        FAKE_DETECTION_API_URL, json=data
    )
    if response.status_code == 200:
        parsed_response = response.json()
        return parsed_response
    else:
        return {}