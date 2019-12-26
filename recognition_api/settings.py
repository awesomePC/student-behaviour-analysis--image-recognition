import os

BASE_DIR = os.getcwd()

MEDIA_ROOT = os.path.join(
    BASE_DIR, "media"
)

facenet_model_file = os.path.join(
    MEDIA_ROOT, 'neural_models/facenet_keras.h5'
)

face_verification_model_file = os.path.join(
    MEDIA_ROOT, 'neural_models/face-verification-model.h5'
)
