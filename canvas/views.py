from django.shortcuts import render
from django.views.generic.list import ListView
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse, Http404
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
        context = super().get_context_data(**kwargs)
        context["object_list"] = Enrollment.objects.filter(
            course=self.kwargs['course_id']).order_by("user__sortable_name", )
        try:
            context["course"] = context["object_list"][0].course
        except IndexError:
            raise Http404("no enrollments found for the class")
        return context
    def process_exception(self, request, exception):
        return HttpResponseNotFound("sorry, there was an error with that request")

class HomeView(ListView):
    model = Course
    paginate_by = 100
    ordering = ['-start_at']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

def courses_json(request):
    data = Course.objects.all().values().order_by("-start_at", "name", )
    for d in data:
        for attribute in d:
            print(attribute, type(d[attribute]))
            if attribute.endswith("id") and type(d[attribute]) is int:
                d[attribute] = str(d[attribute]) # don't you love javascript?
    print(data)
    return JsonResponse(list(data), safe=False)

def d3(request):
    return render(request, 'd3.html')
