"""Tests for record/domain ownership"""

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

from powerdns.models.powerdns import Domain, Record
from powerdns.models.requests import (
    RecordRequest,
    can_auto_accept_record_request,
)
from powerdns.tests.utils import (
    DomainFactory,
    RecordFactory,
    ServiceOwnerFactory,
    UserFactory,
    user_client,
)
from powerdns.utils import AutoPtrOptions


class TestOwnershipBase(TestCase):
    """Base test class creating some users."""

    def setUp(self):
        self.user1 = User.objects.create_superuser(
            'user1', 'user1@example.com', 'password'
        )
        self.user2 = User.objects.create_superuser(
            'user2', 'user2@example.com', 'password'
        )
        self.client = user_client(self.user1)
        mail.outbox = []

    def tearDown(self):
        for Model in [Domain, Record, User]:
            Model.objects.all().delete()

    def assertOwner(self, request, username, mailed):
        """Assert the owner in returned data is username and he
        was/was not mailed"""
        self.assertEqual(request.data['owner'], username)
        if len(mail.outbox) > 1:
            raise RuntimeError('Tests broken. Clean the outbox on teardown')
        if mailed and len(mail.outbox) == 0:
            raise AssertionError('Notification not sent, while it should be')
        if not mailed and len(mail.outbox) == 1:
            raise AssertionError("Notification sent, while it shouldn't be")


class TestDomainOwnership(TestOwnershipBase):
    """Tests for domain ownership"""

    def test_auto_user(self):
        """Domain owner is set to current user if no owner is specified"""
        request = self.client.post(
            '/api/domains/',
            data={'name': 'owned.example.com'},
        )
        self.assertOwner(request, 'user1', mailed=False)

    def test_explicit_user(self):
        """Domain owner is set to explicitly set value"""
        request = self.client.post(
            '/api/domains/',
            data={'name': 'owned.example.com', 'owner': 'user2'},
        )
        self.assertOwner(request, 'user2', mailed=True)


class TestRecordOwnership(TestOwnershipBase):
    """Tests for record ownership"""

    def setUp(self):
        super(TestRecordOwnership, self).setUp()
        self.domain = DomainFactory(name='owned.example.com')

    def test_auto_user(self):
        """Record owner is set to current user if no owner is specified"""
        request = self.client.post(
            '/api/records/',
            data={
                'domain': '/api/domains/{}/'.format(self.domain.pk),
                'type': 'CNAME',
                'name': 'www.owned.example.com',
                'content': 'blog.owned.example.com',
            },
        )
        self.assertOwner(request, 'user1', mailed=False)

    def test_explicit_user(self):
        """Record owner is set to explicitly set value"""
        request = self.client.post(
            '/api/records/',
            data={
                'domain': '/api/domains/{}/'.format(self.domain.pk),
                'type': 'CNAME',
                'name': 'www.owned.example.com',
                'content': 'blog.owned.example.com',
                'owner': 'user2',
            },
        )
        self.assertOwner(request, 'user2', mailed=True)


#TODO:: add test for missing service too

class TestCreateRecordAccessByServiceOwnership(TestCase):

    def setUp(self):
        self.clicker = UserFactory(username='clicker')
        self.some_dude = UserFactory(username='some_dude')
        self.example_domain = DomainFactory(
            owner=self.clicker,
            name='example.com',
            unrestricted=False,
            auto_ptr=AutoPtrOptions.NEVER,
        )

    def _test_create(self, domain_owner, domain_ownership, expected):
        self.example_domain.owner = domain_owner
        self.example_domain.service.owners.clear()
        self.service = ServiceOwnerFactory(
            service=self.example_domain.service, user=domain_ownership,
        )
        self.example_domain.save()
        self.service.save()

        record_request = RecordRequest(
            domain=self.example_domain,
            record=None,
        )

        result = can_auto_accept_record_request(
            record_request, self.clicker, 'create'
        )
        self.assertEqual(result, expected)

    def test_domain_ownership_allows_to_create_new_record_when_blank_auth(
        self
    ):
        self._test_create(
            domain_owner=None,
            domain_ownership=self.clicker,
            expected=True
        )

    def test_domain_ownership_allows_to_create_new_record_when_no_auth(
        self
    ):
        self._test_create(
            domain_owner=self.some_dude,
            domain_ownership=self.clicker,
            expected=True
        )

    def test_domain_ownership_rejects_to_create_new_record_when_no_both_perms(
        self
    ):
        self._test_create(
            domain_owner=self.some_dude,
            domain_ownership=self.some_dude,
            expected=False,
        )


class TestUpdateRecordAccessByServiceOwnership(TestCase):

    def setUp(self):
        self.clicker = UserFactory(username='clicker')
        self.some_dude = UserFactory(username='some_dude')
        self.example_domain = DomainFactory(
            owner=self.clicker,
            name='example.com',
            unrestricted=False,
            auto_ptr=AutoPtrOptions.NEVER,
        )
        self.example_record = RecordFactory(
            owner=None,
            type='A',
            name='example.com',
            content='192.168.1.0',
        )

    def _test_update(self, record_owner, record_ownership, expected):
        self.example_record.owner = record_owner
        self.example_record.service.owners.clear()
        self.service = ServiceOwnerFactory(
            service=self.example_record.service, user=record_ownership,
        )
        self.example_record.save()
        self.service.save()

        record_request = RecordRequest(
            domain=self.example_domain,
            record=self.example_record,
        )

        result = can_auto_accept_record_request(
            record_request, self.clicker, 'update'
        )
        self.assertEqual(result, expected)

    def test_ownership_allows_update_when_blank_auth(self):
        self._test_update(
            record_owner=None,
            record_ownership=self.clicker,
            expected=True
        )

    def test_ownership_allows_update_when_no_auth(self):
        self._test_update(
            record_owner=self.some_dude,
            record_ownership=self.clicker,
            expected=True
        )

    def test_ownership_rejects_update_when_no_both_perms(self):
        self._test_update(
            record_owner=self.some_dude,
            record_ownership=self.some_dude,
            expected=False
        )
