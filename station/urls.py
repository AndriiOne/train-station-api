from django.urls import path, include
from rest_framework import routers

from station.views import (
    StationViewSet,
    TrainTypeViewSet,
    CrewViewSet,
    TrainViewSet,
)

router = routers.DefaultRouter()
router.register("stations", StationViewSet)
router.register("train_types", TrainTypeViewSet)
router.register("crews", CrewViewSet)
router.register("trains", TrainViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "station"
