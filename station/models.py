from django.core.exceptions import ValidationError
from django.db import models


class Station(models.Model):
    name = models.CharField(max_length=100)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station, on_delete=models.PROTECT, related_name="routes_from"
    )
    destination = models.ForeignKey(
        Station, on_delete=models.PROTECT, related_name="routes_to"
    )
    distance = models.PositiveIntegerField()

    @staticmethod
    def validate_source_not_equal_to_destination(
            source, destination, error_to_raise
    ):
        if source.id == destination.id:
            raise error_to_raise(
                {"destination": "Destination must be different from source."}
            )

    def clean(self):
        Route.validate_source_not_equal_to_destination(
            self.source, self.destination, ValidationError
        )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source.name} → {self.destination.name}"


class TrainType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=100, unique=True)
    cargo_num = models.PositiveIntegerField()
    places_in_cargo = models.PositiveIntegerField()
    train_type = models.ForeignKey(
        TrainType, on_delete=models.PROTECT, related_name="trains"
    )

    @property
    def capacity(self):
        return self.cargo_num * self.places_in_cargo

    def __str__(self):
        return self.name