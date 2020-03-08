from celery.decorators import task
import os
import cv2
import cvlib as cv
from cvlib.object_detection import draw_bbox
import imutils
import numpy as np

from django.conf import settings
from helper.utils.error_handling import trace_error

from exam.models import ExamCandidatePhoto

import logging
logger = logging.getLogger(__name__)


@task()
def recognize_emotion(image__path):
    from keras.preprocessing.image import img_to_array
    from keras.models import load_model

    dir_root_emotion = os.path.join(
        settings.BASE_DIR,
        *["recognize", "emotion-recognition"]
    )
    # parameters for loading data and images
    detection_model_path = os.path.join(
        dir_root_emotion,
        *["haarcascade_files", "haarcascade_frontalface_default.xml"]
    )
    emotion_model_path = os.path.join(
        dir_root_emotion,
        *["models", "_mini_XCEPTION.102-0.66.hdf5"]
    )

    try:
        # hyper-parameters for bounding boxes shape
        # loading models
        face_detection = cv2.CascadeClassifier(detection_model_path)
        emotion_classifier = load_model(emotion_model_path, compile=False)
        EMOTIONS = [
            "angry" ,"disgust","scared", "happy", "sad",
            "surprised", "neutral"
        ]

        frame = cv2.imread(image__path)

        frame = imutils.resize(frame,width=300)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detection.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE)
        
        canvas = np.zeros((250, 300, 3), dtype="uint8")
        frameClone = frame.copy()
        if len(faces) > 0:
            faces = sorted(faces, reverse=True,
            key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
            (fX, fY, fW, fH) = faces
                        # Extract the ROI of the face from the grayscale image, resize it to a fixed 28x28 pixels, and then prepare
                # the ROI for classification via the CNN
            roi = gray[fY:fY + fH, fX:fX + fW]
            roi = cv2.resize(roi, (64, 64))
            roi = roi.astype("float") / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)
            
            
            preds = emotion_classifier.predict(roi)[0]
            emotion_probability = np.max(preds)
            label = EMOTIONS[preds.argmax()]
            return (preds, emotion_probability, label)
            
    except Exception as e:
        error = trace_error()
        logger.error(error)

    return (None, None, None)


@task()
def do_emotion_recognition():
    """
    Recognize image emotion by iterating over table data
    """
    all_exam_data = ExamCandidatePhoto.objects.filter(is_emotion_calc_done=False)
    for exam_candidate_data in all_exam_data:
        image_file__path = exam_candidate_data.photo.path

        emotion_message = ""

        if len(exam_candidate_data.detected_persons_list) == 1:
            # ***********
            # detect emotions in image
            preds, emotion_probability, label = recognize_emotion(image_file__path)
            emotions = {
                "emotion_probability": str(emotion_probability),
                "label": label,
            }
            exam_candidate_data.emotions = emotions
            emotion_message = "Emotion calculated successfully"

        elif len(exam_candidate_data.detected_persons_list) == 0:
            emotion_message = f"exam_candidate_data with id {exam_candidate_data.id} image has no person detected so skipping emotion calculation"
        else:
            emotion_message = f"It looks like image of exam_candidate_data with id {exam_candidate_data.id} contains multiple persons.. skipping emotion analysis"
        
        exam_candidate_data.emotion_message = emotion_message
        exam_candidate_data.is_emotion_calc_done = True
        exam_candidate_data.save()
        print(emotion_message)

@task()
def detect_objects(image__path):
    """
    Detect common objects in image
    
    Args:
        image__path (str): Image full path
    
    Returns:
        tuple: (box, label, confidence)
    """
    img = cv2.imread(image__path)
    bbox, label, conf = cv.detect_common_objects(img)
    # output_image = draw_bbox(img, bbox, label, conf)
    print(bbox, label, conf)
    return (bbox, label, conf)

@task()
def do_object_detection():
    """
    Iterate inside table and perform common object detection
    """
    all_exam_data = ExamCandidatePhoto.objects.filter(is_object_detection_done=False)
    for exam_candidate_data in all_exam_data:
        image_file__path = exam_candidate_data.photo.path
        
        bbox, label, conf = detect_objects(image_file__path)
        detected_objects = {
            "bbox": bbox,
            "label": label,
            "conf": conf,
        }
        exam_candidate_data.detected_objects = detected_objects
        exam_candidate_data.is_object_detection_done = True
        exam_candidate_data.save()
    return True
