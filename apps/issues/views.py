from django.db.models import Q
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
    serializer_class = IssueSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Issue.objects.all().order_by('-created_at')

        category_id = self.request.query_params.get('category')
        district_id = self.request.query_params.get('district')
        municipality_id = self.request.query_params.get('municipality')
        ward_id = self.request.query_params.get('ward')
        search_query = self.request.query_params.get('search')

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if district_id:
            queryset = queryset.filter(
                ward__municipality__district_id=district_id
            )
        if municipality_id:
            queryset = queryset.filter(
                ward__municipality_id=municipality_id
            )
        if ward_id:
            queryset = queryset.filter(ward_id=ward_id)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        return queryset


class IssueDetailView(generics.RetrieveAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [AllowAny]


