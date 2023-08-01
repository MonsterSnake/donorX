from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('', login_view, name=''),
    path('register', register_view, name='register'),
    path('logout', logout_view, name='logout'),
    path('home', homepage, name='home'),
    path('transactions', transactions, name='transactions'),
    path('prepare_razorpay_data', prepare_razorpay_data, name='prepare_razorpay_data'),
	path('post_payment', post_payment, name='post_payment'),
]
