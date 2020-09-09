from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.
class Course(models.Model):
    """ a model for a course

    based on Canvas output, we use postgres jsonb column for all the data

    for indexing purposes, we'll use the id from Canvas as the primary key

    """
    id = models.BigIntegerField(primary_key=True)
    data = JSONField()
    name = models.CharField(max_length=100, blank=True, default=None, null=True)
    created_at = models.DateTimeField(blank=True, default=None, null=True)
    start_at = models.DateTimeField(blank=True, default=None, null=True)
    end_at = models.DateTimeField(blank=True, default=None, null=True)
    course_code = models.CharField(max_length=100, blank=True, default=None, null=True)
    sis_course_id = models.CharField(max_length=100, blank=True, default=None, null=True)

    def __str__(self):
        return f"Course(id={self.id}, name={self.name}, created_at={self.created_at}, start_at={self.start_at}, end_at={self.end_at}, course_code={self.course_code}, sis_course_id={self.sis_course_id}"
