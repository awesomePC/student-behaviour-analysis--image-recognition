# import the necessary packages
import os, random
import io
import json
import logging

import flask
from flask import request
from flask_restful import Resource, Api, reqparse
import werkzeug

import cv2
import numpy as np
from PIL import Image
import operator

from test import verify_real
import helpers

# initialize our Flask application and the Keras model
app = flask.Flask(__name__)

# init Flask-RESTful API
api = Api(app)


@app.route("/verify-real", methods=["POST"])
def api_verify_real():
    """
    API to check is real or fake image
    """
    data = {}
    # print(flask.request.data)

    # ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            # read the image in PIL format
            realtime_image = flask.request.files["image"].read()
            realtime_pil_image = Image.open(io.BytesIO(realtime_image)).convert('RGB')
            np_realtime_image_array = np.asarray(realtime_pil_image)

            np_realtime_image_array = cv2.cvtColor(np_realtime_image_array, cv2.COLOR_RGB2BGR) 

            label, score, image_bbox = encoded_img = verify_real(
                np_realtime_image_array,
                model_dir="./resources/anti_spoof_models",
            )

            if label == 1:
                label = "real"
            else:
                label = "fake"
            
            data["label"] = label
            data["score"] = score
            data["image_bbox"] = image_bbox

            # indicate that the request was a success
            data["success"] = True

            # app.logger.info("Recognized faces highlighted successfully.")
        else:
            data["success"] = False
            data["reason"] = "Error .. reading uploaded image"
    else:
        data["success"] = False
        reason = "Error .. only 'POST' method allowed"
        data["reason"] = reason
        app.logger.error(reason)
        
    # return the data dictionary as a JSON response
    return json.dumps(data, cls=helpers.MyEncoder)


# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
    print(
        "* starting Flask server..."
        "please wait until server has fully started"
    )
    app.run(
        debug=False,threaded = False,
        host="0.0.0.0",
        port=5003
    )