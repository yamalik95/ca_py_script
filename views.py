from django.shortcuts import render, redirect
from ORM.models import PseudocodeObject
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def explode_up(request, obj_id):
    obj = PseudocodeObject.objects.get(id=obj_id)

    import pdb;pdb.set_trace()