from django.urls import path
from . import views

# Namespacing URL names
app_name = 'exam'

urlpatterns = [
    # path('/', views.sign_up, name=""),
    path('get_question_info/', views.get_question_info, name='get_question_info'),
]