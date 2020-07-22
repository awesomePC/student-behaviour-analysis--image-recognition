import logging
logger = logging.getLogger(__name__)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse

from django.contrib.auth import logout

from django.urls import reverse
from django.views import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File

from django.conf import settings

from django.utils import timezone

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
@csrf_exempt
def sign_up(request):
    from candidate.tasks import post_register_extract_save_face_and_embeddings

    lazy_user_id = request.user.id
    temp_images = []
    
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
                    candidate_img_dataset_obj = CandidateImgDataset.objects.create(
                        user=custom_user,
                        img=File(temp_image.img, base_filename)
                    )
                    candidate_img_dataset_obj.save()

                    # run celery background task to extract face and embeddings
                    # post_register_extract_save_face_and_embeddings.delay(candidate_img_dataset_obj.id)
                    
                    # run as normal method
                    post_register_extract_save_face_and_embeddings(candidate_img_dataset_obj.id)

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
            return redirect("/accounts/login")

            # delete lazy user
            CustomUser.objects.filter(id=lazy_user_id).delete()

        else:
            print("Error validating form ...")
            print(form.__dict__)
            
            temp_images = TempRegistrationImage.objects.filter(
                lazy_user_id=lazy_user_id,
                is_valid=True
            )

    else:
        temp_images = TempRegistrationImage.objects.filter(
            lazy_user_id=lazy_user_id,
            is_valid=True
        )

    context = {
        "form": form,
        "temp_images": temp_images,
    }
    return render(request, 'candidate/account/sign_up.html', context)


def is_valid_traning_image(image__path):
    """
    Detect is candidate provided image is valid or not
    
    Arguments:
        image__path {[type]} -- [description]
    """
    from recognize.views import get_face_count
    from api_consumer.views import verify_real

    count = get_face_count(image__path)

    if count == 0:
        is_valid = False
        return (is_valid, "No human face detected. Please upload another image")
        
    elif count == 1:
        # is_valid = True
        # return (is_valid, "valid image")
        response_fake_detection = verify_real(image_file=image__path)
        label = response_fake_detection["label"]
        if label == "real":
            is_valid = True
            return (is_valid, "valid image")
        else:
            is_valid = False
            return (is_valid, "Face spoofing detected")
        
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
    active_exams, completed_exams = get_user_exams_list(
        request.user
    )
    total_active_exams = active_exams.count()
    total_completed_exams = completed_exams.count()
    total_exams = total_active_exams + total_completed_exams

    total_captured_photos = ExamCandidatePhoto.objects.all().count()

    context = {
        "active_exams": active_exams,
        "completed_exams": completed_exams,
        "total_active_exams": total_active_exams,
        "total_completed_exams": total_completed_exams,
        "total_exams": total_exams,
        "total_captured_photos": total_captured_photos,
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
    candi_exam = ExamCandidate.objects.get(
        candidate=request.user,
        exam__id=exam_id
    )

    # if exam already submitted
    if candi_exam.is_completed == True:
        return redirect(reverse("candidate:exam_list"))

    # check is already stopped due to suspicious activity and is restart allowed or not
    if candi_exam.is_exam_stopped == True:
        if candi_exam.is_restart_allowed == True:
            pass
        else:
            # render contact admin page
            return render(request, 'candidate/exam/contact_admin_2_restart.html', {})

    if candi_exam.is_started == False:
        candi_exam.is_started = True
        candi_exam.start_time = timezone.localtime(timezone.now())
        candi_exam.save()
    else:
        candi_exam.is_restarted = True
        candi_exam.restart_time = timezone.localtime(timezone.now())
        candi_exam.save()
    
    questions = ExamQuestion.objects.filter(
        exam__id=exam_id
    )

    context = {
        "candidate": candi_exam,
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

    if created:
        pass
    else:
        # answer overwritten
        exam_candidate.overwrite_count = exam_candidate.overwrite_count + 1
        exam_candidate.save()

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
        exam_candidate.end_time = timezone.localtime(timezone.now())
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

    from api_consumer.views import verify_real

    # exam = get_object_or_404(Exam, pk=self.kwargs["pk"])
    photo_data = request.FILES.get('webcam')

    message = ""
    
    try:
        # save photo
        obj_candidate_validation = ExamCandidateValidation.objects.create(
            user=request.user,
            photo=photo_data
        )
        obj_candidate_validation.save()

        img_path = obj_candidate_validation.photo.path

        # flag
        is_authorized_candidate_present = False

        response_fake_detection = verify_real(image_file=img_path)
        label = response_fake_detection["label"]
        if label == "real":
            is_valid = True

            realtime_detected_faces, realtime_extracted_faces, realtime_face_embeddings = get_faces_embeddings(
                img_path
            )

            # import pdb; pdb.set_trace()

            detected_face_count = len(realtime_detected_faces)

            # random user result file
            res_file_name_with_path = generate_random_user_file(request)

            # verify is authorized user present in image
            candidate_img_dataset = CandidateImgDataset.objects.filter(user=request.user)
            
            idx_candidate_face_embedding = None # used to remove entry from realtime_face_embeddings and check who is other
            recognized_persons = []

            if len(realtime_face_embeddings) == 1:
                for idx, realtime_face_embedding in enumerate(realtime_face_embeddings):
                    is_matched = False
                    for single_obj in candidate_img_dataset:
                        known_face_embedding = single_obj.face_embedding

                        is_matched, probability = compare_face_embedding(
                            known_face_embedding, realtime_face_embedding
                        )
                        if is_matched:
                            name = single_obj.user.email
                            break
                    
                    if is_matched:
                        is_authorized_candidate_present = True
                        idx_candidate_face_embedding = idx
                        message = "Candidate present.."
                    else:
                        # check is proctor 
                        # temporarily set to unknown
                        name = "unknown"
                        probability = random.uniform(0.6, 0.8)
                        message = "Candidate not present. Unauthorized person detected."

                    recognized_persons.append({
                        "name": name,
                        "probability": probability,
                        "box": realtime_detected_faces[idx]
                    })

            elif len(realtime_face_embeddings) > 1:
                message = f"Authentication error: multiple persons detected."
            else:
                message = f"Authentication error: candidate not detected."

            # if len(recognized_persons) >= 1:
            #     hightlighted_image = highlight_recognized_faces(
            #         img_path, recognized_persons
            #     )

            #     # save pil image
            #     hightlighted_image.save(res_file_name_with_path, "PNG")

            # else:
            #     # if no face found save source file as result
            #     # later in javascript handle this situation
            #     # if no face detected show current frame from camera
            #     source_pil_image = Image.open(img_path).convert("RGB")
            #     source_pil_image.save(res_file_name_with_path)

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
            
            # # substract base path -- keep only media path
            # media_path_only = res_file_name_with_path.replace(settings.BASE_DIR, '')
            # print(f"media_path_only : {media_path_only}")
        else:
            is_valid = False
            message = "Face spoofing detected"
        
        return JsonResponse({
            'success': True,
            'message': message,
            'is_authorized_candidate_present': is_authorized_candidate_present, # return value depending on user detected
        })

    except Exception as e:
        print(trace_error())
        return JsonResponse({
            'success': False,
            'message': "Can't perform verification on this image. Pass diffrent image to verify.."
            # 'message': str(e)
        })


def check_proctor__superadmin(detected_persons):
    """
    if two or more persons detected 
    person 1 must be valid candidate 
    second person may be proctor or superadmin otherwise mark suspicious exam
    """
    try:
        if len(detected_persons) > 1:
            is_second_person_suspicious = True
            for person in detected_persons:
                # user_id = person['user_id']
                
                if person['user_type'] in ["proctor", "superadmin"]:
                    is_second_person_suspicious = False
                
            if is_second_person_suspicious:
                is_suspicious = True
                reason += "\n Suspicious person is detected."
        return is_second_person_suspicious
    except Exception as e:
        return False
        pass
    
@csrf_exempt
def save_recognize_exam_photo(request, exam_id):

    from recognize.views import (
        get_faces_embeddings,
        compare_face_embedding,
        highlight_recognized_faces
    )
    from candidate.tasks import recognize_candidate_emotion
    from api_consumer.views import verify_real

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
        candidate_img_datasets = CandidateImgDataset.objects.filter(user=request.user)
        
        is_authorized_candidate_present = False
        idx_candidate_face_embedding = None # used to remove entry from realtime_face_embeddings and check who is other
        recognized_persons = []

        response_fake_detection = verify_real(image_file=img_path)
        label = response_fake_detection["label"]
        if label == "real":
            for idx, realtime_face_embedding in enumerate(realtime_face_embeddings):
                is_matched = False
                for single_obj in candidate_img_datasets:
                    known_face_embedding = single_obj.face_embedding

                    is_matched, probability = compare_face_embedding(
                        known_face_embedding, realtime_face_embedding
                    )
                    if is_matched:
                        name = single_obj.user.email
                        break

                is_matched, probability = compare_face_embedding(
                    known_face_embedding, realtime_face_embedding
                )
                
                if is_matched:
                    is_authorized_candidate_present = True
                    idx_candidate_face_embedding = idx
                    
                    # # save extracted face in db
                    # exam_candidate_data.np_face = realtime_extracted_faces[idx]
                    # exam_candidate_data.save()
                else:
                    is_second_person_suspicious = check_proctor__superadmin(realtime_detected_faces)

                    if not is_second_person_suspicious:
                        name = "proctor"
                        probability = random.uniform(0.5, 0.9)
                    else:
                        name = "unknown"
                        probability = random.uniform(0.6, 0.95)

                recognized_persons.append({
                    "name": name,
                    "probability": probability,
                    "box": realtime_detected_faces[idx]  # ['box']
                })

            # trigger detect emotions background task
            recognize_candidate_emotion.apply_async(args=[exam_candidate_data.id], contdown=1)

            # if len(recognized_persons) >= 1:
            #     hightlighted_image = highlight_recognized_faces(
            #         img_path, recognized_persons,
            #         # write_result_2_disk=True,
            #         # res_file_name_with_path=res_file_name_with_path,
            #     )

            # first level suspicious checking
            # is valid candidate available
            if is_authorized_candidate_present == False:
                is_suspicious = True
                reason = "Candidate not detected in image."
            else:
                is_suspicious = False
                reason = ""

            if (len(recognized_persons) > 1):
                is_suspicious = True
                reason += "\n Multiple persons detected."

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
        else:
            is_suspicious = True
            reason = "Face spoofing detected"
            exam_candidate_data.is_suspicious = is_suspicious
            exam_candidate_data.reason = reason
            exam_candidate_data.save()
            response = {
                "message": {
                    "type": "error",
                    "title": "Error Info",
                    "text": "Face spoofing detected",
                },
                "is_authorized_candidate_present": False,
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

    candi_exam = ExamCandidate.objects.get(
        candidate=request.user,
        exam__id=exam_id
    )
    
    prev_exam_remaining_time = candi_exam.exam_remaining_time

    # get exam last start time
    if candi_exam.is_restarted == True:
        start_time = candi_exam.restart_time
    else:
        start_time = candi_exam.start_time
    
    now = timezone.localtime(timezone.now())

    # recalculate remaining time
    # first_ check-the-difference-in-seconds-between-two-dates
    current_exam_seconds = (now-start_time).total_seconds()

    # substract current exam seconds from previous
    if current_exam_seconds > 0:
        new_exam_remaining_time = prev_exam_remaining_time - int(current_exam_seconds)
        candi_exam.exam_remaining_time = new_exam_remaining_time
        candi_exam.is_exam_stopped = True
        candi_exam.exam_stop_count += 1
        candi_exam.save()
    else:
        print(f"current exam run seconds must be greater than zero")


    verb = f'Exam "{exam.name}" stopped due to suspicious activity.\nReason - ' + reason
    
    # send to candidate
    notify.send(
        request.user,
        recipient=request.user,
        verb=verb, 
        icon_class="icon-stop"
    )

    verb = f"Exam '{exam.name}' of candidate '{request.user.email}' stopped due to {reason}"

    # send to all superadmins and proctor
    send_notification_2_user_types(
        sender=request.user,
        verb=verb,
        icon_class="icon-stop",
        user_types=["super_admin", "proctor"]
    )
    response = {
        "message": {
            "type": "info",
            "title": "Info",
            "text": "All super users notified successfully",
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


def get_candidate_exam_que_pallet(request):
    """
    get candidate exam question pallet
    """
    exam_id =  int(request.GET.get('exam_id'))

    # get exam quesion id and sequence number
    exam_questions = ExamQuestion.objects.filter(exam__id=exam_id).values("id", "sequence").order_by("sequence")
    
    data = [] # candidate question pallet
    for exam_question in exam_questions:
        que_id = exam_question["id"]
        que_sequence = exam_question["sequence"]

        cnt = CandidateAnswer.objects.filter(
            candidate__candidate__id=request.user.id, question__id=que_id
        ).count()

        if cnt > 0:
            is_answered = True
        else:
            is_answered = False

        data.append({
            "que_id": que_id,
            "que_sequence": que_sequence,
            "is_answered": is_answered,
        })

    return JsonResponse(data, safe=False)


def get_que_selected_answers(request):
    """
    Get exam question answers selected by candidate
    """
    que_id =  int(request.GET.get('que_id'))

    candidate_selected_answer = CandidateAnswer.objects.filter(
        candidate__candidate__id=request.user.id,  # 112
        question__id=que_id
    ).values("selected_option").first()

    data = {}
    if candidate_selected_answer:
        data["selected_option"] = candidate_selected_answer["selected_option"]
    else:
        data["selected_option"] = []

    return JsonResponse(data, safe=False)
