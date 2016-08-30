from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.widgets import AdminRadioSelect
from django.db import models
from django.forms import NullBooleanSelect
from powerdns.models.requests import (
    DeleteRequest,
    DomainRequest,
    RecordRequest,
)
from django.utils.translation import ugettext_lazy as _
from django_extensions.admin import ForeignKeyAutocompleteAdmin

from powerdns.models.powerdns import (
    CryptoKey,
    Domain,
    DomainMetadata,
    Record,
    SuperMaster,
)
from powerdns.models.templates import (
    DomainTemplate,
    RecordTemplate,
)
from powerdns.models.tsigkeys import TsigKey


RECORD_LIST_FIELDS = (
    'name',
    'type',
    'content',
    'ttl',
    'prio',
)


class ReverseDomainListFilter(SimpleListFilter):
    title = _('domain class')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'domain_class'

    def lookups(self, request, model_admin):
        return (
            ('fwd', _('domain:forward')),
            ('rev', _('domain:reverse')),
        )

    def queryset(self, request, queryset):
        q = (
            models.Q(name__endswith='.in-addr.arpa') |
            models.Q(name__endswith='.ip6.arpa')
        )
        if self.value() == 'fwd':
            return queryset.exclude(q)
        if self.value() == 'rev':
            return queryset.filter(q)


class DomainMetadataInline(admin.TabularInline):
    model = DomainMetadata
    extra = 0


class DomainAdmin(ForeignKeyAutocompleteAdmin, admin.ModelAdmin):
    inlines = [DomainMetadataInline]
    list_display = (
        'name',
        'type',
        'last_check',
        'account',
        'add_record_link',
        'request_change',
        'request_deletion'
    )
    list_display_links = None
    list_filter = (
        ReverseDomainListFilter, 'type', 'last_check', 'account', 'created',
        'modified'
    )
    list_per_page = 250
    save_on_top = True
    search_fields = ('name',)
    radio_fields = {'type': admin.HORIZONTAL}
    readonly_fields = ('notified_serial', 'created', 'modified')


class NullBooleanRadioSelect(NullBooleanSelect, AdminRadioSelect):
    pass


class RecordAdmin(ForeignKeyAutocompleteAdmin, admin.ModelAdmin):
    list_display = (
        'name',
        'type',
        'content',
        'domain',
        'owner',
        'ttl',
        'prio',
        'change_date',
    )
    list_filter = ('type', 'ttl', 'auth', 'domain', 'created', 'modified')
    list_per_page = 250
    save_on_top = True
    search_fields = ('name', 'content',)
    readonly_fields = ('change_date', 'ordername', 'created', 'modified')
    related_search_fields = {
        'domain': ('name',),
    }
    fieldsets = (
        (None, {
            'fields': (
                'owner',
                'domain',
                ('type', 'name', 'content',),
                'auth',
            ),
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('prio', 'ttl', 'ordername', 'change_date',)
        }),
        (None, {'fields': ('created', 'modified')})
    )
    formfield_overrides = {
        models.NullBooleanField: {
            'widget': NullBooleanRadioSelect(
                attrs={'class': 'radiolist inline'}
            ),
        },
    }

    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)
        form.user = request.user
        return form


class RecordTemplateAdmin(ForeignKeyAutocompleteAdmin):
    list_display = RECORD_LIST_FIELDS


class SuperMasterAdmin(admin.ModelAdmin):
    list_display = ('ip', 'nameserver', 'account',)
    list_filter = ('ip', 'account', 'created', 'modified')
    search_fields = ('ip', 'nameserver',)
    readonly_fields = ('created', 'modified')


class DomainMetadataAdmin(ForeignKeyAutocompleteAdmin):
    list_display = ('domain', 'kind', 'content',)
    list_filter = ('kind', 'domain', 'created', 'modified')
    list_per_page = 250
    list_filter = ('created', 'modified')
    readonly_fields = ('created', 'modified')
    related_search_fields = {
        'domain': ('name',),
    }
    save_on_top = True
    search_fields = ('content',)


class CryptoKeyAdmin(ForeignKeyAutocompleteAdmin):
    list_display = ('domain', 'flags', 'active', 'content',)
    list_filter = ('active', 'domain', 'created', 'modified')
    list_per_page = 250
    readonly_fields = ('created', 'modified')
    related_search_fields = {
        'domain': ('name',),
    }
    save_on_top = True
    search_fields = ('content',)
    formfield_overrides = {
        models.NullBooleanField: {
            'widget': NullBooleanRadioSelect(
                attrs={'class': 'radiolist inline'}
            ),
        },
    }


class DeleteRequestAdmin(admin.ModelAdmin):
    fields = ['owner', 'target_id', 'content_type']


class RecordTemplateInline(admin.StackedInline):
    model = RecordTemplate
    extra = 1


class DomainTemplateAdmin(ForeignKeyAutocompleteAdmin):
    inlines = [RecordTemplateInline]
    list_display = ['name', 'add_domain_link', 'is_public_domain']


class DomainRequestAdmin(admin.ModelAdmin):
    list_display = ['domain']
    readonly_fields = ['key']


class RecordRequestAdmin(admin.ModelAdmin):
    list_display = ['target_' + field for field in RECORD_LIST_FIELDS]


#TODO:: permissions
    #TODO:: restrict all only for superuser
    #TODO:: new admin requests readonly
#TODO:: main look and feel (so fk from autocomplete, or something to prevent long requests)
admin.site.register(Domain, DomainAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(RecordTemplate, RecordTemplateAdmin)
admin.site.register(SuperMaster, SuperMasterAdmin)
admin.site.register(DomainMetadata, DomainMetadataAdmin)
admin.site.register(CryptoKey, CryptoKeyAdmin)
admin.site.register(TsigKey)
admin.site.register(DomainTemplate, DomainTemplateAdmin)
admin.site.register(DomainRequest, DomainRequestAdmin)
admin.site.register(RecordRequest, RecordRequestAdmin)
admin.site.register(DeleteRequest, DeleteRequestAdmin)
