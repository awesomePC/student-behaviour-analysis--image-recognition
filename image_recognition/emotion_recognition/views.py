from django.conf import settings

import json
import requests
from urllib.parse import urljoin


def detect_image_emotions(image_path):
    files = {
        'image_file': open(image_path, "rb"), # image buffer
    }

    EMOTIONS_API_URL = urljoin(
        settings.EMOTION_DETECTION_BASE_API_URL,
        '/detect-emotions'
    )

    response = requests.post(
        EMOTIONS_API_URL, files=files
    )

    if response.status_code == 200:
        parsed_response = response.json()

        # parsed_response
        all_emotions = parsed_response['all_emotions']
        topmost_emotion = parsed_response['topmost_emotion']

        return (all_emotions, topmost_emotion)
    else:
        return ([], [])