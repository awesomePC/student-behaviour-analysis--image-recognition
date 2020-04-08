from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from notifications.signals import notify

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect


# Create your views here.
@csrf_exempt
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
