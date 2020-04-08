from django.shortcuts import render

import os 
import sys

import json
from helper.utils.image_conversion import base64_to_pil

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

