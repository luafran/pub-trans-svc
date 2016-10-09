import json
from tornado import ioloop
from tornado import testing
from tornado.httpclient import HTTPRequest

from pubtrans import application
from pubtrans.domain import api

app = application.make_app()


class TestSchedule(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestSchedule, self).setUp()

    def get_app(self):
        return app

    def get_new_ioloop(self):
        return ioloop.IOLoop.instance()

    def test_get_schedule(self):
        request = HTTPRequest(
            self.get_url('/v1/sf-muni/routes/E/schedule'),
            method='GET'
        )

        self.http_client.fetch(request, self.stop)
        response = self.wait()

        self.assertEqual(response.code, 200)
        schedule = json.loads(response.body)

        self.assertIsNotNone(schedule)
        self.assertIsNotNone(schedule.get(api.TAG_SCHEDULE_CLASS))
        schedule_items = schedule.get(api.TAG_SCHEDULE_ITEMS)
        self.assertIsNotNone(schedule_items)
        self.assertGreater(len(schedule_items), 1)
        self.assertIsNotNone(schedule_items[0].get(api.TAG_SERVICE_CLASS))
        self.assertIsNotNone(schedule_items[0].get(api.TAG_DIRECTION))
