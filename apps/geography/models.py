from django.db import models


class District(models.Model):
    district_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.district_name
class Municipality(models.Model):
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name='municipalities'
    )
    municipality_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.municipality_name
class Ward(models.Model):
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.PROTECT,
        related_name='wards'
    )
    ward_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['municipality', 'ward_number'],
                name='unique_ward_number_per_municipality'
            )
        ]

    def __str__(self):
        return f"{self.municipality} - Ward {self.ward_number}"
