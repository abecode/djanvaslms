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
from canvas.models import RawJsonCourse, Course, User, Enrollment
import lib.canvas

token_env_var = "DJANVAS_TOKEN"
per_page = 10
interesting_fields = ['id', "name", "course_code", "workflow_state", "start_at", "uuid", "enrollments"]
exponential_backoff_start_ms = 1000
canvasapi = lib.canvas.api()

def import_raw_json_courses(**options):
    """ get the raw course info from canvas api """
    
    courses = canvasapi.get_all_courses()
    for course_json in courses:
        record = RawJsonCourse(api_id=course_json["id"], json=json.dumps(course_json))
        try:
            record.save()
        except IntegrityError as e:
            print("skipping")
        except Exception as e:
            raise e
    
def save_courses(**options):
    for raw_json_course in RawJsonCourse.objects.all():
        print(raw_json_course.json)
        json_obj = json.loads(raw_json_course.json)
        if not options.get('pretend'):
            record = Course(id=json_obj.get('id'),
                            rawjsoncourse=raw_json_course,
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
                record.save()
            except Exception as e: 
                raise e
        

def import_users_and_enrollments(**options):
    """ here, users are students, teachers, etc.

    requires that Courses have been saved already

    """
    skip_ids = set()
    skip_ids.add(73770000000007599) # keen
    skip_ids.add(73770000000029537) # diversityEDU
    skip_ids.add(73770000000017333) # something I'm not authorized for
    skip_ids.add(73770000000018196) # devops
    skip_ids.add(73770000000037256) # instructional continuity resources
    skip_ids.add(73770000000028287) # something with >500 pages of enrollments
    token = os.environ.get(token_env_var,"")
    if not token:
        raise CommandError(f'no token in "{token_env_var}"')
    headers = {"Authorization": f"Bearer {token}"}
    for course in Course.objects.all():
        print(course.id, course.rawjsoncourse_id)
        if course.id in skip_ids:
            print("skipping", course.id)
            continue
        #only get 630 sp 2021
        # if course.id not in set([73770000000043027,
        #                         73770000000040995,
        #                          73770000000040848]):
            #continue
#        if course.id != "73770000000043027":  # for now just 630
#            continue

        page = 0
        results = []
        # for some reason, the pagination seems different than for courses
        orig_url = f"https://canvas.instructure.com/api/v1/courses/{course.id}/enrollments?per_page={per_page}&page={page}"
        url = orig_url
        while(True):
            page += 1
            r = requests.get(url, headers=headers)
            status = r.status_code
            xratelimitremaining = float(r.headers['X-Rate-Limit-Remaining'])
            # be nice
            print("course", course.id, "pages", page)
            #print(r.json())
            if r.status_code == 403 and xratelimitremaining == 0:
                print("sleeping")
                time.sleep(exponential_backoff_start_ms/1000)
                exponential_backoff_start_ms *= 2
                page -= 1
            results.extend(r.json())
            try:
                url = r.links['next']['url']
                print("new url", url)
            except KeyError:
                break
        print("course", course.id, "pages", page)
        print()
        print(f"there were total {len(results)} results before filtering",
              file=sys.stderr
        )
        for res in results:
            if type(res) == str:
                continue
            print(res)
            if not options.get('pretend'):
                try:
                    userobj = res['user']
                except TypeError: # this seems to be when I'm not a teacher
                    print("not able to get", res)
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
                    userrecord.save()
                except Exception as e:
                    raise e
                enrollrecord = Enrollment(
                    id=res.get('id'),
                    user_id=res.get('user_id'),
                    course_id=res.get('course_id'),
                    type=res.get('type'),
                    created_at=res.get('created_at'),
                    updated_at=res.get('updated_at'),
                    course_section_id=res.get('course_section_id'),
                    enrollment_state=res.get('enrollment_state'),
                    role=res.get('role'),
                    role_id=res.get('role_id'),
                    last_activity_at=res.get('last_activity_at'),
                    last_attended_at=res.get('last_attended_at'),
                    total_activity_time=res.get('total_activity_time')
                    )
                try:
                    enrollrecord.save()
                except IntegrityError as e:
                    print(e)
    
            
class Command(BaseCommand):

    help = "reads courses from the canvas api"

    def handle(self, *args, **options):
        #import_raw_json_courses(**options)
        #save_courses(**options)
        import_users_and_enrollments(**options)
