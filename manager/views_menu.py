from django.shortcuts import render
from manager.models import *
from django import http
from django.views import View
from django.core import serializers
from django.db.models import Sum, Count, Max, Min, Avg
import json, xmltodict, requests
import numpy as np
from pulp import *
from datetime import datetime
from manager.schedule_order import *
import manager.dicttoxml as dicttoxml
from manager.xml_to_dict import xml_to_dict

# 进行与前台计算的转化，同时在初始化的时候需要向供应链发送原材料请求
class dishingredient():
    def __init__(self, current_dishes):
        from manager.models import dish, dish_ingredient
        # 向仓库发送剩余所有原材料的请求
        ## 真实代码应该如下[未完]:
        
        supply_url = "http://127.0.0.1:8080/g4/material"
        r = requests.get(supply_url)
        all_material = xml_to_dict(r)['raw_material']
        # 转化为如下的测试样例的样子
        self.all_remain_ingredient = dict()
        for ig_detail in all_material:
            self.all_remain_ingredient[ig_detail['ingredient_name']] = float(ig_detail['ingredient_number']) 
        
        # 这只是一个测试样例
        # self.all_remain_ingredient = {'白条净膛鹅（克）': 300.0, '白萝卜（克）': 900.0, '茅台（瓶）': 1.0, '梭子蟹（克）': 250.0, '花蛤（克）': 1200.0, '扇贝（地播）（克）': 500.0, '白条湖鸭（克）': 700.0, '五花肉（瘦）（克）': 1750.0, '荔浦芋头（克）': 300.0, '鸡蛋（只）': 200.0, '胡萝卜（克）': 150.0, '绿菜花（克 ）': 900.0, '空心菜（克）': 300.0}
        self.remaining_ingredient = self.all_remain_ingredient.copy()
        self.current_dishes = current_dishes
        self.fail_dishes = []
        self.ingredient_all = dict()

    # 菜和原材料的转化
    def dish_to_ingredient(self):
        
        for dish_detail in self.current_dishes:
            dish_id = dish_detail['dish_id']
            count = int(dish_detail['count'])
            ig_list = dish_ingredient.objects.filter(dish_id = dish_id).values('ingredient_name', 'ingredient_number')
            for ig_detail in ig_list:
                ig_name = ig_detail['ingredient_name']
                if ig_name in self.ingredient_all.keys():
                    self.ingredient_all[ig_name] += ig_detail['ingredient_number']*count
                else:
                    #print(ig_detail['ingredient_number'], count, type(ig_detail['ingredient_number']), type(count))
                    self.ingredient_all[ig_name] = ig_detail['ingredient_number']*count
        return self.ingredient_all

    # 仅考虑购物车的情况
    def left_current_ingredient(self):
        # 向供应链发出GET请求，获取所有剩余原材料
        # 这只是一个测试样例
        # all_remain_ingredient = {'白条净膛鹅（克）': 300.0, '白萝卜（克）': 900.0, '茅台（瓶）': 1.0, '梭子蟹（克）': 250.0, '花蛤（克）': 1200.0, '扇贝（地播）（克）': 500.0, '白条湖鸭（克）': 700.0, '五花肉（瘦）（克）': 1750.0, '荔浦芋头（克）': 300.0, '鸡蛋（只）': 200.0, '胡萝卜（克）': 150.0, '绿菜花（克 ）': 900.0, '空心菜（克）': 300.0}
        remaining_ingredient = self.all_remain_ingredient.copy()
        # 目前下单需要的dish
        current_dish_ingredient = self.dish_to_ingredient()
        # remain = all - dish
        for dish_ig in current_dish_ingredient.keys():
            dish_number = current_dish_ingredient[dish_ig]
            #print(type(dish_number))
            self.remaining_ingredient[dish_ig] -= dish_number

        dish_id_list = dish.objects.all().values('dish_id')
        dish_dict = []
        for dish_set in dish_id_list:
            ig_list = dish_ingredient.objects.filter(dish_id = dish_set['dish_id']).values('ingredient_name', 'ingredient_number')
            sold_out_status = 1
            success_status = 1
            # 为方便计算，之后需要对sold_out_status和success_status进行相反计算
            for ig_detail in ig_list:
                ig_name = ig_detail['ingredient_name']
                ## 如果某个原材料严格不足，则标记success 和sold_out_status均为失败.
                ### *******下面这个if后续需要删除，仅作为样例使用*****************
                if ig_name in self.all_remain_ingredient.keys():
                    success_status = max(min(success_status, int(self.all_remain_ingredient[ig_name]/ig_detail['ingredient_number'])), 0)
                    if success_status == 0:
                        sold_out_status = 0
                        break
                    sold_out_status = max(min(sold_out_status, int(self.remaining_ingredient[ig_name]/ig_detail['ingredient_number'])), 0)
                    
            # 更新售罄标志
            dish.objects.filter(dish_id = dish_set['dish_id']).update(success = 1 - success_status)
            # 发送给前台的标志
            dish_dict.append({'dish_id': dish_set['dish_id'], 'sold_out':1 - sold_out_status})
        return dish_dict

    # 若下单超过库存，后厨推荐删除哪些菜
    # minimize overall costs
    def fail_dish_selection(self, short_ingredient):
        print(self.current_dishes, short_ingredient)
        
        dish_id_list = [int(self.current_dishes[i]['dish_id']) for i in range(len(self.current_dishes))]
        dish_id_max = [int(self.current_dishes[i]['count']) for i in range(len(self.current_dishes))]
        dish_id_price = [dish.objects.get(dish_id = did).price for did in dish_id_list]

        # 使退菜的损失总价格最小
        model = LpProblem("min_remove_cost", LpMinimize)
        x = LpVariable.dicts('_', dish_id_list, lowBound = 0, cat = LpInteger)
        model += (lpSum([dish_id_price[i]*x[dish_id_list[i]] for i in range(len(dish_id_list))]))
        
        A = np.zeros((len(short_ingredient), len(dish_id_list)))
        short_ingredient_list = list(short_ingredient.keys())
        for j in range(len(short_ingredient_list)):
            ig_name = short_ingredient_list[j] 
            dish_ig = dish_ingredient.objects.filter(ingredient_name = ig_name).values('dish_id')
            dish_ig = [dish_ig[i]['dish_id'] for i in range(len(dish_ig))]
            #匹配上相应的消耗量
            for i in range(len(dish_id_list)):
                if dish_id_list[i] in dish_ig:
                    A[j][i] = dish_ingredient.objects.get(dish_id = dish_id_list[i], ingredient_name = ig_name).ingredient_number
            model += lpSum([A[j][i]*x[dish_id_list[i]] for i in range(len(dish_id_list))])>=short_ingredient[ig_name]      
        print(A)
        # 优化求解
        model.solve()
        self.fail_dishes = []
        count = 0
        
        for v in model.variables():
            ## 只给出fail_dishes的数据
            if v.varValue > 0:
                res_dict = dict()
                res_dict['dish_id'] = dish_id_list[count]
                res_dict['count'] = v.varValue        
                self.fail_dishes.append(res_dict)
            count += 1
        # print(res_dict)
        # self.fail_dishes = res_dict

        
    # 考虑下单的情况
    def left_order_ingredient(self):
        # 需要调算法返回是否成功以及计算缺少的部分
        # 目前下单需要的dish
        current_dish_ingredient = self.dish_to_ingredient()
        # remain = all - dish
        short_ingredient = dict()
        print(current_dish_ingredient, self.remaining_ingredient)
        for dish_ig in current_dish_ingredient.keys():
            dish_number = current_dish_ingredient[dish_ig]
            self.remaining_ingredient[dish_ig] -= dish_number
            if self.remaining_ingredient[dish_ig] < 0:
                short_ingredient[dish_ig] = -self.remaining_ingredient[dish_ig]
        ## 如果删减后存在某种材料小于0，需要计算哪些材料fail
        if len(short_ingredient) > 0:
            self.fail_dish_selection(short_ingredient)
        
        

class dish_menu(View):
    def get(self, request):
        from manager.models import dish
       
        dishes = dish.objects.all()
        dish_list = []
        for dish in dishes:
            dish = {
                "name":dish.name,
                "price":dish.price,
                "type":dish.dish_type,
                "id":dish.dish_id,
                "picture":dish.dish_pic
            }
            dish_list.append(dish)
        dish_json = {"dishes":dish_list}
        data = dicttoxml.dicttoxml(dish_json, root = True, attr_type = False)
        return http.HttpResponse(data)
        #print(data)
        return http.JsonResponse(dish_json)

class dish_menu_residue(View):
    def get(self, request):
        from manager.models import dish
        #获取用户现在得到的current_dishes, 并将XML解析为json
        dish_json = xml_to_dict(request)
        current_dishes = dish_json['current_dishes']
        current_ingredient = dishingredient(current_dishes)
        dish_json = {"dishes":current_ingredient.left_current_ingredient()}
        print(dish_json)
        data = dicttoxml.dicttoxml(dish_json, root = True, attr_type = False)
        return http.HttpResponse(data)
        return http.JsonResponse(dish_json)

# 堂食下单
def add_order(request): 
    # ************将XML解析为Json*******
    dict_data = xml_to_dict(request)
    order_dish = dict_data['dishes']
    print(order_dish)
    table_id = dict_data['table_id']
    serial_number = dict_data['serial']
    
    dish_json = {"table_id": table_id, "success":1, "fail_dishes":None, "serial":serial_number}
    
    order_ingredient = dishingredient(order_dish)
    
    order_ingredient.left_order_ingredient()
    print(order_ingredient.ingredient_all)
    # 下单成功, 向仓库发出库单
    if len(order_ingredient.fail_dishes) == 0:
        print('向仓库发出库单!')
        ## 发给供应链的格式转化
        max_id = all_order_log.objects.all().aggregate(Max('order_id'))['order_id__max']

        all_consumption = order_ingredient.ingredient_all
        all_consumption_list = []
        for item in all_consumption.keys():
            consumption = {"ingredient_name":item, "ingredient_number":all_consumption[item]}
            all_consumption_list.append(consumption)
        print(all_consumption_list)
        scm_order = {"order_id": max_id + 1, "order_type":0, "raw_material":all_consumption_list}
        scm_order = dicttoxml.dicttoxml(scm_order, root = True, attr_type = False)
        # 向仓库发送POST请求 confirm_order_scm
        url = 'http://127.0.0.1:8080/g4/confirm_order_scm'
        r = requests.post(url, scm_order)
        # 向自己的数据库添加数据
        ## 在all_order_log中插入该条下单记录
        all_order_log.objects.create(order_id = max_id + 1, order_type = 0, table_id = table_id, serial = serial_number, takeout = -1)
# *************传入参数为order_dish， 调用后台排程算法，返回waiting_list和station_id********
        KitchenUpdate = kitchen_update()
        KitchenUpdate.order_update(max_id + 1, order_dish)
    # 下单失败
    else:
        dish_json['success'] = 0
        dish_json['fail_dishes'] = order_ingredient.fail_dishes

    data = dicttoxml.dicttoxml(dish_json, root = True, attr_type = False)
    return http.HttpResponse(data)

# 外卖下单
def add_takeout(request): 
    # ************将XML解析为Json*******

    dict_data = xml_to_dict(request)
    order_dish = dict_data['dishes']
    takeout_id = dict_data['takeout_id']
    dish_json = {"takeout_id": takeout_id, "success":1, "fail_dishes":None}
    order_ingredient = dishingredient(order_dish)
    
    order_ingredient.left_order_ingredient()
    # 下单失败
    if len(order_ingredient.fail_dishes) > 0:
        dish_json['success'] = 0
        dish_json['fail_dishes'] = order_ingredient.fail_dishes
    
    else:
        print('外卖预出库!')
        # 外卖预出库
        ## 发给供应链的格式转化
        max_id = all_order_log.objects.all().aggregate(Max('order_id'))['order_id__max']
        all_consumption = order_ingredient.ingredient_all
        all_consumption_list = []
        for item in all_consumption.keys():
            consumption = {"ingredient_name":item, "ingredient_number":all_consumption[item]}
            all_consumption_list.append(consumption)
        print(all_consumption_list)
        scm_order = {"order_id": max_id + 1, "order_type":1, "raw_material":all_consumption_list}
        scm_order = dicttoxml.dicttoxml(scm_order, root = True, attr_type = False)
        # 向仓库发送POST请求 confirm_order_scm
        url = 'http://127.0.0.1:8080/confirm_order_scm'
        r = requests.post(url, scm_order)
        # 向自己的数据库添加数据
        ## 在all_order_log中插入该条下单记录
        all_order_log.objects.create(order_id = max_id + 1, table_id = -1, serial = -1, takeout = takeout_id)
    
    data = dicttoxml.dicttoxml(dish_json, root = True, attr_type = False)
    return http.HttpResponse(data)

# 外卖确认订单
def confirm_takeout(request):
    # ************将XML解析为Json*******

    dict_data = xml_to_dict(request)
    order_dish = dict_data['dishes']
    takeout_id = dict_data['takeout_id']
    print(order_dish, takeout_id)
    # takeout_ingredient = dishingredient(order_dish)
    # all_consumption = order_ingredient.ingredient_all
    # all_consumption_list = []
    # for item in all_consumption.keys():
    #     consumption = {"ingredient_name":item, "ingredient_number":all_consumption[item]}
    #     all_consumption_list.append(consumption)
    # #提取之前的all_order_log的外卖单号
    # order_id_pre = all_order_log.objects.get(takeout_id = takeout_id).order_id

    # # 更新向供应链发的订单
    # scm_takeout = {"order_id": order_id_pre, "action":dict_data['action'], "raw_material":all_consumption_list}
    # url = 'http://127.0.0.1:8080/confirm_takeout_scm'
    # r = requests.post(url, scm_takeout)
    
    # if dict_data['action'] == 0:
    #     print('外卖正式出库！')
    #     ## 添加到自己的订单细节数据集中
    # # *************传入参数为order_id, order_dish和对应下单选项， 调用后台排程算法，直接修改waiting_list和station_id********
    #     KitchenUpdate = kitchen_update()
    #     KitchenUpdate.order_update(order_id_pre, order_dish)
    # else:
    #     print('外卖预定的原材料释放！')    
    data = dicttoxml.dicttoxml({}, root = True, attr_type = False)
    return http.HttpResponse(data)

# 催单
def nudge(request):
    dict_data = xml_to_dict(request)
    nudge_table_id = dict_data['table_id']
    nudge_serial = dict_data['serial']
    
    nudge_order_id = all_order_log.objects.get(table_id = nudge_table_id, serial = nudge_serial).order_id
    # ## 已经催单，不需要再次调用了
    # for order_detail.objects.filter(order_id = 1)
    # if order_detail.objects.filter(order_id = 1).values('dish_status')[0]['dish_status'] == 1:
    #     print("您之前已经催单!")
    #     pass
    # else:
        # *************传入参数为order_id， 调用后台排程算法，直接修改waiting_list和station_id********
        # 向后厨更新数据库
    # KitchenUpdate = kitchen_update()
    # KitchenUpdate.nudge_update(nudge_order_id)
    print('后厨已接受您的催单!')
    data = dicttoxml.dicttoxml({}, root = True, attr_type = False)
    return http.HttpResponse(data)

# 退菜
def remove_order(request):
    dict_data = xml_to_dict(request)
    remove_table_id = dict_data['table_id']
    remove_serial = dict_data['serial']
    remove_dishes = dict_data['dishes']
    print(remove_dishes)
    
    # remove_order_id = all_order_log.objects.get(table_id = remove_table_id, serial = remove_serial).order_id
    
    # # 标注相应的退菜记录
    # for dish_detail in remove_dishes:
    #     current_order_dish = order_detail.objects.get(order_id = remove_order_id, dish_id = dish_detail['dish_id'])
    #     current_dish_status = current_order_dish.dish_status
        
    #     # 如果这份菜还没有开始做, 之后的菜提前
    #     if current_dish_status == 0 or 1:
    #         current_station = current_order_dish.station_id
    #         current_wl = current_order_dish.waiting_list
    #         # 将这道菜标为废弃
    #         current_order_dish.update(dish_status = 3, waiting_list = -1)
    #         # 将之后的菜提前WL一位
    #         later_orders = order_detail.objects.filter(station_id = current_station, waiting_list__gte = current_wl)
    #         for later_order in later_orders:
    #             later_order.waiting_list = later_order.waiting_list - 1

    #     # 如果这份菜开始做了
    #     elif current_dish_status == 4:
    #     #提取开始做的时间，计算目前已经完成的菜数
    #     # 需要修改到时候是用秒还是分钟!!!
    #         time_speed = order_choice_log.objects.all().last().param
    #         have_seconds = (datetime.now() - current_order_dish.finish_time).seconds/time_speed
    #         current_dish = dish.objects.get(dish_id = dish_detail['dish_id'])
    #         dish_time = current_dish.time_cost
    #         require_seconds = dish_time*(current_order_dish.count - dish_detail['count'])
    #         # 已经完全做完, 计算相应的已经花费的成本
    #         if require_seconds <= have_seconds:
    #             current_order_dish.update(dish_status = 3, waiting_list = -1, ingd_cost = have_seconds/dish_time*current_dish.ingd_cost)
    #             # 将之后的菜提前WL一位
    #             later_orders = order_detail.objects.filter(station_id = current_station, waiting_list__gte = current_wl)
    #             for later_order in later_orders:
    #                 later_order.waiting_list = later_order.waiting_list - 1
    #                 # 如果修改滞后的WL值为1
    #                 if later_order.waiting_list == 0:
    #                     later_order.dish_status = 4
    #                     later_order.start_time = datetime.now()
    #                 later_order.save()

    #         # 剩余的并没有完全做完
    #         elif require_seconds > have_seconds:
    #             # 更新剩余的原材料份数
    #             ## 这种情况不算废弃, 因为剩余的仍然需要处理
    #             current_order_dish.count = current_order_dish.count - dish_detail['count']
    #             current_order_dish.save()            

    #     elif current_dish_status == 3:
    #         print('已经删了哥哥！')
        
    #     elif current_dish_status == 2:
    #         print("已经做完送给你了, 退单想都别想！")
    data = dicttoxml.dicttoxml({}, root = True, attr_type = False)
    return http.HttpResponse(data)
    
