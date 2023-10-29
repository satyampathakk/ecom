from django.db import models
from django.contrib.auth.models import User

# Create your models here.
cate= (('bike','bike'),('shoes','shoes'),('hello','hello'),)
states=(('up','up'),('bihar','bihar'),('mp','mp'),)
class Items(models.Model):
    title=models.CharField(max_length=100)
    sell_price=models.IntegerField()
    description=models.TextField()
    image=models.ImageField(upload_to='images/')
    category=models.CharField(choices=cate,max_length=100,default='')
    def __str__(self):
        return self.title
class Customer(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=300,default='')
    locality=models.CharField(max_length=300,default='')
    city=models.CharField(max_length=100,default='')
    mobile=models.IntegerField(default=0,)
    state=models.CharField(choices=states,max_length=100,default='')
    def __str__(self):
        return self.name
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    item=models.ForeignKey(Items,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)

    @property
    def total_cost(self):
        return self.item.sell_price * self.quantity

class Payment(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    amount=models.FloatField()
    razorpay_oid=models.CharField(max_length=100,blank=True)
    razorpay_pid=models.CharField(max_length=100,blank=True)
    paid=models.BooleanField(default=False)

class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
    item=models.ForeignKey(Items,on_delete=models.CASCADE)
    payment=models.ForeignKey(Payment,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    status = models.BooleanField(default=False)
    order_date=models.DateTimeField( auto_now_add=True)
    def total_cost(self):
        return self.item.sell_price * self.quantity
class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    item=models.ForeignKey(Items,on_delete=models.CASCADE)