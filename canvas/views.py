from django.shortcuts import render
from django.views.generic.list import ListView
from django.http import HttpResponse
import datetime
from django.utils import timezone

from canvas.models import Course, Enrollment

def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

async def async_datetime(request):
    now = datetime.datetime.now()
    html = '<html><body>It is now asynchronously %s.</body></html>' % now
    return HttpResponse(html)

class CourseListView(ListView):
    model = Course
    paginate_by = 100
    ordering = ['-start_at']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
    
class CourseEnrollmentListView(ListView):
    model = Enrollment
    paginate_by = 100
    #ordering = ['-start_at']
    def get_context_data(self, **kwargs):
        print("request: ", self.request)
        print("self.kwargs: ", self.kwargs)
        print("self.request.GET: ", self.request.GET)
        context = super().get_context_data(**kwargs)
        print(context)
        context["object_list"] = Enrollment.objects.filter(
            course=self.kwargs['course_id'])
        context["course"] = context["object_list"][0].course

        return context
