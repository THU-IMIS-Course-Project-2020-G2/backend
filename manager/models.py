from django.db import models

# Create your models here.
class managerInfo(models.Model):
    userid = models.TextField(verbose_name = '用户名')
    password = models.TextField(verbose_name = '密码')
    user_type = models.IntegerField(verbose_name = '用户类')

    class Meta:
        db_table = 'manager_info'
        verbose_name = '管理员'
    
    def __str__(self):
    #定义每个数据类对象的显示信息
        return self.userid
    
class dish(models.Model):
    dish_id = models.IntegerField(max_length = 5, primary_key = True, verbose_name = '菜品编号')
    name = models.TextField(max_length = 20, verbose_name = '菜品名称')
    dish_pic = models.TextField(verbose_name = '图片', blank = True)
    
    time_cost = models.IntegerField(verbose_name = '用时')
    dish_type = models.TextField(verbose_name = '种类')
    
    price = models.FloatField(verbose_name = '价格')
    success = models.IntegerField(verbose_name = '售空状态')
    ingd_cost = models.FloatField(verbose_name = '其他成本', default = 1)

    class Meta:
        db_table = 'dish'
        verbose_name = '菜'
        constraints = [
            models.CheckConstraint(check = models.Q(time_cost__gte = 0), name = 'time_constraint'),
            models.CheckConstraint(check = models.Q(ingd_cost__gte = 0), name = 'cost_constraint'),
            models.CheckConstraint(check = models.Q(price__gte = 0), name = 'price_constraint')
        ]

    def __str__(self):
        return self.name

class dish_ingredient(models.Model):
    
    dish_id = models.ForeignKey(dish, on_delete=models.CASCADE, verbose_name = '菜品编号')
    ingredient_name = models.TextField(max_length = 256, verbose_name = '原材料名称')
    ingredient_number = models.FloatField(verbose_name = '原材料数量')

    class Meta:
        db_table = 'dish_ingredient'
        verbose_name = '菜-原材料'
        
        #约束
        constraints = [
            models.CheckConstraint(check = models.Q(ingredient_number__gte = 0), name = 'ingredient_constraint')
        ]

class all_order_log(models.Model):
    order_id = models.BigAutoField(primary_key = True)
    order_type = models.IntegerField(verbose_name = '订单类别')
    table_id = models.IntegerField(verbose_name = '桌号')
    serial = models.BigIntegerField(verbose_name = '流水号')
    takeout = models.BigIntegerField(verbose_name = '外卖号')

    class Meta:
        db_table = 'all_order_log'
        verbose_name = '订单-基本信息'

    def __str__(self):
        return str(self.order_id)

class order_detail(models.Model):
    order_id = models.ForeignKey(all_order_log, on_delete = models.CASCADE)
    dish_id = models.IntegerField(max_length = 5, verbose_name = '菜品编号')
    count = models.IntegerField(verbose_name = '点菜数量')
    create_time = models.DateTimeField(verbose_name = '下单时间', auto_now_add = True)
    dish_status = models.IntegerField(verbose_name = '菜品状态')
    start_time = models.DateTimeField(verbose_name = '开始下单时间', null = True)
    finish_time = models.DateTimeField(verbose_name = '完成时间', auto_now = True)
    station_id = models.IntegerField(verbose_name = '分到的工位号')
    waiting_list = models.IntegerField(verbose_name = '等待队列号')
    ingd_cost = models.FloatField(default = 0, verbose_name = '其他成本')
    class Meta:
        unique_together = ("order_id", "dish_id")
        db_table = 'order_detail'
        constraints = [
            models.CheckConstraint(check = models.Q(ingd_cost__gte = 0), name = 'ingd_cost_constraint'),
            models.CheckConstraint(check = models.Q(count__gte = 0), name = 'order_num_constraint')
        ]
    def __str__(self):
        return str(self.order_id) + '_' + str(self.dish_id)

class order_choice_log(models.Model):
    choice_id = models.AutoField(primary_key = True)
    add_order_type = models.IntegerField(verbose_name = '加单算法选择', default = 0)
    nudge_order_type = models.IntegerField(verbose_name = '催单算法选择', default = 0)
    param = models.FloatField(verbose_name = '时间流逝关系', default = 1)
    create_time = models.DateTimeField(verbose_name = '使用算法的时间', auto_now = True)
