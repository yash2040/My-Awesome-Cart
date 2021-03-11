from django.shortcuts import render, redirect
from .models import Product,Contact,Orders,OrderUpdate
from django.contrib.auth.models import User
from math import ceil
from django.contrib import messages
from django.http import HttpResponse
from Paytm import checksum
from django.views.decorators.csrf import csrf_exempt

import json
Email="######"
MERCHANT_KEY = 'Q2xCvdEs7Q3PeQvw'
def index(request):
    print(request.user)
    if request.user.is_authenticated:
        pass
    else:
        return redirect("http://localhost:8000/loginuser")
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    thank=False
    if request.method=="POST":
        name=request.POST.get('name','')
        email=request.POST.get('email','')
        phone=request.POST.get('phone','')
        desc=request.POST.get('desc','')

        contact1=Contact(user_name=name,user_email=email,user_phn=phone,user_desc=desc)
        Contact.save(contact1)
        thank=True
        if len(name)==0 or len(email)==0 or len(phone)==0 or len(desc)==0:
            messages.error(request, "Please Fill Form Correctly")

        else:
            messages.success(request, "Thanks For Your Review")
    return render(request, 'shop/contact.html',{'thank': thank})

def tracker(request):
    global response
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order) > 0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates,order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')

    return render(request, 'shop/tracker.html')
def searchmatch(query,item):
    if query.lower() in item.desc.lower() or query.lower() in item.product_name.lower() or query.lower() in item.category.lower():
        return True
    return False
def search(request):
    query=request.GET.get('search')
    print(query)
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod=[item for item in prodtemp if searchmatch(query,item)]
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod)!=0:
            allProds.append([prod, range(1, nSlides), nSlides])
    if len(allProds)==0:
        messages.error(request, "Your Search did not match Our results")
    else:
        messages.success(request, "Matched Results")
    params = {'allProds': allProds}
    return render(request, 'shop/search.html', params)

def productView(request, myid):
    # Fetch the product using the id
    product = Product.objects.filter(id=myid)


    return render(request, 'shop/prodView.html', {'product':product[0]})

def checkout(request):
    thank1=False
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        amount=request.POST.get('amount','')
        print(amount)
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone','')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone,amount=amount)
        order.save()
        update=OrderUpdate(order_id=order.order_id,update_desc="Order Not Placed")
        update.save()
        # Request paytm to transfer the amount to your account after payment by user
        param_dict = {

            'MID': 'RDdJwq12425149429201',
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'shop/paytm.html', {'param_dict': param_dict})
    return render(request, 'shop/checkout.html')
@csrf_exempt
def handlerequest(request):
    form = request.POST
    response_dict = {}
    checksum1="#####"
    id=0
    for i in form.keys():
        print(i,form[i])
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum1 = form[i]
        if i == 'ORDERID':
            id = form[i]
    if checksum1=="#####" :
        return HttpResponse("404 Page NotFound")
    verify = checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum1)
    if verify:
        if response_dict['RESPCODE'] == '01':
            updates=OrderUpdate.objects.filter(order_id=id)
            for i in updates:
                i.update_desc="Order has been Placed"
                i.save()

            print('order successful')
        else:
            OrderUpdate.objects.filter(order_id=id).delete()
            Orders.objects.filter(order_id=id).delete()
            print('order was not successful because ' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})
