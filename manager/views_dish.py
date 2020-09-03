from django.shortcuts import render
from manager.models import dish, dish_ingredient
from django import http
from django.views import View
import json, requests
from django.db.models import Max
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Sum, Count, Max, Min, Avg
import json, xmltodict

# Create your views here.
'''
获取所有菜 | GET | /dish
加某种菜 | POST | /dish
获取某个菜的详细信息 | GET | /dish/{pk}
修改某个菜的详细信息 | PUT | /dish/{pk}
删某种菜 | DELETE | /dish/{pk}
'''
# 向仓库发送请求添加原材料种类，触发在修改 / 添加菜的时候
def check_ingredient(ingredients):
    new_ingredient_name = [ig_detail["ingredient_name"] for ig_detail in ingredients]
    add_material = []
    current_ig_list = dish_ingredient.objects.all().values('ingredient_name')
    current_ig_name = [ig_item['ingredient_name'] for ig_item in current_ig_list]

    for new_ig_name in new_ingredient_name:
        if new_ig_name not in current_ig_name:
            add_material.append(new_ig_name) 
    if len(add_material)>0:
        url_add_material = 'http://127.0.0.1:8080/add_material'
        requests.post(url_add_material, {'add_material':add_material})


class dishView(View):
    
    def get(self, request):
        from manager.models import dish
        dishes = dish.objects.all()

        dish_list = []
        for dish in dishes:
            dish = {
                "dish_id":dish.dish_id,
                "name":dish.name,
                "time_cost":dish.time_cost,
                "dish_type":dish.dish_type,
                "price":dish.price,
                "success":dish.success,
            }
            dish_list.append(dish)
        dish_list = {'dishes':dish_list}
        return http.JsonResponse(dish_list, safe = False)

    #添加某类菜品
    @transaction.atomic
    def post(self, request):
        
        # 获取参数
        dict_data = json.loads(request.body, strict = False)
        print(dict_data)
        # 理论上没有dish_id,需要根据类别手动调整
        ## 获取所有的类
        all_dish_type = dish.objects.values("dish_type").distinct()
        all_type = [type_dict['dish_type'] for type_dict in all_dish_type]
        ## 类别判断
        new_type = dict_data.get('dish_type')
        if dict_data.get('dish_type') in all_type:
            ## 提取该类的最大编号
            max_id = dish.objects.filter(dish_type = new_type).aggregate(Max('dish_id'))['dish_id__max']
            dict_data['dish_id'] = max_id + 1

        else:
            ## 提取目前序号最大的类
            max_id = dish.objects.filter().aggregate(Max('dish_id'))['dish_id__max']
            print(max_id)
            dict_data['dish_id'] = (int(max_id/100) + 1)*100 + 1
        
        add_info = {'dish_id':dict_data['dish_id'], 'add_status':1}
        print('wtf1')
        ## 这一类菜品数量太多
        if dict_data['dish_id']%100 == 0:
            add_info['add_status'] = 0
            return http.JsonResponse(add_info)
        print('wtf2')
        name = dict_data.get('name')
        dish_pic = dict_data.get('dish_pic')
        time_cost = dict_data.get('time_cost')
        ingredients = dict_data.get('ingredients')
        print(ingredients)
        price = dict_data.get('price')
        
        ## 默认沽清状态，可能需要供应链剩余材料进行计算 [需要后续计算]
        ### 实际情况:向仓库发送GET material获取所有原材料，同时如果材料有新加的还需要重新向仓库发送一条POST add material.
        dict_data['success'] = 1
        ingd_cost = dict_data.get('ingd_cost')

        # 检验参数
        save_tag = transaction.savepoint()
        try:
        # 数据入库(入菜单库)
        ## 首先去除原材料的数据
            with transaction.atomic():
                del dict_data['ingredients']
                
                dish_info = dish.objects.create(**dict_data)
                print(dict_data['dish_id'])
                # 数据入库（入材料库）
                for ingredient_detail in ingredients:
                    #print(ingredient_detail)
                    name = ingredient_detail['ingredient_name']
                    #print(dict_data.get('dish_id'), name, ingredient_detail[name])
                    
                    new_dish_ingredient = dish_ingredient()
                    dish_info_new = dish.objects.get(dish_id = dict_data.get('dish_id'))
                    #print(dish_info_new)
                    new_dish_ingredient.dish_id = dish_info_new
                    new_dish_ingredient.ingredient_name = name
                    new_dish_ingredient.ingredient_number = ingredient_detail['ingredient_number']
                    #print('test')
                    if ingredient_detail['ingredient_number'] != 0:
                        new_dish_ingredient.save()
                # 入库完成，如果有新材料向供应链报告。
                check_ingredient(ingredients)

                
        except Exception as e:
            transaction.savepoint_rollback(save_tag)
            add_info['add_status'] = 0
        # 返回响应
        return http.JsonResponse(add_info)


class dishdetailView(View):
    def get(self, request, pk):
        from manager.models import dish, dish_ingredient
        
        try:
            dish = dish.objects.get(dish_id = pk)
            ingredient_list = dish_ingredient.objects.filter(dish_id_id = pk)
        except Exception as e:
            return http.HttpResponse(status = 404)
        ingredient = []
        for ig in ingredient_list:
            ig_dict = {
                "ingredient_name":ig.ingredient_name,
                "ingredient_number":ig.ingredient_number
            }
            ingredient.append(ig_dict)

        dish_dict = {
            "dish_id":dish.dish_id,
            "name":dish.name,
            "time_cost":dish.time_cost,
            "dish_pic":dish.dish_pic,
            "dish_type":dish.dish_type,
            "price":dish.price,
            "success":dish.success,
            "ingredients":ingredient,
        }
        print(dish_dict)
        # data = dicttoxml.dicttoxml(dish_dict, root = True, attr_type = False)
        # return http.HttpResponse(data)
        return http.JsonResponse(dish_dict)
    
    #修改某道菜的详细信息 --设置回滚
    @transaction.atomic
    def put(self, request, pk):
        edit_info = {
            "dish_id":pk,
            "edit_status":1}
        # 获取参数
        put = http.QueryDict(request.body)
        #将获取的QueryDict对象转换为str类型
        put_str = list(put.items())[0][0]
        put_dict = eval(put_str)
        dict_data = json.loads(request.body.decode())
        print(dict_data)
        
        # 校验参数
        ## 没有这道菜
        try:
            dish_info = dish.objects.get(dish_id = pk)
        except Exception:
            return http.HttpResponse(status = 404)

        ## 不满足修改约束
        try:
            with transaction.atomic():
        # 数据入库 
                ingredients = dict_data['ingredients']
                del dict_data['ingredients']
            
                dish.objects.filter(dish_id = pk).update(**dict_data)
                
                # 提取之前的菜的种类防止误删
                old_ingredient = dish_ingredient.objects.filter(dish_id = pk)
                for i in range(len(old_ingredient)):
                    dish_ingredient.objects.filter(dish_id = pk, ingredient_name = old_ingredient[i].ingredient_name).delete()
                
                for ingredient_detail in ingredients:
                    name = ingredient_detail['ingredient_name']
                    print(name)
                    new_dish_ingredient = dish_ingredient()
                    print(dict_data['dish_id'])
                    dish_info_new = dish.objects.get(dish_id = dict_data['dish_id'])
                    if ingredient_detail['ingredient_number'] != 0:
                        dish_ingredient.objects.create(dish_id = dish_info_new, ingredient_name = name, ingredient_number = ingredient_detail['ingredient_number'])
                ## 入库更新
                check_ingredient(ingredients)
        #没有修改成功，需要回滚
        except Exception:
            edit_info['edit_status'] = 0
            
        return http.JsonResponse(edit_info)

    def delete(self, request, pk):
        # 获取参数
        try:
            dish_info = dish.objects.get(dish_id = pk)
        except dish.DoesNotExist:
            delete_info = {
                "dish_id":pk,
                "delete_status":0}
            return http.JsonResponse(delete_info)

        # 删除信息
        dish_info.delete()
        # 返回响应
        delete_info = {
            "dish_id":pk,
            "delete_status":1
        }
        return http.JsonResponse(delete_info)

#对菜的具体信息进行模糊查询
def dish_search(request):
    from manager.models import dish, dish_ingredient
    dict_data = json.loads(request.body, strict = False)
    print(dict_data)
    select_dishid = []
    ## 搜寻到最终需要满足的要求
    select_dishes = dish.objects.all()
    for dict_key in dict_data.keys():
        if dict_data[dict_key] is not None:
            if dict_key == 'time_cost_ub':
                select_dishes = select_dishes.filter(time_cost__lte = dict_data[dict_key])
            elif dict_key == 'time_cost_lb':
                select_dishes = select_dishes.filter(time_cost__gte = dict_data[dict_key])
            elif dict_key == 'price_ub':
                #print(select_dishes)
                select_dishes = select_dishes.filter(price__lte = dict_data[dict_key])
                #print(select_dishes)
            elif dict_key == 'price_lb':
                select_dishes = select_dishes.filter(price__gte = dict_data[dict_key])
            ## 对原材料种类的模糊查询
            elif dict_key == 'ingredients':
                ## 返回满足条件的含有该种原材料的查询结果, 返回全部满足条件的dish_id
                select_dish_ig_list = dish_ingredient.objects.filter(ingredient_name__contains = dict_data[dict_key]).values('dish_id').distinct()
                select_dishid = [dish['dish_id'] for dish in select_dish_ig_list]
            else:
                # 其他种类的模糊查询
                if dict_key == 'name':
                    select_dishes = select_dishes.filter(name__contains = dict_data[dict_key])
                elif dict_key == 'dish_type':
                    select_dishes = select_dishes.filter(dish_type__contains = dict_data[dict_key])
                elif dict_key == 'success':
                    select_dishes = select_dishes.filter(success = dict_data[dict_key])
    query_dish = []
    
    # 和原材料的最终交的查询
    for select_dish in select_dishes:
        #在原材料的部分里
        #print(select_dish)
        if len(select_dishid) == 0 or select_dish.dish_id in select_dishid:
            dish = {
                "dish_id":select_dish.dish_id,
                "name":select_dish.name,
                "time_cost":select_dish.time_cost,
                "dish_type":select_dish.dish_type,
                "price":select_dish.price,
                "success":select_dish.success,
            }
            query_dish.append(dish)
    return http.JsonResponse({"dishes":query_dish})


class dishpriceView(View):
        
    def put(self, request, pk):
    # 修改某道菜的价格
        edit_info = {
        "dish_id":pk,
        "special_success":1
        }
        put = http.QueryDict(request.body)
        #将获取的QueryDict对象转换为str类型
        put_str = list(put.items())[0][0]
        put_dict = eval(put_str)
        print(put_dict)
        dish_price = put_dict.get('price')
        try:
            dish_info = dish.objects.filter(dish_id = pk)
        except Exception as e:
            return http.HttpResponse(status = 404)
        try:
            dish_info.update(price = dish_price)
        except Exception as e:
            edit_info["special_success"] = 0
            return http.JsonResponse(edit_info)
        return http.JsonResponse(edit_info)        

#分类查询
class dishtypeView(View):
    ## 初始的统计信息
    def get(self, request):
        from manager.models import dish, dish_ingredient
        dish_type_all = dish.objects.all().values('dish_type').distinct()
        dish_type_all = [dishtype['dish_type'] for dishtype in dish_type_all]
        dishes = []
        ## 加入各类菜的种类和个数信息
        for dishtype in dish_type_all:
            dish_dict = dict()
            dish_dict['dish_type'] = dishtype
            dish_dict['count'] = dish.objects.filter(dish_type = dishtype).aggregate(Count('dish_id'))['dish_id__count']
            dishes.append(dish_dict)
        print(dishes)
        return http.JsonResponse({"dishes":dishes})


    ## 点进去每一个的详细信息
    def post(self, request):
        from manager.models import dish, dish_ingredient
        dict_data = json.loads(request.body, strict = False)
        print(dict_data)
    #    all_dishes = dish.objects.filter(dish_type = dict_data['params']['query'])
        all_dishes = dish.objects.filter(dish_type = dict_data['dish_type'])
        dish_list = []
        for dish in all_dishes:
            dish = {
                "dish_id":dish.dish_id,
                "name":dish.name,
                "time_cost":dish.time_cost,
                "dish_type":dish.dish_type,
                "price":dish.price,
                "success":dish.success,
            }
            dish_list.append(dish)
        return http.JsonResponse({"dishes":dish_list}, safe = False)

def search_price(request):
    from manager.models import dish, dish_ingredient
    all_dishes = dish.objects.order_by('price')
    dish_list = []
    for dish in all_dishes:
        dish = {
            "dish_id":dish.dish_id,
            "name":dish.name,
            "time_cost":dish.time_cost,
            "dish_type":dish.dish_type,
            "price":dish.price,
            "success":dish.success,
        }
        dish_list.append(dish)
    return http.JsonResponse({"dishes":dish_list}, safe = False)
def search_time(request):
    from manager.models import dish, dish_ingredient
    all_dishes = dish.objects.order_by('time_cost')
    dish_list = []
    for dish in all_dishes:
        dish = {
            "dish_id":dish.dish_id,
            "name":dish.name,
            "time_cost":dish.time_cost,
            "dish_type":dish.dish_type,
            "price":dish.price,
            "success":dish.success,
        }
        dish_list.append(dish)
    return http.JsonResponse({"dishes":dish_list}, safe = False)
    
# 按条件查询界面
class dishsearchView(View):
    def post():
        pass