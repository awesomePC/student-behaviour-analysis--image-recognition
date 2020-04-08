from django.forms import ModelForm

from exam.models import Exam

class ExamForm(ModelForm):
    class Meta:
        model = Exam
        fields = [
            'name', 'instruction', 'description',
            'is_active', 'total_time', 'total_mark',
            'total_question', 'instructions_max_read_time',
            'capture_image_time', 'suspicious_show_warning_after',
        ]
