from django.contrib import admin
from .models import Issue


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'user',
        'category',
        'ward',
        'priority',
        'created_at',
    )
    list_filter = ('priority', 'category')
    search_fields = ('title', 'description', 'user__username')