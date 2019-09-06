from xml.dom import minidom # For reading in XML file
from openpyxl import Workbook # For writing to an excel sheet
from openpyxl.styles import Alignment # For styling an excel sheet
from string import ascii_uppercase # For refering to columns in excel sheet
xml_scripts = minidom.parse('DMSCALIB.XML')
# We only care about function loops for now, so we get the elements in the XML files corresponding to loops
functions = xml_scripts.getElementsByTagName('FUNCTION')
attrs = [att for att in functions if att.attributes.get('name').value[1] == 'A']

if_starts = list()
for att in attrs:
    if 'IIF(' == att.attributes.get('result').value[:4]:
        if_starts.append(att)


ops = ['in', '<>', '>=', '<', '<=', '>', '=', 'IN', 'CONTAINS', 'BETWEEN']
left_cond = list()
ops_used = list()
weirds = list()
right_cond = list()
conds = list()

def get_args(links, dim):
    args = list()
    last_arg_end_index = 0
    for i, link in enumerate(links):
        if link['char'] == ',' and link['dim'] == dim:
            arg_slice = slice(links[last_arg_end_index]['abs_index'], link['abs_index']) 
            args.append(result[arg_slice])
            last_arg_end_index = i+1

    last_arg_slice = slice(links[last_arg_end_index]['abs_index'], links[-1]['abs_index']+1)
    args.append(result[last_arg_slice])

    return args



def rtrim(args):
    return f'{args[0]} trailing whitespace REMOVED'

def val_max(args):
    return f'MAX({args[0]}, {args[1]})'

def strlen(args):
    return f'LENGTH({args[0]})'

def left(args):
    return f'SUBSTRING {args[0]} positions 0 to {args[1]}'

def substr(args):
    return f'SUBSTRING {args[0]} positions {args[1]} to {args[2]}'

def datestr(args):
    return f'DATESTRING {args[0]} in MM/DD/YY'

# Note that an att as arg which may or may not return 0 must be handled specially
def substitute(args):
    if args[3].strip() != '0':
        return f'{args[0]} with {args[2]} REPLACING occurrence {args[3]} of {args[1]}'
        return f'{args[0]} '
    else:
        return f'{args[0]} with {argsp[2]} REPLACING all occurences of {args[1]}'

def isnull(args):
    return f'{args[0]} IF not equal to null; ELSE {args[1]}'

def strinstr(args):
    return f'START position of {args[0]} in {args[1]} IF found; ELSE 0'

def assign(args):
    return f'SET {args[0]} to {args[1]}'

def round_num(args):
    return f'{args[0]} ROUND to INTEGER'

def countchar(args):
    return f'COUNT occurences of {args[1]} in {args[0]}'

def repeat(args):
    return f'"{args[0]}" REPEATED {args[1]} times'

def text_reverse(args):
    return f'{args[0]} REVERSED'

def replace(args):
    if args[2].strip() != '0':
        return f'{args[0]} with {args[3]} REPLACING {args[2]} characters starting at position {args[1]}'
    else:
        return f'{args[0]} with {args[3]} INSERTED at position {args[1]}'

def trim(args):
    return f'{args[0]} with boundary whitespace & multiple space REMOVED'

def stringi(args):
    return f'{args[0]} ROUNDED to INTEGER & CONVERTED to STRING with at least {args[1]} digits (0\'s prepended if needed)'

def abso(args):
    return f'ABS({args[0]})'

def findchars(args):
    return f'COUNT {args[3]} in {args[0]} START at position {args[1]} SEARCH {args[2]} characters'

def num(args):
    return f'{args[0]} as NUMBER'

def val_min(args):
    return f'MIN({args[0]}, {args[0]})'

fun_map = {'rtrim': rtrim, 'max': val_max, 'strlen': strlen, 'left': left, 'substr': substr, 'datestr': datestr, 'substitute': substitute, 'findchars': findchars,
'isnull': isnull, 'strinstr': strinstr, 'assign': assign, 'int': round_num, 'round': round_num, 'countchar': countchar, 'rept': repeat, 'textreverse': text_reverse,
'replace': replace, 'trim': trim, 'stringi': stringi, 'abs': abso, 'num': num, 'min': val_min}

keys = list(fun_map.keys())
up_keys = [key.upper() for key in keys]

gvs = xml_scripts.getElementsByTagName('USERVAR')
import re
all_function_names = list()
for f in functions:
    all_function_names.append(f.attributes.get('name').value)
for gv in gvs:
    all_function_names.append(gv.attributes.get('name').value)

tags = set()
for att in attrs:
    words = re.findall(r'\w+', att.attributes.get('result').value)
    for x in words:
        if x not in ['AND', 'OR', 'BETWEEN', 'IN', 'null', 'not_in', 'NULL', 'contains', 'CONTAINS', 'in', 'and'] + all_function_names + keys + up_keys and all(not c.isnumeric() for c in x) and not x.isupper() and len(x)>2:
            tags.add(x)
            if len(x) == 1:
                print(att.attributes.get('result').value)
tags = list(tags)

def name_split_index(name):
    if 'EQ5_V6' in name:
        return 13
    elif 'EFX' in name:
        return 10
    else:
        return 6

def style_attr_name(name, split_name):
    if 'S' == name[1]:
        return f'[{split_name}]'
    else:
        return f'<{split_name}>'

for att in attrs:
    sub_comps = list()
    result = att.attributes.get('result').value
    for tag in tags:
        if tag in result:
            formatted_tag = f'{result.attributes.get("class")[:2]}.{tag}'
            result = result.replace(tag, formatted_tag)
            sub_comps.append(formatted_tag)
    for name in all_function_names:
        if name in result:
            formatted_name = style_attr_name(name, name[name_split_index(name):])
            result = result.replace(name, formatted_name)
            sub_comps.append(formatted_name)
    sub_comps = list(set(sub_comps))

    split_res = list(result)
    found_comp = False
    calculation = 'IF '


    last_was_open_paren = False
    dim = 0
    char_dims = [-1 for i in range(len(result))]
    prev_paren = -1
    for i, c in enumerate(result):
        if c == '(' and not last_was_open_paren:
            last_was_open_paren = True
            char_dims[prev_paren+1:i+1] = [(dim-1) for j in range(prev_paren+1, i)] + [dim]
            prev_paren = i
        elif c == ')' and not last_was_open_paren:
            dim -= 1
            char_dims[prev_paren+1:i+1] = [(dim) for j in range(prev_paren+1, i)] + [dim]
            prev_paren = i
        elif c == '(' and last_was_open_paren:
            dim += 1
            char_dims[prev_paren+1:i+1] = [(dim-1) for j in range(prev_paren+1, i)] + [dim]
            prev_paren = i
        elif c == ')' and last_was_open_paren:
            last_was_open_paren = False
            char_dims[prev_paren+1:i+1] = [(dim) for j in range(prev_paren+1, i)] + [dim]
            prev_paren = i

        if c == '(':
            difference = 0
            for j in reversed(range(i)):
                if not result[j].isalpha() and not (j == i-1 and result[j] == ' '):
                    difference = i-j
                    # manual override of loops
                    if difference >= 3 and result[j+1:i].replace(' ', '').lower() not in ('and', 'or', 'loop', 'between', 'in'):
                        for k in range(j+1, i):
                            char_dims[k] = dim
                    break


    linked_dims = list()
    for i, c in enumerate(result):
        linked_dims.append({'char': c, 'dim': char_dims[i], 'abs_index': i})
    original_result = result
    max_dim = max(char_dims)
    current_iteration_dim = max_dim
    
    while current_iteration_dim > 0:
        current_dim_fun_open_paren_indices = [i for i, link in enumerate(linked_dims) if link['char'] == '(' and link['dim'] == current_iteration_dim == linked_dims[i-1]['dim']]
        i = 0
        while i < len(current_dim_fun_open_paren_indices):
            sub_fun = ''
            sub_fun_end = 0
            open_paren_i = current_dim_fun_open_paren_indices[i]
            for j in reversed(range(open_paren_i)):
                if char_dims[j] == current_iteration_dim-1 or j == 0:
                    sub_fun = result[j+1:open_paren_i].replace(' ', '').lower()
                    if not sub_fun in ('if', 'iif'):
                        for k in range(open_paren_i, len(result)):
                            if linked_dims[k]['char'] == ')' and linked_dims[k]['dim'] == current_iteration_dim:
                                sub_fun_end = k
                                fun = {
                                    'dim': current_iteration_dim, 
                                    'name':sub_fun, 
                                    'args': get_args(linked_dims[open_paren_i+1:sub_fun_end], current_iteration_dim),
                                    'start_index': j+1,
                                    'end_index': sub_fun_end
                                }
                                transformation_text = fun_map[fun['name']](fun['args'])
                                if current_iteration_dim >= 1:
                                    transformation_text = f'({transformation_text})'
                                result_after_fun = result[fun['end_index']+1:]
                                result = result[:fun['start_index']] + transformation_text
                                next_search_index = len(result)
                                result += result_after_fun
                                char_dims = char_dims[:fun['start_index']] + [current_iteration_dim for l in range(len(transformation_text))] + char_dims[fun['end_index']+1:]
                                linked_dims = [{'char': c, 'dim': char_dims[i], 'abs_index': i} for i, c in enumerate(result)]
                                current_dim_fun_open_paren_indices[i+1:] = [link['abs_index'] for i, link in enumerate(linked_dims[next_search_index:]) if link['char'] == '(' and link['dim'] == current_iteration_dim  == linked_dims[link['abs_index']-1]['dim']]
                                break
                    else:
                        end_if_index = 0
                        first_comma_index = 0
                        sec_comma_index = 0
                        for i in range(open_paren_i, len(result)):
                            if (result[i], char_dims[i]) == (')', current_iteration_dim) and not end_if_index:
                                end_if_index = i
                                break
                            if (result[i], char_dims[i]) == (',', current_iteration_dim):
                                if not first_comma_index:
                                    first_comma_index = i
                                elif not sec_comma_index:
                                    sec_comma_index = i
                        start_index = 0 if j == 0 else j+1
                        transformation_text = f'\n{"    "*current_iteration_dim}IF'
                        if result[open_paren_i+1] != ' ':
                            transformation_text += ' '

                        conditions = result[open_paren_i+1:first_comma_index]
                        formatted_conditions = ''
                        multiple_cond_check_done = False
                        cond_joiners = list()
                        last_join_i = 0
                        for  i, c in enumerate(conditions):
                            if conditions[i:i+4].lower() == 'and ':
                                formatted_conditions += conditions[last_join_i:i] + f'\n{"    "*(current_iteration_dim+1)}AND ' 
                                last_join_i = i+4
                            elif conditions[i:i+3].lower() == 'or ':
                                formatted_conditions += conditions[last_join_i:i] + f'\n{"    "*(current_iteration_dim+1)}OR '
                                last_join_i = i+3
                            elif i == len(conditions) - 1:
                                formatted_conditions += conditions[last_join_i:]

                        sec_comma_index = sec_comma_index if sec_comma_index else len(result)
                        true_returnz
                            


                                 
                    break
            i += 1                       
                    
        current_iteration_dim -= 1

    print(result)
    print(original_result)
    print('\n\n')


                
