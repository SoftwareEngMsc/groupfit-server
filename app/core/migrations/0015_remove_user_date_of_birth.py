# Generated by Django 3.2.25 on 2024-07-08 23:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_friends_connected_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='date_of_birth',
        ),
    ]
