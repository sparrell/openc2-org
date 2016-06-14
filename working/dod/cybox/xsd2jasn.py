import json, os
from lxml import etree

xs = '{http://www.w3.org/2001/XMLSchema}'

def get_atts(e):
    tag = str(e.tag).replace(xs, '')
    atts = dict(e.items())
    if e.text and e.text.strip():
        print('SchemaError: unexpected text:', tag, atts, e.text.strip())
    return tag, atts

def get_children(e):
    children = [c.tag.replace(xs, '') for c in e]
    return [c for c in children if c != 'annotation']

def get_child(e, tag):
    children = {c.tag.replace(xs, ''): c for c in e}
    return children[tag]

def process_schema(schema):
    dtype = {'enumeration': 'Enumerated'}
    atts = dict(schema.items())
    jmeta = {'targetNamespace': atts['targetNamespace'], 'version': atts['version']}
    jtypes = []
    nsmap = {}
    for el in schema:
        tag, atts = get_atts(el)
        if tag == 'element':
            name = atts['name']
        elif tag == 'import':
            ns = os.path.split(atts['schemaLocation'])[1]
            ns = '??' + os.path.splitext(ns)[0]
            nsmap[ns] = atts['namespace']
            jmeta['import'] = {atts['namespace']: [ns, atts['schemaLocation']]}
        elif tag == 'simpleType':
            name = atts['name']
            elist = el
            types = set()
            vals = []
            opts = {}
            ch = get_children(el)
            if ch == ['restriction']:
                e2 = get_child(el, 'restriction')
                t2, a2 = get_atts(e2)
                opts['base'] = a2['base']
                elist = e2
            elif len(ch) > 1:
                print('SchemaError: unexpected simpleType nodes:', ch)
            for el2 in elist:
                t2, a2 = get_atts(el2)
                types.update((t2,))
                vals.append(a2['value'])
            if len(types) != 1:
                print('SchemaError: more than one type found:', types)
            else:
                jtypes.append([name, dtype[[t for t in types][0]], opts, vals])
        elif tag == 'complexType':
            pass
        elif tag == 'annotation':
            pass
        elif tag == 'attributeGroup':
            pass
        else:
            print('ParseError: Unknown tag:', tag)
    return jmeta, jtypes

schemadir = 'data'
files = ['Address_Object.xsd']
for ifile in files:
    with open(os.path.join(schemadir, ifile)) as f:
        tree = etree.parse(f)
    jmeta, jtypes = process_schema(tree.getroot())
    jasn = {"meta": jmeta, "types": jtypes}
    print(json.dumps(jasn, indent=2))
