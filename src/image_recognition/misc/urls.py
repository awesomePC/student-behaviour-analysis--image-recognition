from django.urls import path
from . import views

# Namespacing URL names
# usage : {% url 'polls:detail' question.id %}
app_name = 'misc'

urlpatterns = [
    path('mark_noti_as_read/', views.mark_noti_as_read, name="mark_noti_as_read"),
]