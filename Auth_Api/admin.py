from django.contrib import admin
from .models import User, TrainerProfile, CounsellorProfile, StudentProfile, AdminProfile, Course, Enrollment, Batch

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')

class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'middle_name', 'age', 'gender', 'contact_info', 'address', 'dob')
    search_fields = ('user__email', 'middle_name')

class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'middle_name', 'expertise', 'subject_taught', 'contact_info', 'date_joined', 'added_by')
    search_fields = ('user__email', 'expertise')

class CounsellorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'middle_name', 'short_profile_summary', 'contact_info', 'date_joined', 'added_by')
    search_fields = ('user__email', 'short_profile_summary')

class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'middle_name')
    search_fields = ('user__email',)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'duration', 'created_at')
    search_fields = ('title',)

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    search_fields = ('student__email', 'course__title')

class BatchAdmin(admin.ModelAdmin):
    list_display = ('course', 'trainer', 'start_date', 'end_date', 'capacity', 'current_enrollment')
    search_fields = ('course__title', 'trainer__email')

# Registering models with the admin site
admin.site.register(User, UserAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(TrainerProfile, TrainerProfileAdmin)
admin.site.register(CounsellorProfile, CounsellorProfileAdmin)
admin.site.register(AdminProfile, AdminProfileAdmin)
admin.site.register(Course, CourseAdmin)  # New course model registration
admin.site.register(Enrollment, EnrollmentAdmin)  # New enrollment model registration
admin.site.register(Batch, BatchAdmin)  # New batch model registration
