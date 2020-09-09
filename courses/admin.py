from django.contrib import admin

# Register your models here.
from .models import Course


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'start_at', 'end_at',
                    'course_code', 'sis_course_id')


admin.site.register(Course, CourseAdmin)
