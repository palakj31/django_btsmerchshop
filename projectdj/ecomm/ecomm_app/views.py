from django.shortcuts import render, HttpResponse,redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from ecomm_app.models import product, Cart,Order
from django.db.models import Q
import random 
import razorpay
from django.core.mail import send_mail
# Create your views here.
def about(request):
    return render(request,'about.html')

def edit(request,rid):
    print("id to be edited: ",rid)
    return HttpResponse("id to be edited :"+rid)

def delete(request,rid):
    print("id to be deleted: ",rid)
    return HttpResponse("id to be deleted :"+rid)


class SimpleView(View):
    def get(self,request):
        return HttpResponse("Hello from simple view")

def hello(request):
    context={}
    context['greet']="Good Morning,we are learning DTL"
    context['x']=120
    context['y']=100
    context['l']=[10,20,33,40,50]
    context['products']=[
        {'id':1,'name':'Kim Namjoon','cat':'RM merch','price':2000},
        {'id':2,'name':'Kim Seokjin','cat':'Jin merch','price':500},
        {'id':3,'name':'Min Yoongi','cat':'Suga merch','price':1500},
        {'id':1,'name':'Jung Hoseok','cat':'Jhope merch','price':2000},
        {'id':2,'name':'Park Jimin','cat':'Jimin merch','price':500},
        {'id':3,'name':'Kim Taehyung','cat':'V merch','price':1500},
        {'id':3,'name':'Jeon Jungkook','cat':'JK merch','price':1500},
    ]
    return render(request,'hello.html',context)

def home(request):
    #userid=request.user.id
    #print("id of logged in user:",userid)
    #print("result is:",request.user.is_authenticated)
    context={}
    p=product.objects.filter(is_active=True)
    context['products']=p
    #print(p)
    return render(request,'index.html',context)

def product_details(request,pid):
    p=product.objects.filter(id=pid)
    context={}
    context['products']=p
    return render(request,'product_details.html',context)

def register(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        ucpass=request.POST['ucpass']
        context={}
        if uname=="" or upass=="" or ucpass=="":
            context['errmsg']="fields can not be empty"
            return render(request,'register.html',context) 
        elif upass != ucpass:
            context['errmsg']="password and confirm password didn't match"
            return render(request,'register.html',context) 
        else:
            try:
                u=User.objects.create(password=upass,username=uname,email=uname)
                u.set_password(upass)    #encrypted format
                u.save()
                context['success']="User created succesfully"
                return render(request,'register.html',context) 
                #return HttpResponse("Army User created succesfully!!")
            except Exception:
                context['errmsg']="User with same username already Exist!!"
                return render(request,'register.html',context) 
    else:
        return render(request,'register.html')

def user_login(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        context={}
        if uname=="" or upass=="":
            context['errmsg']="fields ca not be empty"
            return render(request,'login.html',context)
        else:
            u=authenticate(username=uname,password=upass)
            #print
            if u is not None:
                login(request,u)
                return redirect('/home')
            else:
                context['errmsg']="Invalid username & password"
                return render(request,'login.html',context)
            #return HttpResponse("in else part")
    else:
        return render(request,'login.html')

def user_logout(request):
    logout(request)
    return redirect('/home')

def catfilter(request,cv):
    q1=Q(is_active=True)
    q2=Q(cat=cv)
    p=product.objects.filter(q1 & q2) 
    context={}
    context['products']=p 
    return render(request,'index.html',context) 

def sort(request,sv):
    if sv == '0':
        col='price'
    else:
        col="-price"

    p=product.objects.filter(is_active=True).order_by(col)
    context={}
    context['products']=p 
    return render(request,'index.html',context) 

def range(request):
    min=request.GET['min']
    max=request.GET['max']
    #print(min)
    #print(max)
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=True)
    p=product.objects.filter(q1 & q2 & q3)
    context={}
    context['products']=p 
    return render(request,'index.html',context) 

def addtocart(request,pid):
    if request.user.is_authenticated:
        userid=request.user.id
        #print(pid)
        #print(userid)
        u=User.objects.filter(id=userid)
        print(u[0])
        p=product.objects.filter(id=pid)
        print(p[0])
        q1=Q(uid=u[0])
        q2=Q(pid=p[0])
        c=Cart.objects.filter(q1 & q2)
        n=len(c)
        context={}
        context['products']=p
        if n==1:
            context['msg']="Product Already Exist in CART !!"
        else:
            c=Cart.objects.create(uid=u[0],pid=p[0])
            c.save()
            context['success']="Product Added Successfully in the cart"
        return render(request,'product_details.html',context)
        #return HttpResponse("data is fetched")
    else:
        return redirect('/login')

def viewcart(request):
    if request.user.is_authenticated:
        userid=request.user.id
        c=Cart.objects.filter(uid=request.user.id)
        np=len(c)
        s=0
        for x in c:
            #print(x)
            #print(x.pid.price)
            s=s+x.pid.price * x.qty
        print(s)
        context={}
        context['products']=c
        context['total']=s
        context['n']=np
        return render(request,'cart.html',context)
    else:
        return redirect('/login')

def remove(request,cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')

def updateqty(request,qv,cid):
    c=Cart.objects.filter(id=cid)
    # print(c)
    # print(c[0])
    # print(c[0].qty)
    if qv == '1':
        t=c[0].qty + 1
        c.update(qty=t) 
    else:
        if c[0].qty >1:
            t=c[0].qty-1
            c.update(qty=1)
    #return HttpResponse("quantity")
    return redirect('/viewcart')

def placeorder(request):
    userid=request.user.id
    #print(userid)
    c=Cart.objects.filter(uid=userid)
    #print(c)
    oid=random.randrange(1000,9999)
    #print("order id:",oid)
    for x in c:
       o=Order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
       o.save()
       x.delete()
    orders=Order.objects.filter(uid=request.user.id)
    context={}
    context['products']=orders
    np=len(orders)
    s=0
    for x in orders:
        s=s + x.pid.price*x.qty
    context['total']=s
    context['n']=np
    #return HttpResponse("order place successfully")
    return render(request,'placeorder.html',context)

def makepayment(request):
    orders=Order.objects.filter(uid=request.user.id)
    s=0
    for x in orders:
        s=s+ x.pid.price*x.qty
        oid=x.order_id
    client = razorpay.Client(auth=("rzp_test_3vp7A0liURLi5m", "UhNaRWVDtSuSDInOjZKH9NaZ"))
    data = { "amount": s*100, "currency": "INR", "receipt": oid }
    payment = client.order.create(data=data)
    print(payment)
    context={}
    uname=request.user.username
    #print(uname)
    context['uname']=uname
    context['data']=payment
    return render(request,'pay.html',context)
    #return HttpResponse("in makepayment section")

def sendusermail(request,uname):
    #print(uname)
    msg="Order Details Are:"
    send_mail(
        "BTS MERCH SHOP - Order placed successfully",
        msg,
        "jasoriyapalak@gmail.com",
        [uname],
        fail_silently=False,
        )

    return HttpResponse("mail send successfully")