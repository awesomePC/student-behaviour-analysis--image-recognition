from django.urls import path
from . import views

# Namespacing URL names
app_name = 'recognize'

urlpatterns = [
    path('start_embedding_training_model/', views.start_embedding_training_model, name="start_embedding_training_model"),
    
]