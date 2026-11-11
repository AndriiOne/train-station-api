from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings


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


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Journey(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.PROTECT, related_name="journeys"
    )
    train = models.ForeignKey(
        Train, on_delete=models.PROTECT, related_name="journeys"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="journeys")

    @staticmethod
    def validate_departure_earlier_than_arrival_time(
        departure_time, arrival_time, error_to_raise
    ):
        if departure_time >= arrival_time:
            raise error_to_raise(
                {
                    "arrival_time": (
                        "Departure time must be earlier than arrival time."
                    ),
                }
            )

    def clean(self):
        Journey.validate_departure_earlier_than_arrival_time(
            self.departure_time, self.arrival_time, ValidationError
        )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.route} ({self.departure_time})"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    cargo = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    journey = models.ForeignKey(
        Journey, on_delete=models.PROTECT, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    @staticmethod
    def validate_ticket(cargo, seat, train, error_to_raise):
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo, "cargo", "cargo_num"),
            (seat, "seat", "places_in_cargo"),
        ]:
            count_attrs = getattr(train, train_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {train_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.journey.train,
            ValidationError,
        )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.journey}: cargo: {self.cargo}, seat: {self.seat}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["journey", "seat", "cargo"],
                name="unique_ticket_journey_cargo_seat",
            )
        ]
        ordering = ["journey", "cargo", "seat"]
