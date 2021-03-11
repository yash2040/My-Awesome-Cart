from django.shortcuts import render, redirect
from math import ceil
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.conf import settings as conf_settings
from shop.models import ExtendedUser 
def index(request):
    return render(request,'index.html')
def loginuser(request):
    if request.method=="POST":
        name=request.POST.get('username')
        password=request.POST.get('password')
        user = authenticate(username=name, password=password)
        if user is not None:
            login(request,user)
            response=redirect(conf_settings.BASE_URL_LOCAL+"/shop/")
            extendedUser=ExtendedUser.objects.filter(user=user)
            response.set_cookie('uuid',extendedUser[0].userUuid);
            return response
            # A backend authenticated the credentials
        else:
            messages.error(request,"Please Enter your details correctly")
            return render(request, 'loginuser.html')
            # No backend authenticated the credentials
    return render(request,'loginuser.html')
def signinuser(request):
    if request.method == "POST":
        uname = request.POST.get('username')
        password = request.POST.get('password')
        email=request.POST.get('email')
        lname = request.POST.get('lname')
        fname=request.POST.get('fname')
        checkUser = authenticate(username=uname, password=password)
        if checkUser is None:
            user = User.objects.create_user(uname, email, password)
            user.last_name = lname
            user.first_name=fname
            user.save()
            extendedUser=ExtendedUser.objects.create(user=user)
            extendedUser.save()
            messages.success(request,"Account Created Successfully.Please LogIn")
        else:
            messages.error(request,"Username Already taken.Please Choose different user name")
    return render(request, 'signinuser.html')
def logoutuser(request):
    logout(request)
    return render(request, 'index.html')