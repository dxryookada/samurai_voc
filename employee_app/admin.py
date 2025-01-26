from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, WorkArea, AwardType, AwardCount, ConstructionWorker

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'name', 'employee_id', 'work_area', 'is_staff', 'is_active', 'login_lock_until')
    list_filter = ['is_staff', 'is_active']
    search_fields = ['email', 'name', 'employee_id']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'employee_id', 'work_area')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'name', 'employee_id', 'work_area'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('password'):
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)
class WorkAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class AwardTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class AwardCountAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'award_type')

class ConstructionWorkerAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'construction')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(WorkArea, WorkAreaAdmin)
admin.site.register(AwardType, AwardTypeAdmin)
admin.site.register(AwardCount, AwardCountAdmin)
admin.site.register(ConstructionWorker, ConstructionWorkerAdmin)