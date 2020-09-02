from django.test import TestCase
import dicttoxml, xmltodict, json
import xml.etree.cElementTree as ET
dish_json = {"current_dishes":[{"dish_id":101, "count":1}, {"dish_id":102, "count":1}]}
data = dicttoxml.dicttoxml(dish_json, attr_type = False)
print(data)

jsonstr = xmltodict.parse(data)
jsonstr = json.dumps(jsonstr)
jsonstr = json.loads(jsonstr)
print(jsonstr['root'])

# #全局唯一标识 

