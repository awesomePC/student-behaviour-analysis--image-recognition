# import the logging library
import logging
logger = logging.getLogger(__name__)

from django.shortcuts import render

from helper.utils.error_handling import trace_error

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from helper.utils.text_processing import is_html_text

from notifications.signals import notify

from .models import *


def get_user_exams_list(user):
    """
    Get active and completed exam list
    
    Arguments:
        user {[type]} -- [description]
    """
    try:
        active_exams = ExamCandidate.objects.filter(
            candidate=user,
            is_completed=False
        )
        completed_exams = ExamCandidate.objects.filter(
            candidate=user,
            is_completed=True
        )
        return (active_exams, completed_exams)

    except:
        error = trace_error()
        logger.error(error)
        return (None, None)

def get_exam_record(exam_id):
    """
    [summary]
    
    Arguments:
        exam_id {[type]} -- [description]
    """
    exam = Exam.objects.get(
        id=exam_id
    )
    return exam


def is_opt_selected(exam_id, user_id, question_id, option_id):
    """
    Is option selected by user or not
    
    Returns:
        Bool -- [description]
    """
    candidate_answer = CandidateAnswer.objects.filter(
        candidate__exam__id= exam_id,
        candidate__candidate__id=user_id,
        question__id=question_id,
        is_answered=True,
    ).first()
    if candidate_answer:
        selected_opt_list = candidate_answer.selected_option.split(",")
        if option_id in selected_opt_list:
            return True
        else:
            return False
    else:
        return False


def get_candidate_next_question_index(request_user_id, exam_id, prev_question_index=None):
    """
    Get next question to display
    
    Arguments:
        request {[type]} -- [description]
    """
    # get all question ids
    all_questions_ids = ExamQuestion.objects.filter(
        exam__id=exam_id,
        is_active=True,
    ).values_list('id', flat=True).order_by('sequence')

    # get candidate answers
    candidate_answers = CandidateAnswer.objects.filter(
        candidate__exam__id= exam_id,
        candidate__candidate__id=request_user_id,
        is_answered=True
    )
    # get answered question ids
    answered_que_ids = []
    for candidate_answer in candidate_answers:
        answered_que_ids.append(candidate_answer.question.id)

    if len(all_questions_ids) == len(answered_que_ids):
        return {
            "message": {
                "type": "error",
                "title": "Error Info",
                "text": "No any question remaining to answer.The length of all questions and answered questions is same.",
            },
            "next_action_needed": {
                "show_msg": {
                    "type": "info",
                    "title": "Success Info",
                    "text": "All questions attempted. You can now submit exam"
                }
            }
        }
        
    # Remove all the elements that occur in one list from another
    not_answered_question_ids = [int(x) for x in all_questions_ids if x not in answered_que_ids]
    
    if prev_question_index:
        prev_question_index = int(prev_question_index)
        next_question_id = next(v for i, v in enumerate(not_answered_question_ids) if v > prev_question_index)
    else:
        next_question_id = None

    if not next_question_id:
        # get first unsolved question
        next_question_id = not_answered_question_ids[0]

    next_question = ExamQuestion.objects.get(
        id=next_question_id
    )

    return {
        "message": {
            "type": "success",
            "title": "Success Info",
            "text": "Next question index calculated",
        },
        "next_question_index": next_question.sequence,

    }

@csrf_exempt
def get_question_info(request):
    # import pdb
    # pdb.set_trace()
    
    exam_id = request.POST.get("exam_id")
    question_index = request.POST.get("question_index")

    question = ExamQuestion.objects.filter(
        exam__id=exam_id,
        sequence=question_index,
        is_active=True,
    ).order_by('sequence').first()

    if question:
        # get question options
        options = QuestionOption.objects.filter(
            question=question,
            is_active=True,
        ).order_by('sequence')

        options_data = []
        for option in options:
            # check is option selected by user
            is_opt_selected_by_user = is_opt_selected(
                exam_id=question.exam.id,
                user_id=request.user.id,
                question_id=question.id,
                option_id=option.id
            )

            options_data.append({
                "id": option.id,
                "title": option.title,
                "sequence": option.sequence,
                "is_correct": option.is_correct,
                "is_selected_by_user": is_opt_selected_by_user,
                "is_html": True if is_html_text(option.title) else False,
            })

        response = {
            "success": True,
            "question": {
                "id": question.id,
                "title": question.title,
                "sequence": question.sequence,
                "marks": question.marks,
                "is_multi_answer": question.is_multi_answer,
                "is_html": True if is_html_text(question.title) else False,
            },
            "options": options_data
        }
        return JsonResponse(response, safe=True)
    else:
        response = {
            "success": False,
            "message": {
                "type": "error",
                "title": "Error Info",
                "text": "No Questions found",
            }
        }
        return JsonResponse(response, safe=True)
