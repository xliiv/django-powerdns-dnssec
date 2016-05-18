# -*- encoding: utf-8 -*-

from urllib import parse
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.core.urlresolvers import resolve, reverse
from django.http import QueryDict
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from powerdns.models.powerdns import Record
from powerdns.models.requests import RecordRequest
from powerdns.tests.utils import (
    DomainFactory,
    DomainTemplateFactory,
    RecordFactory,
)
from powerdns.utils import AutoPtrOptions
from powerdns.views import RecordViewSet


class TestApi(TestCase):
    def setUp(self):
        super().setUp()
        self.request_factory = APIRequestFactory()
        get_user_model().objects.create_superuser(
            'test', 'test@test.test', 'test'
        )
        get_user_model().objects.create_user(
            'user', 'user@test.test', 'user'
        )

        self.client = APIClient()
        self.client.login(username='user', password='user')

        DomainTemplateFactory(
            name='reverse', type=None, unrestricted=False, record_auto_ptr=2)
        for i in range(3):
            RecordFactory(
                type='A', name='example{}.com'.format(i),
                content='192.168.0.{}'.format(i),
                auto_ptr=AutoPtrOptions.ALWAYS)
            RecordFactory(
                type='CNAME', name='www.example{}.com'.format(i),
                content='example{}.com'.format(i),
                auto_ptr=AutoPtrOptions.NEVER)
            RecordFactory(
                type='TXT', name='example{}.com'.format(i),
                content='Some information{}'.format(i),
                auto_ptr=AutoPtrOptions.NEVER)

    def test_record_filters_by_ip_and_type(self):
        request = self.request_factory.get('/')
        request.query_params = QueryDict(
            urlencode([
                ('ip', '192.168.0.1'),
                ('ip', '192.168.0.2'),
                ('type', 'A'),
                ('type', 'CNAME'),
                ('type', 'TXT'),
                ('type', 'PTR'),
            ])
        )

        mvs = RecordViewSet()
        mvs.request = request
        self.assertEqual(len(mvs.get_queryset()), 8)


class BaseApiTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.request_factory = APIRequestFactory()
        self.super_user = get_user_model().objects.create_superuser(
            'super_user', 'test@test.test', 'super_user'
        )
        self.client = APIClient()


class TestAddingRecords(BaseApiTestCase):
    def setUp(self):
        super().setUp()
        self.regular_user1 = get_user_model().objects.create_user(
            'regular_user1', 'regular_user1@test.test', 'regular_user1'
        )
        self.regular_user2 = get_user_model().objects.create_user(
            'regular_user2', 'regular_user2@test.test', 'regular_user2'
        )

    def test_when_user_is_superuser(self):
        self.client.login(username='super_user', password='super_user')
        domain = DomainFactory(name='example.com', owner=self.super_user)
        data = {
            'type': 'cname'.upper(),
            'domain': '/api/domains/' + str(domain.id) + '/',
            'name': 'example.com',
            'content': '192.168.0.1',
        }
        response = self.client.post(
            reverse('record-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        record_pk = resolve(parse.urlparse(
            response.data['record']).path).kwargs['pk']
        self.assertTrue(Record.objects.get(pk=record_pk))

    def test_regular_user_owns_domain(self):
        self.client.login(username='regular_user1', password='regular_user1')
        domain = DomainFactory(name='example.com', owner=self.regular_user1)
        data = {
            'type': 'cname'.upper(),
            'domain': '/api/domains/' + str(domain.id) + '/',
            'name': 'example.com',
            'content': '192.168.0.1',
        }
        response = self.client.post(
            reverse('record-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        record_pk = resolve(parse.urlparse(
            response.data['record']).path).kwargs['pk']
        self.assertTrue(Record.objects.get(pk=record_pk))

    def test_regular_user_not_own_domain(self):
        self.client.login(username='regular_user1', password='regular_user1')
        domain = DomainFactory(name='example.com', owner=self.regular_user2)
        data = {
            'type': 'cname'.upper(),
            'domain': '/api/domains/' + str(domain.id) + '/',
            'name': 'example.com',
            'content': '192.168.0.1',
        }
        response = self.client.post(
            reverse('record-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        request_record = RecordRequest.objects.get(
            pk=resolve(parse.urlparse(response.data['url']).path).kwargs['pk']
        )
        self.assertFalse(request_record.record)
