from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from station.models import (
    Station,
    TrainType,
    Crew,
    Train,
    Route,
    Journey,
    Order,
    Ticket,
)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "train_type",
            "capacity",
            "cargo_num",
            "places_in_cargo",
        )


class TrainListSerializer(serializers.ModelSerializer):
    train_type = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )

    class Meta:
        model = Train
        fields = ("id", "name", "train_type", "capacity")


class RouteSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(RouteSerializer, self).validate(attrs=attrs)
        Route.validate_source_not_equal_to_destination(
            attrs["source"], attrs["destination"], ValidationError
        )
        return data

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(read_only=True, slug_field="name")
    destination = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteDetailSerializer(serializers.ModelSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance",
        )


class TicketSeatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "cargo",
            "seat",
        )


class JourneySerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(JourneySerializer, self).validate(attrs=attrs)
        Journey.validate_departure_earlier_than_arrival_time(
            attrs["departure_time"], attrs["arrival_time"], ValidationError
        )
        return data

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crew",
        )


class JourneyListSerializer(serializers.ModelSerializer):
    train_name = serializers.CharField(source="train.name", read_only=True)
    route = serializers.StringRelatedField(read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = (
            "id",
            "train_name",
            "route",
            "arrival_time",
            "departure_time",
            "tickets_available",
        )


class JourneyDetailSerializer(serializers.ModelSerializer):
    route = RouteListSerializer(read_only=True)
    train = TrainListSerializer(read_only=True)
    crew = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )
    taken_places = TicketSeatsSerializer(
        source="tickets", read_only=True, many=True
    )

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "crew",
            "arrival_time",
            "departure_time",
            "taken_places",
        )
