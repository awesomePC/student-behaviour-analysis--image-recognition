import os, random

import flask
import io
import json

import numpy as np
from PIL import Image

import imutils
import cv2

# # error logging
# import sentry_sdk
# from sentry_sdk.integrations.flask import FlaskIntegration

# sentry_sdk.init(
#     dsn="https://8d26f88b68514b468461247a6c09c57b@o387239.ingest.sentry.io/5222221",
#     integrations=[FlaskIntegration()]
# )

# initialize our Flask application and the Keras model
app = flask.Flask(__name__)

from settings import (
    DETECTOR_NUMBER, 
    DIR_MODEL_DETECTION, 
    DIR_MEDIA
)
import helpers

from detector import (
    ObjectDetectorModels,
    ObjectDetector
)

model_detector = ObjectDetectorModels(DETECTOR_NUMBER)
object_detector = ObjectDetector(
    model=model_detector, path=DIR_MODEL_DETECTION
)

from nb_utils.pil_helper import save_image
from nb_utils.basic_file_folder_creation import generate_filename

### API's
@app.route("/detect-objects", methods=["POST"])
def api_detect_objects():
    """
    detect objects in image
    """
    # initialize the data dictionary that will be returned from the
    # view
    data = {}

    # ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            # read the image in PIL format
            image = flask.request.files["image"].read()
            pil_image = Image.open(io.BytesIO(image))

            input_image_path = save_image(pil_image)
            output_image_path = generate_filename(extension=".jpg", base_folder=DIR_MEDIA)
            detections = object_detector.detect(
                input_image_path,
                output_image_path
            )

            highlighted_image = Image.open(output_image_path)
            
            encoded_img = helpers.pil_to_base64(
                highlighted_image
            )

            data["detection_count"] = len(detections)
            data["detections"] = detections
            data["encoded_img"] = encoded_img

            # indicate that the request was a success
            data["success"] = True
        else:
            data["success"] = False
            data["reason"] = "Error .. reading uploaded image"
    else:
        data["success"] = False
        data["reason"] = "Error .. only 'POST' method allowed"
        
    # return the data dictionary as a JSON response
    return json.dumps(data, cls=helpers.MyEncoder)

# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
    print(
        "* Loading Keras model and Flask starting server..."
        "please wait until server has fully started"
    )
    app.run(
        debug=False,threaded = False,
        host="0.0.0.0",
        port=5005
    )