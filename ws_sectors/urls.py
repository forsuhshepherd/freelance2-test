from django.urls import path
from .views import SectorListCreateView, SectorRetrieveUpdateView


urlpatterns = [
  path('api/v1/sectors', SectorListCreateView.as_view(), name='sector-list-create'),
  path('api/v1/sectors/<int:pk>', SectorRetrieveUpdateView.as_view(), name='sector-update')

]
