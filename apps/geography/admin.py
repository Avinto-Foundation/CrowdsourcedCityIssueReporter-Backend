from django.contrib import admin
from .models import District, Municipality, Ward


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('district_name', 'created_at')
    search_fields = ('district_name',)


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('municipality_name', 'district', 'created_at')
    list_filter = ('district',)
    search_fields = ('municipality_name',)


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('ward_number', 'municipality', 'created_at')
    list_filter = ('municipality',)