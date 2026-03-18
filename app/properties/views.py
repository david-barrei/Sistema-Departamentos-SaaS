from django.shortcuts import render,redirect, get_object_or_404
from django.views.generic import TemplateView,CreateView
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib import messages

from .forms import BuildingForm, UnitForm
from .models import Building, Unit
from leases.models import Lease


@login_required(login_url="users:login")
def BuildingView(request):
    if request.method == "POST":
        form = BuildingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Edificio creado correctamente")
            return redirect("properties:building_list")
    else:
        form = BuildingForm()
    return render(request,"building.html",{'form':form})


def Building_list(request):
    """
    Vista que muestra todos los edificios en formato cards.

    Además calcula estadísticas por edificio:
    - total de unidades
    - unidades rentadas
    - unidades disponibles

    Usamos annotate() para que la base de datos haga los conteos
    y evitar hacer consultas dentro del template.
    """
    buildings = (Building.objects.annotate
                 (
                     #Cuenta todas las unidades relacionadas con el edificio
                     total_units=Count("units"),
                     #Cuenta unidades de status es rented
                     rented_units=Count("units",
                                        filter=Q(units__status="rented")),
                    #Cuenta unidades de status es availeble
                    available_units=Count("units",
                                          filter=Q(units__status="available"))

                 )
                 ).order_by("name") #Ordena los edificios por nombre


    # Recorremos los edificios para agregarles el porcentaje de ocupación
    for building in buildings:
        if building.total_units > 0:
            building.occupancy_percent = int(
                (building.rented_units / building.total_units) * 100
            )
        else:
            building.occupancy_percent = 0
    return render(request,"building_list.html", {"buildings": buildings})
    


@login_required(login_url="users:login")
def UnitView(request, building_id):
    building = get_object_or_404(Building, pk=building_id)
    if request.method == "POST":
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.building = building
            unit.save()
            messages.success(request,"Unidad creada correctamente")
            return redirect("properties:unit_list", building_id=building_id)
    else:
            form = UnitForm(initial={"building": building})
    return render(request, "unit.html", {'form': form})


def UnitlistView (request, building_id):
    building = get_object_or_404(Building, pk=building_id)
    units = Unit.objects.filter(building=building).order_by("floor","code")

    # Agregamos manualmente el lease activo a cada unidad
    for unit in units:
        unit.active_lease = unit.leases.filter(status=Lease.Status.ACTIVE).first()

    return render(request,"unit_list.html",{"building": building,"units":units})


@login_required(login_url="users:login")
def toggle_maintenance(request, unit_id):
    
    # Busca la unidad o devuelve 404
    unit = get_object_or_404(Unit, pk=unit_id)

    # Si está disponible → pasa a mantenimiento
    if unit.status == "available":
        unit.status = "maintenance"

    # Si está en mantenimiento → vuelve a disponible
    elif unit.status == "maintenance":
        unit.status = "available"
    
    if unit.status == "rented":
        messages.error(request, "No puedes poner en mantenimiento una unidad rentada")

    # Guarda el cambio
    unit.save()

    # Redirige nuevamente a la lista de unidades del edificio
    return redirect("properties:unit_list", building_id=unit.building.id)