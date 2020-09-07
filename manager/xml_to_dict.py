import xmltodict, json
def xml_to_dict(request):
    try:
        jsonstr = xmltodict.parse(request.body)
        jsonstr = json.dumps(jsonstr)
        return json.loads(jsonstr)['root']
    except Exception as e:
        try:
            jsonstr = xmltodict.parse(request.text)
            jsonstr = json.dumps(jsonstr)
            return json.loads(jsonstr)['root']
        except Exception as e:
            try:
                jsonstr = xmltodict.parse(request)
                jsonstr = json.dumps(jsonstr)
                return json.loads(jsonstr)['root']
            ## 如果确实数据项里面为空
            except Exception as e:
                return {"current_dishes":''}
