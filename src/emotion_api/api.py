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

from nb_utils.pil_helper import save_image
from nb_utils.basic_file_folder_creation import generate_filename


# # error logging
# import sentry_sdk
# from sentry_sdk.integrations.flask import FlaskIntegration

# sentry_sdk.init(
#     dsn="https://74dd13493d6342be85d7f279e2fa6fbd@sentry.io/1866536",
#     integrations=[FlaskIntegration()]
# )

from fer_detect_emotion import detect_emotions

# initialize our Flask application and the Keras model
app = flask.Flask(__name__)

# init Flask-RESTful API
api = Api(app)

# init request parser
parse = reqparse.RequestParser()


@app.route('/detect-emotions', methods=['POST'])
def api_detect_emotions():
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
            emotions, top_emotion = detect_emotions(
                input_image_path
            )

            data["emotions"] = emotions
            data["top_emotion"] = top_emotion

            # indicate that the request was a success
            data["success"] = True
        else:
            data["success"] = False
            data["reason"] = "Error .. reading uploaded image"
    else:
        data["success"] = False
        data["reason"] = "Error .. only 'POST' method allowed"
        
    # return the data dictionary as a JSON response
    return flask.jsonify(data)



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
        port=5002
    )