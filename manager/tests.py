from django.test import TestCase
import manager.dicttoxml as dicttoxml
import json
from django import http
from manager.xml_to_dict import *
import xml.etree.cElementTree as ET
import xml.dom.minidom
# dish_json = {"current_dishes":[{"dish_id":101, "count":1}, {"dish_id":102, "count":1}]}
# data = dicttoxml.dicttoxml(dish_json, attr_type = False)
# print(data)

# jsonstr = xmltodict.parse(data)
# jsonstr = json.dumps(jsonstr)
# jsonstr = json.loads(jsonstr)
# print(jsonstr['root'])

# def material_request(request):
#     json_dict = {"raw_material":[{"ingredient_name":'白条净膛鹅（克）',"ingredient_number":300.0},
#                        {"ingredient_name":'白萝卜（克）',"ingredient_number":900.0},
#                        {"ingredient_name":'茅台（瓶）',"ingredient_number":1.0}, 
#                        {"ingredient_name":'梭子蟹（克）',"ingredient_number": 250.0},
#                        {"ingredient_name":'花蛤（克）',"ingredient_number": 1200.0},
#                        {"ingredient_name":'扇贝（地播）（克）',"ingredient_number": 500.0},
#                        {"ingredient_name":'白条湖鸭（克）',"ingredient_number": 700.0},
#                        {"ingredient_name":'五花肉（瘦）（克）',"ingredient_number": 1750.0},
#                        {"ingredient_name":'荔浦芋头（克）',"ingredient_number": 300.0},
#                        {"ingredient_name":'鸡蛋（只）',"ingredient_number": 200.0},
#                        {"ingredient_name":'胡萝卜（克）', "ingredient_number":150.0},
#                        {"ingredient_name":'绿菜花（克）', "ingredient_number":450.0}]}
#     data = dicttoxml.dicttoxml(json_dict, root = True, attr_type = False)
#     print(data)
#     return http.HttpResponse(data)

def order_request(request):
    data = dicttoxml.dicttoxml({}, root = True, attr_type = False)
    return http.HttpResponse(data)

def takeout_request(request):
    data = dicttoxml.dicttoxml({}, root = True, attr_type = False)
    return http.HttpResponse(data)

def add_material_request(request):
    data = dicttoxml.dicttoxml({}, root = True, attr_type = False)
    return http.HttpResponse(data)

def material_request(request):
    data ="""<?xml version='1.0' encoding='UTF-8' ?>
    <root>
    <raw_material>
        <ingredient_name>白条净膛鹅（克）</ingredient_name>
        <ingredient_number>300</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>五花肉（瘦）（克）</ingredient_name>
        <ingredient_number>560</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>纯排骨（克）</ingredient_name>
        <ingredient_number>630</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>羊排骨（克）</ingredient_name>
        <ingredient_number>350</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>梭子蟹（克）</ingredient_name>
        <ingredient_number>850</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>肉鸡（克）</ingredient_name>
        <ingredient_number>850</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>羊排（克）</ingredient_name>
        <ingredient_number>850</ingredient_number>
    </raw_material>
        <raw_material>
        <ingredient_name>牛柳（克）</ingredient_name>
        <ingredient_number>850</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>桂鱼（克）</ingredient_name>
        <ingredient_number>1000</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>白萝卜（克）</ingredient_name>
        <ingredient_number>900</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>扇贝（地播）（克）</ingredient_name>
        <ingredient_number>600</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>荔浦芋头（克）</ingredient_name>
        <ingredient_number>200</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>活白虾（克）</ingredient_name>
        <ingredient_number>400</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>番茄（克）</ingredient_name>
        <ingredient_number>250</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>花生米（克）</ingredient_name>
        <ingredient_number>600</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>白条湖鸭（克）</ingredient_name>
        <ingredient_number>1000</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>鸡胸（克）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>纯瘦肉（克）</ingredient_name>
        <ingredient_number>500</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>牛柳（里脊）（克）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>花蛤（克）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>多宝鱼（克）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>藕（克）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>黄瓜（克）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>绿菜花（克）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
        <raw_material>
        <ingredient_name>胡萝卜（克）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>莜麦面（克）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>东北大米（克）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>ef</ingredient_name>
        <ingredient_number>2</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>彩椒（克）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>柿子椒（克）</ingredient_name>
        <ingredient_number>400</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>空心菜（克）</ingredient_name>
        <ingredient_number>500</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>芥兰（克）</ingredient_name>
        <ingredient_number>400</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>茄子（克）</ingredient_name>
        <ingredient_number>300</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>韭菜（克）</ingredient_name>
        <ingredient_number>400</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>土豆（克）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>好面缘面粉（克）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>泰国糯米（克）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>鸡蛋（只）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>红星二锅头（瓶）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>可乐（瓶）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>雪碧（瓶）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>北冰洋（瓶）</ingredient_name>
        <ingredient_number>100</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>加多宝（瓶）</ingredient_name>
        <ingredient_number>90</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>青岛啤酒（瓶）</ingredient_name>
        <ingredient_number>90</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>肉</ingredient_name>
        <ingredient_number>90</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>大肉</ingredient_name>
        <ingredient_number>90</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>大菜</ingredient_name>
        <ingredient_number>90</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>大肠</ingredient_name>
        <ingredient_number>90</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>1234</ingredient_name>
        <ingredient_number>90</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>美汁源橙汁（瓶）</ingredient_name>
        <ingredient_number>90</ingredient_number>
    </raw_material>
    <raw_material>
        <ingredient_name>茅台（瓶）</ingredient_name>
        <ingredient_number>90</ingredient_number>
    </raw_material>
    </root>
    """
    return http.HttpResponse(bytes(data, encoding = 'utf-8'))