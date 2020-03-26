import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

classifier_file = os.path.join(
    BASE_DIR, 'classifier/classifier.joblib'
)

classes_file = os.path.join(
    BASE_DIR, 'classifier/classes.npy'
)
