from django.db import models


class Category(models.Model):
    category_name_en = models.CharField(max_length=100)
    category_name_ne = models.CharField(max_length=100)
    description_en = models.TextField()
    description_ne = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_name_en