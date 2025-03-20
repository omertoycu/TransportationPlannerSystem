from abc import ABC, abstractmethod
import math

class DistanceCalculator(ABC):
    @abstractmethod
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        pass

class HaversineCalculator(DistanceCalculator):
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine formülü ile iki nokta arasındaki mesafeyi hesaplar."""
        R = 6371  # Dünya'nın yarıçapı (km)
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

class EuclideanCalculator(DistanceCalculator):
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111  # Yaklaşık km cinsinden

class ManhattanCalculator(DistanceCalculator):
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        return (abs(lat2 - lat1) + abs(lon2 - lon1)) * 111  # Yaklaşık km cinsinden

class DistanceCalculatorFactory:
    @staticmethod
    def create_calculator(calculator_type: str) -> DistanceCalculator:
        calculators = {
            "haversine": HaversineCalculator(),
            "euclidean": EuclideanCalculator(),
            "manhattan": ManhattanCalculator()
        }
        return calculators.get(calculator_type, HaversineCalculator()) 