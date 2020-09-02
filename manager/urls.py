from django.conf.urls import url
from manager import views_dish, views_menu, views_kitchen, views_test, views_order_param

# dish + cook
urlpatterns = [
    # dish management
    url('api/dish$', views_dish.dishView.as_view()),
    url('api/dish/(?P<pk>\d+)', views_dish.dishdetailView.as_view()),
    url('api/dish/price/(?P<pk>\d+)', views_dish.dishpriceView.as_view()),
    url('api/dish/search$', views_dish.dish_search),
    url('api/dish/search_type', views_dish.dishtypeView.as_view()),
    url('api/dish/search_price', views_dish.search_price),
    url('api/dish/search_time', views_dish.search_time),
    # kitchen management
    url('api/kitchen$', views_kitchen.kitchenView.as_view()),
    url('api/kitchen/order$', views_kitchen.kitchendetailView.as_view()),
    url('api/kitchen/search', views_kitchen.search),
    url('api/kitchen/detail', views_kitchen.kitchendetail.as_view()),
    url('api/kitchen/dish', views_kitchen.KitchenDish.as_view()),
    url('api/kitchen/workstation', views_kitchen.KitchenWorkstation.as_view()),
    url('api/kitchen/finish', views_kitchen.KitchenFinish.as_view()),
    ## kitchen param management
    url('api/kitchen/order_type', views_order_param.order_type.as_view()),
    # with group 1 REQUEST
    url('dish$',views_menu.dish_menu.as_view()),
    url('dish_residue',views_menu.dish_menu_residue.as_view()),
    url('add_order', views_menu.add_order),
    url('add_takeout', views_menu.add_takeout),
    url('confirm_takeout', views_menu.confirm_takeout),
    url('nudge', views_menu.nudge),
    url('remove_order', views_menu.remove_order), 

    # self test with menu, supply chain and robots
    url('finish_dish', views_test.finish_order)
    
]