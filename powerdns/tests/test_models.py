# -*- encoding: utf-8 -*-
from django.test import TestCase

from powerdns.models import RequestStates
from powerdns.tests.utils import (
    RecordFactory,
    RecordRequestFactory,
)


class TestModels(TestCase):
    def test_any_opened_request_is_false_when_no_requests(self):
        record = RecordFactory()
        self.assertEqual(record.any_request_opened, False)

    def test_any_request_opened_is_true_when_opened(self):
        record = RecordFactory()
        RecordRequestFactory(record=record, state=RequestStates.OPEN)
        self.assertEqual(record.any_request_opened, True)

    def test_any_request_opened_is_false_when_closed_mixed(self):
        record = RecordFactory()
        RecordRequestFactory(record=record, state=RequestStates.REJECTED)
        RecordRequestFactory(record=record, state=RequestStates.ACCEPTED)
        self.assertEqual(record.any_request_opened, False)

    def test_any_request_opened_is_true_when_all_mixed(self):
        record = RecordFactory()
        RecordRequestFactory(record=record, state=RequestStates.OPEN)
        RecordRequestFactory(record=record, state=RequestStates.REJECTED)
        RecordRequestFactory(record=record, state=RequestStates.ACCEPTED)
        self.assertEqual(record.any_request_opened, True)
