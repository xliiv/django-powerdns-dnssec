# -*- encoding: utf-8 -*-

from django.test import TestCase

from powerdns.models import PowerDNSRecord, Record
from powerdns.models.powerdns import _create_dnsaas_record
from powerdns.tests.utils import PowerDNSRecordFactory


class TestDNSaaSRecord(TestCase):

    def test_is_created_ok_from_powerdns_record(self):
        powerdns_record = PowerDNSRecordFactory()
        self.assertEqual(Record.objects.count(), 0)
        self.assertEqual(PowerDNSRecord.objects.count(), 1)

        record = _create_dnsaas_record(powerdns_record)

        self.assertEqual(Record.objects.count(), 1)
        self.assertEqual(PowerDNSRecord.objects.count(), 1)
        self.maxDiff = None
        self.assertEqual(record.record_ptr_id, powerdns_record.id)
        excluded = {'modified', 'purpose', 'record_ptr_id'}
        self.assertEqual(
            {k: v for k, v in record.__dict__.items() if k not in excluded},
            {k: v for k, v in powerdns_record.__dict__.items() if k not in excluded},  # noqa
        )
