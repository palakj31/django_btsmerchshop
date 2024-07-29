from django.shortcuts import render,HttpResponse,redirect
from .models import Msg
# Create your views here.
def home(request):
    return HttpResponse("hello!! linked successfully")

def create(request):
    if request.method=='POST': 
        n=request.POST['uname']
        mail=request.POST['uemail']
        mob=request.POST['mobile']
        msg=request.POST['msg']
        # print(n)
        m=Msg.objects.create(name=n,email=mail,mobile=mob,msg=msg)
        m.save()
        #return HttpResponse("Data inserted successfully")
        return redirect('/dashboard')
    else:
        print("request is:",request.method)
        return render(request,'create.html')

def dashboard(request):
    m=Msg.objects.all()
    #print(m)
    context={}
    context['data']=m
    #return HttpResponse("Data fetched successfully")
    return render(request,'dashboard.html',context)

def delete(request,rid):
    #print("id of record to be deleted:",rid)
    m=Msg.objects.filter(id=rid)
    m.delete()
    return redirect('/dashboard')
    #return HttpResponse("id:"+rid)

def edit(request,rid):
    # print("id of record to be edited:",rid)
    if request.method=="POST":
        n=request.POST['uname']
        mail=request.POST['uemail']
        mob=request.POST['mobile']
        msg=request.POST['msg']
        #print(n)
        #print(mail)
        m=Msg.objects.filter(id=rid)
        m.update(name=n,email=mail,mobile=mob,msg=msg)
        return redirect('/dashboard')
        return HttpResponse("updated")
    else:
        #display form with old data
        m=Msg.objects.get(id=rid)
        context={}
        context['data']=m 
        return render(request,'edit.html',context)

    #return HttpResponse("id:"+rid)


