from django.db import connection
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Hashes all unhashed Passwords, which were imported by SQL Script!'


    def handle(self, *args, **options):

        from django.contrib.auth import get_user_model

        # Look for all users with raw password!
        UserModel = get_user_model()
        users = UserModel.objects.all()
        for user in users:
            if user.password.startswith('pbkdf2_sha256'):
                continue
            
            # update password
            user.set_password(user.password)
            user.save()
        
        self.stdout.write(self.style.SUCCESS('Successfully updated all raw passwords!'))
