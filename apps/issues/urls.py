
from django.urls import path

from .views import (
    IssueCreateView,
    IssueListView,
    IssueDetailView,
    IssueVoteView,
    IssueRemoveVoteView,
)

urlpatterns = [
    path('', IssueListView.as_view(), name='issue-list'),
    path('create/', IssueCreateView.as_view(), name='issue-create'),
    path('<int:pk>/vote/', IssueVoteView.as_view(), name='issue-vote'),
    path('<int:pk>/unvote/', IssueRemoveVoteView.as_view(), name='issue-unvote'),
    path('<int:pk>/', IssueDetailView.as_view(), name='issue-detail'),
]
