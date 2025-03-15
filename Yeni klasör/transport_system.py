from abc import ABC, abstractmethod
from typing import List

class Location:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

class Passenger(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_discount(self) -> float:
        pass

class GeneralPassenger(Passenger):
    def get_discount(self) -> float:
        return 0.0

class StudentPassenger(Passenger):
    def get_discount(self) -> float:
        return 0.5

class ElderlyPassenger(Passenger):
    def get_discount(self) -> float:
        return 1.0

class Vehicle(ABC):
    def __init__(self, id: str, vehicle_type: str):
        self.id = id
        self.vehicle_type = vehicle_type

    @abstractmethod
    def calculate_cost(self, distance: float) -> float:
        pass

class Bus(Vehicle):
    def __init__(self, id: str):
        super().__init__(id, "Bus")

    def calculate_cost(self, distance: float) -> float:
        return distance * 1.5

class Tram(Vehicle):
    def __init__(self, id: str):
        super().__init__(id, "Tram")

    def calculate_cost(self, distance: float) -> float:
        return distance * 1.2

class Taxi(Vehicle):
    def __init__(self, id: str, opening_fee: float, cost_per_km: float):
        super().__init__(id, "Taxi")
        self.opening_fee = opening_fee
        self.cost_per_km = cost_per_km

    def calculate_cost(self, distance: float) -> float:
        return self.opening_fee + (distance * self.cost_per_km)

class Payment(ABC):
    @abstractmethod
    def pay(self, amount: float):
        pass

class CashPayment(Payment):
    def pay(self, amount: float):
        print(f"Paid {amount} using Cash")

class CreditCardPayment(Payment):
    def pay(self, amount: float):
        print(f"Paid {amount} using Credit Card")

class KentkartPayment(Payment):
    def pay(self, amount: float):
        print(f"Paid {amount} using Kentkart")

class RouteCalculator:
    @staticmethod
    def calculate_route(start_location: Location, end_location: Location, passenger: Passenger, transport_modes: List[Vehicle]):
        # Rota hesaplama algoritmasını buraya ekleyin.
        route = f"Route from ({start_location.latitude}, {start_location.longitude}) to ({end_location.latitude}, {end_location.longitude}) for passenger {passenger.name}"
        return route