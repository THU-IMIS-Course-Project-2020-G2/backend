from django.shortcuts import render
from manager.models import *
from django import http
from django.views import View
import json
from django.db.models import Max
from django.db import transaction
from django.core import serializers


"""
获取所有订单 GET api/kitchen
获取某个订单 GET api/kitchen/{pk}
通过状态查询菜品  POST api/kitchen/dish     parms:dish_status  
通过工号查询菜品  POST api/kitchen/workstation     parms:station_id
"""

class kitchenView(View):
    def get(self, request):
        orders = order_detail.objects.all()
        order_list = []
        for order in orders:
            order = {
                'order_id':order.order_id.pk,
                'order_type':all_order_log.objects.get(order_id = order.order_id.pk).order_type,
                'dish_name':dish.objects.get(dish_id = order.dish_id).name,
                'count':order.count,
                'create_time':order.create_time.strftime('%Y%m%d %H:%M:%S'),
                'dish_status':order.dish_status,
                'station_id':order.station_id,
                'waiting_list':order.waiting_list
            }
            order_list.append(order)
        #print(order_list)
        return http.JsonResponse({"dishes":order_list})

# 查看菜品完成情况
class KitchenDish(View):
    def post(self, request):
        print('查看菜品完成情况')  # dish_status
        dict_data = json.loads(request.body, strict = False)
        print(dict_data)
        orders = order_detail.objects.filter(dish_status = dict_data['dish_status'])
        dishes_list = []
        for order in orders:
            order = {
                'order_id': order.order_id.pk,
                'dish_name': dish.objects.get(dish_id = order.dish_id).name,
                'count': order.count,
                'create_time': order.create_time.strftime('%Y%m%d %H:%M:%S'),
                'dish_status': order.dish_status,
                'station_id': order.station_id,
            }
            dishes_list.append(order)
        return http.JsonResponse({"dishes":dishes_list}, safe=False)

class kitchendetailView(View):
    # 查看某一订单的详情
    def get(self, request, pk):
        try:
            all_orders = order_detail.objects.filter(order_id=pk)
            all_order = []
            for order in all_orders:
                order = {
                    'order_id': order.order_id.pk,
                    'order_type': all_order_log.objects.get(order_id=order.order_id.pk).order_type,
                    'dish_name': dish.objects.get(dish_id = order.dish_id).name,
                    'count': order.count,
                    'create_time': order.create_time.strftime('%Y%m%d %H:%M:%S'),
                    'dish_status': order.dish_status,
                    'waiting_list': order.waiting_list
                }
                all_order.append(order)
            return http.JsonResponse({"dishes":all_order}, safe=False)
        except Exception as e:
            return http.HttpResponse(status = 404)

    # 添加新的成功下单
    
    @transaction.atomic
    # 考虑设置回滚, 比如在订单不存在的情况下
    def post(self, request):
        save_tag = transaction.savepoint()
        pass


class KitchenWorkstation(View):
    def post(self, request):
        try:
            dict_data = json.loads(request.body, strict = False)
            print(dict_data)
            orders = order_detail.objects.filter(station_id = dict_data['station_id'])
            dishes_list = []
            for order in orders:
                order = {
                    'order_id': order.order_id.pk,
                    'dish_name': dish.objects.get(dish_id = order.dish_id).name,
                    'count': order.count,
                    'create_time': order.create_time.strftime('%Y%m%d %H:%M:%S'),
                    'dish_status': order.dish_status,
                    'waiting_list': order.waiting_list,
                }
                dishes_list.append(order)
            return http.JsonResponse({"work_station":dishes_list}, safe=False)
        except:
            return http.HttpResponse(status = 404)

## 待删*************************
class KitchenFinish(View):
    def get(self, request):
        finish_orders = order_detail.objects.filter(dish_status = 2)
        Finish_list = []
        for order in finish_orders:
            order = {
                'order_id': order.order_id.pk,
                'table_id':all_order_log.objects.get(order_id = order.order_id.pk).table_id,
                'takeout_id':all_order_log.objects.get(order_id = order.order_id.pk).takeout,
                'dish_id': dish.objects.get(dish_id = order.dish_id).name,
                'count': order.count,
                'create_time': order.create_time.strftime('%Y%m%d %H:%M:%S'),
                'dish_status': order.dish_status,
                'station_id': order.station_id,
                'finish_time': order.finish_time.strftime('%Y%m%d %H:%M:%S'),
            }
            Finish_list.append(order)
        return http.JsonResponse({"dishes": Finish_list}, safe=False)

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



