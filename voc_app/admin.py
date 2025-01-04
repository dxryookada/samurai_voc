from django.contrib import admin
from .models import Gender, AgeGroup, Survey, Work

class GenderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class SurveyAdmin(admin.ModelAdmin):
    list_display = ('id', 'submitted_at')

class WorkAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'receipt_number', 'receipt_date')

admin.site.register(Gender, GenderAdmin)
admin.site.register(AgeGroup, AgeGroupAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Work, WorkAdmin)
