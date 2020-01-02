#https://blog.keras.io/building-a-simple-keras-deep-learning-rest-api.html

# advanced 
# https://www.pyimagesearch.com/2018/01/29/scalable-keras-deep-learning-rest-api/
# https://www.pyimagesearch.com/2018/02/05/deep-learning-production-keras-redis-flask-apache/

# import the necessary packages
import os, random
import io
import json
import logging

import flask
from flask_restful import Resource, Api, reqparse
import werkzeug

import numpy as np
from fer import FER
import cv2

import settings

# # error logging
# import sentry_sdk
# from sentry_sdk.integrations.flask import FlaskIntegration

# sentry_sdk.init(
#     dsn="https://74dd13493d6342be85d7f279e2fa6fbd@sentry.io/1866536",
#     integrations=[FlaskIntegration()]
# )

# initialize our Flask application and the Keras model
app = flask.Flask(__name__)

# init Flask-RESTful API
api = Api(app)

# init request parser
parse = reqparse.RequestParser()

# init Emotion detector
detector = FER(mtcnn=True)


class EmotionsDetector(Resource):
    """
    Detect emotions from image
    """
    def post(self):
        # parse uploaded image file
        parse.add_argument(
            'image_file', 
            type=werkzeug.datastructures.FileStorage,
            location='files', required=True
        )
        args = parse.parse_args()
        image_bytes = args['image_file'].read()
    
        img = cv2.imdecode(np.fromstring(image_bytes, np.uint8), cv2.IMREAD_UNCHANGED)

        emotions = detector.detect_emotions(
            img
        )
        if emotions:
            topmost_emotion = detector.top_emotion(img)
        else:
            topmost_emotion = (None, None)

        return {
            'all_emotions': emotions,
            'topmost_emotion': topmost_emotion,
        }


# API
api.add_resource(EmotionsDetector, '/detect-emotions')


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