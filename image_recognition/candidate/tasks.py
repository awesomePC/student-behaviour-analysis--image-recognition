from django.conf import settings
import os
from celery.decorators import task
from helper.utils.error_handling import trace_error


import logging
logger = logging.getLogger(__name__)


@task()
def task_extract_save_face_and_embeddings(id_candidate_img):
    from recognize.face_recognition import (
        read_image,
        detect_extract_faces_from_image,
        get_embedding
    )
    from candidate.models import CandidateImgDataset

    candidate_img = CandidateImgDataset.objects.filter(
        id=id_candidate_img
    ).first()

    if candidate_img:
        file_candidate_image = candidate_img.img.path
        pil_image, image_array = read_image(file_candidate_image)
        _, extracted_faces = detect_extract_faces_from_image(image_array)
        
        if extracted_faces:
            extracted_face = extracted_faces[0]
            face_embedding = get_embedding(extracted_face)

            candidate_img.face = extracted_face
            candidate_img.face_embedding = face_embedding
            candidate_img.save()
        pass
    else:
        pass