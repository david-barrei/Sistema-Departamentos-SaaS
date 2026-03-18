from django.urls import path, include
from .views import *

app_name = "bases"

urlpatterns = [
    path('',dashboardKPIs, name= "home"),

]

