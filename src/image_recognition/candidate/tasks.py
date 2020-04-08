from django.conf import settings
import os
from celery.decorators import task
from helper.utils.error_handling import trace_error

import json
import requests
from urllib.parse import urljoin

from exam.models import ExamCandidatePhoto
from candidate.models import CandidateImgDataset

import logging
logger = logging.getLogger(__name__)


@task()
def post_register_extract_save_face_and_embeddings(id_candidate_img_dataset_obj):
    from recognize.views import get_faces_embeddings

    candidate_img_dataset = CandidateImgDataset.objects.filter(
        id=id_candidate_img_dataset_obj
    ).first()

    if candidate_img_dataset:
        file_candidate_image = candidate_img_dataset.img.path

        detected_faces, extracted_faces, face_embeddings = get_faces_embeddings(
            file_candidate_image
        )

        if detected_faces:
            extracted_face = extracted_faces[0]
            face_embedding = face_embeddings[0]

            candidate_img_dataset.face = extracted_face
            candidate_img_dataset.face_embedding = face_embedding
            candidate_img_dataset.save()
        else:
            print("Info ... No face detected in image")
    else:
        pass


@task()
def recognize_candidate_emotion(id_exam_candidate_photo):
    from emotion_recognition.views import detect_image_emotions

    exam_candidate_data = ExamCandidatePhoto.objects.filter(
        id=id_exam_candidate_photo
    ).first() # is_emotion_calc_done=False

    if exam_candidate_data:
        file_candidate_image = exam_candidate_data.photo.path
        all_emotions, topmost_emotion = detect_image_emotions(
            file_candidate_image
        )
        if all_emotions:
            exam_candidate_data.all_emotions = all_emotions
            exam_candidate_data.top_emotion = topmost_emotion
            emotion_message = "Emotion calculated successfully"
            exam_candidate_data.emotion_message = emotion_message
            exam_candidate_data.is_emotion_calc_done = True
            exam_candidate_data.save()
        else:
            pass
    else:
        pass
    return True