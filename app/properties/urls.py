from django.urls import path
from .views import BuildingView,Building_list,UnitView,UnitlistView,toggle_maintenance

app_name = "properties"

urlpatterns = [

    path('building/create/',BuildingView, name= "building"),
    path('building/list',Building_list, name= "building_list"),
    path('building/<int:building_id>/unit/create',UnitView, name= "unit_create"),
    path('building/<int:building_id>/list',UnitlistView, name= "unit_list"),
    path("unit/<int:unit_id>/maintenance/",toggle_maintenance,name="unit_maintenance")

]


