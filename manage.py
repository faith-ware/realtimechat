#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realtimechat.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

def delete_users_online():
    if (Connected_channel.objects.count() == 0) and (Online.objects.count() == 0):
        pass
    else:
        Connected_channel.objects.all().delete()
        Online.objects.all().delete()
    
if __name__ == '__main__':
    main()
    from chat.models import Online, Connected_channel
    delete_users_online()

