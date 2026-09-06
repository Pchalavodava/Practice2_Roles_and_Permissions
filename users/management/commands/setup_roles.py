from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission

from users.models import Role


class Command(BaseCommand):

    def handle(self, *args, **options):
        view_resume = Permission.objects.get(codename='view_resume')
        add_resume = Permission.objects.get(codename='add_resume')
        change_resume = Permission.objects.get(codename='change_resume')
        delete_resume = Permission.objects.get(codename='delete_resume')

        candidate, created = Role.objects.get_or_create(name='candidate', defaults={
            'description': 'Candidate can view, create and edit own resumes'})
        candidate.permissions.set([view_resume, add_resume, change_resume, delete_resume])

        hr, created = Role.objects.get_or_create(name='hr', defaults={
            'description': 'HR can view all resumes'
        })
        hr.permissions.set([view_resume])

        admin, created = Role.objects.get_or_create(name='admin', defaults={
            'description': 'Administrator has full access'
        })
        admin.permissions.set([view_resume, add_resume, change_resume, delete_resume])

        self.stdout.write(
            self.style.SUCCESS('Roles and permissions have been configured successfully')
        )