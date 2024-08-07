# Generated by Django 3.2.25 on 2024-07-01 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_groupmembership_group_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='firstname',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='lastname',
            new_name='last_name',
        ),
        migrations.AddField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=True),
        ),
    ]
