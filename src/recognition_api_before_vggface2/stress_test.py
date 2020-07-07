# import the necessary packages
from threading import Thread
import requests
import time

from urllib.parse import urljoin
import json
from PIL import Image

import helpers

# initialize the Keras REST API endpoint URL along with the input
# image path
BASE_API_URL = "http://localhost:5000/"


# initialize the number of requests for the stress test along with
# the sleep amount between requests
NUM_REQUESTS = 500
SLEEP_COUNT = 0.05
 

def call_predict_endpoint(n):
    from matplotlib import pyplot as plt
    from numpy import asarray, loadtxt

    image_path = "media/images/own_grady.jpg"

    # load the input image and construct the payload for the request
    image = open(image_path, "rb").read()
    # print(type(image))

    np_array_known_embedding = loadtxt('single_face_embedding.txt').view(float)
    # convert to bytes
    known_embedding = np_array_known_embedding.tobytes()

    payload = {
        "image": image,
        "known_embedding": known_embedding
    }

    MATCH_FACE_EMBEDDING_API_URL = urljoin(
        BASE_API_URL, '/match-known-face-embedding'
    )

    # submit the request
    response = requests.post(
        MATCH_FACE_EMBEDDING_API_URL, files=payload
    ).json()

    # ensure the request was sucessful
    if response["success"]:
        print("[INFO] thread {} OK".format(n))
 
    # otherwise, the request failed
    else:
        print("[INFO] thread {} FAILED".format(n))


# loop over the number of threads
for i in range(0, NUM_REQUESTS):
    # start a new thread to call the API
    t = Thread(target=call_predict_endpoint, args=(i,))
    t.daemon = True
    t.start()
    time.sleep(SLEEP_COUNT)
 
# insert a long sleep so we can wait until the server is finished
# processing the images
time.sleep(300)