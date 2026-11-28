from datetime import timedelta

from user.models import User
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from station.models import (
    Route,
    TrainType,
    Station,
    Train,
    Journey,
    Order,
    Ticket,
)


def sample_station(**params):
    defaults = {
        "name": "Kyiv",
        "latitude": 50.4405,
        "longitude": 30.489,
    }
    defaults.update(params)
    return Station.objects.create(**defaults)


def sample_route(**params):
    defaults = {
        "source": sample_station(),
        "destination": sample_station(
            name="Lviv",
            latitude=49.8394,
            longitude=23.9944,
        ),
        "distance": 540,
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_train_type(**params):
    defaults = {
        "name": "Cargo",
    }
    defaults.update(params)
    return TrainType.objects.create(**defaults)


def sample_train(**params):
    defaults = {
        "train_type": sample_train_type(),
        "name": "745",
        "cargo_num": 5,
        "places_in_cargo": 40,
    }
    defaults.update(params)
    return Train.objects.create(**defaults)


def sample_journey(**params):
    defaults = {
        "route": sample_route(),
        "train": sample_train(),
        "departure_time": timezone.now(),
        "arrival_time": timezone.now() + timedelta(hours=5),
    }
    defaults.update(params)
    return Journey.objects.create(**defaults)


class RouteTests(TestCase):
    def setUp(self):
        self.station = sample_station()

    def test_same_stations_error(self):
        with self.assertRaises(ValidationError):
            sample_route(source=self.station, destination=self.station)

    def test_different_stations_save(self):
        sample_route()
        self.assertEqual(Route.objects.count(), 1)


class JourneyTests(TestCase):
    def setUp(self):
        self.route = sample_route()
        self.train = sample_train()

    def test_arrival_earlier_departure_error(self):
        departure_time = timezone.now() + timedelta(hours=5)
        arrival_time = timezone.now()
        with self.assertRaises(ValidationError):
            Journey.objects.create(
                route=self.route,
                train=self.train,
                departure_time=departure_time,
                arrival_time=arrival_time,
            )

    def test_same_time_of_departure_and_arrive_error(self):
        departure_time = arrival_time = timezone.now()
        with self.assertRaises(ValidationError):
            Journey.objects.create(
                route=self.route,
                train=self.train,
                departure_time=departure_time,
                arrival_time=arrival_time,
            )

    def test_correct_data(self):
        departure_time = timezone.now()
        arrival_time = timezone.now() + timedelta(hours=5)
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=departure_time,
            arrival_time=arrival_time,
        )
        self.assertEqual(Journey.objects.count(), 1)


class TicketTests(TestCase):
    def setUp(self):
        self.journey = sample_journey()
        self.user = User.objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.order = Order.objects.create(
            user=self.user,
        )

    def test_cargo_is_0_error(self):
        with self.assertRaises(ValidationError):
            self.ticket = Ticket.objects.create(
                cargo=0,
                seat=1,
                journey=self.journey,
                order=self.order,
            )

    def test_cargo_bigger_cargo_num_error(self):
        with self.assertRaises(ValidationError):
            self.ticket = Ticket.objects.create(
                cargo=6,
                seat=1,
                journey=self.journey,
                order=self.order,
            )

    def test_seat_bigger_places_in_cargo_error(self):
        with self.assertRaises(ValidationError):
            self.ticket = Ticket.objects.create(
                cargo=1,
                seat=46,
                journey=self.journey,
                order=self.order,
            )

    def test_same_places_in_cargo_error(self):
        self.ticket = Ticket.objects.create(
            cargo=1,
            seat=1,
            journey=self.journey,
            order=self.order,
        )

        with self.assertRaises(ValidationError):
            self.ticket = Ticket.objects.create(
                cargo=1,
                seat=1,
                journey=self.journey,
                order=self.order,
            )

    def test_correct_data_ticket(self):
        self.ticket = Ticket.objects.create(
            cargo=1,
            seat=1,
            journey=self.journey,
            order=self.order,
        )
        self.assertEqual(Ticket.objects.count(), 1)
