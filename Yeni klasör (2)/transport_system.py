from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class PassengerType(Enum):
    GENERAL = "Genel"
    STUDENT = "Ogrenci"
    TEACHER = "Ogretmen"
    ELDERLY = "65+"

class PaymentType(Enum):
    CASH = "cash"
    CREDIT_CARD = "creditCard"
    KENTKART = "kentkart"

@dataclass
class Location:
    latitude: float
    longitude: float

class Passenger(ABC):
    def __init__(self, name: str, passenger_type: PassengerType):
        self.name = name
        self.passenger_type = passenger_type

    @abstractmethod
    def get_discount(self) -> float:
        pass

class GeneralPassenger(Passenger):
    def __init__(self, name: str):
        super().__init__(name, PassengerType.GENERAL)

    def get_discount(self) -> float:
        return 0.0

class StudentPassenger(Passenger):
    def __init__(self, name: str):
        super().__init__(name, PassengerType.STUDENT)

    def get_discount(self) -> float:
        return 0.5

class TeacherPassenger(Passenger):
    def __init__(self, name: str):
        super().__init__(name, PassengerType.TEACHER)

    def get_discount(self) -> float:
        return 0.75

class ElderlyPassenger(Passenger):
    def __init__(self, name: str):
        super().__init__(name, PassengerType.ELDERLY)

    def get_discount(self) -> float:
        return 1.0

class Vehicle(ABC):
    def __init__(self, id: str, vehicle_type: str):
        self.id = id
        self.vehicle_type = vehicle_type

    @abstractmethod
    def calculate_cost(self, distance: float, passenger: Passenger) -> float:
        pass

    @abstractmethod
    def calculate_time(self, distance: float) -> float:
        pass

class Bus(Vehicle):
    def __init__(self, id: str):
        super().__init__(id, "Bus")

    def calculate_cost(self, distance: float, passenger: Passenger) -> float:
        base_cost = distance * 1.5
        return base_cost * (1 - passenger.get_discount())

    def calculate_time(self, distance: float) -> float:
        return distance * 2  # Ortalama 30 km/saat hız

class Tram(Vehicle):
    def __init__(self, id: str):
        super().__init__(id, "Tram")

    def calculate_cost(self, distance: float, passenger: Passenger) -> float:
        base_cost = distance * 1.2
        return base_cost * (1 - passenger.get_discount())

    def calculate_time(self, distance: float) -> float:
        return distance * 1.5  # Ortalama 40 km/saat hız

class Taxi(Vehicle):
    def __init__(self, id: str, opening_fee: float, cost_per_km: float):
        super().__init__(id, "Taxi")
        self.opening_fee = opening_fee
        self.cost_per_km = cost_per_km

    def calculate_cost(self, distance: float, passenger: Passenger) -> float:
        base_cost = self.opening_fee + (distance * self.cost_per_km)
        return base_cost * (1 - passenger.get_discount())

    def calculate_time(self, distance: float) -> float:
        return distance * 1.2  # Ortalama 50 km/saat hız

class Payment(ABC):
    def __init__(self, payment_type: PaymentType, balance: float):
        self.payment_type = payment_type
        self.balance = balance

    @abstractmethod
    def pay(self, amount: float) -> bool:
        pass

class CashPayment(Payment):
    def __init__(self, balance: float):
        super().__init__(PaymentType.CASH, balance)

    def pay(self, amount: float) -> bool:
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

class CreditCardPayment(Payment):
    def __init__(self, balance: float):
        super().__init__(PaymentType.CREDIT_CARD, balance)

    def pay(self, amount: float) -> bool:
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

class KentkartPayment(Payment):
    def __init__(self, balance: float):
        super().__init__(PaymentType.KENTKART, balance)

    def pay(self, amount: float) -> bool:
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

class PassengerFactory:
    @staticmethod
    def create_passenger(name: str, passenger_type: PassengerType) -> Passenger:
        passengers = {
            PassengerType.GENERAL: GeneralPassenger,
            PassengerType.STUDENT: StudentPassenger,
            PassengerType.TEACHER: TeacherPassenger,
            PassengerType.ELDERLY: ElderlyPassenger
        }
        return passengers[passenger_type](name)

class PaymentFactory:
    @staticmethod
    def create_payment(payment_type: PaymentType, balance: float) -> Payment:
        payments = {
            PaymentType.CASH: CashPayment,
            PaymentType.CREDIT_CARD: CreditCardPayment,
            PaymentType.KENTKART: KentkartPayment
        }
        return payments[payment_type](balance)

class RouteCalculator:
    @staticmethod
    def calculate_route(start_location: Location, end_location: Location, passenger: Passenger, transport_modes: List[Vehicle]):
        # Rota hesaplama algoritmasını buraya ekleyin.
        route = f"Route from ({start_location.latitude}, {start_location.longitude}) to ({end_location.latitude}, {end_location.longitude}) for passenger {passenger.name}"
        return route