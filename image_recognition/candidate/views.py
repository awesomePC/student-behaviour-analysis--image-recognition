import logging
logger = logging.getLogger(__name__)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse

from django.contrib.auth import logout

from django.views import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File

from django.conf import settings

from lazysignup.decorators import allow_lazy_user

import random
import os
import uuid
import re

from PIL import Image

from numpy import array

from notifications.signals import notify
from helper.utils.error_handling import trace_error

# from django.db.models.signals import post_save
# from django.dispatch import receiver

from candidate.models import CandidateImgDataset, TempRegistrationImage

from users.models import CustomUser
from users.forms import CustomUserCreationForm

from helper.utils.text_processing import is_html_text

from exam.models import (
    Exam,
    ExamCandidate,
    ExamQuestion,
    QuestionOption,
    CandidateAnswer,
    ExamCandidatePhoto,
    ExamCandidateValidation,
)

from exam.views import (
    get_user_exams_list,
    get_exam_record,
    get_candidate_next_question_index,
)


def get_candidate_uploaded_images(lazy_user_id):
    """
    Get training images uploaded by temprory user
    Arguments:
        lazy_user_id {[type]} -- User created only for the purpose of keeping uploaded images at sign up time
    """
    temp_images = TempRegistrationImage.objects.filter(
        lazy_user_id=lazy_user_id,
        is_valid=True
    )
    if temp_images:
        initial_preview = []
        initial_preview_config = []

        for idx, temp_img in enumerate(temp_images):
            url = temp_img.img.url
            initial_preview.append(url)

            filename = os.path.basename(temp_img.img.name) # "file.ext"
            # truncate long word
            length = 20
            suffix = "..."
            file_name_truncated = filename[:length].rsplit(' ', 1)[0] + suffix

            initial_preview_config.append({
                'key': idx, # keys for deleting/reorganizing preview
                'caption': file_name_truncated,
                'size':temp_img.img.size,
                'downloadUrl': url, # the url to download the file
                'url': f'/candidate/delete_sign_up_image/{temp_img.id}/', # server api to delete the file based on key
            })

        return (initial_preview, initial_preview_config)
    else:
        pass
        return ([], [])


@allow_lazy_user
def sign_up(request):
    from candidate.tasks import post_register_extract_save_face_and_embeddings

    lazy_user_id = request.user.id

    initial_preview, initial_preview_config = get_candidate_uploaded_images(
        lazy_user_id
    )

    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST':
        # process form data
        if form.is_valid():
            custom_user = form.save()
            # print("Saved")
            temp_images = TempRegistrationImage.objects.filter(
                lazy_user_id=lazy_user_id,
                is_valid=True
            )
            if temp_images:
                for temp_image in temp_images:
                    base_filename = os.path.basename(temp_image.img.name)
                    candidate_img = CandidateImgDataset.objects.create(
                        user=custom_user,
                        img=File(temp_image.img, base_filename)
                    )
                    candidate_img.save()

                    # run celery background task to extract face and embeddings
                    # post_register_extract_save_face_and_embeddings.delay(candidate_img.id)
                    
                    # run as normal method
                    post_register_extract_save_face_and_embeddings(candidate_img.id)

                    # delete temp
                    temp_image.delete()
            else:
                print("Error ... No temprory images data found  ..")

            notify.send(
                request.user, recipient=custom_user, verb='Account Created successfully', icon_class="icon-paperplane"
            )

            # logout and login again
            # necessary because we are lazy user
            # to change -- request.user from lazyuser model to customuser
            logout(request) 

            # handle log in
            return redirect("accounts_login")

            # delete lazy user
            CustomUser.objects.filter(id=lazy_user_id).delete()

        else:
            print("Error validating form ...")
            print(form.__dict__)


    context = {
        "initialPreview": initial_preview,
        "initialPreviewConfig": initial_preview_config,
        "form": form,
    }
    return render(request, 'candidate/account/sign_up.html', context)


def is_valid_traning_image(image__path):
    """
    Detect is candidate provided image is valid or not
    
    Arguments:
        image__path {[type]} -- [description]
    """
    from recognize.views import get_face_count
    
    count = get_face_count(image__path)

    if count == 0:
        is_valid = False
        return (is_valid, "No human face detected. Please upload another image")
        
    elif count == 1:
        is_valid = True
        return (is_valid, "valid image")
    
    elif count > 1:
        return (False, "Multiple faces detected ..")
    else:
        return (False, "Request to count face was failed ..")

def save_sign_up_image(lazy_user_id, photo_data, fileId, previewId):
    candidate_image = TempRegistrationImage.objects.create(
        lazy_user_id=lazy_user_id,
        img=photo_data
    )
    candidate_image.save()

    # validate candidate face in image and decide 
    # whether to keep or not
    is_valid, reason = is_valid_traning_image(candidate_image.img.path)

    if is_valid:
        candidate_image.is_valid = True
        candidate_image.save()

        url = candidate_image.img.url

        filename = os.path.basename(candidate_image.img.name) # "file.ext"
        
        # truncate long word
        length = 20
        suffix = "..."
        file_name_truncated = filename[:length].rsplit(' ', 1)[0] + suffix

        initial_preview_thumb_tag = {
            'key': fileId, # keys for deleting/reorganizing preview
            'caption': file_name_truncated,
            'size': candidate_image.img.size,
            'fileId': fileId, # file identifier
            'downloadUrl': url, # the url to download the file
            'url': f'/candidate/delete_sign_up_image/{candidate_image.id}/', # server api to delete the file based on key
            'extra': {
                "previewId": previewId
            }
        }

        response = {
            "uploaded": "OK",
            "success" : 1,

            # initial preview thumbnails for server uploaded files if you want it displayed immediately after upload
            "initialPreview": [
                url
            ],

            "initialPreviewConfig" : [
                # initial preview configuration if you directly want initial preview to be displayed with server upload data
                initial_preview_thumb_tag
            ],

            # initial preview thumbnail tags configuration that will be replaced dynamically while rendering
            "initialPreviewThumbTags" : [
                initial_preview_thumb_tag
            ],

            # whether to append content to the initial preview (or set false to overwrite)
            "append": True,
        }

    else:
        # delete image
        candidate_image.delete()

        response = {
            "uploaded": "ERROR",
            "error": reason,
            "success": 0,
            "message": {
                "type": "error",
                "title": "Error Info",
                "text": reason,
            },
        }
    return response


@csrf_exempt
@allow_lazy_user
def save_captured_sign_up_photo(request):
    lazy_user_id = request.user.id
    photo_data = request.FILES.get('webcam')

    try:
        response = save_sign_up_image(lazy_user_id, photo_data, fileId=5, previewId=5)
        return JsonResponse(response)

    except Exception as e:
        print(trace_error())
        return JsonResponse({'success': 0})

def dashboard(request):
    # active_exams, completed_exams = get_user_exams_list(
    #     request.user
    # )
    # total_active_exams = active_exams.count()
    # total_completed_exams = completed_exams.count()

    context = {
        # "active_exams": active_exams,
        # "completed_exams": completed_exams,
        # "total_active_exams": total_active_exams,
        # "total_completed_exams": total_completed_exams,
    }
    return render(request, 'candidate/dashboard.html', context)

def exam_list(request):
    active_exams, completed_exams = get_user_exams_list(
        request.user
    )
    context = {
        'active_exams': active_exams,
        'completed_exams': completed_exams
    }
    return render(request, 'candidate/exam/list_all.html', context)

def exam_instructions(request, exam_id):
    exam = get_exam_record(exam_id)
    context = {
        "exam": exam
    }
    return render(request, 'candidate/exam/instructions.html', context)

def exam(request, exam_id):
    candidate = ExamCandidate.objects.get(
        candidate=request.user,
        exam__id=exam_id
    )

    questions = ExamQuestion.objects.filter(
        exam__id=exam_id
    )

    context = {
        "candidate": candidate,
        "questions": questions,
    }
    return render(request, 'candidate/exam/exam.html', context)

@csrf_exempt
def get_next_question_index(request):
    """
    Get next question to display
    
    Arguments:
        request {[type]} -- [description]
    """
    exam_id = request.POST.get("exam_id")
    prev_question_index = request.POST.get("prev_question_index")

    response = get_candidate_next_question_index(
        request.user.id,
        exam_id,
        prev_question_index
    )
    return JsonResponse(response, safe=True)

@csrf_exempt
def save_candidate_answer(request):
    exam_candidate_id = request.POST.get("exam_candidate_id")
    question_id = request.POST.get("question_id")
    lst_sel_opt_values = request.POST.getlist("arr_sel_opt_values[]")

    exam_candidate = ExamCandidate.objects.get(
        id=exam_candidate_id
    )

    question = ExamQuestion.objects.get(
        id=question_id
    )

    # In this case, if the Person already exists, its name is updated
    exam_candidate, created = CandidateAnswer.objects.update_or_create(
        candidate=exam_candidate,
        question=question
    )

    if lst_sel_opt_values:
        lst_sel_opt_values = list(map(int, lst_sel_opt_values))

        exam_candidate.selected_option = lst_sel_opt_values
        exam_candidate.is_answered = True
        exam_candidate.save()

    if created:
        response = {
            "message": {
                "type": "success",
                "title": "Success Info",
                "text": "Candidate answer inserted successfully",
            }
        }
    else:   
        response = {
            "message": {
                "type": "success",
                "title": "Success Info",
                "text": "Candidate answer updated successfully",
            }
        }
    return JsonResponse(response, safe=True)

@csrf_exempt
def submit_exam(request):
    exam_id = request.POST.get("exam_id")

    cnt_exam_candidate = ExamCandidate.objects.filter(
        exam__id=exam_id,
        candidate=request.user,
    ).count()

    if cnt_exam_candidate:
        
        exam = Exam.objects.get(
            id=exam_id
        )
        exam_candidate = ExamCandidate.objects.get(
            exam=exam,
            candidate=request.user,
        )
        exam_candidate.is_completed = True
        exam_candidate.save()

        notify.send(
            request.user, recipient=request.user,
            verb=f'Exam "{exam.name}" completed successfully',
            icon_class="icon-check"
        )

    response = {
        "message": {
            "type": "success",
            "title": "Success Info",
            "text": "Exam Submitted successfully",
        },
        "next_action_needed": {
            "redirect": {
                "url" : f"/candidate/completed_confirmation/{exam_id}/",
                "timeout": 2000,
                "_comment": "timeout in seconds. After that the url start redirect"
            }
        }
    }
    return JsonResponse(response, safe=True)


def completed_confirmation(request, exam_id):
    """
    Exam Completed confirmation
    """
    exam = Exam.objects.get(
        id=exam_id
    )
    context = {
        "exam": exam
    }
    return render(request, 'candidate/exam/completed_confirmation.html', context)


# @csrf_exempt
# def save_exam_photo(request):
#     from recognize.views import recognize_faces

#     photo_data = request.FILES.get('webcam')

#     try:
#         # save photo
#         exam_candidate_data = ExamCandidatePhoto.objects.create(
#             user=request.user,
#             photo=photo_data
#         )
#         exam_candidate_data.save()

#         image_file__path = exam_candidate_data.photo.path
        
#         cv2_image, detected_faces = recognize_faces(
#             image_file__path
#         )

#         # get detected persons and matching percentages
#         detected_persons = []
#         matching_percentages = []
#         for face in detected_faces:
#             name = face["name"]
#             probability = face["probability"]
#             detected_persons.append(name)
#             matching_percentages.append({
#                 "name": name,
#                 "probability": probability
#             })

#         exam_candidate_data.detected_persons = detected_persons
#         exam_candidate_data.matching_percentages = matching_percentages
#         exam_candidate_data.save()

#         response = {
#             "message": {
#                 "type": "success",
#                 "title": "Success Info",
#                 "text": "Candidate photo uploaded successfully",
#             }
#         }
#         return JsonResponse(response, safe=True)

#     except Exception as e:
#         print(trace_error())
#         response = {
#             "message": {
#                 "type": "error",
#                 "title": "Error Info",
#                 "text": trace_error(),
#             }
#         }
#         return JsonResponse(response, safe=True)

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


def exam_validate_user(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)

    context = {
        "exam": exam
    }
    template_name = 'candidate/exam/validate_user.html'
    return render(request, template_name, context)


def generate_random_user_file(request):
    """
    Generate random file to show face recognition result 
    
    Returns:
        str: Result file name with full path
    """
    # result_file name with path
    res_file_name = str(uuid.uuid4())

    res_file_path = os.path.join(
        settings.MEDIA_ROOT,
        *["result", f"user_{request.user.id}"]
    )
    # make dir if not exists
    os.makedirs(res_file_path, exist_ok=True)

    res_file_name_with_path = os.path.join(
        res_file_path, f"{res_file_name}.png"
    )
    return res_file_name_with_path

@csrf_exempt
def ajax_validate_user(request):
    # from recognize.face_recognition import (
    #     read_image,
    #     get_faces_and_embeddings_by_img_path,
    #     highlight_recognized_faces
    # )

    # from recognize.face_recognition import verify_face_matching

    # import pdb; pdb.set_trace()

    from recognize.views import (
        get_faces_embeddings,
        compare_face_embedding,
        highlight_recognized_faces
    )

    # exam = get_object_or_404(Exam, pk=self.kwargs["pk"])
    photo_data = request.FILES.get('webcam')

    try:
        # save photo
        obj_candidate_validation = ExamCandidateValidation.objects.create(
            user=request.user,
            photo=photo_data
        )
        obj_candidate_validation.save()

        img_path = obj_candidate_validation.photo.path

        realtime_detected_faces, realtime_extracted_faces, realtime_face_embeddings = get_faces_embeddings(
            img_path
        )

        # import pdb; pdb.set_trace()

        detected_face_count = len(realtime_detected_faces)

        # random user result file
        res_file_name_with_path = generate_random_user_file(request)

        # verify is authorized user present in image
        candidate_img_dataset = CandidateImgDataset.objects.filter(user=request.user).first()
        
        is_authorized_candidate_present = False
        idx_candidate_face_embedding = None # used to remove entry from realtime_face_embeddings and check who is other
        recognized_persons = []

        if candidate_img_dataset:
            known_face_embedding = candidate_img_dataset.face_embedding
            
            # convert to numpy array
            # known_face_embedding = array(known_face_embedding)

            for idx, realtime_face_embedding in enumerate(realtime_face_embeddings):
                is_matched, probability = compare_face_embedding(
                    known_face_embedding, realtime_face_embedding
                )
                
                if is_matched:
                    is_authorized_candidate_present = True
                    idx_candidate_face_embedding = idx
                    
                    name = candidate_img_dataset.user.email
                else:
                    # check is proctor 
                    # temporarily set to unknown
                    name = "unknown"
                    probability = random.uniform(0.6, 0.8)

                recognized_persons.append({
                    "name": name,
                    "probability": probability,
                    "box": realtime_detected_faces[idx]['box']
                })

        if len(recognized_persons) >= 1:
            hightlighted_image = highlight_recognized_faces(
                img_path, recognized_persons
            )

            # save pil image
            hightlighted_image.save(res_file_name_with_path, "PNG")

        else:
            # if no face found save source file as result
            # later in javascript handle this situation
            # if no face detected show current frame from camera
            source_pil_image = Image.open(img_path).convert("RGB")
            source_pil_image.save(res_file_name_with_path)

        # detected_person_ids = []
        # # modify recognized name
        # for idx, recognized_face in enumerate(detected_faces):
        #     name = recognized_face["name"]
        #     user = get_user_from_recognized_str(name)
        #     if user:
        #         detected_person_ids.append(user.id)
        #         if user.first_name:
        #             name = user.first_name
        #         elif user.last_name:
        #             name = user.last_name
        #         else:
        #             name = user.email
        #         # store updated name
        #         recognized_face["name"] = name
        #         detected_faces[idx] = recognized_face
        
        # is_valid_candidate = False
        # for person_id in detected_person_ids:
        #     if person_id == request.user.id:
        #         is_valid_candidate = True

        # img_res = draw_recognized_bounding_box(
        #     cv2_image=cv2_image,
        #     detected_faces=detected_faces,
        #     write_result_2_disk=True,
        #     res_file_name_with_path=res_file_name_with_path,
        # )
        
        # substract base path -- keep only media path
        media_path_only = res_file_name_with_path.replace(settings.BASE_DIR, '')
        print(f"media_path_only : {media_path_only}")

        return JsonResponse({
            'success':1,
            'img': media_path_only,
            'detected_person_ids': [],
            'detected_face_count': detected_face_count,
            'is_authorized_candidate_present': is_authorized_candidate_present, # return value depending on user detected
        })

    except Exception as e:
        print(trace_error())
        return JsonResponse({'success': 0})

@csrf_exempt
def save_recognize_exam_photo(request, exam_id):

    from recognize.views import (
        get_faces_embeddings,
        compare_face_embedding,
        highlight_recognized_faces
    )
    from candidate.tasks import recognize_candidate_emotion

    photo_data = request.FILES.get('webcam')

    exam = Exam.objects.get(
        id=exam_id
    )

    exam_candidate_data = ExamCandidatePhoto.objects.create(
        user=request.user,
        exam=exam,
        photo=photo_data
    )
    exam_candidate_data.save()

    try:
        # save photo

        img_path = exam_candidate_data.photo.path

        realtime_detected_faces, realtime_extracted_faces, realtime_face_embeddings = get_faces_embeddings(
            img_path
        )

        detected_face_count = len(realtime_detected_faces)

        # random user result file
        res_file_name_with_path = generate_random_user_file(request)

        # verify is authorized user present in image
        candidate_img_dataset = CandidateImgDataset.objects.filter(user=request.user).first()
        
        is_authorized_candidate_present = False
        idx_candidate_face_embedding = None # used to remove entry from realtime_face_embeddings and check who is other
        recognized_persons = []

        if candidate_img_dataset:
            known_face_embedding = candidate_img_dataset.face_embedding

            for idx, realtime_face_embedding in enumerate(realtime_face_embeddings):
                is_matched, probability = compare_face_embedding(
                    known_face_embedding, realtime_face_embedding
                )
                
                if is_matched:
                    is_authorized_candidate_present = True
                    idx_candidate_face_embedding = idx
                    
                    name = candidate_img_dataset.user.email

                    # save face in db -- for emotion analysis
                    # modify emotion analysis later to work on single face
                    # exam_candidate_data.np_face = realtime_extracted_faces[idx]
                    exam_candidate_data.save()

                else:
                    # check is proctor 
                    # temporarily set to unknown
                    name = "unknown"
                    probability = random.uniform(0.6, 0.8)

                recognized_persons.append({
                    "name": name,
                    "probability": probability,
                    "box": realtime_detected_faces[idx]['box']
                })

            # trigger detect emotions background task
            recognize_candidate_emotion.delay(exam_candidate_data.id)
            
            # for testing run directly
            # recognize_candidate_emotion(exam_candidate_data.id)

        else:
            print(f"Error ... Candidate image dataset is empty")

        # source_pil_image, _ = read_image(img_path)

        if len(recognized_persons) >= 1:
            hightlighted_image = highlight_recognized_faces(
                img_path, recognized_persons,
                # write_result_2_disk=True,
                # res_file_name_with_path=res_file_name_with_path,
            )

        # first level suspicious checking
        # is valid candidate available
        if is_authorized_candidate_present == False:
            is_suspicious = True
            reason = "Candidate not detected in image."
        else:
            is_suspicious = False
            reason = ""
        
        # if two persons detected validate 
        # person 1 must be valid candidate 
        # second person may be proctor or superadmin otherwise mark suspicious exam
        # if is_valid_candidate and (len(detected_persons) > 1):
        #     is_second_person_suspicious = True
        #     for person in detected_persons:
        #         if person['user_id'] == request.user.id:
        #             continue
        #         else:
        #             if person['user_type'] in ["proctor", "superadmin"]:
        #                 is_second_person_suspicious = False
                
        #     if is_second_person_suspicious:
        #         is_suspicious = True
        #         reason += "\n Suspicious person is detected."

        if (len(recognized_persons) > 1):
            is_suspicious = True
            reason += "\n Suspicious person detected."

        exam_candidate_data.is_suspicious = is_suspicious
        exam_candidate_data.reason = reason
        exam_candidate_data.save()

        response = {
            "message": {
                "type": "success",
                "title": "Success Info",
                "text": "Recognition completed successfully",
            },
            "is_authorized_candidate_present": is_authorized_candidate_present,
            "is_suspicious": is_suspicious,
            "reason": reason
        }
        return JsonResponse(response, safe=True)

    except Exception as e:
        print(trace_error())
        response = {
            "message": {
                "type": "error",
                "title": "Error Info",
                "text": trace_error(),
            },
            "is_suspicious": True,
        }
        return JsonResponse(response, safe=True)

@csrf_exempt
def stop_exam(request):
    from misc.views import send_notification_2_user_types
    exam_id = request.POST.get("exam_id")
    exam_candidate_id = request.POST.get("exam_candidate_id")
    reason = request.POST.get("reason")

    exam = Exam.objects.get(
        id=exam_id
    )

    verb = f'Exam "{exam.name}" stopped due to suspicious activity.\nReason - ' + reason
    
    # send to candidate
    notify.send(
        request.user,
        recipient=request.user,
        verb=verb, 
        icon_class="icon-stop"
    )

    verb = f"Exam of candidate with id {request.user.id} stopped.\nReason - " + reason
   
    # send to all superadmins and proctor
    send_notification_2_user_types(
        sender=request.user,
        verb=verb,
        icon_class="icon-stop",
        user_types=["superadmin", "proctor"]
    )
    response = {
        "message": {
            "type": "info",
            "title": "Info",
            "text": "All users notified successfully",
        },
    }
    return JsonResponse(response, safe=True)

def stop_exam_reason(request, exam_id):
    exam = Exam.objects.get(
        id=exam_id
    )
    exam_candidate_photos = ExamCandidatePhoto.objects.filter(
        user=request.user,
        exam=exam
    ).order_by('-id')

    context = {
        "exam": exam,
        "exam_candidate_photos": exam_candidate_photos,
    }
    template_name = 'candidate/exam/stop_reason.html'
    return render(request, template_name, context)
