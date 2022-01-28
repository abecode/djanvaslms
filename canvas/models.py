from datetime import date
from django.db import models
from django.utils.timezone import now
#from django.contrib.postgres.fields import JSONField

INPERSON = "inperson"
VIRTUAL = "virtual"
ABSENT = "absent"
EXCUSED = "excused"
LATE = "late"

ATTENDANCE_CHOICES = (
    (INPERSON, "In Person"),
    (VIRTUAL, "Virtual"),
    (ABSENT, "Absent"),
    (EXCUSED, "Excused"),
    (LATE, "Late"))



# Create your models here.
class RawJsonCourse(models.Model):
    """a model for a course

    based on Canvas output, just the raw json

    for indexing purposes, we'll use the id from Canvas as the primary
    key

    """
    json = models.TextField()
    api_id = models.BigIntegerField(unique=True)
    def __str__(self):
        return f"Course(id={self.id})"

class Course(models.Model):
    """ a model for a course

    based on Canvas output, but unpacked from json

    for indexing purposes, we'll use the id from Canvas as the primary key

    """
    id = models.BigIntegerField(primary_key=True)
    rawjsoncourse = models.ForeignKey(RawJsonCourse, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, default=None, null=True)
    account_id = models.BigIntegerField(null=True)
    uuid = models.CharField(max_length=100, blank=True, default=None, null=True)
    start_at = models.DateTimeField(blank=True, default=None, null=True)
    created_at = models.DateTimeField(blank=True, default=None, null=True)
    course_code = models.CharField(max_length=100, blank=True, default=None, null=True)
    enrollment_term_id = models.BigIntegerField(null=True)
    end_at = models.DateTimeField(blank=True, default=None, null=True)
    sis_course_id = models.CharField(max_length=100, blank=True, default=None, null=True)

    def __str__(self):
        return f"Course(id={self.id}, name={self.name}, created_at={self.created_at}, start_at={self.start_at}, end_at={self.end_at}, course_code={self.course_code}, sis_course_id={self.sis_course_id})"

class User(models.Model):
    """a model for a canvas user 
    
    includes both students, teachers, and observers
    """
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, default=None, null=True)
    created_at = models.DateTimeField(blank=True, default=None, null=True)
    sortable_name = models.CharField(max_length=100, blank=True, default=None, null=True)
    short_name = models.CharField(max_length=100, blank=True, default=None, null=True)
    sis_user_id = models.CharField(max_length=100, blank=True, default=None, null=True)
    root_account = models.CharField(max_length=100, blank=True, default=None, null=True)
    login_id = models.CharField(max_length=100, blank=True, default=None, null=True)


class Enrollment(models.Model):
    """association table for enrollment of users to courses
    
    includes both students, teachers, and observers (see type
    attribute)

    """
    id = models.BigIntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    type = models.CharField(max_length=100, blank=True, default=None, null=True)
    created_at = models.DateTimeField(blank=True, default=None, null=True)
    updated_at = models.DateTimeField(blank=True, default=None, null=True)
    course_section_id = models.BigIntegerField(blank=True, default=None, null=True)
    enrollment_state = models.CharField(max_length=100, blank=True, default=None, null=True)
    role = models.CharField(max_length=100, blank=True, default=None, null=True)
    role_id = models.BigIntegerField(blank=True, default=None, null=True)
    last_activity_at = models.DateTimeField(blank=True, default=None, null=True)
    last_attended_at = models.DateTimeField(blank=True, default=None, null=True)
    total_activity_time = models.BigIntegerField(blank=True, default=None, null=True)
    class Meta:
        unique_together = ('user', 'course', 'type')

class ClassSesh(models.Model):
    """ a course meets for (usually) 14 class sessions per semester 
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(blank=False, null=False, default=date.today)

class Attendance(models.Model):
    """for each classSesh, for each student, there can be zero or more
    attendance taken"""
    course = models.ForeignKey(ClassSesh, on_delete=models.CASCADE)
    datetime = models.DateField(default=now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    state =  models.CharField(max_length=10, choices=ATTENDANCE_CHOICES)

class Participation(models.Model):
    """for each classSesh, for each student, there can be zero or more
    attendance taken"""
    course = models.ForeignKey(ClassSesh, on_delete=models.CASCADE)
    datetime = models.DateField(default=now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(default=1)
    note = models.CharField(max_length=420, null=True, blank=True)
    
