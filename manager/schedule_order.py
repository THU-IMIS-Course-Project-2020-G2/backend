from django.shortcuts import render
from manager.models import *
from django import http
from django.views import View
from django.core import serializers
from django.db.models import Sum, Count, Max, Min, Avg
import json, dicttoxml, xmltodict, requests
import numpy as np
from pulp import *
from datetime import datetime
from manager.param import *

#根据新的下单, 催单, 更新排班情况
## 简单随机算法
class kitchen_update():

    def __init__(self):
    # 读取现在的后厨做菜信息
    ## 目前采用冷菜1-3 + 热菜4-7
        self.all_station_number = all_number
        self.cold_station_number = cold_number
        self.hot_station_number = hot_number
    ## 对每个工位更新为(order_id, dish_id, require_time, priority)的四元数组
    ## station_id + waiting_list能唯一确定(order_id, dish_id)
        self.station_info = [[] for i in range(self.all_station_number)]
        for sid in range(self.all_station_number):
        # 读取该工位的最长WL, 先判断sid除了当前正在做的菜是否为空
            sid_list = order_detail.objects.filter(station_id = sid)
            if len(sid_list)> 0: 
                max_wl = sid_list.aggregate(Max('waiting_list'))['waiting_list__max']
                for i in range(1, max_wl + 1):
                    temp_dish = order_detail.objects.get(station_id = sid, waiting_list = i)
                    dish_info = dish.objects.get(dish_id = temp_dish.dish_id)
                    # 记录目前等待的信息
                    self.station_info[sid].append({"order_id":temp_dish.order_id.pk, 
                                                    "dish_id":temp_dish.dish_id,
                                                    "require_time":dish_info.time_cost*temp_dish.count,
                                                    "priority":1})
                                                    
    def order_update(self, current_id, dishes):
        # 下单更新结合dish_id和require_time, 结合目前的station_info进行计算
        ## 如果采用实际算法, 对这一单每道菜会返回一个(dish_id, station_id, waiting_list)的数组
       
        add_type = order_choice_log.objects.all().last().add_order_type
        ## 否则按照随机算法我目前会直接随机生成一个这样的序列
        if add_type == 0:
            current_allocation = []
            for dish_detail in order_dish:
                dish_id = dish_detail['dish_id']
                ## 冷菜工位
                if dish.objects.get(dish_id = dish_id).dish_type in ['开胃冷菜', '酒水', '主食点心', '营养汤羹']:
                    alloc_id = np.random.randint(1, self.cold_station_number + 1)
                ## 热菜工位
                else:
                    alloc_id = np.random.randint(self.cold_station_number + 1, self.all_station_number + 1)
                # 该工位目前没有菜在做
                if len(self.station_info[alloc_id - 1]) == 0:
                    alloc_wl = 0                
                else:
                # 随机进入队列
                    alloc_wl = np.random.randint(1, len(self.station_info[alloc_id - 1]) + 2)
                current_allocation.append({"dish_id":dish_id, "count":dish_detail['count'], "station_id":alloc_id, "waiting_list":alloc_wl})
            # 插入新的订单到数据库里

            for curr_loc in current_allocation:
                if curr_loc['alloc_wl'] == 0:
                    order_detail.objects.create(order_id = current_id, dish_id = curr_loc['dish_id'], count = curr_loc['count'], 
                                                dish_status = 4, station_id = curr_loc['station_id'], waiting_list = 0, start_time = datetime.now())
                else:
                    order_detail.objects.create(order_id = current_id, dish_id = curr_loc['dish_id'], count = curr_loc['count'], 
                                                dish_status = 0, station_id = curr_loc['station_id'], waiting_list = curr_loc['alloc_wl'])
                ## 更新这个工位之后其他的菜的WL, 将之后的菜WL滞后一位
                    later_orders = order_detail.objects.filter(station_id = current_station, waiting_list__gt = curr_loc['alloc_wl'])
                    for later_order in later_orders:
                        later_order.waiting_list = later_order.waiting_list + 1
                        later_order.save()
        # 下单更新结合dish_id和require_time, 结合目前的station_info进行计算
        ## 采用优先级调整算法
        ## 如果采用实际算法, 对这一单每道菜会返回一个(dish_id, station_id, waiting_list)的数组             
        elif add_type == 1:
            pass

        ## 采用DP的方式
        elif add_type == 2:
            pass
    def nudge_update(self, current_id):
        nudge_type = order_choice_log.objects.all().last().nudge_order_type
        if nudge_type == 0:
            # 随机前置
            nudge_order_dishes = order_detail.objects.filter(order_id = current_id)
            for nudge_dish in nudge_order_dishes:
                ## 已经是WL = 1, 不需要继续修改
                if nudge_dish.waiting_list == 1:
                    nudge_dish.dish_status = 1
                    nudge_dish.save()
                elif nudge_dish.waiting_list > 1:
                    nudge_dish.dish_status = 1
                    ## 这道菜修改后的WL
                    if nudge_dish.waiting_list == 2:
                        change_id = nudge_dish.waiting_list - 1
                    else:
                        change_id = np.random.randint(1, nudge_dish.waiting_list - 1)

                    before_orders = order_detail.objects.filter(station_id = nudge_dish.station_id, waiting_list__gte = change_id, waiting_list__lt = nudge_dish.waiting_list)
                    nudge_dish.waiting_list = change_id
                    nudge_dish.save()
                    ## 更新这个工位之后其他的菜的WL, 将修改change_id及之后的菜WL滞后一位
                    for before_order in before_orders:
                        before_order.waiting_list = before_order.waiting_list + 1
                        before_order.save()
        elif nudge_type == 1:
        # 催单更新, 结合目前的station_info进行计算
        ## 更新催单信息到数据库里, 基于优先级的调整策略
            pass
        elif nudge_type == 2:
        # 基于值函数的调整策略
            pass