#https://blog.keras.io/building-a-simple-keras-deep-learning-rest-api.html

# advanced 
# https://www.pyimagesearch.com/2018/01/29/scalable-keras-deep-learning-rest-api/
# https://www.pyimagesearch.com/2018/02/05/deep-learning-production-keras-redis-flask-apache/

# import the necessary packages
import os, random

import flask
import io
import json

from PIL import Image
import numpy as np

import settings
import helpers

from face_verification import (
    init_face_detector,
    load_models,
    read_image,
    detect_faces,
    detect_extract_faces,
    extract_save_face,
    get_embedding,
    get_faces_and_embeddings,
    verify_face_matching,
    highlight_faces,
    highlight_recognized_faces
)

# error logging
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://8d26f88b68514b468461247a6c09c57b@o387239.ingest.sentry.io/5222221",
    integrations=[FlaskIntegration()]
)

# initialize our Flask application and the Keras model
app = flask.Flask(__name__)


### API's
@app.route("/get-face-count", methods=["POST"])
def get_face_count():
    """
    Get face count in image
    """
    # initialize the data dictionary that will be returned from the
    # view
    data = {}

    # ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            # read the image in PIL format
            image = flask.request.files["image"].read()
            pil_image = Image.open(io.BytesIO(image)).convert('RGB')
            
            np_image_array = np.asarray(pil_image)

            detected_faces = detect_faces(
                np_image_array
            )
            
            data["face_count"] = len(detected_faces)
            data["detected_faces"] = detected_faces

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


@app.route("/hightlight-faces", methods=["POST"])
def api_highlight_faces():
    """
    highlight_faces in image
    """
    # initialize the data dictionary that will be returned from the
    # view
    data = {}

    # ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            # read the image in PIL format
            image = flask.request.files["image"].read()
            pil_image = Image.open(io.BytesIO(image)).convert('RGB')

            np_image_array = np.asarray(pil_image)

            detected_faces = detect_faces(
                np_image_array
            )
            
            highlighted_image = highlight_faces(pil_image, detected_faces)
            
            encoded_img = helpers.pil_to_base64(
                highlighted_image
            )

            # import pdb;pdb.set_trace()

            data["face_count"] = len(detected_faces)
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
    return flask.jsonify(data)

@app.route("/hightlight-recognized-faces", methods=["POST"])
def api_hightlight_recognized_faces():
    """
    hightlight-recognized-faces photo faces
    """
    data = {}
    # print(flask.request.data)

    # ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            # read the image in PIL format
            realtime_image = flask.request.files["image"].read()
            realtime_pil_image = Image.open(io.BytesIO(realtime_image)).convert('RGB')
            # np_realtime_image_array = np.asarray(realtime_pil_image)


            # read the recognized_faces dict passed as json
            str_json = flask.request.files["json"].read()
            json_data = json.loads(str_json)

            recognized_faces = json_data['recognized_faces']

            hightlighted_pil_image = highlight_recognized_faces(
                realtime_pil_image, recognized_faces
            )

            encoded_img = helpers.pil_to_base64(
                hightlighted_pil_image
            )
            data["encoded_img"] = encoded_img

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
    return flask.jsonify(data)

@app.route("/extract-faces-and-embeddings", methods=["POST"])
def api_extract_faces_and_embeddings():
    """
    highlight_faces in image
    """
    # initialize the data dictionary that will be returned from the
    # view
    data = {}

    # ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            # read the image in PIL format
            image = flask.request.files["image"].read()
            pil_image = Image.open(io.BytesIO(image)).convert('RGB')

            np_image_array = np.asarray(pil_image)

            detected_faces, extracted_faces, face_embeddings = get_faces_and_embeddings(
                np_image_array
            )

            data["face_count"] = len(detected_faces)
            data["detected_faces"] = detected_faces
            data["extracted_faces"] = extracted_faces
            data["face_embeddings"] = face_embeddings

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


@app.route("/compare-face-embedding", methods=["POST"])
def api_compare_face_embedding():
    """
    Match known face embedding with realtime face embedding
    """
    data = {}

    # ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        if flask.request.files.get("known_embedding"):
            # read the known face embedding
            str_known_embedding = flask.request.files["known_embedding"].read()
            np_known_face_embedding = np.frombuffer(str_known_embedding, dtype='float64')

            # print(type(np_known_face_embedding))
            # print(np_known_face_embedding.shape)

            # read the realtime face embedding
            str_realtime_embedding = flask.request.files["realtime_embedding"].read()
            np_realtime_face_embedding = np.frombuffer(str_realtime_embedding, dtype='float64')

            is_matched, probability, _, _ = verify_face_matching(
                np_known_face_embedding, np_realtime_face_embedding, thresh=0.40
            )
            
            data["is_matched"] = is_matched
            data["probability"] = probability

            # indicate that the request was a success
            data["success"] = True
        else:
            data["success"] = False
            data["reason"] = "Error .. reading uploaded known_embedding"
    else:
        data["success"] = False
        data["reason"] = "Error .. only 'POST' method allowed"
        
    # return the data dictionary as a JSON response
    return flask.jsonify(data)


@app.route("/match-known-face-embedding", methods=["POST"])
def api_match_known_face_embedding():
    """
    Match known face embedding from photo faces
    """
    data = {}
    # print(flask.request.data)

    # ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            # read the image in PIL format
            realtime_image = flask.request.files["image"].read()
            realtime_pil_image = Image.open(io.BytesIO(realtime_image))
            np_realtime_image_array = np.asarray(realtime_pil_image)

            # read the face embedding
            str_known_embedding = flask.request.files["known_embedding"].read()
            np_known_face_embedding = np.frombuffer(str_known_embedding, dtype='float64')

            # print(type(np_known_face_embedding))
            # print(np_known_face_embedding.shape)

            realtime_detected_faces, realtime_extracted_faces, realtime_face_embeddings = get_faces_and_embeddings(
                np_realtime_image_array
            )

            matches_result = []
            for idx, realtime_face_embedding in enumerate(realtime_face_embeddings):

                is_matched, probability, _, _ = verify_face_matching(
                    np_known_face_embedding, realtime_face_embedding, thresh=0.40
                )
                
                result = {
                    "is_matched": is_matched,
                    "probability": probability,
                    "detected_face": realtime_detected_faces[idx],
                    "extracted_face": realtime_extracted_faces[idx],
                    "face_embedding": realtime_face_embedding,
                }
                matches_result.append(result)

            data["face_count"] = len(realtime_detected_faces)
            data["matches_result"] = matches_result

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

    # init mtcnn
    init_face_detector()

    # 
    load_models()
    
    # debug and threaded set to false
    # to stop ValueError: 
    # Tensor Tensor("fc1000/Softmax:0", shape=(?, 1000), dtype=float32) 
    # is not an element of this graph.
    app.run(
        debug=False,threaded = False,
        host="0.0.0.0",
        port=5001
    )