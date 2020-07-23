"""read list of courses from canvas api

uses $DJANVAS_TOKEN env var

cf https://docs.djangoproject.com/en/3.0/howto/custom-management-commands/
cf https://canvas.instructure.com/doc/api/courses.html
cf https://canvas.instructure.com/doc/api/file.pagination.html
cf https://canvas.instructure.com/doc/api/file.throttling.html

"""
import time
import os
import requests
import dateutil.parser as dp
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, reset_queries

from courses.models import Course

token_env_var = "DJANVAS_TOKEN"
per_page = 10
interesting_fields = ['id', "name", "course_code", "workflow_state", "start_at", "uuid", "enrollments"]
exponential_backoff_start_ms = 1000

class Command(BaseCommand):

    help = "reads the list of courses from the canvas api"

    def add_arguments(self, parser):
        parser.add_argument('--current', action='store_true', default=False, help='try to get only the current courses')
        parser.add_argument('--raw', action='store_true', default=False, help='print raw json output instead of interesting fields')
        parser.add_argument('--load_db', action='store_true', default=False, help='load the courses into the db via django')
        
    def handle(self, *args, **options):
        token = os.environ.get(token_env_var,"")
        if not token:
            raise CommandError(f'no token in "{token_env_var}"')
        headers = {"Authorization": f"Bearer {token}"}
        page = 0
        results = []
        while(True):
            page += 1
            r = requests.get(f"https://canvas.instructure.com/api/v1/courses?per_page={per_page}&page={page}", headers=headers)
            status = r.status_code
            xratelimitremaining = float(r.headers['X-Rate-Limit-Remaining'])
            # be nice
            if r.status_code == 403 and xratelimitremaining == 0:
                time.sleep(exponential_backoff_start_ms/1000)
                exponential_backoff_start_ms *= 2
                page -= 1
            results.extend(r.json())
            if r.links['current']['url'] == r.links['last']['url']:
                break
        self.stderr.write(f"there were total {len(results)} results before filtering")
        for res in results:
            if options['current']:
                if res.get("start_at", None) == None:
                    continue
                timediff = time.time() - dp.parse(res.get("start_at")).timestamp()
                if timediff > 60*60*24*6:  # start_at not within last 6 months
                    continue
            if options['raw']:
                self.stdout.write(str(res))
            else:
                self.stdout.write(str({key:res.get(key,"") for key in interesting_fields}))
            if options['load_db']:
                record = Course(id = res['id'], data=res)
                try:
                    record.save()
                except Exception as e:
                    #print(connection.queries)
                    #reset_queries()
                    raise e
