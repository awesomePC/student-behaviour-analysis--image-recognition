from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from notifications.signals import notify

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

from django.conf import settings

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

import random
import os
import uuid
import re
from PIL import Image
from numpy import array

from datetime import datetime

import base64
from django.core.files.base import ContentFile

# Create your views here.
def handle_login(request):
    user = request.user
    print("user.user_type", user.__dict__)
    try:
        if user.is_superuser or user.user_type == 'superadmin':
            return redirect('/superadmin/')

        if user.user_type == 'candidate':
            return redirect('/candidate/')

        elif user.user_type == 'proctor':
            return redirect('/proctor/')
        else:
            # import pdb;pdb.set_trace()
            # default
            print("Error .. Not valid login type ")
            return redirect('/accounts/logout/')
    except:
        print("Not logged in .. redirect to login")
        return redirect('account_login')   
    # pass

    # ## for testing log and notification functionality
    # ## temp -- default -- remove after removing comments from above code
    # print("Testing logger : ")
    # logger.info("Logger is working properly ... ")

    # # testing notify
    # notify.send(sender=user, recipient=user, verb='you reached level 10', icon_class="icon-paperplane")
    # # reading all
    # # from notifications.models import Notification
    # # notifications = Notification.objects.unread()
    # # print(notifications)
    # # reading single user
    # # print("Notifications : ")
    # # print(user.notifications.unread())

    # return render(request, 'users/template.html', {})

def dataset_builder(request):
    context = {}
    return render(request, 'users/template.html', context)

@csrf_exempt
def save_photo_snap(request):
    if request.method == 'POST':
        from recognize.views import (
            get_faces_embeddings,
            compare_face_embedding,
            highlight_faces
        )

        photo_data = request.POST.get("photo", "")
        category = request.POST.get("category", "")
        # print(category)
        
        today_date = datetime.today().strftime('%Y-%m-%d')
        current_hour = datetime.today().strftime('%H')

        folder = os.path.join(
            settings.MEDIA_ROOT,
            f'dataset/{category}/{today_date}/{current_hour}'
        )
        os.makedirs(folder, exist_ok=True)

        # save file
        format, imgstr = photo_data.split(';base64,')
        ext = format.split('/')[-1]
        print(f"ext : {ext}")

        file_name = str(uuid.uuid4()) + "." +  ext

        filename__path = os.path.join(
            folder,
            file_name,
        )
        print(filename__path)

        with open(filename__path, "wb") as f:
            f.write(base64.b64decode(imgstr))

        # highlight faces
        hightlighted_encoded_image = highlight_faces(
            filename__path
        )

        response = {
            "status": 1,
            "hightlighted_encoded_image": hightlighted_encoded_image,
        }
        return JsonResponse(response, safe=False)

    elif request.method == 'GET':
        return HttpResponse("GET Method not allowed")

