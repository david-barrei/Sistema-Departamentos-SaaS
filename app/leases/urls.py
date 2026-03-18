from django.urls import path
from .views import LeaseView,TenantProfileView,LeaseDeatil,LeaseList,TenantListView,lease_end,TenantUpdateView,TenantDetailView,TenantDeleteView,LeaseUpdateView

app_name = "lease"


urlpatterns = [
    path("create/tenant", TenantProfileView, name="lease_tenant"),
    path("tenant/list", TenantListView, name="tenant_list"),
    path("tenant/<int:pk>/update", TenantUpdateView.as_view(), name="tenant_edit"),
    path("tenant/<int:pk>/detail", TenantDetailView.as_view(), name="tenant_detail"),
    path("tenant/<int:pk>/delete", TenantDeleteView.as_view(), name="tenant_delete"),
  


    path("create/<int:unit_id>/", LeaseView, name="lease_create"),
    path("lease/list", LeaseList, name="lease_list"),
    path("detail/<int:lease_id>/lease", LeaseDeatil, name="lease_detail"),
    path("lease/<int:lease_id>/end/",lease_end, name="lease_end"),
    path("tenant/<int:pk>/edit", LeaseUpdateView.as_view(), name="lease_edit"),
]



