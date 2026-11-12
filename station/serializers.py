from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from station.models import(
    Station,
    Route,
    Journey,
    Order,
    Ticket,
)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("name", "latitude", "longitude")

