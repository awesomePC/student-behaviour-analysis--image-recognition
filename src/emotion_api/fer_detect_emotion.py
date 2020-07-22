import os
import cv2
import numpy as np

import operator

import json
from deepface import DeepFace
from deepface.extendedmodels import Emotion

models = {}
models["emotion"] = Emotion.loadModel()


def truncate_float(value, digits_after_point=2):
    """
    Truncate long float numbers
    >>> truncate_float(1.1477784, 2)
       1.14
    """
    pow_10 = 10 ** digits_after_point
    return (float(int(value * pow_10))) / pow_10


EMOTION_MAPPING = {
    'angry': 'anger', 
    'disgust': 'disgust', 
    'fear': 'fear', 
    'happy': 'happy', 
    'sad': 'sadness', 
    'surprise': 'surprise',
}

def post_process_emotions(detected_emotions):
    """
    remap emotion label to remap

    Args:
        detected_emotions ([type]): [description]

    Returns:
        [type]: [description]
    """
    emotions = detected_emotions.get("emotion", {})
    dominant_emotion = detected_emotions.get("dominant_emotion", "")

    modified_emotions = {}
    for key in emotions.keys():
        if key == "neutral":
            if emotions[key] < 70:
                # make emotion contempt instead of happy
                modified_emotions["contempt"] = emotions[key]
            else:
                if emotions["happy"] < 7:
                    modified_emotions["contempt"] = emotions["happy"]
                    modified_emotions["happy"] = emotions[key]
                else:
                    modified_emotions["happy"] = emotions[key]
        else:
            modified_keyname = EMOTION_MAPPING.get(key)
            # rename keyname
            modified_emotions[modified_keyname] = emotions[key]

    if "contempt" not in emotions:
        emotions["contempt"] = 0.00

    # get key with max value
    dominant_emotion = max(modified_emotions.items(), key=operator.itemgetter(1))[0]

    return (modified_emotions, dominant_emotion)


def detect_emotions(image_file):
    """
    Detect emotions from image

    Args:
        image_file (str): image file to detect emotions
    """
    detected_emotions = DeepFace.analyze(image_file, actions = ['emotion'], models=models, enforce_detection=False)
    # print(f"detected_emotion: {detected_emotion}")

    return post_process_emotions(detected_emotions)


if __name__ == "__main__":
    emotions, top_emotion = detect_emotions(image_file="media/images/happy_vishal.jpg")
    print(f"emotions: {emotions}")
    print(f"top_emotion: {top_emotion}")