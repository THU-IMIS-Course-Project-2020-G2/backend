from django.shortcuts import render
from manager.models import dish, dish_ingredient
from django import http
from django.views import View
from django.core import serializers
import json, dicttoxml, xmltodict
import numpy as np

#向机器人发送完餐确认
def finish_order(request):
    
    print('机器人已看到这道菜！')
    # 向后厨标注退的菜并更新对应的数据库
    data = dicttoxml.dicttoxml({}, root = True, attr_type = False)
    return http.HttpResponse(data)