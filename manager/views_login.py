from django.shortcuts import render
from manager.models import *
from django import http
from django.views import View
import json, requests
from django.db.models import Max
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Sum, Count, Max, Min, Avg

def login_check(request):
    dict_data = json.loads(request.body, strict = False)
    mg_info = managerInfo.objects.filter(user_id = dict_data['user_id'], password = dict_data['password'], type = dict_data['type'])
    login_response = {"user_id":dict_data['user_id'], "success":0, "power":dict_data['type']}
    # 登录失败
    if len(mg_info) == 0:
        login_response['success'] = 1
    return http.JsonResponse(login_response)