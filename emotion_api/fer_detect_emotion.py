from fer import FER
import cv2

img = cv2.imread("images/no_face.jpg")
detector = FER(mtcnn=True)
emotions = detector.detect_emotions(img)

print(emotions)

if emotions:
    top_emotion, score = detector.top_emotion(img)

    print(f"top_emotion : {top_emotion}")
    print(f"score : {score}")