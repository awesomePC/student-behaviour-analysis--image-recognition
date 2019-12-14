from django.shortcuts import render
import logging
logger = logging.getLogger(__name__)

import os 
import sys

import cv2
import cvlib as cv
from cvlib.object_detection import draw_bbox

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

from helper.utils.error_handling import trace_error

# global vars
dir_dataset = os.path.join(settings.MEDIA_ROOT, "dataset")
open_cv_dir = os.path.join(
    settings.BASE_DIR,
    *["recognize", "opencv_face_recognition"]
)


def detect_faces(image__path):
    """
    Detect faces from the image
    
    Returns:
        tuple -- faces and confidence

    output samples:
        faces - [[599, 230, 810, 503]]
        confidence - [0.9845196]
    """
    image = cv2.imread(image__path)
    faces, confidences = cv.detect_face(image)

    # print(faces)
    # print(confidences)
    return (faces, confidences)


@csrf_exempt
def start_embedding_training_model(request):
    from recognize.opencv_face_recognition.extract_embeddings import extract_embeddings
    from recognize.opencv_face_recognition.train_model import train_model
    
    try:
        embeddings = os.path.join(open_cv_dir, "output/embeddings.pickle")
        detector_folder = os.path.join(open_cv_dir, "face_detection_model")
        embedding_model = os.path.join(open_cv_dir, "openface_nn4.small2.v1.t7")
        
        # call function
        is_embedding_extracted = extract_embeddings(
            open_cv_dir,
            dir_dataset_with_path=dir_dataset,
            embeddings=embeddings,
            detector_folder=detector_folder,
            embedding_model=embedding_model,
            min_confidence=0.5
        )

        embeddings_pickle_file = os.path.join(open_cv_dir, "output/embeddings.pickle")
        recognizer_file = os.path.join(open_cv_dir, "output/recognizer.pickle")
        label_encoder = os.path.join(open_cv_dir, "output/le.pickle")

        # call function
        train_model(
            embeddings_pickle_file=embeddings_pickle_file,
            recognizer_file=recognizer_file,
            label_encoder=label_encoder
        )
        response = {
            "message": {
                "type": "success",
                "title": "Success Info",
                "text": "Model trained successfully",
            }
        }
        return JsonResponse(response)

    except Exception as e:
        error = trace_error()
        logger.error(error)
        response = {
            "message": {
                "type": "error",
                "title": "Error Info",
                "text": error,
            }
        }
        return JsonResponse(response)


def get_user_from_recognized_str(s):
    if s:
        matched_num = re.search(r'\d+', s)
        if matched_num:
            num = int(matched_num.group())

            user = CustomUser.objects.filter(
                id=num
            ).first()

            return user
        else:
            print(f"Error .. Number cannot be extracted from {s}")
    else:
        print("Please pass proper string .. ")
    return None

def recognize_faces(image_file):
    from recognize.opencv_face_recognition.recognize import (
        face_recognize
    )

    face_detection_model_folder = os.path.join(
        open_cv_dir, "face_detection_model"
    )
    embedding_model = os.path.join(
        open_cv_dir, "openface_nn4.small2.v1.t7"
    )

    embeddings_pickle_file = os.path.join(
        open_cv_dir, "output/embeddings.pickle"
    )
    recognizer_file = os.path.join(
        open_cv_dir, "output/recognizer.pickle"
    )

    label_encoder = os.path.join(
        open_cv_dir, "output/le.pickle"
    )
    
    cv2_image, detected_faces = face_recognize(
        face_detection_model_folder=face_detection_model_folder,
        embedding_model=embedding_model,
        recognizer_file=recognizer_file,
        label_encoder=label_encoder,
        image_file=image_file,
        min_confidence=0.7,
    )
    return (cv2_image, detected_faces)

