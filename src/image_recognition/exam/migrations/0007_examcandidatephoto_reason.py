# Generated by Django 2.2.1 on 2019-09-13 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0006_auto_20190913_2230'),
    ]

    operations = [
        migrations.AddField(
            model_name='examcandidatephoto',
            name='reason',
            field=models.TextField(blank=True, help_text='Reason if suspicious activity', null=True),
        ),
    ]