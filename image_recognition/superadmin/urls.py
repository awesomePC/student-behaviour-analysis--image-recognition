from django.urls import path
from django.urls import re_path # custom regex path
from . import views

# Namespacing URL names
app_name = 'superadmin'

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path("model-training/", views.model_training, name="model_training"),
    
    path("exam/list/", views.exam_list, name="exam_list"),
    path("exam/add/", views.add_exam, name="add_exam"),
    path("exam/<int:pk>/delete/", views.exam_delete, name="exam_delete"),
    path("exam/<int:pk>/add/questions/", views.ExamAddQuestionView.as_view(), name="exam_add_questions"),
    
    path("exam/<int:pk>/manage/candidates/", views.ExamManageCandidateView.as_view(), name="exam_manage_candidates"),
    
    path("exam/<int:pk>/report/", views.ExamReportView.as_view(), name="exam_report"),

    path('analysis/candidate/list/', views.AnalysisCandidateListView.as_view(), name='analysis-candidate-list'),
    path('candidate/<int:pk>/analysis/', views.CandidateAnalysis.as_view(), name='candidate-analysis'),
    path('emotion/analysis/data/', views.EmotionAnalysisData.as_view(), name='emotion-analysis-data'),
    
]
