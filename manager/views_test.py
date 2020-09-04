from django.shortcuts import render
from manager.models import dish, dish_ingredient
from django import http
from django.views import View
from django.core import serializers
import json, dicttoxml, xmltodict
import numpy as np

#向机器人发送完餐确认
def finish_dish(request):
    print('机器人已看到这道菜！')
    # 向后厨标注退的菜并更新对应的数据库
    data = dicttoxml.dicttoxml({}, root = True, attr_type = False)
    return http.HttpResponse(data)

def serve(request):    
    print('堂食某个菜已经完成！')
    # 向后厨标注退的菜并更新对应的数据库
    data = dicttoxml.dicttoxml({}, root = True, attr_type = False)
    return http.HttpResponse(data)

def order_other_cost(request):    
    print('已经将信息发送给财务！')
    # 向后厨标注退的菜并更新对应的数据库
    data = dicttoxml.dicttoxml({}, root = True, attr_type = False)
    return http.HttpResponse(data)

def deliver_takeout(request):    
    print("这一单外卖已经完成！")
    # 向后厨标注退的菜并更新对应的数据库
    data = dicttoxml.dicttoxml({}, root = True, attr_type = False)
    return http.HttpResponse(data)

