import json
import os
import requests
import sys
import time

from django.core.management.base import CommandError

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

def get_paginated_results(url, headers, timeout=5, *, skip_forbidden=False):
    """ helper function that implements the paginated api query """
    results = []
    retries = 0
    urlplusquery = f"{url}?per_page={per_page}&page=1"
    while True:
        print(urlplusquery, file=sys.stderr)
        try:
            resp = requests.get(urlplusquery, headers=headers, timeout=timeout)
        except requests.RequestException:
            raise CommandError(f"Canvas request failed for {urlplusquery}; check connectivity.") from None
        status = resp.status_code
        try:
            remaining = float(resp.headers.get('X-Rate-Limit-Remaining', 1))
        except (ValueError, TypeError):
            remaining = None
        print(f"Canvas HTTP {status}", file=sys.stderr)
        retryable = status in (429, 500, 502, 503, 504) or (
            status == 403 and remaining is not None and remaining <= 0
        )
        if retryable and retries < 3:
            delay = exponential_backoff_start_ms / 1000 * 2 ** retries
            retries += 1
            print(f"Retrying in {delay:g}s ({retries}/3)", file=sys.stderr)
            time.sleep(delay)
            continue
        if status == 401:
            raise CommandError("Canvas HTTP 401: check DJANVAS_TOKEN and DJANVAS_CANVAS_BASE_URL.")
        if status == 403 and skip_forbidden and not retryable:
            print(
                f"WARNING: Canvas HTTP 403 for {urlplusquery}; "
                "skipping this course resource (access denied). "
                f"Discarding {len(results)} records from earlier pages.",
                file=sys.stderr,
            )
            return []
        if status == 404:
            return []
        if not 200 <= status < 300:
            raise CommandError(
                f"Canvas HTTP {status} for {urlplusquery}. "
                "Check DJANVAS_CANVAS_BASE_URL matches your institution's Canvas site; "
                "if correct, try again later."
            )
        try:
            data = resp.json()
        except ValueError:
            raise CommandError(f"Canvas returned invalid JSON for {urlplusquery} (HTTP {status}).") from None
        if not isinstance(data, list):
            raise CommandError(f"Canvas returned an unexpected response for {urlplusquery}; expected a list.")
        results.extend(item for item in data if isinstance(item, dict))
        retries = 0
        if 'next' not in resp.links:
            break
        urlplusquery = resp.links['next']['url']
        time.sleep(normal_sleep_time_ms / 1000)
    print(f"there were total {len(results)} results before filtering", file=sys.stderr)
    return results



class api:
    """ general class to get data from Canvas """
    def __init__(self):
        self.base_url = os.environ.get("DJANVAS_CANVAS_BASE_URL", base_url).rstrip("/")
        self.token = os.environ.get(token_env_var,"")
        if not self.token:
            raise CommandError(f'no token in "{token_env_var}"')

    def get_all_courses(self):
        page = 1
        results = []
        nrequests = 0
        url = f"{self.base_url}{courses_api_path}"
        headers = {"Authorization": f"Bearer {self.token}"}
        courses = get_paginated_results(url, headers)

        # for res in courses:
        #     Print.dumps(res, sort_keys=True, indent=4), sys.stderr)
        #     interesting_fields = ['id', "name", "course_code",
        #                           "workflow_state", "start_at", "uuid", "enrollments"]
        #     #print(str({key:res.get(key,"") for key in interesting_fields}))

        return courses

    def get_course_sections(self, course_id):
        url = f"{self.base_url}{courses_api_path}/{course_id}/sections"
        headers = {"Authorization": f"Bearer {self.token}"}
        sections  = get_paginated_results(url, headers, skip_forbidden=True)
        return sections

    def get_course_enrollments(self, course_id):
        url = f"{self.base_url}{courses_api_path}/{course_id}/enrollments"
        headers = {"Authorization": f"Bearer {self.token}"}
        enrollments  = get_paginated_results(url, headers, skip_forbidden=True)
        return enrollments
