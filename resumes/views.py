from rest_framework import viewsets
from .models import Resume
from .serializers import ResumeSerializer
from .permissions import ResumePermission


class ResumeViewSet(viewsets.ModelViewSet):

    serializer_class = ResumeSerializer
    permission_classes = [ResumePermission]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Resume.objects.none()

        if user.role and user.role.name == 'candidate':
            return Resume.objects.filter(user=user)

        if user.role and user.role.name in ('admin', 'hr'):
            return Resume.objects.all()

        return Resume.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

