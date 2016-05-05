# -*- encoding: utf-8 -*-

from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.http import QueryDict
from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory

from powerdns.tests.utils import DomainTemplateFactory, RecordFactory
from powerdns.utils import AutoPtrOptions
from powerdns.views import RecordViewSet


class TestApi(TestCase):
    def setUp(self):
        super().setUp()
        self.request_factory = APIRequestFactory()
        get_user_model().objects.create_superuser(
            'test', 'test@test.test', 'test'
        )
        self.client = APIClient()
        self.client.login(username='test', password='test')

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


from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from powerdns.models.powerdns import Record
from powerdns.tests.utils import DomainFactory, user_client
from powerdns.models.requests import RecordRequest
import json
class TestAddingRecords(BaseApiTestCase):
    def setUp(self):
        super().setUp()
        self.regular_user1 = get_user_model().objects.create_superuser(
            'regular_user1', 'regular_user1@test.test', 'regular_user1'
        )
        self.regular_user2 = get_user_model().objects.create_superuser(
            'regular_user2', 'regular_user2@test.test', 'regular_user2'
        )

    def test_when_user_is_superuser(self):
        self.client = APIClient()
        self.client.login(username='super_user', password='super_user')
        url = '/api/records/' # TODO: reverse('record-create')
        domain = DomainFactory(name='example.com', owner=self.super_user)
        data = {
            'type': 'cname'.upper(),
            'domain': '/api/domains/' + str(domain.id) + '/',
            'name': 'example.com',
            'content': '192.168.0.1',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_regular_user_owns_domain(self):
        self.client = APIClient()
        self.client.login(username='regular_user1', password='regular_user1')
        url = '/api/records/' # TODO: reverse('record-create')
        domain = DomainFactory(name='example.com', owner=self.regular_user1)
        data = {
            'type': 'cname'.upper(),
            'domain': '/api/domains/' + str(domain.id) + '/',
            'name': 'example.com',
            'content': '192.168.0.1',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_regular_user_not_own_domain(self):
        self.client = APIClient()
        self.client.login(username='regular_user2', password='regular_user2')
        url = '/api/records/' # TODO: reverse('record-create')
        domain = DomainFactory(name='example.com', owner=self.regular_user2)
        data = {
            'type': 'cname'.upper(),
            'domain': '/api/domains/' + str(domain.id) + '/',
            'name': 'example.com',
            'content': '192.168.0.1',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = json.loads(response.content.decode('utf8'))
        self.assertTrue(RecordRequest.objects.filter(record_id=data['id']))
