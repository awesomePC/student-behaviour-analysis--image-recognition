from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse

from django.urls import reverse_lazy

from django.views.generic import ListView, DetailView 
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

import json

# to use collections.Counter() 
import collections 

from exam.models import *
from exam.forms import *
from users.models import CustomUser

# Create your views here.

def dashboard(request):
    total_users = CustomUser.objects.all().count()
    total_exams = Exam.objects.all().count()
    total_questions = ExamQuestion.objects.all().count()
    total_options = QuestionOption.objects.all().count()

    context = {
        "total_users": total_users,
        "total_exams": total_exams,
        "total_questions": total_questions,
        "total_options": total_options,
    }
    return render(request, 'superadmin/dashboard.html', context)

def model_training(request):
    context = {}
    return render(request, 'superadmin/model_training/train.html', context)
    
def exam_list(request):
    exams = Exam.objects.filter()
    context = {
        'exams': exams,
    }
    return render(request, 'superadmin/exam/list_all.html', context)

def add_exam(request, template_name='superadmin/exam/add_exam.html'):
    form = ExamForm(request.POST or None)
    if form.is_valid():
        exam = form.save()
        return redirect('superadmin:exam_add_questions', exam.id)
    
    context = {
        'form': form,
    }
    return render(request, template_name, context)

def exam_delete(request, pk, template_name='superadmin/exam/exam_confirm_delete.html'):
    exam = get_object_or_404(Exam, pk=pk)    
    if request.method=='POST':
        exam.delete()
        return redirect('superadmin:exam_list')
    
    context = {
        'object': exam,
    }
    return render(request, template_name, context)


@method_decorator(login_required, name='dispatch')
class ExamAddQuestionView(View):
    """
    Exam add questions
    """
    template_name = 'superadmin/exam/exam_add_questions.html'

    def get(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam, pk=self.kwargs["pk"])
        if exam:
            lst = range(0, exam.total_question)
        else:
            lst = []

        numbers = range(0, 4)

        context = {
            'exam': exam,
            'lst': lst,
            'numbers': numbers,
        }
        return render(request, self.template_name, context)
        
    def post(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam, pk=self.kwargs["pk"])
        questions_data = json.loads(
            request.POST.get("questions")
        )

        for idx, question in enumerate(questions_data):
            que_type = question.get("question-type")
            if que_type == 'single_choice':
                is_multi_answer = False
            else:
                is_multi_answer = True

            exam_question = ExamQuestion.objects.create(
                exam=exam,
                title=question.get("question-title"),
                sequence=(idx + 1),
                marks=question.get("question-marks"),
                is_multi_answer=is_multi_answer,
            )
            exam_question.save()

            # options
            options = question.get("options")
            for idx, option in enumerate(options):
                question_option = QuestionOption.objects.create(
                    question=exam_question,
                    title=option.get("option"),
                    sequence=(idx + 1),
                    is_correct=option.get("correct")
                )
                question_option.save()
        
        # redirect to exam candidate allocation
        return redirect("superadmin:exam_manage_candidates", exam.id)


class ExamManageCandidateView(View):
    """
    Manage Candidate allocation for exam
    """
    template_name = 'superadmin/exam/allocate_candidate.html'

    def get(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam, pk=self.kwargs["pk"])
        candidates = CustomUser.objects.filter(
            user_type="candidate",
        )

        # get list of pre-allocated exam candidates if exists
        exam_candidate_ids = ExamCandidate.objects.filter(
            exam=exam,
        ).values_list('candidate__id', flat=True)

        context = {
            'exam': exam,
            'candidates': candidates,
            'exam_candidate_ids': exam_candidate_ids,
        }
        return render(request, self.template_name, context)
        
    def post(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam, pk=self.kwargs["pk"])
        allocate = request.POST.get("allocate")
        candidate_id = request.POST.get("candidate_id")
        
        candidate = CustomUser.objects.get(
            id=candidate_id
        )

        if allocate == "true":
            exam_candidate = ExamCandidate.objects.create(
                exam=exam,
                candidate=candidate,
                exam_remaining_time=exam.total_time * 60,
            )
            exam_candidate.save()

            response = {
                "success": True,
                "message": "Candidate allocated successfully"
            }
        else:
            ExamCandidate.objects.filter(
                exam=exam,
                candidate=candidate
            ).delete()

            response = {
                "success": True,
                "message": "Candidate De-allocated successfully.."
            }
        return JsonResponse(response, safe=True)


class ExamReportView(View):
    """
    Manage Exam reports
    """

    def get(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam, pk=self.kwargs["pk"])
        exams = Exam.objects.filter()
        context = {
            'exams': exams,
        }
        template_name = 'superadmin/reports/list_all.html'
        return render(request, template_name, context)
        
    def post(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam, pk=self.kwargs["pk"])
        allocate = request.POST.get("allocate")
        candidate_id = request.POST.get("candidate_id")
        
        candidate = CustomUser.objects.get(
            id=candidate_id
        )

        if allocate == "true":
            exam_candidate = ExamCandidate.objects.create(
                exam=exam,
                candidate=candidate,
                exam_remaining_time=exam.total_time * 60,
            )
            exam_candidate.save()

            response = {
                "success": True,
                "message": "Candidate allocated successfully"
            }
        else:
            ExamCandidate.objects.filter(
                exam=exam,
                candidate=candidate
            ).delete()

            response = {
                "success": True,
                "message": "Candidate De-allocated successfully.."
            }
        return JsonResponse(response, safe=True)


class AnalysisCandidateListView(ListView):
    """
    To view the list of objects
    """
    template_name = 'superadmin/analysis/list_candidate.html'
    model = CustomUser
    context_object_name = 'candidates'

    def get_queryset(self):
        return CustomUser.objects.filter(user_type="candidate")


class EmotionClasses:
    """
    Emotion classes
    """
    labels = {
        0: "angry",
        1: "disgust",
        2: "fear",
        3: "happy",
        4: "sad",
        5: "surprise",
        6: "neutral",
        7: "unknown", # empty
    }

    color_mapping = {
        "angry": "rgba(244, 67, 54, 0.87)",
        "disgust": "rgba(230, 127, 220, 0.85)",
        "fear": "rgb(67, 67, 72)",
        "happy": "rgba(49, 183, 54, 0.72)",
        "sad": "rgb(247, 163, 92)",
        "surprise": "rgb(241, 92, 128)",
        "neutral": "rgb(124, 181, 236)",
        "unknown": "rgb(144, 124, 124)",
    }

    @classmethod
    def _get_labels(cls):
        return cls.labels

    @classmethod
    def _get_labels_list(cls):
        lst = []
        for key, value in cls.labels.items():
            lst.append(value)
        return lst

    def add_colors(cls, lst_emotions_dict):
        """
        lst_emotions_dict = [
          {
            "name": "fear"
          }
        ]

        call:
        EmotionClasses().add_colors(lst_emotions_dict)
        
        output:

        lst_emotions_dict = [
          {
            "name": "fear",
            'color': 'rgb(67, 67, 72)'
          }
        ]
        """
        for emotion_info in lst_emotions_dict:
            emotion_name = emotion_info["name"]

            # get color
            color = cls.color_mapping.get(emotion_name)
            if color:
                emotion_info["color"] = color
            else:
                emotion_info["color"] = "rgb(124, 181, 236)"

        return lst_emotions_dict


class CandidateExamList(View):
    def get(self, request, *args, **kwargs):
        candidate_id = self.kwargs["pk"]
        candidate_exams = ExamCandidate.objects.filter(candidate__id=candidate_id)
        # print(candidate_exams)
        context = {
            "candidate_exams": candidate_exams,
            "candidate_id": candidate_id,
        }
        template_name = 'superadmin/analysis/candidate_exam_list.html'
        return render(request, template_name, context)


class CandidateAnalysis(View):
    def get(self, request, *args, **kwargs):
        # get value from url
        candidate_id = self.kwargs["pk"]

        # get value from param
        exam_id = request.GET.get("exam_id")

        # import pdb;pdb.set_trace()

        exam = Exam.objects.get(
            id=exam_id
        )
        candidate_exam = ExamCandidate.objects.filter(
            exam=exam,
            candidate__id=candidate_id
        ).first()

        answer_report = CandidateAnswerEvaluation.get_answer_report(
            exam, candidate_exam
        )

        candidate_photos = ExamCandidatePhoto.objects.filter(
            user__id=candidate_id, exam__id=exam_id
        ).order_by('-created_at')

        suspicious_cnt, normal_cnt, total_cnt = 0, 0, 0

        for idx, candidate_photo in enumerate(candidate_photos):
            total_cnt += 1
            if candidate_photo.is_suspicious:
                suspicious_cnt = suspicious_cnt + 1
            else:
                normal_cnt = normal_cnt + 1

        if total_cnt > 0:
            suspicious_per = round((suspicious_cnt *100) / total_cnt, 2)
        else:
            suspicious_per = 0

        threshold = 4
        if suspicious_per > threshold:
            is_suspicious = True
        else:
            is_suspicious = False

        answered = 0
        not_visited = 0
        not_answered = 0
        total_score = 0
        correct_answers = 0

        context = {
            "candidate_exam": candidate_exam,
            "candidate_id": candidate_id,
            "exam_id": exam_id,
            "suspicious_cnt": suspicious_cnt,
            "suspicious_per": suspicious_per,
            "is_suspicious": is_suspicious,
            "normal_cnt": normal_cnt,

            "answered": answer_report.get("answered"),
            "not_visited": answer_report.get("not_visited"),
            "not_answered": answer_report.get("not_answered"),
            "total_score": answer_report.get("total_score"),
            "correct_answers": answer_report.get("correct_answers"),
        }
        template_name = 'superadmin/analysis/candidate_analysis.html'
        return render(request, template_name, context)


def count_frequency(my_list): 
    """
    count the frequency of elements in a list using a dictionary 
    
    Args:
        my_list ([type]): [description]
    
    Returns:
        [type]: [description]
    Example::
        >> my_list = ["happy", "neutral", "happy"]
        >> count_frequency(my_list)
        {'happy': 2, 'neutral': 1}
    """
    # Creating an empty dictionary  
    freq = {} 
    for items in my_list: 
        freq[items] = my_list.count(items) 
    return freq


class EmotionOverallAnalysis(View):
    """
    Emotion analysis data for graph
    """
    def get(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        candidate_id = request.GET.get("candidate_id")
        exam_id = request.GET.get("exam_id")
        candidate_photos = ExamCandidatePhoto.objects.filter(user__id=candidate_id, exam__id=exam_id)
        
        emotions = []

        for candidate_photo in candidate_photos:
            if isinstance(candidate_photo.top_emotion, list):
                if len(candidate_photo.top_emotion) == 2:
                    label = candidate_photo.top_emotion[0]
                    emotion_probability = candidate_photo.top_emotion[1]
                    if label:
                        emotions.append(label)
                    else:
                        emotions.append("unknown")

        emotion_frequency = count_frequency(emotions)
        # print(emotion_frequency)

        data = []
        for key, value in emotion_frequency.items():
            data.append({
                "name": key,
                "y": value
            })

        # add colors in dict
        data = EmotionClasses().add_colors(data)

        return JsonResponse(data, safe=False)


class EmotionTimelineData(View):
    """
    Emotion timeline data for graph
    """
    def get(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        candidate_id = request.GET.get("candidate_id")
        exam_id = request.GET.get("exam_id")
        candidate_photos = ExamCandidatePhoto.objects.filter(
            user__id=candidate_id, exam__id=exam_id
        ).order_by('-created_at')
        
        emotions_overtime = []

        for idx, candidate_photo in enumerate(candidate_photos):
            if isinstance(candidate_photo.top_emotion, list):
                if len(candidate_photo.top_emotion) == 2:
                    label = candidate_photo.top_emotion[0]
                    # emotion_probability = candidate_photo.top_emotion[1]
                    if label:
                        str_time = candidate_photo.created_at.strftime('%H:%M:%S')
                    else:
                        label = "unknown"

                    emotions_overtime.append({
                        "text": f"{label} \n{str_time}",
                        "y": idx,
                        "x": "1",
                        "center": "left" if (idx % 2 != 0) else "right" # position
                    })

        # print(emotions_overtime)

        return JsonResponse(emotions_overtime, safe=False)


class CandidateAnswerEvaluation:
    @classmethod
    def get_answer_report(cls, exam, exam_candidate):

        # get total questions
        exam_questions = ExamQuestion.objects.filter(exam=exam)
        total_questions = len(exam_questions)

        # get status of each question
        answered = 0
        not_visited = 0
        not_answered = 0
        total_score = 0
        correct_answers = 0

        report = []

        for question in exam_questions:
            # import pdb; pdb.set_trace()
            # get all correct options sequences
            correct_options = QuestionOption.objects.filter(
                question=question,
                is_correct=True
            ).values_list('sequence', flat=True).order_by('sequence')

            # select candidate answers
            candidate_answer = CandidateAnswer.objects.filter(
                candidate=exam_candidate,
                question=question,
            ).first()

            if candidate_answer:
                answered += 1

                # str_selected_option = candidate_answer.selected_option
                # lst_selected_option = list(
                #     map(
                #         int, str_selected_option.split(",")
                #     )
                # )

                lst_selected_option = candidate_answer.selected_option

                # using collections.Counter() to check if  
                # lists are equal 
                if collections.Counter(correct_options) == collections.Counter(lst_selected_option): 
                    correct_answers += 1
                    total_score += question.marks
                    is_correctly_answered = True
                else: 
                    is_correctly_answered = False
                    pass

                report.append({
                    "candidate_answer_id": candidate_answer.id,
                    "created_at": candidate_answer.created_at,
                    "is_correctly_answered": is_correctly_answered,
                })
            else:
                not_answered += 1
            pass
        
        return {
            "answered": answered,
            "not_visited": not_visited,
            "not_answered": not_answered,
            "total_score": total_score,
            "correct_answers": correct_answers,
            "report": report
        }


class CandidateAnswerNearestEmotion:
    """
    Candidate last emotion before candidate answers
    """
    @classmethod
    def candidate_answer_last_emotion(cls, exam_id, candidate_id, lst_answers):
        # print(exam_id)
        # print(candidate_id)
        # print(lst_answers)

        for answer_info in lst_answers:
            answer_created_at = answer_info["created_at"]
            # print(f"answer_created_at: {answer_created_at}")

            candidate_photo = ExamCandidatePhoto.objects.filter(
                user__id=candidate_id, exam__id=exam_id,
                created_at__gt=answer_created_at
            ).order_by('created_at').first()

            emotion_label = "unknown"

            # print(f"candidate_photo: {candidate_photo}")

            if candidate_photo:
                if isinstance(candidate_photo.top_emotion, list):
                    if len(candidate_photo.top_emotion) == 2:
                        emotion_label = candidate_photo.top_emotion[0]
                        # emotion_probability = candidate_photo.top_emotion[1]
            else:
                pass
            
            answer_info["emotion"] = emotion_label
        return lst_answers


class AnswerCorrectnessOverEmotion(View):
    """
    Answer correct or not over emotion
    """
    # def get_user_answers()
    def get(self, request, *args, **kwargs):
        
        candidate_id = request.GET.get("candidate_id") # 56
        exam_id = request.GET.get("exam_id") # 1

        exam = Exam.objects.get(
            id=exam_id
        )

        exam_candidate = ExamCandidate.objects.get(
            exam=exam,
            candidate__id=candidate_id,
        )

        answer_report = CandidateAnswerEvaluation.get_answer_report(
            exam, exam_candidate
        )

        lst_answers = answer_report["report"]

        lst_answers_with_emotions = CandidateAnswerNearestEmotion.candidate_answer_last_emotion(
            exam_id, candidate_id, lst_answers
        )
        # print(f"lst_answers_with_emotions : {lst_answers_with_emotions}")
        
        # emotions_overtime = lst_answers_with_emotions

        emotions_list = EmotionClasses._get_labels_list()

        # init all emotions count as zero
        correct_dict = { key: 0 for key in emotions_list }
        wrong_dict = { key: 0 for key in emotions_list }

        for answer_info in lst_answers_with_emotions:
            emotion = answer_info["emotion"]
            is_correctly_answered = answer_info["is_correctly_answered"]

            if is_correctly_answered:
                correct_dict[emotion] = correct_dict[emotion] + 1
            else:
                wrong_dict[emotion] = wrong_dict[emotion] + 1
        
        emotions_overtime = [
            {
                "name": 'Correct',
                "data": list(correct_dict.values()),
                "color": '#43a047'

            }, 
            {
                "name": 'Wrong',
                "data": list(wrong_dict.values()),
                "color": '#dc1818cc'
            }
        ]
        response = {
            "emotions_list": emotions_list,
            "emotions_overtime": emotions_overtime
        }
        # print(f"response : {response}")
        # import pdb;pdb.set_trace()
        return JsonResponse(response, safe=False)


class AnswerSpeedOverEmotion(View):
    """
    Answer solving speed over emotion
    """
    def get(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        candidate_id = request.GET.get("candidate_id") # 56
        exam_id = request.GET.get("exam_id") # 1

        exam = Exam.objects.get(
            id=exam_id
        )

        exam_candidate = ExamCandidate.objects.get(
            exam=exam,
            candidate__id=candidate_id,
        )

        answer_report = CandidateAnswerEvaluation.get_answer_report(
            exam, exam_candidate
        )

        lst_answers = answer_report["report"]

        lst_answers_with_emotions = CandidateAnswerNearestEmotion.candidate_answer_last_emotion(
            exam_id, candidate_id, lst_answers
        )

        # emotions_overtime = lst_answers_with_emotions

        emotions_list = EmotionClasses._get_labels_list()

        # init
        emotion_dict = { key: [] for key in emotions_list }

        for idx, answer_info in enumerate(lst_answers_with_emotions):
            emotion = answer_info["emotion"]
            is_correctly_answered = answer_info["is_correctly_answered"]

            if idx == 1:
                answer_time_seconds = 5 # 5 seconds later replace with exam start time
            else:
                current_answer_time = answer_info["created_at"]
                previous_answer_time = lst_answers_with_emotions[idx -1 ]["created_at"]
                
                seconds = (previous_answer_time - current_answer_time).total_seconds()
                answer_time_seconds = int(seconds)
                pass 
        
            emotion_dict[emotion].append(answer_time_seconds)

        response = []
        for key, time_data in emotion_dict.items():
            if time_data:
                avg = sum(time_data) / len(time_data)
                avg = round(abs(avg), 2)
            else:
                avg = 0.0

            response.append({
                "name": key,
                "y": avg
            })

        response = EmotionClasses().add_colors(response)

        return JsonResponse(response, safe=False)


class AnswerOverwritingEmotion(View):
    """
    Answer overwriting over emotion
    """
    def get(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        candidate_id = request.GET.get("candidate_id") # 56
        exam_id = request.GET.get("exam_id") # 1

        exam = Exam.objects.get(
            id=exam_id
        )

        exam_candidate = ExamCandidate.objects.get(
            exam=exam,
            candidate__id=candidate_id,
        )

        # emotions_list = EmotionClasses._get_labels_list()

        # # init
        # emotion_dict = { key: 0 for key in emotions_list }

        # response = []
        # for key, value in emotion_dict.items():
        #     response.append({
        #         "name": key,
        #         "y": value
        #     })

        # response = EmotionClasses().add_colors(response)

        # CandidateAnswer.objects.filter(candidate=exam_candidate).order_by('question__sequence')

        queryset = CandidateAnswer.objects.filter(candidate=exam_candidate).values("question__sequence","overwrite_count").order_by('question__sequence')

        data = list(queryset)

        # rename dict keys as per hicharts requirements
        # map question__sequence -> name & overwrite_count -> y
        for d in data:
            d['name'] = d.pop('question__sequence')
            d['y'] = d.pop('overwrite_count')
            
        return JsonResponse(data, safe=False)


class OverAllSuspiciousActivity(View):
    """
    overall Suspicious activity
    """
    def get(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        candidate_id = request.GET.get("candidate_id") # 56
        exam_id = request.GET.get("exam_id") # 1

        candidate_photos = ExamCandidatePhoto.objects.filter(
            user__id=candidate_id, exam__id=exam_id
        ).order_by('-created_at')
        
        emotions_overtime = []

        suspicious_cnt, normal_cnt, unknown_cnt = 0, 0, 0

        for idx, candidate_photo in enumerate(candidate_photos):
            if candidate_photo.is_suspicious:
                suspicious_cnt = suspicious_cnt + 1
            else:
                normal_cnt = normal_cnt + 1

        response = [{
            "name": "Suspicious Activity",
            "y": suspicious_cnt,
            "color": "rgba(244, 67, 54, 0.87)"
        },
        {
            "name": "Normal Activity",
            "y": normal_cnt,
            "color": "rgba(49, 183, 54, 0.72)"
        }]
        print(f"suspicious activity graph data: {response}")
        return JsonResponse(response, safe=False)