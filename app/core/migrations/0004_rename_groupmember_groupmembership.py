# Generated by Django 3.2.25 on 2024-06-25 09:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_groupmember'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='GroupMember',
            new_name='GroupMembership',
        ),
    ]