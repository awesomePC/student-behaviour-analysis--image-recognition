import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

EMOTION_MODEL = os.environ.get("EMOTION_MODEL", "mobilenet")  # inceptionresnetv2