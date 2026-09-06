from rest_framework import serializers
# from django.contrib.auth.models import Permission
from .models import User, Role


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        candidate = Role.objects.get(name='candidate')

        return User.objects.create_user(username=validated_data['username'], password=validated_data['password'],
                                        role=candidate)
