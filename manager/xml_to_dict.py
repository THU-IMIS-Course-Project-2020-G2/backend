import xmltodict, json
def xml_to_dict(request):
    jsonstr = xmltodict.parse(request.body)
    jsonstr = json.dumps(jsonstr)
    return json.loads(jsonstr)['root']