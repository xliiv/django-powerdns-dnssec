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

        for key in [
            'auth', 'auto_ptr', 'change_date', 'content', 'created',
            'depends_on_id', 'disabled', 'domain_id', 'name', 'number',
            'ordername', 'owner_id', 'prio', 'remarks', 'template_id', 'ttl',
            'type',
        ]:
            self.assertEqual(
                getattr(record, key), getattr(powerdns_record, key)
            )
