from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from notifications.signals import notify

from django.views.decorators.csrf import csrf_exempt

from users.models import CustomUser

# Create your views here.

@csrf_exempt
def mark_noti_as_read(request):
    """
    Mark notification as read
    
    Arguments:
        request {[type]} -- [description]
    """
    from notifications.models import Notification
    msg_id = request.POST.get("id")
    notifications = Notification.objects.filter(
        id=msg_id
    )
    for notification in notifications:
        # print(notification)
        notification.mark_as_read()

    response = {
        "success": 0,
        "message": {
            "type": "success",
            "title": "Success Info",
            "text": "Notification marked as read",
        },
    }
    return JsonResponse(response, safe=False)


def send_notification_2_user_types(sender, verb, icon_class, user_types=["superadmin"]):
    users = CustomUser.objects.filter(
        user_type__contains=user_types
    )
    notify.send(
        sender=sender,
        recipient=users,
        verb=verb, 
        icon_class=icon_class
    )
    return True