from django.urls import path
from .views import SectorListCreateView, SectorRetrieveUpdateView


urlpatterns = [
  path('sectors', SectorListCreateView.as_view(), name='sector-list-create'),
  path('sectors/<int:pk>', SectorRetrieveUpdateView.as_view(), name='sector-update')

]
