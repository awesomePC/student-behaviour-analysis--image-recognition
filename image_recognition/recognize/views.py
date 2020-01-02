# from django.shortcuts import render
# import logging
# logger = logging.getLogger(__name__)

# import os 
# import sys

# import cv2
# 
# from cvlib.object_detection import draw_bbox

# from django.conf import settings
# from django.views.decorators.csrf import csrf_exempt
# from django.http import HttpResponse, JsonResponse
import json
from helper.utils.image_conversion import base64_to_pil

# # global vars
# dir_dataset = os.path.join(settings.MEDIA_ROOT, "dataset")
# open_cv_dir = os.path.join(
#     settings.BASE_DIR,
#     *["recognize", "opencv_face_recognition"]
# )


# def detect_faces(image__path):
#     """
#     Detect faces from the image using cvlib
    
#     Returns:
#         tuple -- faces and confidence

#     output samples:
#         faces - [[599, 230, 810, 503]]
#         confidence - [0.9845196]
#     """
#     from cvlib import detect_face
#     image = cv2.imread(image__path)
#     faces, confidences = detect_face(image)

#     # print(faces)
#     # print(confidences)
#     return (faces, confidences)


# @csrf_exempt
# def start_embedding_training_model(request):
#     from recognize.opencv_face_recognition.extract_embeddings import extract_embeddings
#     from recognize.opencv_face_recognition.train_model import train_model
    
#     try:
#         embeddings = os.path.join(open_cv_dir, "output/embeddings.pickle")
#         detector_folder = os.path.join(open_cv_dir, "face_detection_model")
#         embedding_model = os.path.join(open_cv_dir, "openface_nn4.small2.v1.t7")
        
#         # call function
#         is_embedding_extracted = extract_embeddings(
#             open_cv_dir,
#             dir_dataset_with_path=dir_dataset,
#             embeddings=embeddings,
#             detector_folder=detector_folder,
#             embedding_model=embedding_model,
#             min_confidence=0.5
#         )

#         embeddings_pickle_file = os.path.join(open_cv_dir, "output/embeddings.pickle")
#         recognizer_file = os.path.join(open_cv_dir, "output/recognizer.pickle")
#         label_encoder = os.path.join(open_cv_dir, "output/le.pickle")

#         # call function
#         train_model(
#             embeddings_pickle_file=embeddings_pickle_file,
#             recognizer_file=recognizer_file,
#             label_encoder=label_encoder
#         )
#         response = {
#             "message": {
#                 "type": "success",
#                 "title": "Success Info",
#                 "text": "Model trained successfully",
#             }
#         }
#         return JsonResponse(response)

#     except Exception as e:
#         error = trace_error()
#         logger.error(error)
#         response = {
#             "message": {
#                 "type": "error",
#                 "title": "Error Info",
#                 "text": error,
#             }
#         }
#         return JsonResponse(response)


# def get_user_from_recognized_str(s):
#     if s:
#         matched_num = re.search(r'\d+', s)
#         if matched_num:
#             num = int(matched_num.group())

#             user = CustomUser.objects.filter(
#                 id=num
#             ).first()

#             return user
#         else:
#             print(f"Error .. Number cannot be extracted from {s}")
#     else:
#         print("Please pass proper string .. ")
#     return None

# def recognize_faces(image_file):
#     from recognize.opencv_face_recognition.recognize import (
#         face_recognize
#     )

#     face_detection_model_folder = os.path.join(
#         open_cv_dir, "face_detection_model"
#     )
#     embedding_model = os.path.join(
#         open_cv_dir, "openface_nn4.small2.v1.t7"
#     )

#     embeddings_pickle_file = os.path.join(
#         open_cv_dir, "output/embeddings.pickle"
#     )
#     recognizer_file = os.path.join(
#         open_cv_dir, "output/recognizer.pickle"
#     )

#     label_encoder = os.path.join(
#         open_cv_dir, "output/le.pickle"
#     )
    
#     cv2_image, detected_faces = face_recognize(
#         face_detection_model_folder=face_detection_model_folder,
#         embedding_model=embedding_model,
#         recognizer_file=recognizer_file,
#         label_encoder=label_encoder,
#         image_file=image_file,
#         min_confidence=0.7,
#     )
#     return (cv2_image, detected_faces)

from django.conf import settings

import requests
from urllib.parse import urljoin


def get_face_count(image__path):
    image = open(image__path, "rb").read()

    payload = {
        "image": image
    }

    FACE_COUNT_API_URL = urljoin(
        settings.FACE_RECOGNITION_BASE_API_URL,
        '/get-face-count'
    )

    # submit the request
    response = requests.post(
        FACE_COUNT_API_URL, files=payload
    ).json()

    if response["success"]:
        count = response["face_count"]
    else:
        count = False
    return count


def get_faces_embeddings(image__path):
    from numpy import array

    # load the input image and construct the payload for the request
    image = open(image__path, "rb").read()

    payload = {
        "image": image
    }
    
    FACE_EXTRACTION_API_URL = urljoin(
        settings.FACE_RECOGNITION_BASE_API_URL,
        '/extract-faces-and-embeddings'
    )

    # submit the request
    response = requests.post(
        FACE_EXTRACTION_API_URL, files=payload
    ).json()

    if response["success"]:
        detected_faces = response['detected_faces']
        
        # convert json list to numpy array
        extracted_faces = array(response['extracted_faces'])
        face_embeddings = array(response['face_embeddings'])

        return (detected_faces, extracted_faces, face_embeddings)
    else:
        return ([], [], [])

def compare_face_embedding(known_embedding, realtime_embedding):
    """
    Compare face embedding
    
    Args:
        known_face_embedding ([type]): [description]
        realtime_face_embedding ([type]): [description]
    """
    # convert to bytes
    bytes_known_embedding = known_embedding.tobytes()

    # convert to bytes
    bytes_realtime_embedding = realtime_embedding.tobytes()

    payload = {
        "known_embedding": bytes_known_embedding,
        "realtime_embedding": bytes_realtime_embedding
    }

    COMPARE_FACE_EMBEDDING_API_URL = urljoin(
        settings.FACE_RECOGNITION_BASE_API_URL, 
        '/compare-face-embedding'
    )

    # submit the request
    response = requests.post(
        COMPARE_FACE_EMBEDDING_API_URL, files=payload
    ).json()

    # # ensure the request was successful
    if response["success"]:
        # print(response)
        is_matched = response["is_matched"]
        probability = response["probability"]
        return (is_matched, probability)
    else:
        # print("Request failed")
        return (None, None)


def highlight_recognized_faces(image_path, recognized_faces):

    # load the input image and construct the payload for the request
    image = open(image_path, "rb").read()

    FACE_HIGHTLIGHT_RECOGNIZED_API_URL = urljoin(
        settings.FACE_RECOGNITION_BASE_API_URL, 
        '/hightlight-recognized-faces'
    )

    # recognized_faces = [
    #     {
    #         "name": "Nivratti",
    #         "probability": 0.95,
    #         "box": (50, 50, 60, 50)
    #     }
    # ]

    data_json = {
        "recognized_faces": recognized_faces
    }

    files = {
        "image": image,
        'json': ("demo.json", json.dumps(data_json), 'application/json'),
    }

    # submit the request
    response = requests.post(
        FACE_HIGHTLIGHT_RECOGNIZED_API_URL, files=files
    ).json()

    # # ensure the request was successful
    if response["success"]:
        encoded_img = response["encoded_img"]
        pil_image = base64_to_pil(encoded_img)
        return pil_image
    else:
        print("Request failed")

