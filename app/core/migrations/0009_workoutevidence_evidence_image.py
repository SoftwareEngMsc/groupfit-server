# Generated by Django 3.2.25 on 2024-07-04 20:15

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_workout_workoutevidence'),
    ]

    operations = [
        migrations.AddField(
            model_name='workoutevidence',
            name='evidence_image',
            field=models.ImageField(null=True, upload_to=core.models.workout_evidence_image_file_path),
        ),
    ]
