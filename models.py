from django.db import models


class PseudocodeObject(models.Model):
    name = models.CharField(max_length=42, default="SU_ATTR")
    description = models.CharField(max_length=42, null=True, blank=True)
    version = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    bureau = models.CharField(max_length=42, null=True, blank=True)
    object_type = models.CharField(max_length=42)
    sub_components = models.TextField(null=True, blank=True)
    calculation = models.TextField(null=True, blank=True)
    first_interrogation = models.OneToOneField('LUTInterrogation', on_delete=models.SET_NULL, null=True, blank=True)

class PseudocodeComponentRelation(models.Model):
    master = models.ForeignKey(PseudocodeObject, on_delete=models.CASCADE, related_name='master')
    subject = models.ForeignKey(PseudocodeObject, on_delete=models.CASCADE, related_name='subject')

# class LUTReturnValue(models.Model):
#     value = models.CharField(max_length=42, default="Return Value")
#     enumeration = models.TextField(null=True, blank=True)


class LUTInterrogation(models.Model):
    component = models.ForeignKey(PseudocodeObject, on_delete=models.CASCADE, related_name='look_up_table')
    field_to_interrogate = models.CharField(max_length=42)
    comparison = models.CharField(max_length=42)
    comparison_value = models.CharField(max_length=42)
    return_value = models.CharField(max_length=42, default="Return Value")
    next_interrogation = models.OneToOneField(to='self', on_delete=models.SET_NULL, null=True, blank=True)


def init_attr_load(attrs, type):
    for i, row in enumerate(attrs):
        if row[0] == row[0]:
            info = {'name': row[0], 'description': row[2], 'version': float(row[1]), 'bureau': row[4], 'calculation': row[-1], 'sub_components': '', 'object_type': type}
            k = 0
            while i+k < len(attrs) and row[-4] == row[-4] and (k == 0 or attrs[i+k][0] != attrs[i+k][0]):
                if type(attrs[i+k][-4]) == float:
                    import pdb;pdb.set_trace()
                info['sub_components'] += f'{attrs[i+k][-4]} '
                k += 1
            new_su_attr = PseudocodeObject(**info)
            new_su_attr.save()

def init_lut_load(luts):
    for i, row in enumerate(luts):
        if row[0] == row[0]:
            if row[1] == 'n' or row[1] is str:
                import pdb;pdb.set_trace()
            if row[-11] != row[-11]:
                row[-11] = 'NULL'
            lut_info = {'name': row[0], 'description': row[2], 'version': float(row[1]), 'bureau': row[4], 'calculation': row[-11], 'sub_components': '', 'object_type': 'L.U.T'}

            interrogations = list()
            k = 0
            while i+k < len(luts) and (k == 0 or luts[i+k][0] != luts[i+k][0]):
                if luts[i+k][-8] == luts[i+k][-8]:
                    lut_info['sub_components'] += f'{luts[i+k][-8]} '
                interrogation = luts[i+k][-5:-1]
                interrogation_info = {'component': '', 'field_to_interrogate': interrogation[0], 'comparison': interrogation[1], 'comparison_value': interrogation[2], 'return_value': interrogation[3]}
                interrogations.append(interrogation_info)
                k += 1

            new_lut = PseudocodeObject(**lut_info)
            new_lut.save()

            last_interrogation = None
            for j, interrogation in enumerate(interrogations[::-1]):
                interrogation['component'] = new_lut
                if not last_interrogation is None:
                    interrogation['next_interrogation'] = last_interrogation
                new_interrogation = LUTInterrogation(**interrogation)
                new_interrogation.save()
                if j == len(interrogations) - 1:                    
                    new_lut.first_interrogation = new_interrogation
                    new_lut.save()
                last_interrogation = new_interrogation

            
def init_rel_load():
    objs = PseudocodeObject.objects
    luts = objs.filter(object_type='L.U.T')
    non_luts = objs.exclude(object_type='L.U.T')
    all_objs = objs.all()
    count = 0
    obj_count = 0
    for obj in objs.all():
        if obj.sub_components is not None:
            print(obj.sub_components)
            obj_count += 1
            subs = obj.sub_components.split(' ')[:-1]
            for sub in subs:
                if '.' not in sub:
                    count += 1
                    if sub[0] == '[':
                        subject_filter = luts.filter(name=sub[1:-1])
                    else:
                        subject_filter = non_luts.filter(name=sub[1:-1])

                    if len(subject_filter) != 1:
                        import pdb;pdb.set_trace()
                    else:
                        new_rel = PseudocodeComponentRelation(master=obj, subject=subject_filter[0])
                        new_rel.save()
                else:
                    tag_filter = PseudocodeObject.objects.filter(name=sub)
                    if len(tag_filter) == 0:
                        new_bureau_tag = PseudocodeObject(name=sub, object_type='XML Tag')
                        new_bureau_tag.save()
                        new_rel = PseudocodeComponentRelation(master=obj, subject=new_bureau_tag)
                    else:
                        new_rel = PseudocodeComponentRelation(master=obj, subject=tag_filter[0])
                    new_rel.save()
        elif '.' not in obj.name:
            import pdb;pdb.set_trace()
    print(count)
    print(obj_count)


