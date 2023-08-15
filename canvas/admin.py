from django.contrib import admin

# Register your models here.
from .models import (Pull, RawJson, Course, CourseSection, User, Enrollment)



class PullAdmin(admin.ModelAdmin):
    date_hierarchy = "ts"
    ordering = ["-ts"]
    list_display = ("id", "ts")

admin.site.register(Pull, PullAdmin)

class RawJsonAdmin(admin.ModelAdmin):
    list_display = ("id", "api_id", "model", "pull",)

admin.site.register(RawJson, RawJsonAdmin)

class CourseAdmin(admin.ModelAdmin):
    date_hierarchy = "start_at"
    ordering = ["-start_at"]
    list_display = ("name", "created_at", "start_at", "course_code",
                    "enrollment_term_id", "sis_course_id", )

admin.site.register(Course, CourseAdmin)

class CourseSectionAdmin(admin.ModelAdmin):
    date_hierarchy = "start_at"
    ordering = ["-start_at"]
    list_display = ("name", "course", "created_at", "start_at",
                    "sis_course_id", )

admin.site.register(CourseSection, CourseSectionAdmin)

class UserAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
    list_display = ("name", "created_at")

admin.site.register(User, UserAdmin)

class EnrollmentAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
    list_display = ("user", "course", "type", "created_at",
                    "course_section", "enrollment_state", "role")

admin.site.register(Enrollment, EnrollmentAdmin)
