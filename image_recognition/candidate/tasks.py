from django.conf import settings
import os
from celery.decorators import task
from helper.utils.error_handling import trace_error

from recognize.face_recognition import (
    read_image,
    detect_extract_faces_from_image,
    get_embedding
)
# from exam.models import ExamCandidatePhoto

import logging
logger = logging.getLogger(__name__)


@task()
def extract_save_face_and_embeddings(candidate_img_dataset, detector, facenet_model):
    file_candidate_image = candidate_img_dataset.img.path
    pil_image, image_array = read_image(file_candidate_image)
    _, extracted_faces = detect_extract_faces_from_image(image_array, detector)
    
    if extracted_faces:
        extracted_face = extracted_faces[0]
        face_embedding = get_embedding(facenet_model, extracted_face)

        candidate_img.face = extracted_face
        candidate.face_embedding = face_embedding
        candidate_img.save()
    pass