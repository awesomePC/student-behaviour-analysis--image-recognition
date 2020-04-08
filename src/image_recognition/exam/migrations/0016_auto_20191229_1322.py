# Generated by Django 2.2.5 on 2019-12-29 07:52

from django.db import migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0015_auto_20191216_0034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='examcandidatephoto',
            name='emotions',
        ),
        migrations.AddField(
            model_name='examcandidatephoto',
            name='all_emotions',
            field=picklefield.fields.PickledObjectField(blank=True, editable=False, help_text='person face with emotions -- happy, sad, fear', null=True),
        ),
        migrations.AddField(
            model_name='examcandidatephoto',
            name='top_emotion',
            field=picklefield.fields.PickledObjectField(blank=True, editable=False, help_text='person face with emotions -- happy, sad, fear', null=True),
        ),
        migrations.AlterField(
            model_name='examcandidatephoto',
            name='np_face',
            field=picklefield.fields.PickledObjectField(blank=True, editable=False, help_text='face extracted from image by MTCNN face detector of authorized user in numpy array', null=True),
        ),
        migrations.AlterField(
            model_name='examcandidatephoto',
            name='np_highlighted_faces',
            field=picklefield.fields.PickledObjectField(blank=True, editable=False, help_text='highlighted_faces extracted from image in numpy array format', null=True),
        ),
    ]