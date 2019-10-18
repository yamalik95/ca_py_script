from django.contrib import admin
from .models import PseudocodeObject, PseudocodeComponentRelation, LUTInterrogation
from django.utils.html import format_html
from django.db.models import Q





class InputFilter(admin.SimpleListFilter):
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
            if filter_type == 'NameFilter':    
                matches &= ( Q(name__icontains=part) | Q(name__icontains=part) )
            elif filter_type == 'DescriptionFilter':
                matches &= ( Q(description__icontains=part) | Q(description__icontains=part) ) 
            elif filter_type == 'ObjectTypeFilter':
                matches &= ( Q(object_type__icontains=part) | Q(object_type__icontains=part) )
        return queryset.filter(matches)



class NameFilter(InputFilter):
    parameter_name = 'name'
    title = 'Object Name'

    queryset = InputFilter.pseudocode_queryset

class DescriptionFilter(InputFilter):
    parameter_name = 'description'
    title = 'Object Description'

    queryset = InputFilter.pseudocode_queryset

class ObjectTypeFilter(InputFilter):
    parameter_name = 'object_type'
    title = 'Object Type'

    queryset = InputFilter.pseudocode_queryset




class InterrogationInline(admin.TabularInline):
    model = LUTInterrogation
    fields = ('field_to_interrogate', 'interrogation_operator', 'interrogation_target', 'interrogation_return')
    extra = 0
    ordering = ('index',)


class SubcomponentInline(admin.StackedInline):
    model = PseudocodeComponentRelation
    fk_name = 'master'
    fields = ('subject', 'subject_description', 'subject_object_type')
    readonly_fields = ('subject_description', 'subject_object_type')
    extra = 0
    
    def subject_description(self, obj):
        return obj.subject.description
    def subject_object_type(self, obj):
        return obj.subject.object_type


class PseudocodeObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'object_type')
    list_filter = (NameFilter, DescriptionFilter, ObjectTypeFilter)
    inlines = (SubcomponentInline, InterrogationInline)
    exclude = ('sub_components',)
    

class LUTInterrogationAdmin(admin.ModelAdmin):
    search_fields = ('field_to_interrogate', 'id')
    list_display = ('id', 'look_up_table_name',)
    def look_up_table_name(self, obj):
        return format_html("<a href='{url}'>{name}</a>", url=f'/admin/ORM/pseudocodeobject/{obj.component.id}/change/', name=obj.component.name)

class PseudocodeComponentRelationAdmin(admin.ModelAdmin):
    search_fields = ('subject__name',)
    list_display = ('relation_id', 'master_name', 'subject_name')
    def master_name(self, obj):
        return format_html("<a href='{url}'>{name}</a>", url=f'/admin/ORM/pseudocodeobject/{obj.master.id}/change/', name=obj.master.name)
    def subject_name(self, obj):
        return format_html("<a href='{url}'>{name}</a>", url=f'/admin/ORM/pseudocodeobject/{obj.subject.id}/change/', name=obj.subject.name)
    def relation_id(self, obj):
        return obj.id


admin.site.register(PseudocodeObject, PseudocodeObjectAdmin)
admin.site.register(PseudocodeComponentRelation, PseudocodeComponentRelationAdmin)
admin.site.register(LUTInterrogation, LUTInterrogationAdmin)
