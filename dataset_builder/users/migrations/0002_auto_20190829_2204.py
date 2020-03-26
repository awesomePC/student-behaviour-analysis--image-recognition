# Generated by Django 2.2.1 on 2019-08-29 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='phone',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('candidate', 'Candidate'), ('proctor', 'Proctor'), ('super_admin', 'Super Admin')], max_length=15),
        ),
    ]
