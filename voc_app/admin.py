from django.contrib import admin
from .models import Gender, AgeGroup, Work, Survey, SurveyResponse, Question, Choice

class GenderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class WorkAdmin(admin.ModelAdmin):
    list_display = ('id', 'work_area', 'receipt_number', 'receipt_date')

class SurveyAdmin(admin.ModelAdmin):
    list_display = ('id', 'work', 'gender', 'age_group', 'free_text', 'free_text_ai_rating', 'submitted_at')

class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'question', 'choice')

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'weight', 'order')
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'content', 'points', 'order')

admin.site.register(Gender, GenderAdmin)
admin.site.register(AgeGroup, AgeGroupAdmin)
admin.site.register(Work, WorkAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(SurveyResponse, SurveyResponseAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Question, QuestionAdmin)