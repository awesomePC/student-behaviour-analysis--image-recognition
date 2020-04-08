# Consuming the Keras REST API programmatically

# import the necessary packages
import os
import requests
from urllib.parse import urljoin
import json
from PIL import Image

import helpers
import settings

# initialize the Keras REST API endpoint URL along with the input
# image path
BASE_API_URL = "http://localhost:5003/"
# BASE_API_URL = "http://10.128.0.11:5003/"


def test_api_verify_genuine(image_path):
    # load the input image and construct the payload for the request
    image = open(image_path, "rb").read()

    payload = {
        "image": image
    }

    API_URL = urljoin(BASE_API_URL, '/verify-genuine')

    # submit the request
    response = requests.post(
        API_URL, files=payload
    ).json()

    return response


if __name__ == "__main__":
    from numpy import asarray, loadtxt

    IMAGE_PATH = "media/images/own_grady.jpg"
    
    ### 1 ###############
    response = test_api_verify_genuine(IMAGE_PATH)
    print(response)