import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

facenet_model_file = os.path.join(
    BASE_DIR, 'neural_models/facenet_keras.h5'
)

face_verification_model_file = os.path.join(
    BASE_DIR, 'neural_models/face-verification-model.h5'
)
