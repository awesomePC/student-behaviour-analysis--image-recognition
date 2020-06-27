import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

facenet_model_file = os.path.join(
    BASE_DIR, 'neural_models/facenet_keras.h5'
)

face_verification_model_file = os.path.join(
    BASE_DIR, 'neural_models/face-verification-model.h5'
)

MEDIA_ROOT = os.path.join(
    BASE_DIR, 'media'
)
os.makedirs(MEDIA_ROOT, exist_ok=True)


MODEL_DIR = os.path.join(
    BASE_DIR, 'models'
)

DETECTOR_NUMBER = os.getenv("DETECTOR_NUMBER", 6)  # 0
