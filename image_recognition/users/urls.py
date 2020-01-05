from django.urls import path
from . import views

# Namespacing URL names
# usage : {% url 'polls:detail' question.id %}
app_name = 'users'

urlpatterns = [
    # default will be handle login
    path('', views.handle_login, name='handle_login'),
]

