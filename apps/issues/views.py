from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Issue
from .serializers import IssueSerializer
from .permissions import IsRegisteredUser

class IssueCreateView(generics.CreateAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsRegisteredUser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IssueListView(generics.ListAPIView):
    queryset = Issue.objects.all().order_by('-created_at')
    serializer_class = IssueSerializer
    permission_classes = [AllowAny]


class IssueDetailView(generics.RetrieveAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [AllowAny]


