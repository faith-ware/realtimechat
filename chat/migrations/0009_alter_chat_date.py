# Generated by Django 3.2.4 on 2021-07-12 08:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0008_alter_chat_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
    ]
