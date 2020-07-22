import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

CKPT_DIR = os.path.join(BASE_DIR, "ckpt")
os.makedirs(CKPT_DIR, exist_ok=True)

EMOTION_MODEL = os.environ.get("EMOTION_MODEL", "vgg16")  # inceptionresnetv2