"""djanvaslms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from canvas.views import (current_datetime,
                          async_datetime,
                          CourseListView,
                          CourseEnrollmentListView,
                          HomeView,
                          courses_json,
                          d3
                          )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('datetime/', current_datetime),
    path('adt/', async_datetime),
    path('courses/', CourseListView.as_view(),
         name='course-list'),
    path('course-enrollments/<int:course_id>/',
         CourseEnrollmentListView.as_view(),
         name='course-enrollment-list'),
    path('courses-json/', courses_json, name='courses-json'),
    path('d3/', d3, name='d3'),
    path('', HomeView.as_view(), name='home-view'),

]
