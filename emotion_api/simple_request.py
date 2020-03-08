# Consuming the Keras REST API programmatically

# import the necessary packages
import os
import json
import requests

from urllib.parse import urljoin
# from PIL import Image

# import settings

# initialize the Keras REST API endpoint URL along with the input
# image path
BASE_API_URL = "http://localhost:5002/"


def test_api_detect_emotions(image_path):
    files = {
        'image_file': open(image_path, "rb"), # image buffer
    }

    EMOTIONS_API_URL = urljoin(BASE_API_URL, '/detect-emotions')

    return requests.post(
        EMOTIONS_API_URL, files=files
    )


if __name__ == "__main__":
    # from numpy import asarray, loadtxt

    IMAGE_PATH = "media/images/n.jpg"
    
    #### 1 ###############
    response = test_api_detect_emotions(IMAGE_PATH)
    print(f"Response status code: {response.status_code}")
    print(response.json())
    # print(type(response.json()))
