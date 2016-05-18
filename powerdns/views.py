"""Views and viewsets for DNSaaS API"""

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView

from powerdns.models import (
    CryptoKey,
    DeleteRequest,
    Domain,
    DomainMetadata,
    DomainTemplate,
    DomainRequest,
    Record,
    RecordTemplate,
    RecordRequest,
    SuperMaster,
)
from rest_framework import status
from rest_framework.filters import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.response import Response

from powerdns.serializers import (
    CryptoKeySerializer,
    DomainMetadataSerializer,
    DomainSerializer,
    DomainTemplateSerializer,
    RecordRequestSerializer,
    RecordSerializer,
    RecordTemplateSerializer,
    SuperMasterSerializer,
)
from powerdns.utils import VERSION, to_reverse


class DomainPermission(DjangoObjectPermissions):

    def has_permission(self, request, view):
        if request.method == 'POST' and not request.user.is_superuser:
            return False
        return super().has_permission(request, view)


class FiltersMixin(object):

    filter_backends = (DjangoFilterBackend,)


class OwnerViewSet(FiltersMixin, ModelViewSet):
    """Base view for objects with owner"""

    def perform_create(self, serializer, *args, **kwargs):
        if serializer.validated_data.get('owner') is None:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()
            # object_ = serializer.save()
            # usless? this is handled by jira in design
            # object_.email_owner(self.request.user)


class DomainViewSet(OwnerViewSet):

    queryset = Domain.objects.all().select_related('owner')
    serializer_class = DomainSerializer
    filter_fields = ('name', 'type')
    permission_classes = (DomainPermission,)


class RecordRequestsViewSet(ModelViewSet):
    queryset = RecordRequest.objects.all() # .select_related('owner', 'domain')
    serializer_class = RecordRequestSerializer
    # filter_fields = ('name', 'content', 'domain')
    # search_fields = filter_fields


class RecordViewSet(OwnerViewSet):

    queryset = Record.objects.all().select_related('owner', 'domain')
    serializer_class = RecordSerializer
    filter_fields = ('name', 'content', 'domain')
    search_fields = filter_fields

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            serializer_class = RecordRequestSerializer
        else:
            serializer_class = RecordSerializer
        print(serializer_class)
        return serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # TODO:: moved to model + added check in save() that this was called?
        auto_accept = (
            self.request.user.is_superuser or
            serializer.instance.domain.unrestricted == True or
            self.request.user == serializer.instance.domain.owner or
            request.user.id in serializer.instance.domain.authorisations.values_list('authorised', flat=True) # noqa
        )
        if auto_accept:
            record = serializer.instance.accept()
            serializer.instance.record = record
            serializer.instance.save()
            serializer.data['record'] = record
            code = status.HTTP_201_CREATED
            headers = {'Location': serializer.data['record']}
        else:
            code = status.HTTP_202_ACCEPTED
            headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=code, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = get_object_or_404(
            RecordRequest, record__pk=self.get_object().pk)
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        auto_accept = (
            self.request.user.is_superuser or
            # serializer.instance.domain.unrestricted == True or
            # self.request.user == serializer.instance.domain.owner or
            request.user.id == instance.record.owner.id or
            request.user.id in instance.record.authorisations.values_list(
                'authorised', flat=True)
        )
        if auto_accept:
            record = serializer.instance.accept()
            serializer.instance.record = record
            serializer.instance.save()
            serializer.data['record'] = record
            code = status.HTTP_200_OK
            headers = {'Location': serializer.data['record']}
        else:
            code = status.HTTP_202_ACCEPTED
            headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=code, headers=headers)

    def get_queryset(self):
        queryset = super().get_queryset()
        ips = self.request.query_params.getlist('ip')
        if ips:
            a_records = Record.objects.filter(content__in=ips, type='A')
            ptrs = [
                "{1}.{0}".format(*to_reverse(r.content)) for r in a_records
            ]
            queryset = queryset.filter(
                (Q(content__in=[r.content for r in a_records]) & Q(type='A')) |
                (Q(content__in=[r.name for r in a_records]) & Q(type='CNAME')) | # noqa
                (Q(name__in=[r.name for r in a_records]) & Q(type='TXT')) |
                (Q(name__in=ptrs) & Q(type='PTR'))
            )
        types = self.request.query_params.getlist('type')
        if types:
            queryset = queryset.filter(type__in=types)
        return queryset


class CryptoKeyViewSet(FiltersMixin, ModelViewSet):

    queryset = CryptoKey.objects.all()
    serializer_class = CryptoKeySerializer
    filter_fields = ('domain',)


class DomainMetadataViewSet(FiltersMixin, ModelViewSet):

    queryset = DomainMetadata.objects.all()
    serializer_class = DomainMetadataSerializer
    filter_fields = ('domain',)


class SuperMasterViewSet(FiltersMixin, ModelViewSet):

    queryset = SuperMaster.objects.all()
    serializer_class = SuperMasterSerializer
    filter_fields = ('ip', 'nameserver')


class DomainTemplateViewSet(FiltersMixin, ModelViewSet):

    queryset = DomainTemplate.objects.all()
    serializer_class = DomainTemplateSerializer
    filter_fields = ('name',)


class RecordTemplateViewSet(FiltersMixin, ModelViewSet):

    queryset = RecordTemplate.objects.all()
    serializer_class = RecordTemplateSerializer
    filter_fields = ('domain_template', 'name', 'content')


class HomeView(TemplateView):

    """
    Homepage. This page should point user to API or admin site. This package
    will provide some minimal homepage template. The administrators of
    DNSaaS solutions are encouraged however to create their own ones.
    """

    template_name = "powerdns/home.html"

    def get_context_data(self, **kwargs):

        return {
            'version': VERSION,
        }


def accept_request_factory(request_model, model_name=None):
    def result(request, pk):
        request = request_model.objects.get(pk=pk)
        domain = request.accept()
        if model_name:
            return redirect(
                reverse(
                    'admin:powerdns_{}_change'.format(model_name),
                    args=(domain.pk,)
                )
            )
        else:
            return redirect(reverse('admin:index'))
    return result

accept_domain_request = accept_request_factory(DomainRequest, 'domain')
accept_record_request = accept_request_factory(RecordRequest, 'record')
accept_delete_request = accept_request_factory(DeleteRequest)
