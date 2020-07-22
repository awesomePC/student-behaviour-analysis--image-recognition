# Consuming the Keras REST API programmatically

# import the necessary packages
import os
import json
import requests

from urllib.parse import urljoin
# from PIL import Image
import cv2

# import settings

# initialize the Keras REST API endpoint URL along with the input
# image path
BASE_API_URL = "http://localhost:5002/"


def test_api_detect_emotions(face_array):
    data = {'face': face_array.tolist()}

    EMOTIONS_API_URL = urljoin(BASE_API_URL, '/detect-emotions')

    return requests.post(
        EMOTIONS_API_URL, json=data
    )

def test_api_detect_emotions(image_path):
    # load the input image and construct the payload for the request
    image = open(image_path, "rb").read()

    payload = {
        "image": image
    }

    EMOTIONS_API_URL = urljoin(BASE_API_URL, '/detect-emotions')

    # submit the request
    response = requests.post(
        EMOTIONS_API_URL, files=payload
    )
    if response.status_code == 200:
        return response.json()
    else:
        print("Emotion detection request failed")
        return {}


if __name__ == "__main__":
    image_path = "media/images/happy_vishal.jpg"

    #### 1 ###############
    response = test_api_detect_emotions(image_path)
    print(response)
