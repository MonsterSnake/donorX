import os
import razorpay
from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from .models import User,payment_master
import json
import datetime
import copy as cp
import io
import base64
import matplotlib.pyplot as plt

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
	auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

# Create your views here.

def register_view(request):
	if request.method == 'POST':
		try:
			if request.POST.get('email',''):
				email = request.POST.get('email','')
				password = request.POST.get('password','')

				if User.objects.filter(email=email):
					return JsonResponse({'status': 'fail', 'msg':'Email already registered'})
				
				username = email.split('@')[0]

				hashed_password = make_password(password)

				user_obj = User(username=username, email=email, password=hashed_password)
				user_obj.save()
				return JsonResponse({'status': 'success', 'msg':'User registered'})
			else:
				return JsonResponse({'status': 'fail', 'msg':'Invalid email'})
		except Exception as e:
			return JsonResponse({'status': 'fail', 'msg':str(e)})
	return render(request, 'register.html')


def login_view(request):
	if request.method == 'POST':
		try:
			user_obj = User.objects.get(email=request.POST.get('email'))
			if	user_obj.check_password(request.POST.get('password')): #,password=)
				login(request, user_obj)
				return redirect('home')
		except Exception as e:
			return render(request, 'login.html')
	return render(request, 'login.html')

@login_required(login_url='/')
def logout_view(request):
    logout(request)
    return redirect('')

@login_required(login_url='/')
def homepage(request):
	month_list = []
	amount_list = []
	data_list = payment_master.objects.filter(user_id=request.user,is_active=True)
	for d in data_list:
		if d.created_on.month == datetime.datetime.now().month:
			month_list.append(str(d.created_on.month) + "-" + str(d.created_on.year))
			amount_list.append(d.amount)
	
	plt.plot(month_list,amount_list,marker='o')
	plt.xlabel('Months')
	plt.ylabel('Amounts')
	plt.title('Monthly Donation Chart')
	buffer = io.BytesIO()
	plt.savefig(buffer,format='png')
	buffer.seek(0)
	plt.close()
	image_base64 = base64.b64encode(buffer.getvalue()).decode()
	buffer.close()
	return render(request, 'dashboard.html', context={'data':image_base64})

@login_required(login_url='/')
def transactions(request):
	payment_id = payment_master.objects.filter(user_id = request.user, is_active = True)
	# p_details = payment_details.objects.filter(payment_id=payment_id)

	t_data=[]

	for line in payment_id:
		t_dict = cp.deepcopy({})
		t_dict['amount'] = line.amount
		t_dict['requested_checksum'] = line.requested_checksum
		t_dict['responsed_checksum'] = line.responsed_checksum
		t_dict['created_on'] = line.created_on
		t_dict['status'] = "Succes" if line.responsed_checksum else "Pending"
		t_data.append(t_dict)

	return render(request, 'transactions.html', context={"data": t_data})

@login_required(login_url='/')
def prepare_razorpay_data(request):
	amount = 0
	if request.POST.get('donation_amount', ''):
		if str(request.POST.get('donation_amount', '')).replace(".", "").isnumeric():
			try:
				amount = float(request.POST.get('donation_amount', ''))
			except Exception as e:
				pass
		else:
			return JsonResponse({"status": "fail", "msg": "Invalid Amount"})
	else:
		return JsonResponse({"status": "fail", "msg": "Invalid Amount"})

	currency = 'INR'

	# Create a Razorpay Order
	razorpay_order = razorpay_client.order.create(dict(amount=amount,
													currency=currency,
													payment_capture='0'))

	# order id of newly created order.
	razorpay_order_id = razorpay_order['id']
	callback_url = 'post_payment'

	# we need to pass these details to frontend.
	context = {}
	context['razorpay_order_id'] = razorpay_order_id
	context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
	context['razorpay_amount'] = amount
	context['currency'] = currency
	context['callback_url'] = callback_url

	payment_id = payment_master()
	payment_id.user_id = request.user
	payment_id.created_on = datetime.datetime.now()
	payment_id.is_active = True
	payment_id.amount = amount
	payment_id.requested_checksum = json.dumps(context)
	payment_id.responsed_checksum = ""
	payment_id.save()

	context['razorpay_amount'] = amount * 10000
	context['payment_id'] = payment_id.pk
	os.environ['payment_id'] = str(payment_id.pk)

	return JsonResponse(context)


# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
@csrf_exempt
@login_required(login_url='/')
def post_payment(request):

	# only accept POST request.
	if request.method == "POST":
		try:
		
			# get the required parameters from post request.
			payment_id = request.POST.get('razorpay_payment_id', '')
			razorpay_order_id = request.POST.get('razorpay_order_id', '')
			signature = request.POST.get('razorpay_signature', '')
			params_dict = {
				'razorpay_order_id': razorpay_order_id,
				'razorpay_payment_id': payment_id,
				'razorpay_signature': signature
			}

			# verify the payment signature.
			result = razorpay_client.utility.verify_payment_signature(
				params_dict)
			if result is not None:
				# amount = 20000 # Rs. 200
				try:
					params_dict['result'] = result
					payment_id = payment_master.objects.get(id = int(os.environ.get('payment_id')))
					payment_id.responsed_checksum = json.dumps(params_dict)
					payment_id.save()
					os.environ['payment_id'] = ""
					return redirect('transactions')
				except:

					# if there is an error while capturing payment.
					return redirect('transactions')
			else:

				# if signature verification fails.
				return redirect('transactions')
		except:

			# if we don't find the required parameters in POST data
			return redirect('transactions')
	else:
	# if other than POST request is made.
		return redirect('transactions')
