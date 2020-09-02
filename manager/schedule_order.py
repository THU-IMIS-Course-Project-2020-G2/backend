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
### 因为这里不涉及时间的绝对关系，在优化比较只考虑时间的相对关系即可。
class kitchen_update():

    def __init__(self):
    # 读取现在的后厨做菜信息
    ## 目前采用冷菜1-3 + 热菜4-7
        self.all_station_number = all_number
        self.cold_station_number = cold_number
        self.hot_station_number = hot_number
    ## 对每个工位更新为(order_id, dish_id, require_time, priority)的四元数组
    ## station_id + waiting_list >= 1能唯一确定(order_id, dish_id)
        self.station_info = [[] for i in range(self.all_station_number)]
        ## 找到目前在等的所有单号的信息, 将这些作为一个字典的键
        id_list = order_detail.objects.filter(waiting_list__gt = 0).values("order_id").distinct()
        order_key = [id_serial['order_id'] for id_serial in id_list]
        self.order_wt = dict()
        ## 对这个字典的每个键赋初值, 值包括(station_id, station_loc, waiting_time)
        for id_key in order_key:
            self.order_wt[id_key] = {"sid":0, "sloc":0, "waiting_time":10000}
        for sid in range(self.all_station_number):
        # 读取该工位的最长WL, 先判断sid除了当前正在做的菜是否为空
            sid_list = order_detail.objects.filter(station_id = sid + 1)
            if len(sid_list)> 0: 
                max_wl = sid_list.aggregate(Max('waiting_list'))['waiting_list__max']
                ## 找到目前正在做的菜, 最多只会存在一个                
                current_dish = order_detail.objects.filter(station_id = sid + 1, dish_status = 4)
                ### 目前该工位没有正在做的菜
                if len(current_dish) == 0:
                    continue
                else:
                    ## 对于这道菜所在的工位, 计算相应的时间
                    time_speed = order_choice_log.objects.all().last().param
                    consume_time = dish.objects.get(dish_id = current_dish[0].dish_id).time_cost
                    current_waiting_time = current_dish[0].count*consume_time - (datetime.now() - current_dish[0].start_time).total_seconds()/time_speed
                    for i in range(1, max_wl + 1):
                        temp_dish = order_detail.objects.get(station_id = sid, waiting_list = i)
                        dish_info = dish.objects.get(dish_id = temp_dish.dish_id)
                        current_waiting_time += dish_info.time_cost*temp_dish.count
                        # flag表示是否为当前等待工位最先等待的菜, True表示是最先等待的菜
                        ## 判断是否为当前等待时间最小的菜
                        if order_wt[temp_dish.order_id.pk]["waiting_time"] > current_waiting_time:
                            pre_sid = order_wt[temp_dish.order_id.pk]['sid']
                            pre_sloc = order_wt[temp_dish.order_id.pk]['sloc']
                            if pre_sid != 0:
                            ## 将原来的waiting_time对应的列flag设置为False
                                self.station_info[pre_sid][pre_sloc]['flag'] = False
                            ## 更新为自己的sid和Loc
                            order_wt[temp_dish.order_id.pk]['sid'] = sid + 1
                            order_wt[temp_dish.order_id.pk]['sloc'] = i
                            ## 记录目前等待的信息
                            self.station_info[sid].append({"order_id":temp_dish.order_id.pk, 
                                                        "dish_id":temp_dish.dish_id,
                                                        "total_waiting_time":current_waiting_time,
                                                        "flag":True})
                        else:
                            ## 记录目前等待的信息
                            self.station_info[sid].append({"order_id":temp_dish.order_id.pk, 
                                                        "dish_id":temp_dish.dish_id,
                                                        "total_waiting_time":current_waiting_time,
                                                        "flag":False})
            
    ## 插入时间最短的菜, 并计算对应的最短时间增量
    ## add_time表示该单用时最少的菜的时间增量
    def minimum_waiting_time_computation(self, add_time, dish_type):
        # 表示冷菜
        if dish_type == 0:
            start_point = 0
            end_point = self.cold_station_number
        # 表示热菜
        else:
            start_point = self.cold_station_number
            end_point = self.all_station_number
        insert_loc = {"sid": 0, "snum": 0, "waiting_time":add_time + 100000}
        # 判断是否会影响等待时间
        curr_waiting_time = np.zeros(end_point - start_point)
        ## 存在当前闲的工位
        for sid in range(start_point, end_point):
            current_dish = order_detail.objects.filter(station_id = sid + 1, dish_status = 4)
            ### 目前该工位没有正在做的菜
            if len(current_dish) == 0:
                insert_loc["sid"] = sid + 1
                insert_loc["waiting_time"] = add_time
                return insert_loc
            else:    
                time_speed = order_choice_log.objects.all().last().param
                consume_time = dish.objects.get(dish_id = current_dish[0].dish_id).time_cost
                curr_waiting_time[sid - start_point] = current_dish[0].count*consume_time - (datetime.now() - current_dish[0].start_time).total_seconds()/time_speed
        # 如果有WL = 1，选择一个最短的插入.
        for sid in range(start_point, end_point):
            if len(self.station_info[sid]) == 0:
                if curr_waiting_time[sid] + add_time < insert_loc["waiting_time"]: 
                    insert_loc["sid"] = sid + 1
                    insert_loc["snum"] = 1
                    insert_loc["waiting_time"] = curr_waiting_time[sid] + add_time
        # 有WL = 1的情况
        if insert_loc["sid"] !=0:
            return insert_loc
        # 遍历所有的等待位, 计算在这之前或之后产生的变化
        ## 对于每一个工位i 如果有M_i个等待位置，那么就需要有(M_i + 1)种情况
        ## 总计需要遍历的次数为\sum_{i = N}(M_i + 1)
        else:
            for sid in range(start_point, end_point):
                for loc in range(len(self.station_info[sid]) + 1):
                ## 计算每种Loc带来的时间改变和增量
                    if loc == 0:
                        loc_add_time = curr_waiting_time[sid - start_point] + add_time
                    else:
                        loc_add_time = curr_waiting_time[sid - start_point] + self.station_info[sid][loc - 1]["total_waiting_time"] + add_time
                ## 对整个系统时间的改变量
                ## 查看对之后工位的影响
                    for after_loc in range(loc, len(self.station_info[sid])):
                        ## 之后工位存在某个菜是某单的第一个菜
                        if self.station_info[sid][after_loc - 1]["flag"] == True:
                            loc_add_time += add_time
                    # 更新等待时间
                    if loc_add_time < insert_loc["waiting_time"]:
                        insert_loc["sid"] = sid + 1
                        insert_loc["snum"] = loc + 1
                        insert_loc["waiting_time"] = loc_add_time
        return insert_loc

    
    ## 计算目前所有菜的等待时间指标
    def total_waiting_time_computation(self):
        return 0
    def order_update(self, current_id, dishes):
        # 下单更新结合dish_id和require_time, 结合目前的station_info进行计算
        ## 如果采用实际算法, 对这一单每道菜会返回一个(dish_id, station_id, waiting_list)的数组
        # 选择对应的算法进行调整
        add_type = order_choice_log.objects.all().last().add_order_type
        current_allocation = []
        ## 否则按照随机算法我目前会直接随机生成一个这样的序列
        if add_type == 0:
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
        # 下单更新结合dish_id和require_time, 结合目前的station_info进行计算
        ## 采用优先级调整算法
        ### 如果采用实际算法, 对这一单每道菜会返回一个(dish_id, station_id, waiting_list)的数组  
        ### 不管冷菜热菜我们直接进行计算
        ### 其他的菜直接随机           
        elif add_type == 1:
            dish_time = dict()
        ## 按照consume_time进行时间的排序
            for dish_detail in order_dish:
                dish_id = dish_detail['dish_id']
                consume_time = dish.objects.get(dish_id = dish_id).time_cost*dish_detail['count']
                dish_time[dish_id] = consume_time
            ## 选择其中用时最短的菜
            min_time_dish = min(dish_time, key = lambda k:dish_time[k])
            ## 判断这是冷菜还是热菜
            type_flag = 1
            if dish.objects.get(dish_id = min_time_dish).dish_type in ['开胃冷菜', '酒水', '主食点心', '营养汤羹']:
                type_flag = 0
            dish_insert_loc = self.minimum_waiting_time_computation(dish_time[min_time_dish], type_flag)
            ## 找出其对应的count
            for dish_detail in order_dish:
                ## 最小时间的菜
                if dish_detail['dish_id'] == min_time_dish:
                    current_allocation.append({"dish_id":min_time_dish, "count":dish_detail['count'], 
                                                "station_id":dish_insert_loc["sid"], "waiting_list":dish_insert_loc["snum"]})
                else:
                    ## 其他菜随机分配位置
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
                    # 随机进入队列, 但需要保证在最小菜的位置之后
                        if alloc_id == dish_insert_loc["sid"]:
                            alloc_wl = np.random.randint(dish_insert_loc['snum'] + 1, len(self.station_info[alloc_id - 1]) + 2)
                    current_allocation.append({"dish_id":dish_id, "count":dish_detail['count'], "station_id":alloc_id, "waiting_list":alloc_wl})
    

        ### 冷菜热菜分别计算时间排序, 对热菜的一个使用epsilon-greedy + DP
        ### 其他的菜直接随机
        elif add_type == 2:
            # epsilon为给定的参数
            epsilon = 0.5
            dish_time_cold = dict()
            dish_time_hot = dict()
            ## 按照consume_time进行时间的排序
            for dish_detail in order_dish:
                dish_id = dish_detail['dish_id']
                consume_time = dish.objects.get(dish_id = dish_id).time_cost*dish_detail['count']
                if dish.objects.get(dish_id = dish_id).dish_type in ['开胃冷菜', '酒水', '主食点心', '营养汤羹']:
                    dish_time_cold[dish_id] = consume_time
                else:
                    dish_time_hot[dish_id] = consume_time
            ## 选择其中用时最短的菜
            dish_insert_hot = dict()
            dish_insert_cold = dict()
            min_time_dish_cold = 0
            min_time_dish_hot = 0
            # 这一单存在冷菜
            if len(dish_time_cold) > 0:
                min_time_dish_cold = min(dish_time_cold, key = lambda k:dish_time_cold[k])
                dish_insert_cold = self.minimum_waiting_time_computation(dish_time_cold[min_time_dish_cold], 0)
            # 这一单存在热菜
            if len(dish_time_hot) > 0:    
                min_time_dish_hot = min(dish_time_hot, key = lambda k: dish_time_hot[k])
                # 看情况是否选择计算
                if np.random.rand() >= epsilon:
                   dish_insert_hot = self.minimum_waiting_time_computation(dish_time[min_time_dish_hot], 1)

            ## 找出其对应的count
            for dish_detail in order_dish:
                ## 最小时间的冷菜
                if dish_detail['dish_id'] == min_time_dish_cold:
                    current_allocation.append({"dish_id":min_time_dish_cold, "count":dish_detail['count'], 
                                                "station_id":dish_insert_cold["sid"], "waiting_list":dish_insert_cold["snum"]})
                ## 最小时间且计算过的热菜
                elif dish_detail['dish_id'] == min_time_dish_cold and len(dish_insert_hot) > 0:
                    current_allocation.append({"dish_id":min_time_dish_hot, "count":dish_detail['count'], 
                                                "station_id":dish_insert_hot["sid"], "waiting_list":dish_insert_hot["snum"]})
                else:
                    ## 其他菜随机分配位置
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
                    # 随机进入队列, 但需要保证在最小菜的位置之后
                        if alloc_id == dish_insert_cold["sid"]:
                            alloc_wl = np.random.randint(dish_insert_cold['snum'] + 1, len(self.station_info[alloc_id - 1]) + 2)
                        if len(dish_insert_hot) > 0 and alloc_id == dish_insert_hot["sid"]:
                            alloc_wl = np.random.randint(dish_insert_cold['snum'] + 1, len(self.station_info[alloc_id - 1]) + 2)
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
        ## 找到目前在排队的某个用时最短的菜，将其移到WL = 1的位置
            nudge_order_dishes = order_detail.objects.filter(order_id = current_id, waiting_list__gte = 1).update(dish_status = 1)
            
            sort_nudge_dishes = order_detail.objects.filter(order_id = current_id, waiting_list__gt = 1)
            ## 不需要催了
            if len(sort_nudge_dishes) == 0:
                pass
            ## 存在WL >= 2的情况，还是催一下吧
            else:
                consume_time = dict()
                for nudge_dish in sort_nudge_dishes:
                    consume_time[nudge_dish.dish_id] = dish.objects.get(dish_id = nudge_dish.dish_id).time_cost*nudge_dish.count
                min_dish_id = min(consume_time, key = lambda k:consume[k])
                ## 找到这道用时最短的菜
                nudge_dish = order_detail.objects.get(order_id = current_id, dish_id = min_dish_id)
                ## 更新这个工位之后其他菜的WL
                before_orders = order_detail.objects.filter(station_id = nudge_dish.station_id, waiting_list__gte = 1, waiting_list__lt = nudge_dish.waiting_list)
                nudge_dish.waiting_list = change_id
                nudge_dish.save()
                ## 更新这个工位之后其他的菜的WL, 将修改change_id及之后的菜WL滞后一位
                for before_order in before_orders:
                    before_order.waiting_list = before_order.waiting_list + 1
                    before_order.save()

        elif nudge_type == 2:
        ## 找到目前在排队的N个菜(N随机, default = 2, 1个时间短 + 1个随机挑的，可重), 将其移到WL = 1的位置
            nudge_order_dishes = order_detail.objects.filter(order_id = current_id, waiting_list__gte = 1).update(dish_status = 1)
            
            sort_nudge_dishes = order_detail.objects.filter(order_id = current_id, waiting_list__gt = 1)
            ## 不需要催了
            if len(sort_nudge_dishes) == 0:
                pass
            ## 存在WL >= 2的情况，还是催一下吧
            else:
                consume_time = dict()
                for nudge_dish in sort_nudge_dishes:
                    consume_time[nudge_dish.dish_id] = dish.objects.get(dish_id = nudge_dish.dish_id).time_cost*nudge_dish.count
                min_dish_id = min(consume_time, key = lambda k:consume[k])
                ## 找到这道用时最短的菜
                nudge_dish = order_detail.objects.get(order_id = current_id, dish_id = min_dish_id)
                ## 更新这个工位的WL
                before_orders = order_detail.objects.filter(station_id = nudge_dish.station_id, waiting_list__gte = 1, waiting_list__lt = nudge_dish.waiting_list)
                nudge_dish.waiting_list = change_id
                nudge_dish.save()
                ## 更新这个工位之后其他的菜的WL, 将修改change_id及之后的菜WL滞后一位
                for before_order in before_orders:
                    before_order.waiting_list = before_order.waiting_list + 1
                    before_order.save()
                ## 改了之后我们再把这一单WL >= 2的菜给找出来
                sort_nudge_dishes = order_detail.objects.filter(order_id = current_id, waiting_list__gt = 1)
                if len(sort_nudge_dishes) == 0:
                    pass
                else:
                    random_index = np.random.randint(0, len(sort_nudge_dishes))
                    ## 随机挑一个把它修改变成WL = 1
                    nudge_dish = sort_nudge_dishes[random_index] 
                    ## 更新这个工位的WL
                    before_orders = order_detail.objects.filter(station_id = nudge_dish.station_id, waiting_list__gte = 1, waiting_list__lt = nudge_dish.waiting_list)
                    nudge_dish.waiting_list = change_id
                    nudge_dish.save()
                    ## 更新这个工位之后其他的菜的WL, 将修改change_id及之后的菜WL滞后一位
                    for before_order in before_orders:
                        before_order.waiting_list = before_order.waiting_list + 1
                        before_order.save()
