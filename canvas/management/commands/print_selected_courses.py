from django.core.management.base import BaseCommand, CommandError
from canvas.models import RawJsonCourse

class Command(BaseCommand):
    help = 'prints the selected RawJsonCourses'



    def handle(self, *args, **options):
        for rc in RawJsonCourse.objects.filter(selected=True):
            print(rc, rc.api_id, rc.json)

                
