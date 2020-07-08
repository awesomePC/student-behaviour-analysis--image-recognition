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


if __name__ == "__main__":
    # from numpy import asarray, loadtxt

    img_face = cv2.imread("media/cropped-faces/happy.png")

    #### 1 ###############
    response = test_api_detect_emotions(img_face)
    print(f"Response status code: {response.status_code}")
    print(response.json())
    # print(type(response.json()))
