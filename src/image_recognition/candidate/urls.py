from django.urls import path
from . import views

# Namespacing URL names
# usage : {% url 'polls:detail' question.id %}
app_name = 'candidate'

urlpatterns = [
    path('sign_up/', views.sign_up, name="sign_up"),

    path('save_captured_sign_up_photo/', views.save_captured_sign_up_photo, name="save_captured_sign_up_photo"),
    
    # path('upload_sign_up_images/', views.upload_sign_up_images, name="upload_sign_up_images"),
    # path('delete_sign_up_image/<int:image_id>/', views.delete_sign_up_image, name="delete_sign_up_image"),

    path('', views.dashboard, name='dashboard'),

    # # exam
    path('exam_list/', views.exam_list, name="exam_list"),
    path('exam_instructions/<int:exam_id>/', views.exam_instructions, name='exam_instructions'),
    
    path('exam_validate_user/<int:exam_id>/', views.exam_validate_user, name="exam_validate_user"),
    path('ajax_validate_user/', views.ajax_validate_user, name="ajax_validate_user"),
    
    path('exam/<int:exam_id>/', views.exam, name='exam'),
    
    path('get_next_question_index/', views.get_next_question_index, name="get_next_question_index"),
    
    path('save_candidate_answer/', views.save_candidate_answer, name="save_candidate_answer"),
    path('submit_exam/', views.submit_exam, name="submit_exam"),

    path('completed_confirmation/<int:exam_id>/', views.completed_confirmation, name='completed_confirmation'),
    
    # path('save_exam_photo/', views.save_exam_photo, name="save_exam_photo"),

    path('save_recognize_exam_photo/<int:exam_id>/', views.save_recognize_exam_photo, name="save_recognize_exam_photo"),
    path('stop_exam/', views.stop_exam, name="stop_exam"),
    path('stop_exam_reason/<int:exam_id>/', views.stop_exam_reason, name="stop_exam_reason"),

    # 
    path('get_candidate_exam_que_pallet/', views.get_candidate_exam_que_pallet, name="get_candidate_exam_que_pallet"),
    path('get_que_selected_answers/', views.get_que_selected_answers, name="get_que_selected_answers"),
]