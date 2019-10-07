from django.contrib import admin
from .models import PseudocodeObject, PseudocodeComponentRelation, LUTInterrogation
from django.utils.html import format_html

class PseudocodeObjectAdmin(admin.ModelAdmin):
    search_fields = ('name', 'id')
    list_display = ('id', 'name')

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
    
    master_name.mark_safe = True

admin.site.register(PseudocodeObject, PseudocodeObjectAdmin)
admin.site.register(PseudocodeComponentRelation, PseudocodeComponentRelationAdmin)
admin.site.register(LUTInterrogation, LUTInterrogationAdmin)
