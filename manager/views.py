from django.shortcuts import render
from django.db.models import Q
from datetime import datetime
from manager.models import *
import requests
# Create your views here.
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.db.models import Sum, Count, Max, Min, Avg
import json
import manager.dicttoxml as dicttoxml
from manager.xml_to_dict import xml_to_dict
# 实例化调度器
scheduler = BackgroundScheduler()
# 调度器使用默认的DjangoJobStore()
scheduler.add_jobstore(DjangoJobStore(), 'default')

# 每隔一秒更新数据库
@register_job(scheduler, 'interval', seconds = 1)
def kitchen_work():
    # 具体要执行的代码
    print(datetime.now().strftime('%Y%m%d %H:%M:%S'), '更新对应的排班记录!')
    # try:
    current_dishes = order_detail.objects.filter(dish_status = 4)
    for current_dish in current_dishes:
        
        consume_time = dish.objects.get(dish_id = current_dish.dish_id).time_cost
        time_speed = order_choice_log.objects.all().last().param
        #print(int(current_dish.count)*consume_time)
        if int(current_dish.count)*consume_time <= ((datetime.now() - current_dish.start_time).total_seconds())/time_speed:
            print(current_dish.station_id, '有菜做完了!')
            # 修改相应的其他成本数据栏
            current_dish.dish_status = 2
            current_dish.ingd_cost = current_dish.count*dish.objects.get(dish_id = current_dish.dish_id).ingd_cost               
            current_dish.save()
            
            # 此时需要给各种端口发更新
            current_dish_log = all_order_log.objects.get(order_id = current_dish.order_id.pk)
            ## ***************给自己的前端发消息***************
            dish_finish_time = current_dish.finish_time.strftime('%Y%m%d %H:%M:%S')
            if current_dish_log.order_type == 0:
            ## 给机器人 (堂食，菜)
                url_robot = 'http://127.0.0.1:8080/g5/finish_dish'
                dish_name = dish.objects.get(dish_id = current_dish.dish_id).name
                robot_info = {"order_id":current_dish.order_id.pk, "table_id":current_dish_log.table_id, "name":dish_name, "dish_count":current_dish.count}
                robot_info = dicttoxml.dicttoxml(robot_info, root = True, attr_type = False)
                print('tosee why?')
                requests.post(url_robot, robot_info)
            ## 给前台（堂食, 菜）
                url_order = 'http://127.0.0.1:8080/g1/serve'
                table_info = {"table_id":current_dish_log.table_id, "deliver_time":dish_finish_time,"dishes":[{"dish_id":current_dish.dish_id, "count":current_dish.count}], "serial":current_dish_log.serial}
                table_info = dicttoxml.dicttoxml(table_info, root = True, attr_type = False)
                requests.post(url_order, table_info)
            
            dish_order_id = current_dish.order_id.pk
            ## 判断这一单的菜是否全做完, 是否有正在等候等情况的菜
            order_finish_sign = order_detail.objects.filter(Q(order_id = dish_order_id), Q(dish_status = 0)|Q(dish_status = 1)|Q(dish_status = 4)).exists() 
            ## 不存在任何正在等的菜
            ## 给财务 (单)
            if order_finish_sign == False:
                url_account = 'http://127.0.0.1:8080/g3/order_other_cost'
                order_total_cost = order_detail.objects.filter(order_id = dish_order_id).aggregate(Sum('ingd_cost'))['ingd_cost__sum']
                account_info = {"order_id":dish_order_id, "ingd_cost":order_total_cost, "finish_time":dish_finish_time}
                account_info = dicttoxml.dicttoxml(account_info, root = True, attr_type = False)
                requests.post(url_account, account_info)
                if current_dish_log.order_type == 1:
                ## 给前台（外卖, 单）
                    url_takeout = 'http://127.0.0.1:8080/g1/deliver_takeout'
                    takeout_id = all_order_log.objects.get(order_id = dish_order_id).takeout
                    takeout_info = {"order_id":dish_order_id, "deliver_time":dish_finish_time}
                    takeout_info = dicttoxml.dicttoxml(takeout_info, root = True, attr_type = False)
                    requests.post(url_takeout, takeout_info)
            # 将之后的菜提前WL一位
            later_orders = order_detail.objects.filter(station_id = current_dish.station_id, waiting_list__gte = 1)
            for later_order in later_orders:
                later_order_wl = later_order.waiting_list
                # 如果之前的WL值为1
                if later_order_wl == 1:
                    later_order.update(waiting_list = 0, dish_status = 4, start_time = datetime.now())
                else:
                    later_order.update(waiting_list = later_order_wl - 1)
    # except Exception:
    #     print('目前所有的菜都做完了!')

# 注册定时任务并开始
register_events(scheduler)
scheduler.start()
