
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import AccountLocked,UserList,HomeSinPrivilegio,user_save,UserGroup,user_groups_admin,user_groups_permissions,GroupPermissionAPIView

app_name = "users"

urlpatterns = [

    path('login/',auth_views.LoginView.as_view(template_name='users/login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='users/login.html'), name='logout'),
    path('account/',AccountLocked.as_view(), name='account'),
    path('users/list/',UserList.as_view(), name='user_list'),
    path('sin-privilegios/',HomeSinPrivilegio.as_view(), name='sin_privilegio'),
    path('users/add/',user_save, name='user_add'),
    path('users/modify/<int:id>',user_save, name='user_modify'),

    path('users/groups/list/',UserGroup.as_view(), name='groups_list'),
    path('users/groups/add/',user_groups_admin, name='groups_add'),
    path('users/groups/modify/<int:id>',user_groups_admin, name='groups_modify'),
    path('users/groups/<int:id_grp>/permissions/',user_groups_permissions, name='user_groups_permissions'),
    
    path('users/groups/<int:id>/permission',GroupPermissionAPIView.as_view(), name='groups_groups_permission_list'),
]


