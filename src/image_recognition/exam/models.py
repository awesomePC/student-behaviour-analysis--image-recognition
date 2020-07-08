from django.db import models

from django.db import models

from django.utils import timezone
from datetime import datetime as dt

# PostgreSQL specific model fields
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from picklefield.fields import PickledObjectField

from users.models import CustomUser


class Exam(models.Model):
    """
    Exam Details
    """
    name = models.CharField(max_length=200)
    instruction = models.TextField(
        help_text="Instructions with html structure"
    )
    description = models.TextField(
        blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    total_time = models.IntegerField(
        help_text="In Minutes",
        blank=True, null=True
    )
    total_mark = models.IntegerField(
        help_text="Integer value",
        blank=True, null=True
    )
    total_question = models.IntegerField(
        help_text="Total no. of questions",
        blank=True, null=True
    )
    instructions_max_read_time = models.IntegerField(
        help_text="In Minutes",
        default=10
    )
    capture_image_time = models.IntegerField(
        default=30,
        help_text="In Seconds",
    )
    suspicious_show_warning_after = models.IntegerField(
        default=2,
        help_text="Show warning to user after two consecutive suspicious activity",
    )
    suspicious_stop_exam_after = models.IntegerField(
        default=3,
        help_text="",
    )
    is_negative_marking = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name) 


class ExamCandidate(models.Model):
    """
    Exam and candidate relation ship
    
    Arguments:
        models {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, null=True
    )
    candidate = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True
    )
    exam_remaining_time = models.IntegerField(
        help_text="Exam remaining time in seconds",
        blank=True, null=True
    )
    is_started = models.BooleanField(default=False)
    start_time = models.DateTimeField(
        null=True, blank=True, auto_now=False
    )
    end_time = models.DateTimeField(
        null=True, blank=True, auto_now=False
    )
    is_completed = models.BooleanField(default=False)
    is_restarted = models.BooleanField(default=False)
    restart_time = models.DateTimeField(
        null=True, blank=True, auto_now=False,
        help_text="Last restart time."
    )
    restarted_info = ArrayField(
        models.CharField(max_length=200),
        blank=True,
        default=list,
        help_text="Exam if restarted store it in array"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f"Exam-{self.exam.name} Candidate-{self.candidate.email}") 


class ExamSection(models.Model):
    """
    Questions are divided based on section(Implement it later)
    
    Arguments:
        models {[type]} -- [description]
    """
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, null=True
    )
    name = models.TextField(
        blank=True, null=True,
        help_text="section Name"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ExamQuestion(models.Model):
    """
    Exam and Question Mapping
    
    Arguments:
        models {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, null=True
    )
    title = models.TextField(
        blank=True, null=True,
        help_text="Either text or html detect using lxml while rendering"
    )
    sequence = models.IntegerField(
        help_text="Question sequence number",
        blank=True, null=True
    )
    marks = models.IntegerField(
        blank=True, null=True
    )

    is_multi_answer = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f"Exam-{self.exam.name}  Q.{self.sequence}-{self.title}")


class QuestionOption(models.Model):
    """
    Question Options
    
    Arguments:
        models {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    question = models.ForeignKey(
        ExamQuestion, on_delete=models.CASCADE, null=True
    )
    title = models.TextField(
        blank=True, null=True,
        help_text="Either text or html detect using lxml while rendering"
    )
    sequence = models.IntegerField(
        help_text="option sequence number",
        blank=True, null=True
    )
    is_correct = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f"{self.question}-Option-{self.title}")


class CandidateAnswer(models.Model):
    """
    Save record when:
        1) Candidate visit the question  --  save candidate id and question id
        2) Candidate answer the question --  save answer
        3) Candidate mark the question   --  set is_marked flag true - remove it after revisit
    
    Arguments:
        models {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    candidate = models.ForeignKey(
        ExamCandidate, on_delete=models.CASCADE, null=True
    )

    question = models.ForeignKey(
        ExamQuestion, on_delete=models.CASCADE, null=True
    )

    selected_option = ArrayField(
        models.IntegerField(),
        blank=True,
        null=True,
        default=list,
        help_text="selected option sequences -- can be empty if not answered"
    )
    is_answered = models.BooleanField(
        default=False,
        help_text=""
    )
    is_flagged = models.BooleanField(
        default=False,
        help_text="Marked question for review"
    )
    overwrite_count = models.PositiveSmallIntegerField(default=0, blank=True)
    # log overwrite time
    # overwrite_info = 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.candidate) 


def user_exam_directory_path(instance, filename):
    return 'exam/{0}/user_{1}/{2}'.format(
        dt.today().strftime('%Y-%m-%d'), instance.user.id, filename
    )


class ExamCandidatePhoto(models.Model):
    """
    User exam photo data will be stored here
    
    Arguments:
        models {[type]} -- [description]

    ---------------------------------------
    store matching percentage as json field
    ex.
    matching_percentages = [
        {
            "person": "user_4",
            "percentage": 90.45
        }
    ]
    """
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, null=True
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True
    )

    photo = models.FileField(upload_to=user_exam_directory_path)
    np_face = PickledObjectField(blank=True, null=True, help_text="face extracted from image by MTCNN face detector of authorized user in numpy array")

    
    detected_persons_list = JSONField(
        blank=True,
        default=list,
        help_text="Detected persons list"
    )

    np_highlighted_faces = PickledObjectField(blank=True, null=True, help_text="highlighted_faces extracted from image in numpy array format")

    detected_objects = JSONField(
        blank=True,
        default=list,
        help_text="list of detected objects such as mobile -- used to detect suspicious activity"
    )
    is_object_detection_done = models.BooleanField(
        default=False,
        help_text="Is object detection done"
    )

    all_emotions = PickledObjectField(
        blank=True, null=True, 
        help_text="person face with emotions -- happy, sadness, fear"
    )
    top_emotion = PickledObjectField(
        blank=True, null=True, 
        help_text="person face with emotions -- happy, sadness, fear"
    )
    is_emotion_calc_done = models.BooleanField(
        default=False,
        help_text="Is emotion calculation done"
    )
    emotion_message = models.TextField(blank=True, null=True, help_text="Message after calculating emotion")

    liveness = JSONField(
        blank=True,
        default=list,
        help_text="Liveness to avoid spoofing"
    )
    is_suspicious = models.BooleanField(
        default=False,
        help_text="Is activity is suspicious"
    )
    reason = models.TextField(
        blank=True, null=True,
        help_text="Reason if suspicious activity"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def exam_candidate_validation_directory_path(instance, filename):
    return 'exam_user_validation/user_{0}/{1}'.format(
        instance.user.id, filename
    )

class ExamCandidateValidation(models.Model):
    """
    User live testing at training phase will be stored here
    
    Arguments:
        models {[type]} -- [description]
    """
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True
    )
    photo = models.FileField(
        upload_to=exam_candidate_validation_directory_path
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
