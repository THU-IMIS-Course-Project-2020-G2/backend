import xmltodict, json
def xml_to_dict(request):
    try:
        jsonstr = xmltodict.parse(request.body)
        jsonstr = json.dumps(jsonstr)
        return json.loads(jsonstr)['root']
    except Exception as e:
        jsonstr = xmltodict.parse(request.text)
        jsonstr = json.dumps(jsonstr)
        return json.loads(jsonstr)['root']
