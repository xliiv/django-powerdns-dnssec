# -*- encoding: utf-8 -*-


from powerdns.models import Record
from powerdns.tests.utils import RecordTestCase, RecordFactory
from powerdns.utils import AutoPtrOptions


class TestSOASerialUpdate(RecordTestCase):

    def setUp(self):
        super(TestSOASerialUpdate, self).setUp()
        self.soa_record = RecordFactory(
            domain=self.domain,
            type='SOA',
            name='example.com',
            content=(
                'na1.example.com. hostmaster.example.com. '
                '0 43200 600 1209600 600'
            ),
        )
        # Less than 1 second will elapse until the test runs, so we update
        # this manually while circumventing save()
        Record.objects.filter(pk=self.soa_record.pk).update(
            change_date=1432720132
        )
        self.a_record = RecordFactory(
            domain=self.domain,
            type='A',
            name='www.example.com',
            content='192.168.1.1',
            auto_ptr=AutoPtrOptions.NEVER,
        )
        self.cname_record = RecordFactory(
            domain=self.domain,
            type='CNAME',
            name='blog.example.com',
            content='www.example.com',
            auto_ptr=AutoPtrOptions.NEVER,
        )

    def test_soa_update(self):
        """Test if SOA change_date is updated when a record is removed"""
        old_serial = Record.objects.get(pk=self.soa_record.pk).change_date
        self.a_record.delete()
        new_serial = Record.objects.get(pk=self.soa_record.pk).change_date
        self.assertGreater(new_serial, old_serial)


from django.test import TestCase
class TestAutoTXTRecords(TestCase):
    def test_record_is_created(self):
        from powerdns.models.powerdns import _update_auto_txt
        domain = DomainFactory(name='example.com')
        data = [{
            'name': '.'.join(['www', domain.name]),
            'type': 'TXT',
            'content': 'content',
            'subtype': 'SOMETYPE',
        }]
        # check no
        self.assertEqual(Record.objects.all(), 0))
        _update_auto_txt(data)
        # check yes
        record = Record.objects.get()
        for field_name in ['name', 'type', 'content', 'subtype']:
            self.assertEqual(getattr(record, field_name), data[field_name])
