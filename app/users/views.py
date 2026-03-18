from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import *
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required,permission_required
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated


from .models import CustomUser
from .forms  import UserForm
from .serealizers import *


class AccountLocked(TemplateView):

    template_name = "users/account_locked.html"


class SinPrivilegios(LoginRequiredMixin,PermissionRequiredMixin):
    login_url = 'users:login'
    raise_exception = False
    redirect_field_name = "redirect_to"
    context_object_name = "obj"

    def handle_no_permission(self):
        from django.contrib.auth.models import AnonymousUser
        if not self.request.user == AnonymousUser():
            self.login_url = 'users:sin_privilegio'
        return HttpResponseRedirect(reverse_lazy(self.login_url))
    
class HomeSinPrivilegio(LoginRequiredMixin,TemplateView):
    login_url = 'users_login'
    template_name= 'users/sin_privilegios.html'

class UserList(SinPrivilegios, ListView):
    template_name = "users/users_list.html"
    model = CustomUser
    context_object_name = "obj"
    login_url = 'users_login'
    permission_required = 'users.viewcustomuser'


@login_required(login_url="users:login")
@permission_required("users.change_customuser", login_url="users:sin_privilegios")
def user_save(request, id = None):
    template_name = "users/users_save.html"
    context = {}
    form = None   
    obj = None

    if request.method == "GET":
        if not id:
            form = UserForm(instance = None)

        else:
            obj =CustomUser.objects.filter(id=id).first()
            form = UserForm(instance=obj)

        context ["form"] = form 
        context ["obj"] = obj
    elif request.method == "POST":
        if not id:
            form = UserForm(request.POST)
        else:
            obj = CustomUser.objects.filter(id=id).first()
            form = UserForm(request.POST, instance = obj)
        
        if form.is_valid():
            obj = form.save(commit=False)
            obj.set_password(form.cleaned_data["password"])
            obj.save()
            messages.success(request, "Guardado satisfactoriamente")
            return redirect("users:user_list")

    return render(request, template_name, context)


class UserGroup(SinPrivilegios,ListView):
    template_name = "users/users_groups_list.html"
    login_url = "user:login"
    model = Group
    permission_required = "users.view_customuser"



@login_required(login_url="users:login")
@permission_required("users.change_customuser", login_url="users:sin_privilegios")
def user_groups_admin(request, id=None):
    template_name = "users/users_groups_admin.html"
    context = {}
    obj = Group.objects.filter(id=id).first()
    context["obj"] = obj
    permisos_grupo = {}

    if request.method == "GET":
        if obj:
            permisos_grupo = obj.permissions.all()
            permisos = Permission.objects.filter(~Q(group =obj))

            context["permisos_grupo"] = permisos_grupo
            context["permisos"] = permisos

    if request.method == "POST":
        name = request.POST.get("name")
        #validar que el grupo no exista
        grp_tmp = Group.objects.filter(name=name).first()
        if grp_tmp:
            if id!= grp_tmp.id:
                print("El grupo ya existe")
                messages.success(request, "Grupo ya existe, no se puede volver a crear")
                return redirect("users:groups_list")
            else:
                return redirect("users:groups_modify", id) 
        else:
            if id:
                grp = Group.objects.filter(id=id).first()
                grp.name = name
                grp.save()
            else:
                grp = Group(name=name)
                grp.save()
        
        id = grp.id
        return redirect("users:groups_modify",id)

    return render(request, template_name, context)


@login_required(login_url="users:login")
@permission_required("users.change_customuser", login_url="users:sin_privilegios")
def user_groups_permissions(request,id_grp):
    if request.method == "POST":
        id_perm = request.POST.get("id")
        accion =  request.POST.get("accion")

        grp = get_object_or_404(Group, id = id_grp)
        perm = get_object_or_404(Permission, id = id_perm)

        if accion == "ADD":
            grp.permissions.add(perm)
            message = "Permiso agregado"
        elif accion == "DEL":
            grp.permissions.remove(perm)
            message = "Permiso eliminado"
        else:
            return JsonResponse({"message": "Accion No Reconocida"}, status = 400)
        return JsonResponse({"message": message}, status = 200)
    else:
        return JsonResponse({"message": "Metodo No permitido"}, status = 405)



class GroupPermissionAPIView(generics.ListAPIView):
    """
    # API de grupo de permisos

    """
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    filter_fields = ['name','id']

    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        if group_id:
            group = Group.objects.filter(id=group_id).first()
            if group:
                return group.permissions.all()
            return []