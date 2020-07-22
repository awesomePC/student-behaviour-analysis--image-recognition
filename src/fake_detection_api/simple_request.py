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
BASE_API_URL = "http://localhost:5003/"


def test_api_verify_real(image_path):
    # load the input image and construct the payload for the request
    image = open(image_path, "rb").read()

    payload = {
        "image": image
    }

    FAKE_DETECTION_API_URL = urljoin(BASE_API_URL, '/verify-real')

    return requests.post(
        FAKE_DETECTION_API_URL, files=payload
    )


if __name__ == "__main__":
    # from numpy import asarray, loadtxt

    # image_file="media/images/own_grady.jpg"
    image_file  = "media/images/h.png"

    response = test_api_verify_real(image_file)
    print(f"Response status code: {response.status_code}")
    print(response.json())

    # label, score, image_bbox = verify_real(image, model_dir="./resources/anti_spoof_models", device_id="0")
    
    # if label == 1:
    #     print("Real Face. Score: {:.2f}.".format(score))
    #     result_text = "RealFace Score: {:.2f}".format(score)
    #     color = (255, 0, 0)
    # else:
    #     print("Fake Face. Score: {:.2f}.".format(score))
    #     result_text = "FakeFace Score: {:.2f}".format(score)
    #     color = (0, 0, 255)

    # print("\n")
    # print(f"Face box: {image_bbox}")

