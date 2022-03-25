"""read list of courses from canvas api

uses $DJANVAS_TOKEN env var

cf https://docs.djangoproject.com/en/3.0/howto/custom-management-commands/
cf https://canvas.instructure.com/doc/api/courses.html
cf https://canvas.instructure.com/doc/api/file.pagination.html
cf https://canvas.instructure.com/doc/api/file.throttling.html

"""
import json
import os
import requests
import sys
import time
import dateutil.parser as dp
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, reset_queries
from django.db.utils import IntegrityError
from canvas.models import (Pull, RawJson, Course, User, Enrollment,
                           CourseSection)

import lib.canvas

token_env_var = "DJANVAS_TOKEN"
per_page = 10
interesting_fields = ['id', "name", "course_code", "workflow_state", "start_at", "uuid", "enrollments"]
exponential_backoff_start_ms = 1000
canvasapi = lib.canvas.api()

def import_raw_json_courses(pull, **options):
    """ get the raw course info from canvas api """
    print(f"Running import raw json courses for pull {pull.id}")
    courses = canvasapi.get_all_courses()
    print(f"Got {len(courses)} Courses from canvas api")
    count = 0
    for course_json in courses:
        record = RawJson(json=json.dumps(course_json),
                         model="Course",
                         api_id=course_json["id"],
                         pull=pull)

        try:
            record.save()
            count += 1
        except IntegrityError as e:
            print(f"skipping Course {record.id} for pull {pull.id} {pull}")
        except Exception as e:
            raise e
    print(f"Saved {count} raw json courses")

def import_raw_json_sections(pull, **options):
    """ get the raw course section info from canvas api """

    print(f"Running import raw json sections for pull {pull.id}")
    count = 0
    for raw_json_course in RawJson.objects.filter(pull=pull, model="Course"):
        course_id = raw_json_course.api_id
        print(f"Getting sections for Course {course_id}")
        sections = canvasapi.get_course_sections(course_id)
        for section  in sections:
            print(f"saving rawjson for {section}")
            record = RawJson(json=json.dumps(section),
                             model="CourseSection",
                             api_id=section["id"],
                             pull=pull)

            try:
                record.save()
                count += 1
            except IntegrityError as e:
                print(e)
            except Exception as e:
                raise e
    print(f"Saved {count} raw json sections")

def import_raw_json_enrollments(pull, **options):
    """ here, users are students, teachers, etc.

    requires that Courses have been saved already

    """
    count = 0
    for raw_json_course in RawJson.objects.filter(pull=pull, model="Course"):
        print(raw_json_course.api_id)
        if raw_json_course.api_id in lib.canvas.skip_course_ids:
            print("skipping: course we don't want", raw_json_course.api_id)
            continue
        enrollments = canvasapi.get_course_enrollments(raw_json_course.api_id)
        for json_obj in enrollments:
            print("\n\n", json_obj, "\n\n")
            record = RawJson(json=json.dumps(json_obj),
                             model="Enrollment",
                             api_id=json_obj["id"],
                             pull=pull)

            try:
                record.save()
                count += 1
            except IntegrityError as e:
                print(e)
            except Exception as e:
                raise e
    print(f"Saved {count} raw json enrollments")

def save_courses(pull, **options):
    count = 0
    for raw_json_course in RawJson.objects.filter(pull=pull, model="Course"):
        print(raw_json_course.json)
        json_obj = json.loads(raw_json_course.json)
        if not options.get('pretend'):
            record = Course(id=json_obj.get('id'),
                            name=json_obj.get('name'),
                            account_id=json_obj.get('account_id'),
                            uuid=json_obj.get('uuid'),
                            start_at=json_obj.get('start_at'),
                            created_at=json_obj.get('created_at'),
                            course_code=json_obj.get('course_code'),
                            enrollment_term_id=json_obj.get('enrollment_term_id'),
                            end_at=json_obj.get('end_at'),
                            sis_course_id=json_obj.get('sis_course_id'),
            )
            try:
                if record.id not in lib.canvas.skip_course_ids:
                    record.save()
            except Exception as e:
                raise e

def save_course_sections(pull, **options):
    for raw_json_section in RawJson.objects.filter(pull=pull,
                                                  model="CourseSection"):
        json_obj = json.loads(raw_json_section.json)
        record = CourseSection(id = json_obj.get('id'),
                               course_id = json_obj.get('course_id'),
                               name = json_obj.get('name'),
                               start_at = json_obj.get('start_at'),
                               end_at = json_obj.get('end_at'),
                               created_at = json_obj.get('created_at'),
                               sis_section_id = json_obj.get('sys_section_id'),
                               sis_course_id = json_obj.get('sys_course_id') )
        try:
            if record.course_id not in lib.canvas.skip_course_ids:
                record.save()
        except IntegrityError as e:
            print(e)


def save_users_and_enrollments(pull, **options):
    """ here, users are students, teachers, etc.

    requires that Courses have been saved already

    """
    for raw_json_course in RawJson.objects.filter(pull=pull, model="Enrollment"):
        if raw_json_course.api_id in lib.canvas.skip_course_ids:
            print("skipping", raw_json_course.api_id)
            continue
        json_obj = json.loads(raw_json_course.json)
        try:
            userobj = json_obj['user']
        except TypeError: # this seems to be when I'm not a teacher
            print("not able to get user object from ", json_obj)

        userrecord = User(id=userobj.get('id'),
                          name=userobj.get('name'),
                          created_at=userobj.get('created_at'),
                          sortable_name=userobj.get('sortable_name'),
                          short_name=userobj.get('short_name'),
                          sis_user_id=userobj.get('sis_user_id'),
                          root_account=userobj.get('root_account'),
                          login_id=userobj.get('login_id')
                          )
        try:
            if json_obj['course_id'] not in lib.canvas.skip_course_ids:
                userrecord.save()
        except IntegrityError as e:
            print(e)
        except Exception as e:
            raise e
        enrollrecord = Enrollment(
            id=json_obj.get('id'),
            user_id=json_obj.get('user_id'),
            course_id=json_obj.get('course_id'),
            type=json_obj.get('type'),
            created_at=json_obj.get('created_at'),
            updated_at=json_obj.get('updated_at'),
            course_section_id=json_obj.get('course_section_id'),
            enrollment_state=json_obj.get('enrollment_state'),
            role=json_obj.get('role'),
            role_id=json_obj.get('role_id'),
            last_activity_at=json_obj.get('last_activity_at'),
            last_attended_at=json_obj.get('last_attended_at'),
            total_activity_time=json_obj.get('total_activity_time')
        )
        try:
            if json_obj['course_id'] not in lib.canvas.skip_course_ids:
                enrollrecord.save()
        except IntegrityError as e:
            print(e)


class Command(BaseCommand):

    help = "reads courses from the canvas api"

    def handle(self, *args, **options):
        #pull = Pull()
        #pull.save()
        pull = Pull.objects.get(id=26)
        print(f"Running Pull {pull.id}")
        #import_raw_json_courses(pull, **options)
        #import_raw_json_sections(pull, **options)
        #import_raw_json_enrollments(pull, **options)

        save_courses(pull, **options)
        save_course_sections(pull)
        save_users_and_enrollments(pull, **options)
