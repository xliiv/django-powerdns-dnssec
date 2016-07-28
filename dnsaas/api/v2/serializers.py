"""Serializer classes for DNSaaS API"""
import ipaddress

from django.contrib.auth.models import User
from powerdns.models import (
    CryptoKey,
    Domain,
    DomainMetadata,
    DomainTemplate,
    Record,
    RecordRequest,
    RecordTemplate,
    SuperMaster,
)
from rest_framework import serializers
from rest_framework.serializers import (
    PrimaryKeyRelatedField,
    ReadOnlyField,
    ModelSerializer,
    SlugRelatedField,
)
from powerdns.models.requests import RequestStates
from powerdns.models.tsigkeys import TsigKey


class OwnerSerializer(ModelSerializer):

    owner = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
    )


class DomainSerializer(OwnerSerializer):

    id = ReadOnlyField()

    class Meta:
        model = Domain
        read_only_fields = ('notified_serial',)


class RecordRequestSerializer(OwnerSerializer):
    last_change = serializers.SerializerMethodField()
    target_owner = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = RecordRequest

    def get_last_change(self, obj):
        if obj.state == RequestStates.OPEN:
            return obj._get_json_history(obj.get_object())
        else:
            return obj.last_change_json


class RecordSerializer(OwnerSerializer):

    class Meta:
        model = Record
        read_only_fields = ('change_date', 'ordername',)

    domain = PrimaryKeyRelatedField(
        queryset=Domain.objects.all(),
    )
    modified = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', read_only=True
    )
    change_request = serializers.SerializerMethodField(
        'get_change_record_request'
    )
    delete_request = serializers.SerializerMethodField(
        'get_delete_record_request'
    )

    def get_change_record_request(self, record):
        record_request = record.requests.all()
        if record_request:
            return record_request[0].key
        return None

    def get_delete_record_request(self, record):
        delete_request = record.delete_request.all()
        if delete_request:
            return delete_request[0].key
        return None

    def validate(self, attrs):
        domain, content, record_type = (
            attrs.get('domain'), attrs.get('content'), attrs.get('type')
        )

        if (
            record_type == 'A'
        ):
            try:
                ipaddress.ip_address(content)
            except ValueError:
                raise serializers.ValidationError(
                    {'content':
                     ['Content should be IP valid address when type="A".']}
                )

        if (
            domain and domain.template and
            domain.template.is_public_domain and
            content and record_type == 'A'
        ):
            address = ipaddress.ip_address(content)
            if address.is_private:
                raise serializers.ValidationError(
                    {'content': ['IP address cannot be private.']}
                )

        return attrs


class CryptoKeySerializer(ModelSerializer):

    class Meta:
        model = CryptoKey


class DomainMetadataSerializer(ModelSerializer):

    class Meta:
        model = DomainMetadata


class SuperMasterSerializer(ModelSerializer):

    class Meta:
        model = SuperMaster


class DomainTemplateSerializer(ModelSerializer):

    class Meta:
        model = DomainTemplate


class RecordTemplateSerializer(ModelSerializer):

    class Meta:
        model = RecordTemplate


class TsigKeysTemplateSerializer(ModelSerializer):

    class Meta:
        model = TsigKey
