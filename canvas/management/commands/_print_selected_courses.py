import sys
sys.path.append(".")
from canvas.models import RawJsonCourse

for rawcourse in RawJsonCourse.objects.filter(selected=True):
    print(rawcourse)
