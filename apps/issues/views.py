
from rest_framework import generics

from .models import Issue
from .serializers import IssueSerializer
from .permissions import IsRegisteredUser


class IssueCreateView(generics.CreateAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsRegisteredUser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
