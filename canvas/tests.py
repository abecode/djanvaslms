import json
from django.test import TestCase

# Create your tests here.
class RestJsonTest(TestCase):
    def setup(self):
        self.log =  logging.getLogger("RestJsonTest")

    def test_read_json(self):
        records_before = {}
        records_after = {}
        with open("canvas/test_data/courses_before.json") as f:
            jsondata = ''.join(line for line in f if not line.startswith('//'))
            records_before = json.loads(jsondata)
        with open("canvas/test_data/courses_after.json") as f:
            jsondata = ''.join(line for line in f if not line.startswith('//'))
            records_after = json.loads(jsondata)
        
        self.assertEqual(len(records_before), 30)
        self.assertEqual(len(records_after), 33)
