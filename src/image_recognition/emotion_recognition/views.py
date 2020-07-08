from django.conf import settings

import json
import requests
from urllib.parse import urljoin


def detect_image_emotions(face_array):
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