from django.urls import path
from .views import Invoce_list,Payment_create,DepositCreateView,quick_payment
app_name = "billing"

urlpatterns = [

    path("invoice/list/",Invoce_list, name="invoice_list"),
    path("create/payment/<int:invoice_id>",Payment_create, name="payment"),
    #path("create/charge/",charge, name="charge"),
    path("deposit/create/<int:lease_id>/",DepositCreateView,name="deposit_create"),
    path('quick-payment/<int:invoice_id>/', quick_payment, name='quick_payment'),
    


]


