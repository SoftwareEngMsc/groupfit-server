# Generated by Django 3.2.25 on 2024-07-07 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_rename_friendship_friends'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friends',
            name='connected_date',
            field=models.DateField(null=True),
        ),
    ]
