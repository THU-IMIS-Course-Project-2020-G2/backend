from django.shortcuts import render
from manager.models import *
from django import http
from django.views import View
import json, requests
from django.db.models import Max
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Sum, Count, Max, Min, Avg

class order_type(View):
    # 历史所有参数修改的请求
    def get(self, request):
        all_past_log = order_choice_log.objects.all()
        all_log = []
        for past_log in all_past_log:
            past_log = {
                'choice_id':past_log.choice_id,
                'add_order_type':past_log.add_order_type,
                'nudge_order_type':past_log.nudge_order_type,
                'param':past_log.param,
                'create_time':past_log.create_time.strftime('%Y%m%d %H:%M:%S')
            }
            all_log.append(past_log)
        print(all_log)
        return http.JsonResponse({'all_log':all_log})

    # 新加的修改参数的请求
    def post(self, request):
        try:
            dict_data = json.loads(request.body, strict = False)
            order_choice_log.objects.create(add_order_type = dict_data['add_order_type'], 
                                        nudge_order_type = dict_data['nudge_order_type'],
                                        param = dict_data['param'])
            return http.JsonResponse({"edit_status": 1})
        except Exception:
            return http.JsonResponse({"edit_status": 0})
