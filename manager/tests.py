from django.test import TestCase
import manager.dicttoxml as dicttoxml
import json
from django import http
from manager.xml_to_dict import *
import xml.etree.cElementTree as ET
# dish_json = {"current_dishes":[{"dish_id":101, "count":1}, {"dish_id":102, "count":1}]}
# data = dicttoxml.dicttoxml(dish_json, attr_type = False)
# print(data)

# jsonstr = xmltodict.parse(data)
# jsonstr = json.dumps(jsonstr)
# jsonstr = json.loads(jsonstr)
# print(jsonstr['root'])

def material_request(request):
    json_dict = {"raw_material":[{"ingredient_name":'白条净膛鹅（克）',"ingredient_number":300.0},
                       {"ingredient_name":'白萝卜（克）',"ingredient_number":900.0},
                       {"ingredient_name":'茅台（瓶）',"ingredient_number":1.0}, 
                       {"ingredient_name":'梭子蟹（克）',"ingredient_number": 250.0},
                       {"ingredient_name":'花蛤（克）',"ingredient_number": 1200.0},
                       {"ingredient_name":'扇贝（地播）（克）',"ingredient_number": 500.0},
                       {"ingredient_name":'白条湖鸭（克）',"ingredient_number": 700.0},
                       {"ingredient_name":'五花肉（瘦）（克）',"ingredient_number": 1750.0},
                       {"ingredient_name":'荔浦芋头（克）',"ingredient_number": 300.0},
                       {"ingredient_name":'鸡蛋（只）',"ingredient_number": 200.0},
                       {"ingredient_name":'胡萝卜（克）', "ingredient_number":150.0},
                       {"ingredient_name":'绿菜花（克）', "ingredient_number":450.0}]}
    data = dicttoxml.dicttoxml(json_dict, root = True, attr_type = False)
    return http.HttpResponse(data)

def order_request(request):
    data = dicttoxml.dicttoxml({}, root = True, attr_type = False)
    return http.HttpResponse(data)

def takeout_request(request):
    data = dicttoxml.dicttoxml({}, root = True, attr_type = False)
    return http.HttpResponse(data)
