from django.contrib import admin
from .models import PseudocodeObject, PseudocodeComponentRelation, LUTInterrogation
from django.utils.html import format_html
from django.db.models import Q
from django.contrib.admin.models import LogEntry

LogEntry.objects.all().delete()


admin.site.site_header = 'DMS Structured Attribute Repository'

class PseudocodeObjectInputFilter(admin.SimpleListFilter):
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = ((k, v) for k, v in changelist.get_filters_params().items() if k != self.parameter_name)
        yield all_choice
    

    def pseudocode_queryset(self, request, queryset):
        term = self.value()
        filter_type = self.__class__.__name__

        if term is None:
            return

        matches = Q()        
        for part in term.split():
            if filter_type == 'NameFilterExact':
                matches &= ( Q(name__iexact=part) | Q(name__iexact=part) )
            elif filter_type == 'NameFilterLike':
                matches &= ( Q(name__icontains=part) | Q(name__icontains=part) )
            elif filter_type == 'DescriptionFilter':
                matches &= ( Q(description__icontains=part) | Q(description__icontains=part) ) 
            elif filter_type == 'ObjectTypeFilter':
                matches &= ( Q(object_type__icontains=part) | Q(object_type__icontains=part) )
            elif filter_type == 'SubcomponentFilter':
                matches &= ( Q(sub_components__icontains=part) | Q(sub_components__icontains=part) )
        return queryset.filter(matches)



class NameFilterExact(PseudocodeObjectInputFilter):
    parameter_name = 'name_exact'
    title = 'Name (Exact)'
    queryset = PseudocodeObjectInputFilter.pseudocode_queryset

class NameFilterLike(PseudocodeObjectInputFilter):
    parameter_name = 'name_like'
    title = 'Name (Like)'
    queryset = PseudocodeObjectInputFilter.pseudocode_queryset


class DescriptionFilter(PseudocodeObjectInputFilter):
    parameter_name = 'description'
    title = 'Description (Like)'
    queryset = PseudocodeObjectInputFilter.pseudocode_queryset


class SubcomponentFilter(PseudocodeObjectInputFilter):
    parameter_name = 'sub_components'
    title = 'Sub-Components (Like)'
    queryset = PseudocodeObjectInputFilter.pseudocode_queryset



class InterrogationInline(admin.TabularInline):
    model = LUTInterrogation
    fields = ('interrogation_index', 'interrogation_field', 'interrogation_operator', 'interrogation_target', 'interrogation_return', 'interrogation_reference')
    readonly_fields = fields
    extra = 0
    ordering = ('index',)
    def interrogation__return(self, obj):
        return format_html("<div>{ret}</div>", ret=obj.interrogation_return)
    def interrogation__target(self, obj):
        return format_html("<div>{tar}</div>", tar=obj.interrogation_target)
    def interrogation__operator(self, obj):
        return format_html("<div>{op}</div>", op=obj.interrogation_operator)
    def interrogation_field(self, obj):
        field_name = obj.field_to_interrogate
        if '.' not in field_name:
            field_name = field_name[1:-1]
        field_id = PseudocodeObject.objects.get(name=field_name).id
        return format_html("<a href='{url}'>{name}</a>", url=f'/admin/ORM/pseudocodeobject/{field_id}/change/', name=field_name)
    def interrogation_index(self, obj):
        return format_html("<div>{i}</div>", i=obj.index + 1)
    def has_add_permission(self, request, obj=None):
        return False
    def interrogation_reference(self, obj):
        return format_html("<a href='{url}'>{name}</a>", url=f'/admin/ORM/lutinterrogation/{obj.id}/change/', name=f'{obj.master.name} Interrogation {obj.index+1}')

class SubcomponentInline(admin.StackedInline):
    model = PseudocodeObject.subject_components.through
    fk_name = 'master'
    fields = ('subject_name', 'description', 'object_type')
    readonly_fields = fields
    extra = 0


    def subject_name(self, obj):
        return format_html("<a href='{url}'>{name}</a>", url=f'/admin/ORM/pseudocodeobject/{obj.subject.id}/change/', name=obj.subject.name)
    def description(self, obj):
        return obj.subject.description
    def object_type(self, obj):
        return obj.subject.object_type

    def has_add_permission(self, request, obj=None):
        return False

class PseudocodeObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'object_type', 'description',  'explode_up')
    list_filter = (NameFilterLike, NameFilterExact, SubcomponentFilter, DescriptionFilter, 'object_type')
    exclude = ('sub_components', 'first_interrogation')

    def explode_up(self, obj):
        return format_html("<a href='{url}/{obj_id}'>Explode Up</a>", url='/explode/up', obj_id = obj.id)
    def get_inline_instances(self, request, obj=None):
        inline_instances = []

        if obj.object_type == 'look-up table':
            inlines = (InterrogationInline, SubcomponentInline)
        elif obj.object_type != 'XML Tag':
            inlines = (SubcomponentInline,)
        else:
            inlines = ()

        for inline_class in inlines:
            inline = inline_class(self.model, self.admin_site)
            if request:
                if not (inline.has_add_permission(request) or
                        inline.has_change_permission(request) or
                        inline.has_delete_permission(request)):
                    continue
                if not inline.has_add_permission(request):
                    inline.max_num = 0
            inline_instances.append(inline)
        return inline_instances


class InterrogationInputFilter(PseudocodeObjectInputFilter):
    def pseudocode_queryset(self, request, queryset):
        term = self.value()
        filter_type = self.__class__.__name__

        if term is None:
            return
        
        matches = Q()        
        for part in term.split():
            if filter_type == 'InterrogationMasterNameFilterExact':
                matches &= ( Q(master__name__iexact=part) | Q(master__name__iexact=part) )
            elif filter_type == 'InterrogationMasterNameFilterLike':    
                matches &= ( Q(master__name__icontains=part) | Q(master__name__icontains=part) )
            elif filter_type == 'InterrogationFieldFilter':
                matches &= ( Q(field_to_interrogate__icontains=part) | Q(field_to_interrogate__icontains=part) ) 
            elif filter_type == 'InterrogationOperatorFilter':
                matches &= ( Q(interrogation_operator__icontains=part) | Q(interrogation_operator__icontains=part) )
            elif filter_type == 'InterrogationTargetFilter':
                matches &= ( Q(interrogation_target__icontains=part) | Q(interrogation_target__icontains=part) )
            elif filter_type == 'InterrogationReturnFilter':
                matches &= ( Q(interrogation_return__icontains=part) | Q(interrogation_return__icontains=part) )
        return queryset.filter(matches)


class InterrogationMasterNameFilterExact(InterrogationInputFilter):
    parameter_name = 'master__name_exact'
    title = 'Look-Up Table Name (Exact)'
    queryset = InterrogationInputFilter.pseudocode_queryset
class InterrogationMasterNameFilterLike(InterrogationInputFilter):
    parameter_name = 'master__name_like'
    title = 'Look-Up Table Name (Like)'
    queryset = InterrogationInputFilter.pseudocode_queryset
class InterrogationFieldFilter(InterrogationInputFilter):
    parameter_name = 'field_to_interrogate'
    title = 'Interrogation Field (Like)'
    queryset = InterrogationInputFilter.pseudocode_queryset
class InterrogationOperatorFilter(InterrogationInputFilter):
    parameter_name = 'interrogation_operator'
    title = 'Interrogation Operator (Like)'
    queryset = InterrogationInputFilter.pseudocode_queryset
class InterrogationTargetFilter(InterrogationInputFilter):
    parameter_name = 'interrogation_target'
    title = 'Interrogation Target (Like)'
    queryset = InterrogationInputFilter.pseudocode_queryset
class InterrogationReturnFilter(InterrogationInputFilter):
    parameter_name = 'interrogation_return'
    title = 'Interrogation Return (Like)'
    queryset = InterrogationInputFilter.pseudocode_queryset

class LUTInterrogationAdmin(admin.ModelAdmin):
    list_display = ('interrogation_reference', 'interrogation_field', 'interrogation_operator', 'interrogation_target', 'interrogation_return', 'look_up_table_link' )
    list_filter = (InterrogationMasterNameFilterLike, InterrogationMasterNameFilterExact, InterrogationFieldFilter, InterrogationOperatorFilter, InterrogationTargetFilter, InterrogationReturnFilter)
    exclude = ('next_interrogation',)

    def look_up_table_link(self, obj):
        return format_html("<a href='{url}'>{name}</a>", url=f'/admin/ORM/pseudocodeobject/{obj.master.id}/change/', name=obj.master.name)
    def interrogation__return(self, obj):
        return format_html("<div style='margin-left:42px'>{ret}</div>", ret=obj.interrogation_return)
    def interrogation__target(self, obj):
        return format_html("<div style='margin-left:42px'>{tar}</div>", tar=obj.interrogation_target)
    def interrogation__operator(self, obj):
        return format_html("<div style='margin-left:42px'>{op}</div>", op=obj.interrogation_operator)
    def interrogation_field(self, obj):
        field_name = obj.field_to_interrogate
        if '.' not in field_name:
            field_name = field_name[1:-1]
        field_id = PseudocodeObject.objects.get(name=field_name).id
        return format_html("<a href='{url}'>{name}</a>", url=f'/admin/ORM/pseudocodeobject/{field_id}/change/', name=field_name)
    def interrogation_index(self, obj):
        return format_html("<div style='margin-left:42px'>{i}</div>", i=obj.index + 1)
    def interrogation_reference(self, obj):
        return f'Interrogation {obj.index+1} by {obj.master}'


class RelationInputFilter(PseudocodeObjectInputFilter):
    def pseudocode_queryset(self, request, queryset):
        term = self.value()
        filter_type = self.__class__.__name__

        if term is None:
            return
        
        matches = Q()        
        for part in term.split():
            if filter_type == 'RelationMasterFilter':    
                matches &= ( Q(master__name__icontains=part) | Q(master__name__icontains=part) )
            elif filter_type == 'RelationSubjectFilter':
                matches &= ( Q(subject__name__icontains=part) | Q(subject__name__icontains=part) ) 
        return queryset.filter(matches)

class RelationMasterFilter(RelationInputFilter):
    parameter_name = 'master__name'
    title = 'Name of Master'
    queryset = RelationInputFilter.pseudocode_queryset

class RelationSubjectFilter(RelationInputFilter):
    parameter_name = 'subject__name'
    title = 'Name of Subject'
    queryset = RelationInputFilter.pseudocode_queryset

class PseudocodeComponentRelationAdmin(admin.ModelAdmin):
    list_display = ('relation_id', 'master_name', 'subject_name')
    list_filter = (RelationMasterFilter, RelationSubjectFilter)
    def master_name(self, obj):
        return format_html("<a href='{url}'>{name}</a>", url=f'/admin/ORM/pseudocodeobject/{obj.master.id}/change/', name=obj.master.name)
    def subject_name(self, obj):
        return format_html("<a href='{url}'>{name}</a>", url=f'/admin/ORM/pseudocodeobject/{obj.subject.id}/change/', name=obj.subject.name)
    def relation_id(self, obj):
        return obj.id


admin.site.register(PseudocodeObject, PseudocodeObjectAdmin)
admin.site.register(PseudocodeComponentRelation, PseudocodeComponentRelationAdmin)
admin.site.register(LUTInterrogation, LUTInterrogationAdmin)
