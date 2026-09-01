from rest_framework import serializers
from django.contrib.auth.models import Permission
from .models import User, Role


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):

        candidate = Role.objects.get(name='candidate')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            role=candidate,
        )

        view_resume = Permission.objects.get(codename='view_resume')
        add_resume = Permission.objects.get(codename='add_resume')
        change_resume = Permission.objects.get(codename='change_resume')
        delete_resume = Permission.objects.get(codename='delete_resume')

        candidate, created = Role.objects.get_or_create(name='candidate', defaults={
            'description': 'Candidate can view, create and edit own resumes'})
        candidate.permissions.set([view_resume, add_resume, change_resume])

        hr, created = Role.objects.get_or_create(name='hr', defaults={
            'description': 'HR can view all resumes'
        })
        hr.permissions.set([view_resume])

        admin, created = Role.objects.get_or_create(name='admin', defaults={
            'description': 'Administrator has full access'
        })
        admin.permissions.set([view_resume, add_resume, change_resume, delete_resume])

        return user
