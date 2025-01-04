from django.contrib import admin
from .models import CustomUser, WorkArea, AwardType, AwardCount, ConstructionWorker

class WorkAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class AwardTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class AwardCountAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'award_type')

class ConstructionWorkerAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'construction')

admin.site.register(CustomUser)
admin.site.register(WorkArea, WorkAreaAdmin)
admin.site.register(AwardType, AwardTypeAdmin)
admin.site.register(AwardCount, AwardCountAdmin)
admin.site.register(ConstructionWorker, ConstructionWorkerAdmin)
