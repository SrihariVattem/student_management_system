# Generated by Django 5.1.4 on 2024-12-11 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0005_remove_student_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='password',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
