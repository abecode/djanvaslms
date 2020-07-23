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
