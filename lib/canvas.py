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


skip_course_ids = set()
skip_course_ids.add(73770000000007599) # keen
skip_course_ids.add(73770000000029537) # diversityEDU
skip_course_ids.add(73770000000017333) # something I'm not authorized for
skip_course_ids.add(73770000000018196) # devops
skip_course_ids.add(73770000000037256) # instructional continuity resources
skip_course_ids.add(73770000000028287) # something with >500 pages of enrollments
skip_course_ids.add(73770000000033834) # strategic planning

def get_paginated_results(url, headers, timeout=5):
    """ helper function that implements the paginated api query """
    page = 1
    results = []
    nrequests = 0

    urlplusquery = f"{url}?per_page={per_page}&page={page}"
    while(True):
        print(url, headers, file=sys.stderr)
        print(urlplusquery)
        resp = requests.get(urlplusquery, headers=headers, timeout=timeout)
        status = resp.status_code
        xratelimitremaining = float(resp.headers.get('X-Rate-Limit-Remaining', 1))

        print("status ", status, ", xratelimitremaining ", xratelimitremaining,
              file=sys.stderr)
        # be nice
        if status == 403 and xratelimitremaining == 0:
            backoff_time_ms = exponential_backoff_start_ms
            print("backing off ", backoff_time_ms, file=sys.stderr)
            time.sleep(backoff_time_ms/1000)
            backoff_time_ms *= 2
        if status == 404:
            return []
        if status == 401:
            return []
        results.extend(resp.json())
        print("\n\n", resp.links, "\n\n")
        if 'next' in resp.links:
            urlplusquery = resp.links['next']['url']
            time.sleep(normal_sleep_time_ms/1000)
            continue
        if 'last' not in resp.links:
             break
        if resp.links['current']['url'] == resp.links['last']['url']:
            break
        #page += 1
        nrequests += 1
        if nrequests > 50:
            break
    print(f"there were total {len(results)} results before filtering",
          file=sys.stderr)
    # check to make sure that each element is a dictionary
    results = [r for r in results if isinstance(r, dict)]
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

    def get_course_sections(self, course_id):
        url = f"{base_url}{courses_api_path}/{course_id}/sections"
        headers = {"Authorization": f"Bearer {self.token}"}
        sections  = get_paginated_results(url, headers)
        return sections

    def get_course_enrollments(self, course_id):
        url = f"{base_url}{courses_api_path}/{course_id}/enrollments"
        headers = {"Authorization": f"Bearer {self.token}"}
        enrollments  = get_paginated_results(url, headers)
        return enrollments
