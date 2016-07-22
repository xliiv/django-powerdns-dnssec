# -*- encoding: utf-8 -*-

from django_migration_testcase import MigrationTest


class TestMigration(MigrationTest):

    app_name = 'powerdns'
    before = '0025_auto_20160721_0517'
    after = '0026_auto_20160721_0517'

    def test_migration(self):
        Domain = self.get_model_before('powerdns.Domain')
        PowerDNSRecord = self.get_model_before('powerdns.Record')
        DNSaaSRecord = self.get_model_before('powerdns.DNSaaSRecord')
        domain = Domain()
        domain.save()
        record = PowerDNSRecord(
            domain=domain,
            name='example.com',
            type='A',
            content='192.168.0.1',
        )
        record.save()

        self.assertEqual(PowerDNSRecord.objects.count(), 1)
        self.assertEqual(DNSaaSRecord.objects.count(), 0)

        self.run_migration()

        PowerDNSRecord = self.get_model_after('powerdns.Record')
        DNSaaSRecord = self.get_model_after('powerdns.DNSaaSRecord')
        self.assertEqual(PowerDNSRecord.objects.count(), 1)
        self.assertEqual(DNSaaSRecord.objects.count(), 1)
        powerdns_record = PowerDNSRecord.objects.get()
        dnsaas_record = DNSaaSRecord.objects.get()
        self.assertEqual(dnsaas_record.record_ptr_id, powerdns_record.id)
        for key in [
            'auth', 'auto_ptr', 'change_date', 'content', 'created',
            'depends_on_id', 'disabled', 'domain_id', 'name', 'number',
            'ordername', 'owner_id', 'prio', 'remarks', 'template_id', 'ttl',
            'type',
        ]:
            self.assertEqual(
                getattr(dnsaas_record, key), getattr(powerdns_record, key)
            )
