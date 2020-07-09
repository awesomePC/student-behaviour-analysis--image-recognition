import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

DIR_MEDIA = os.path.join(
    BASE_DIR, 'media'
)
os.makedirs(DIR_MEDIA, exist_ok=True)

DETECTOR_NUMBER = os.getenv("DETECTOR_NUMBER", 0)  # 0
DIR_MODEL_DETECTION = os.path.join(
    BASE_DIR, "model/detection/"
)
