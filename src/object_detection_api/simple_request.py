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
BASE_API_URL = "http://localhost:5005/"


def test_api_detect_objects(image_path):
    from matplotlib import pyplot as plt

    # load the input image and construct the payload for the request
    image = open(image_path, "rb").read()

    payload = {
        "image": image
    }

    API_DETECT_OBJECTS = urljoin(BASE_API_URL, '/detect-objects')

    # submit the request
    response = requests.post(
        API_DETECT_OBJECTS, files=payload
    ).json()

    return response

if __name__ == "__main__":
    from numpy import asarray, loadtxt
    from matplotlib import pyplot as plt

    from timeit import default_timer as timer
    from datetime import timedelta

    start = timer()

    IMAGE_PATH = "media/images/object_detection_input.jpg"
    

    # #### 2 ###############
    response = test_api_detect_objects(IMAGE_PATH)

    end = timer()
    print(timedelta(seconds=end-start))

    # # ensure the request was successful
    if response["success"]:
        print(response["labels"])
        print(response["conf"])
    else:
        print("Request failed")
