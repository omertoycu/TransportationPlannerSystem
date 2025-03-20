from abc import ABC, abstractmethod
from typing import List, Dict, Any
from distance_calculator import DistanceCalculator

class RouteStrategy(ABC):
    def __init__(self, distance_calculator: DistanceCalculator):
        self.distance_calculator = distance_calculator

    @abstractmethod
    def find_route(self, start_coord: Dict[str, float], end_coord: Dict[str, float], 
                  stops: List[Dict[str, Any]], passenger_type: str, payment_info: Dict[str, float]) -> Dict[str, Any]:
        pass

class BusOnlyStrategy(RouteStrategy):
    def find_route(self, start_coord: Dict[str, float], end_coord: Dict[str, float], 
                  stops: List[Dict[str, Any]], passenger_type: str, payment_info: Dict[str, float]) -> Dict[str, Any]:
        # Sadece otobüs rotası hesaplama mantığı
        pass

class TramOnlyStrategy(RouteStrategy):
    def find_route(self, start_coord: Dict[str, float], end_coord: Dict[str, float], 
                  stops: List[Dict[str, Any]], passenger_type: str, payment_info: Dict[str, float]) -> Dict[str, Any]:
        # Sadece tramvay rotası hesaplama mantığı
        pass

class MixedStrategy(RouteStrategy):
    def find_route(self, start_coord: Dict[str, float], end_coord: Dict[str, float], 
                  stops: List[Dict[str, Any]], passenger_type: str, payment_info: Dict[str, float]) -> Dict[str, Any]:
        # Karma rota hesaplama mantığı
        pass

class TaxiMixedStrategy(RouteStrategy):
    def find_route(self, start_coord: Dict[str, float], end_coord: Dict[str, float], 
                  stops: List[Dict[str, Any]], passenger_type: str, payment_info: Dict[str, float]) -> Dict[str, Any]:
        # Taksi ve toplu taşıma karma rotası hesaplama mantığı
        pass

class WalkingStrategy(RouteStrategy):
    def find_route(self, start_coord: Dict[str, float], end_coord: Dict[str, float], 
                  stops: List[Dict[str, Any]], passenger_type: str, payment_info: Dict[str, float]) -> Dict[str, Any]:
        # Yürüme rotası hesaplama mantığı
        pass

class RouteStrategyFactory:
    @staticmethod
    def create_strategy(strategy_type: str, distance_calculator: DistanceCalculator) -> RouteStrategy:
        strategies = {
            "bus_only": BusOnlyStrategy(distance_calculator),
            "tram_only": TramOnlyStrategy(distance_calculator),
            "mixed": MixedStrategy(distance_calculator),
            "taxi_mixed": TaxiMixedStrategy(distance_calculator),
            "walking": WalkingStrategy(distance_calculator)
        }
        return strategies.get(strategy_type, MixedStrategy(distance_calculator)) 