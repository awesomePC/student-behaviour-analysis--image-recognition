from django.urls import path
from . import views

# Namespacing URL names
# usage : {% url 'polls:detail' question.id %}
app_name = 'users'

urlpatterns = [
    # default will be handle login
    path('', views.handle_login, name='handle_login'),
    path('dataset-builder/', views.dataset_builder, name="dataset_builder"),
    path('save_photo_snap/', views.save_photo_snap, name="save_photo_snap",)
]