from http import client
import json
from django.conf import settings
from django.http import JsonResponse,HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from ecommerce import settings
from .models import *
from .forms import *
import razorpay
from django.core import serializers
# Create your views here.
def index(request):
    return render(request,'index.html')

def dashboard(request):
    user=request.user.username
    products=Items.objects.all()
    context={'user':user,'items':products}
    return render(request, 'dashboard.html',context)

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            return render(request, "index.html", {'message': 'Username already occupied'})
        else:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            login(request,user)
            return redirect('dashboard')
    else:
        return render(request, "index.html")



def submit(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user) 
            return redirect('dashboard')  
    return redirect('/')

@login_required
def log_out(request):
    logout(request)
    return redirect('/')

@login_required
def cart(request):
    context={}
    return render(request, "cart.html", {})

@login_required
def details(request,id):
    context={}
    context['item']=get_object_or_404(Items, id=id)
    return render (request,'productDetails.html',context)

def contact(request):
    if request.method=='POST':
        contact.name=request.POST['name']
        contact.message=request.POST['message']
        contact.email=request.POST['email']
        contact.phone=request.POST['number']
        try :
            contact.save()
            return render(request,'contact.html',{'message':'successfuly submitted'})
        except Exception as e:
            return render(request,'contact.html',{'message':e})
    return render(request,'contact.html')


def profile(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            user=request.user
            name=form.cleaned_data['name']
            mobile=form.cleaned_data['mobile']
            locality=form.cleaned_data['locality']
            city=form.cleaned_data['city']
            state=form.cleaned_data['state']
            reg=Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state)
            reg.save()
            return redirect('profile')

    form = CustomerForm()
    context={}
    context['cust']=Customer.objects.filter(user=request.user)
    first=context['cust'].first()
    context['first']=first
    context['form']=form
    return render(request,"profile.html",context)


def addCart(request):
    user = request.user
    cart = Cart()
    context={}
    id = request.GET.get("id")
    item = Items.objects.get(id=id)
    if Cart.objects.filter(user=user, item=item).exists():
        carts = Cart.objects.get(user=user, item=item)
        carts.quantity += 1
        carts.save()
        message = 'quantity increased'
    else:
        cart.user = user  
        cart.item = item  
        cart.quantity=1
        cart.save()
        message='Item added to Cart'
        context = {'message': message}
    return JsonResponse(context, safe=False)

    
def showCart(request):
    user=request.user
    carts=Cart.objects.filter(user=user)
    total=0
    for p in carts:
        total+=p.item.sell_price*p.quantity
    cust=Customer.objects.filter(user=user)
    return render(request,'cart.html',{'carts':carts,'total':total,'cust':cust})


def quantity(request):
    if request.method == 'GET':
        user = request.user
        qty = request.GET.get('qty')
        item_id = request.GET.get('id')
        
        try:
            item = Items.objects.get(id=item_id)
        except Items.DoesNotExist:
            return redirect('showCart')

        try:
            cart = Cart.objects.get(user=user, item=item)
            cart.quantity = qty
            cart.save()
        except Cart.DoesNotExist:
            return JsonResponse({"data":"data not found"})

    return redirect('showCart')

def remove(request):
    if request.method=='POST':
        user = request.user
        id = request.POST['id']
        item=Items.objects.get(id=id)
        try:
            cart=Cart.objects.get(user=user,item=item)
            if cart.quantity==1:
                cart.delete()
            else:
                quantity=cart.quantity
                quantity-=1
                cart.quantity=quantity
                cart.save()
        except Cart.DoesNotExist:
            pass
    
    return redirect('showCart')


def checkout(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    cust_id=request.GET.get('cus_id')
    
    total = sum([p.item.sell_price * p.quantity for p in cart])
    
    razorpayamt = total * 100

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    
    # Create an order in Razorpay
    data = {"amount": int(total * 100), "currency": "INR", "receipt": "order_rcptid_12"}
    response = client.order.create(data=data)

    order_id = response['id']
    order_status = response['status']

    if order_status == 'created':
        # Create a payment record
        payment = Payment(user=user, amount=total, razorpay_oid=order_id)
        payment.save()
    payment=Payment.objects.get(razorpay_oid=order_id)

    return render(request, 'checkout.html', {'total': razorpayamt,'customer':cust_id,'payment':payment})

def payment(request):
    oid = request.POST['razorpay_order_id']
    pid = request.POST['razorpay_payment_id']
    cid=request.POST['customer']

    user = request.user

    payment = Payment.objects.get(razorpay_oid=oid)

    if payment.paid == False:
        # Update the payment record with the payment details
        payment.razorpay_pid = pid
        payment.paid = True
        payment.save()

        cart = Cart.objects.filter(user=user)
        
        cust = Customer.objects.get(id=cid)
    
        for c in cart:
            Order.objects.create(user=user, item=c.item, customer=cust, quantity=c.quantity, payment=payment)
            c.delete()

        return redirect('order')
    
    return redirect('showCart')

def showlist(request):
    user=request.user
    wishlist=Wishlist.objects.filter(user=user)
    context={"carts":wishlist}
    return render(request,'wishlist.html',context)
def addwish(request):
    user = request.user

    if request.method == "GET":
        id=request.GET.get('id')
        item = get_object_or_404(Items, id=id)

        try:
            wish = Wishlist.objects.get(user=user, item=item)
            wish.delete()
            message = 'Item removed from wishlist'
        except Wishlist.DoesNotExist:
            Wishlist.objects.create(user=user, item=item)
            message = 'Item added to wishlist'

        context = {'message': message}
        return JsonResponse(context, safe=False)

    return JsonResponse({'message': 'Invalid request method'}, status=400)

def order(request):
    user=request.user
    carts=Order.objects.filter(user=user)
    print(carts)
    return  render(request,'order.html',{'carts':carts})

def seller(request):
    pass
 