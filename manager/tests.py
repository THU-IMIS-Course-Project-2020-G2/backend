from django.test import TestCase
import dicttoxml, xmltodict, json

# Create your tests here.
dish_json = {
    "name":"测试菜品",
    "dish_pic":"er",
    "time_cost":10,
    "ingredients":[{"ingredient_name":"大肉", "ingredient_number":5}, {"ingredient_name":"大肉2", "ingredient_number":6}],
    "dish_type":"测试",
    "price":30,
    "success":1,
    "ingd_cost":10
    }
data = xmltodict.unparse(dish_json)
print(data)
json_dict = xmltodict.parse(data)
json_str = json.loads(json_dict)
print(json_str)