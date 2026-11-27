
from django.db import models
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
        status_value = self.request.query_params.get('status')
        sort_by = self.request.query_params.get('sort', 'newest')

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

        if status_value:
            queryset = queryset.filter(status=status_value)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        if sort_by == 'oldest':
            queryset = queryset.order_by('created_at')

        elif sort_by == 'priority':
            queryset = queryset.order_by(
                models.Case(
                    models.When(priority='Urgent', then=0),
                    models.When(priority='High', then=1),
                    models.When(priority='Medium', then=2),
                    models.When(priority='Low', then=3),
                ),
                '-created_at'
            )

        elif sort_by == 'recently_updated':
            queryset = queryset.order_by('-updated_at')

        else:
            queryset = queryset.order_by('-created_at')

        return queryset


class IssueDetailView(generics.RetrieveAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [AllowAny]
