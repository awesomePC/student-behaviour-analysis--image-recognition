
# import the necessary packages
import os, random

import flask
import io
import json

from PIL import Image
import numpy as np

import settings
import helpers


# initialize our Flask application and the Keras model
app = flask.Flask(__name__)


### API's
@app.route("/verify-genuine", methods=["POST"])
def verify_genuine():
    """
    Verify person is genuine or fake
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

            
            data["prediction"] = "real" # real or fake

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
        "* Loading Keras model and Flask starting server..."
        "please wait until server has fully started"
    )
    
    # debug and threaded set to false
    # to stop ValueError: 
    # Tensor Tensor("fc1000/Softmax:0", shape=(?, 1000), dtype=float32) 
    # is not an element of this graph.
    app.run(
        debug=False,threaded = False,
        host="0.0.0.0",
        port=5003
    )