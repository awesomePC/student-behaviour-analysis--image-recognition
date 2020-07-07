

# #####################################################################
# ## 1) own siamese model
# #####################################################################

from face_verification import *

init_face_detector()
load_models()


image_paths = ["static/match/7.jpg", "static/match/8.png"]

all_embeddings = []
for image_path in image_paths:
    image, img_array = read_image(image_path)
    _, _, embeddings = get_faces_and_embeddings(img_array)
    all_embeddings.append(embeddings[0])


result = verify_face_matching(all_embeddings[0], all_embeddings[1])
print(result)




# #####################################################################
# ## 2) vggface keras
# #####################################################################


# from keras_vggface.utils import preprocess_input
# from keras_vggface.vggface import VGGFace
# from scipy.spatial.distance import cosine

# from PIL import Image
# import numpy as np

# from face_verification import *
# init_face_detector()
# load_models()

# # create a vggface model object
# model = VGGFace(model='resnet50',
#     include_top=False,
#     input_shape=(224, 224, 3),
#     pooling='avg'
# )

# def get_model_scores(face):
#     sample = np.asarray(face, 'float32')

#     # prepare the data for the model
#     sample = preprocess_input(sample, version=2)
#     sample = np.expand_dims(sample, axis=0)
#     # perform prediction
#     return model.predict(sample)


# image_paths = ["static/match/7.jpg", "static/match/8.png"]

# faces = []
# for image_path in image_paths:
#     image, img_array = read_image(image_path)
#     _, extracted_faces = detect_extract_faces(img_array)
#     faces.append(extracted_faces[0])


# model_scores = []
# for face in faces:
#     model_score = get_model_scores(face)
#     # print(model_scores)
#     model_scores.append(model_score[0])


# score = cosine(model_scores[0], model_scores[1])
# print(score)


# #####################################################################
# ## 3) deepface vgg
# #####################################################################

# from deepface import DeepFace

# result  = DeepFace.verify("static/match/7.jpg", "static/match/8.png")

# print("Is verified: ", result["verified"])
# print(result)


########################################################################
########################################################################
##### Final result
########################################################################
########################################################################
"""
1) our siamese model
 is_matched, probability, y_pred, distance

 i) ultrafast face detector:
 (True, 0.9300007373094559, array([[0.06999926]], dtype=float32), 0.06999926)

 ii) mtcnn face detector:
 (True, 0.8238801658153534, array([[0.17611983]], dtype=float32), 0.17611983)


2) vggface keras:
  i) ultrafast face detector:
    0.005384266376495361
  ii) mtcnn face detector:
    0.04509955644607544

3) Deepface
{'verified': True, 'distance': 0.01603984832763672,}
"""

########################################################################
########################################################################
##### Final winner
########################################################################
##############
"""
vggface keras + ultrafast face detector

= 0.005384266376495361
"""