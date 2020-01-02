from django.conf import settings
import os
from celery.decorators import task
from helper.utils.error_handling import trace_error

# import cv2
# import imutils
# import numpy as np
import json
import requests
from urllib.parse import urljoin

from exam.models import ExamCandidatePhoto
from candidate.models import CandidateImgDataset

import logging
logger = logging.getLogger(__name__)


@task()
def post_register_extract_save_face_and_embeddings(id_candidate_img):
    # from recognize.face_recognition import (
    #     read_image,
    #     detect_extract_faces_from_image,
    #     get_embedding
    # )
    from recognize.views import get_faces_embeddings


    candidate_img = CandidateImgDataset.objects.filter(
        id=id_candidate_img
    ).first()

    # import pdb; pdb.set_trace()

    if candidate_img:
        file_candidate_image = candidate_img.img.path

        detected_faces, extracted_faces, face_embeddings = get_faces_embeddings(
            file_candidate_image
        )

        if detected_faces:
            extracted_face = extracted_faces[0]
            face_embedding = face_embeddings[0]

            candidate_img.face = extracted_face
            candidate_img.face_embedding = face_embedding
            candidate_img.save()
        else:
            # import pdb; pdb.set_trace()
            print("Info ... No face detected in image")
    else:
        pass


# @task()
# def recognize_emotion_old(image__path):
#     from keras.preprocessing.image import img_to_array
#     from keras.models import load_model

#     dir_root_emotion = os.path.join(
#         settings.BASE_DIR,
#         *["emotion_recognition"]
#     )
#     # parameters for loading data and images
#     detection_model_path = os.path.join(
#         dir_root_emotion,
#         *["haarcascade_files", "haarcascade_frontalface_default.xml"]
#     )
#     emotion_model_path = os.path.join(
#         dir_root_emotion,
#         *["models", "_mini_XCEPTION.102-0.66.hdf5"]
#     )

#     try:
#         # hyper-parameters for bounding boxes shape
#         # loading models
#         face_detection = cv2.CascadeClassifier(detection_model_path)
#         emotion_classifier = load_model(emotion_model_path, compile=False)
#         EMOTIONS = [
#             "angry" ,"disgust","scared", "happy", "sad",
#             "surprised", "neutral"
#         ]

#         frame = cv2.imread(image__path)

#         frame = imutils.resize(frame,width=300)
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = face_detection.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE)
        
#         canvas = np.zeros((250, 300, 3), dtype="uint8")
#         frameClone = frame.copy()
#         if len(faces) > 0:
            
#             breakpoint()

#             faces = sorted(faces, reverse=True,
#             key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
#             (fX, fY, fW, fH) = faces
#                         # Extract the ROI of the face from the grayscale image, resize it to a fixed 28x28 pixels, and then prepare
#                 # the ROI for classification via the CNN
#             roi = gray[fY:fY + fH, fX:fX + fW]
#             roi = cv2.resize(roi, (64, 64)) # (64, 64)
#             roi = roi.astype("float") / 255.0 
#             roi = img_to_array(roi) # (64, 64, 1)
#             roi = np.expand_dims(roi, axis=0) # (1, 64, 64, 1)
            
#             preds = emotion_classifier.predict(roi)[0]
#             emotion_probability = np.max(preds)
#             label = EMOTIONS[preds.argmax()]
#             return (preds, emotion_probability, label)
            
#     except Exception as e:
#         error = trace_error()
#         logger.error(error)

#     return (None, None, None)


# def rgb_2_grey(rgb_img_array):
#     """
#     Numpy to convert rgb pixel array into grayscale
    
#     Args:
#         rgb_img_array (numpy): numpy array
#     """
#     # gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
#     grey_img_array = np.dot(rgb_img_array[...,:3], [0.299, 0.587, 0.114])
#     return grey_img_array

# @task()
# def recognize_emotion(image_path):

#     from emotion_recognition.views import detect_image_emotions

#     from keras.preprocessing.image import img_to_array
#     from keras.models import load_model

#     dir_root_emotion = os.path.join(
#         settings.BASE_DIR,
#         *["emotion_recognition"]
#     )
#     # # parameters for loading data and images
#     # detection_model_path = os.path.join(
#     #     dir_root_emotion,
#     #     *["haarcascade_files", "haarcascade_frontalface_default.xml"]
#     # )
#     emotion_model_path = os.path.join(
#         dir_root_emotion,
#         *["models", "_mini_XCEPTION.102-0.66.hdf5"]
#     )

#     try:
#         # hyper-parameters for bounding boxes shape
#         # loading models
#         # face_detection = cv2.CascadeClassifier(detection_model_path)
#         emotion_classifier = load_model(emotion_model_path, compile=False)
        
#         EMOTIONS = [
#             "angry" ,"disgust","scared", "happy", "sad",
#             "surprised", "neutral"
#         ]

#         if type(rgb_face_array) != None:
#             grey_roi = rgb_2_grey(rgb_face_array)

#             grey_roi = cv2.resize(grey_roi, (64, 64)) # (64, 64)
#             grey_roi = grey_roi.astype("float") / 255.0 
#             grey_roi = img_to_array(grey_roi) # (64, 64, 1)
#             grey_roi = np.expand_dims(grey_roi, axis=0) # (1, 64, 64, 1)
            
#             preds = emotion_classifier.predict(grey_roi)[0]
#             emotion_probability = np.max(preds)
#             label = EMOTIONS[preds.argmax()]
#             print(label)
#             return (preds, emotion_probability, label)
#         else:
#             return (None, None, None)

#     except Exception as e:
#         error = trace_error()
#         logger.error(error)

#     return (None, None, None)

# @task()
# def do_emotion_recognition():
#     """
#     Recognize image emotion by iterating over table data
#     """
#     all_exam_data = ExamCandidatePhoto.objects.filter() # is_emotion_calc_done=False
#     for exam_candidate_data in all_exam_data:
#         rgb_face_array = exam_candidate_data.np_face

#         emotion_message = ""

#         if type(rgb_face_array) != None:
#             # ***********
#             # detect emotions in image
#             preds, emotion_probability, label = recognize_emotion(rgb_face_array)
#             emotions = {
#                 "emotion_probability": str(emotion_probability),
#                 "label": label,
#             }
#             exam_candidate_data.emotions = emotions
#             emotion_message = "Emotion calculated successfully"

#         elif len(exam_candidate_data.detected_persons_list) == 0:
#             emotion_message = f"exam_candidate_data with id {exam_candidate_data.id} image has no person detected so skipping emotion calculation"
#         else:
#             emotion_message = f"It looks like image of exam_candidate_data with id {exam_candidate_data.id} contains multiple persons.. skipping emotion analysis"
        
#         exam_candidate_data.emotion_message = emotion_message
#         exam_candidate_data.is_emotion_calc_done = True
#         exam_candidate_data.save()
#         print(emotion_message)
#     return True


# @task()
# def detect_objects(image__path):
#     """
#     Detect common objects in image
    
#     Args:
#         image__path (str): Image full path
    
#     Returns:
#         tuple: (box, label, confidence)
#     """
#     from cvlib import detect_common_objects
#     img = cv2.imread(image__path)
#     bbox, label, conf = detect_common_objects(img)
#     # output_image = draw_bbox(img, bbox, label, conf)
#     print(bbox, label, conf)
#     return (bbox, label, conf)

# @task()
# def do_object_detection():
#     """
#     Iterate inside table and perform common object detection
#     """
#     all_exam_data = ExamCandidatePhoto.objects.filter(is_object_detection_done=False)
#     for exam_candidate_data in all_exam_data:
#         image_file__path = exam_candidate_data.photo.path
        
#         bbox, label, conf = detect_objects(image_file__path)
#         detected_objects = {
#             "bbox": bbox,
#             "label": label,
#             "conf": conf,
#         }
#         exam_candidate_data.detected_objects = detected_objects
#         exam_candidate_data.is_object_detection_done = True
#         exam_candidate_data.save()
#     return True



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

        # import pdb; pdb.set_trace()

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