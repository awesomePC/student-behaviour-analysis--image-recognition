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
from flask import request
from flask_restful import Resource, Api, reqparse
import werkzeug

import cv2
import numpy as np
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model

import operator

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
CKPT_DIR = "ckpt"

le_filename =  os.path.join(CKPT_DIR, "label_encoder_classes.npy")
labelencoder = LabelEncoder()
labelencoder.classes_ = np.load(le_filename)

# model_file = os.path.join(CKPT_DIR, "inceptionresnetv2_model.best.hdf5")
model_file = os.path.join(CKPT_DIR, "mobilenet_model.best.hdf5")
model = load_model(model_file)


def truncate_float(value, digits_after_point=2):
    """
    Truncate long float numbers
    >>> truncate_float(1.1477784, 2)
       1.14
    """
    pow_10 = 10 ** digits_after_point
    return (float(int(value * pow_10))) / pow_10

def test_single_image(img_single_face, normalize=True):

    if img_single_face.any():
        # vgg16 model requires normalized image
        # whereas resnet50, xception dosnot work properly on normalized image -- it may give wrong result if image is normalized
        if normalize:
            img_single_face = img_single_face.astype(float) / 255

        expanded_img_single_face = np.expand_dims(img_single_face, axis=0)
        pred = model.predict(expanded_img_single_face)

        # import pdb; pdb.set_trace()

        prob_result = [truncate_float(value, 3) for value in pred[0]]
        # get a dictionary of {'classname', 'probability'}
        prob_per_class_dict = dict(zip(labelencoder.classes_, prob_result))
        # print(f"\n prob_per_class_dict : {prob_per_class_dict}")
        
        # get max class name
        predicted_class = max(prob_per_class_dict.items(), key=operator.itemgetter(1))[0]
        # print(f'\n predicted_class : {predicted_class}')

        predicted_prob = prob_per_class_dict[predicted_class]
        # print(f'\n predicted probability : {predicted_prob}')

        # return {
        #     'all_emotions': [
        #         {
        #             'emotions': prob_per_class_dict,
        #         }
        #     ],
        #     'topmost_emotion': [predicted_class, predicted_prob]
        # }

        topmost_emotion = (predicted_class, predicted_prob)
        return (prob_per_class_dict, topmost_emotion)
    else:
        print(f"Skipping.. No face found ")
        return (None, None)


# class EmotionsDetector(Resource):
#     """
#     Detect emotions from image
#     """
#     def post(self):
#         # # parse uploaded image file
#         # parse.add_argument(
#         #     'image_file', 
#         #     type=werkzeug.datastructures.FileStorage,
#         #     location='files', required=True
#         # )
#         # args = parse.parse_args()
#         # image_bytes = args['image_file'].read()

#         data = request.json
#     params = data['params']
#     arr = np.array(data['arr'])

#         img_face = cv2.imdecode(np.fromstring(image_bytes, np.uint8), cv2.IMREAD_UNCHANGED)

#         prob_per_class_dict, topmost_emotion = test_single_image(img_face, normalize=False)
        
#         return {
#             'all_emotions': emotions,
#             'topmost_emotion': topmost_emotion,
#         }


@app.route('/detect-emotions', methods=['POST'])
def detect_emotions():
    data = request.json
    face_array = np.array(data['face'])

    # import pdb;pdb.set_trace()

    prob_per_class_dict, topmost_emotion = test_single_image(face_array, normalize=False)
    
    return {
        'all_emotions': prob_per_class_dict,
        'topmost_emotion': topmost_emotion,
    }

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