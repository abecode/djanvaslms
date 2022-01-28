import json
import os
import requests
import sys
import time

base_url =  "https://canvas.instructure.com/api"
token_env_var = "DJANVAS_TOKEN"
per_page = 20
exponential_backoff_start_ms = 1000
normal_sleep_time_ms = 200

version = "v1"
courses_api_path = f"/{version}/courses"

def get_paginated_results(url, headers, timeout=5):
    """ helper function that implements the paginated api query """
    page = 1
    results = []
    nrequests = 0

    while(True):
        urlplusquery = f"{url}?per_page={per_page}&page={page}"
        print(url, headers, file=sys.stderr)
        resp = requests.get(urlplusquery, headers=headers, timeout=timeout)
        status = resp.status_code
        xratelimitremaining = float(resp.headers['X-Rate-Limit-Remaining'])
        print("status ", status, ", xratelimitremaining ", xratelimitremaining,
              file=sys.stderr)
        # be nice
        if status == 403 and xratelimitremaining == 0:
            backoff_time_ms = exponential_backoff_start_ms
            print("backing off ", backoff_time_ms, file=sys.stderr)
            time.sleep(backoff_time_ms/1000)
            backoff_time_ms *= 2
        results.extend(resp.json())
        if resp.links['current']['url'] == resp.links['last']['url']:
            break
        page += 1
        time.sleep(normal_sleep_time_ms/1000)
        nrequests += 1
        if nrequests > 50:
            break
    print(f"there were total {len(results)} results before filtering",
          file=sys.stderr)
    return results


class api:
    """ general class to get data from Canvas """
    def __init__(self):
        self.token = os.environ.get(token_env_var,"")
        if not self.token:
            raise CommandError(f'no token in "{token_env_var}"')

    def get_all_courses(self):
        page = 1
        results = []
        nrequests = 0
        url = f"{base_url}{courses_api_path}"
        headers = {"Authorization": f"Bearer {self.token}"}
        courses = get_paginated_results(url, headers)

        # for res in courses:
        #     Print.dumps(res, sort_keys=True, indent=4), sys.stderr)
        #     interesting_fields = ['id', "name", "course_code",
        #                           "workflow_state", "start_at", "uuid", "enrollments"]
        #     #print(str({key:res.get(key,"") for key in interesting_fields}))

        return courses
