import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

CKPT_DIR = os.path.join(BASE_DIR, "ckpt")

EMOTION_MODEL = os.environ.get("EMOTION_MODEL", "mobilenet")  # inceptionresnetv2