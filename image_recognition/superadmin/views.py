from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse

from django.urls import reverse_lazy

from django.views.generic import ListView, DetailView 
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.views import View

import json

from exam.models import *
from exam.forms import *
from users.models import CustomUser

# Create your views here.

def dashboard(request):
    context = {}
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


class CandidateAnalysis(View):
    def get(self, request, *args, **kwargs):
        candidate_id = self.kwargs["pk"]
        candidate_exams = ExamCandidate.objects.filter(candidate__id=candidate_id)
        
        # temprory for graph
        if candidate_exams:
            exam_id = candidate_exams[0].exam.id
        else:
            exam_id = 0

        context = {
            "candidate_exams": candidate_exams,
            "candidate_id": candidate_id,
            "exam_id": exam_id,
        }
        # print(context)
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


class EmotionAnalysisData(View):
    """
    Emotion analysis data for graph
    """
    def get(self, request, *args, **kwargs):
        candidate_id = request.GET.get("candidate_id")
        exam_id = request.GET.get("exam_id")
        candidate_photos = ExamCandidatePhoto.objects.filter(user__id=candidate_id, exam__id=exam_id)
        
        emotions = []

        for candidate_photo in candidate_photos:
            # print(candidate_photo.emotions)
            if not candidate_photo.emotions:
                continue
            
            if isinstance(candidate_photo.emotions, dict):
                label = candidate_photo.emotions.get('label')
                emotion_probability = candidate_photo.emotions.get('emotion_probability')
                if label:
                    emotions.append(label)
                else:
                    emotions.append("unknown")

        emotion_frequency = count_frequency(emotions)
        # print(emotion_frequency)

        data = []
        for key, value in emotion_frequency.items():
            data.append({
                "emotion": key,
                "count": value
            })
        return JsonResponse(data, safe=False)