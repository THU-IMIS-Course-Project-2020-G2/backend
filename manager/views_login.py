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
    mg_info = managerInfo.objects.filter(userid = dict_data['userid'], password = dict_data['password'], user_type = dict_data['user_type'])
    login_response = {"userid":dict_data['userid'], "success":0, "power":dict_data['user_type']}
    # 登录失败
    if len(mg_info) == 0:
        login_response['success'] = 1
    return http.JsonResponse(login_response)