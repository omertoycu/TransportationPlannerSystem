import math
import heapq
from typing import List, Dict, Any
from dataclasses import dataclass
from transport_system import Passenger, Vehicle, Payment, Location
from distance_calculator import DistanceCalculator, DistanceCalculatorFactory
from route_strategy import RouteStrategy, RouteStrategyFactory

@dataclass
class RouteStep:
    mode: str
    from_location: Location
    to_location: Location
    distance: float
    time: float
    cost: float
    info: str

@dataclass
class Route:
    steps: List[RouteStep]
    total_distance: float
    total_time: float
    total_cost: float
    stops: List[Dict[str, Any]]

class RoutePlanner:
    def __init__(self, distance_calculator_type: str = "haversine"):
        self.distance_calculator = DistanceCalculatorFactory.create_calculator(distance_calculator_type)

    def plan_route(self, start_coord: Dict[str, float], end_coord: Dict[str, float],
                  stops: List[Dict[str, Any]], passenger: Passenger,
                  payment_info: Dict[str, float], strategy_type: str = "mixed") -> Dict[str, List[Route]]:
        """
        Belirtilen başlangıç ve bitiş noktaları arasında farklı rota stratejileri kullanarak rotalar hesaplar.
        """
        strategy = RouteStrategyFactory.create_strategy(strategy_type, self.distance_calculator)
        return strategy.find_route(start_coord, end_coord, stops, passenger.passenger_type.value, payment_info)

    def find_nearest_stops(self, user_coord: Dict[str, float], stops: List[Dict[str, Any]], k: int = 3) -> List[Dict[str, Any]]:
        """
        Kullanıcının konumuna en yakın k adet durağı bulur.
        """
        distances = []
        for stop in stops:
            dist = self.distance_calculator.calculate_distance(
                user_coord["lat"], user_coord["lng"],
                stop["lat"], stop["lon"]
            )
            distances.append({
                **stop,
                "distance": dist
            })
        
        distances.sort(key=lambda x: x["distance"])
        return distances[:k]

    def calculate_fare(self, distance: float, vehicle: Vehicle, passenger: Passenger,
                      is_transfer: bool = False, total_journey_distance: float = None) -> float:
        """
        Toplu taşıma ücretini hesaplar.
        """
        base_cost = vehicle.calculate_cost(distance, passenger)
        
        if is_transfer:
            if distance <= 2.0:
                transfer_bonus = -2.0
            elif distance <= 5.0:
                transfer_bonus = -1.0
            else:
                transfer_bonus = 0
                base_cost *= 0.5

            if total_journey_distance and total_journey_distance > 10.0:
                transfer_bonus -= 1.0
        else:
            transfer_bonus = 0
        
        total_fare = base_cost + transfer_bonus
        return max(round(total_fare, 2), -5.0)

    def create_route_step(self, mode: str, from_loc: Location, to_loc: Location,
                         vehicle: Vehicle, passenger: Passenger) -> RouteStep:
        """
        Bir rota adımı oluşturur.
        """
        distance = self.distance_calculator.calculate_distance(
            from_loc.latitude, from_loc.longitude,
            to_loc.latitude, to_loc.longitude
        )
        time = vehicle.calculate_time(distance)
        cost = self.calculate_fare(distance, vehicle, passenger)
        
        return RouteStep(
            mode=mode,
            from_location=from_loc,
            to_location=to_loc,
            distance=distance,
            time=time,
            cost=cost,
            info=f"{distance:.2f} km {mode} yolculuğu ({time:.1f} dakika)"
        )

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Dünya yarıçapı (km)
    
    # Koordinatları radyana çevir
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    
    # Haversine formülü
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    
    return distance

def find_nearest_stops(user_coord, stops, k=3):
    """
    Kullanıcının konumuna en yakın k adet durağı bulur.
    """
    distances = []
    for stop in stops:
        dist = haversine(user_coord["lat"], user_coord["lng"], stop["lat"], stop["lon"])
        distances.append({
            **stop,
            "distance": dist
        })
    
    # Mesafeye göre sırala ve en yakın k durağı döndür
    distances.sort(key=lambda x: x["distance"])
    return distances[:k]

def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formülü ile iki nokta arasındaki mesafeyi hesaplar."""
    R = 6371  # Dünya'nın yarıçapı (km)
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def find_nearest_stop(user_coord, stops):
    min_distance = float("inf")
    nearest = None
    
    for stop in stops:
        dist = haversine(user_coord["lat"], user_coord["lng"], stop["lat"], stop["lon"])
        
        if dist < min_distance:
            min_distance = dist
            nearest = stop
    
    return nearest, min_distance

def build_graph(stops):
    graph = {}
    # Normal duraklar arası bağlantıları ekle
    for stop in stops:
        graph[stop["id"]] = []
        # Direkt bağlantılar
        for edge in stop.get("nextStops", []):
            graph[stop["id"]].append({
                "target": edge["stopId"],
                "type": "direct",
                "cost": edge["ucret"],
                "time": edge["sure"],
                "distance": edge["mesafe"],
                "mode": stop["type"]
            })
        
        # Transfer bağlantıları
        if stop.get("transfer"):
            transfer = stop["transfer"]
            graph[stop["id"]].append({
                "target": transfer["transferStopId"],
                "type": "transfer",
                "cost": transfer["transferUcret"],
                "time": transfer["transferSure"],
                "distance": 0.1,  # Transfer için küçük bir mesafe ekle
                "mode": "transfer"
            })
    return graph

def dijkstra(graph, start_id, end_id):
    distances = {node: float('infinity') for node in graph}
    distances[start_id] = 0
    pq = [(0, start_id, [{"id": start_id, "type": "start"}])]
    visited = set()

    while pq:
        current_distance, current_node, path = heapq.heappop(pq)
        
        if current_node == end_id:
            return current_distance, path
            
        if current_node in visited:
            continue
            
        visited.add(current_node)
        
        for edge in graph[current_node]:
            neighbor = edge["target"]
            if neighbor not in visited:
                # Ağırlık hesaplamasını güncelle
                # Mesafe ve süreye daha fazla, ücrete daha az ağırlık ver
                weight = (edge["distance"] * 2) + (edge["time"] / 5) + (edge["cost"] / 2)
                
                # Transfer için ek maliyet
                if edge["type"] == "transfer":
                    weight += 1  # Transfer maliyetini artır
                
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    new_path = path + [{"id": neighbor, "type": edge["type"], "mode": edge["mode"]}]
                    heapq.heappush(pq, (distance, neighbor, new_path))
    
    return float('infinity'), []

def find_routes_by_type(start_coord, end_coord, stops, taxi_info, passenger_type="Genel", payment_info=None, taxi_threshold=3.0):
    """
    Farklı ulaşım tiplerinde rota alternatifleri hesaplar.
    """
    routes = {
        "bus_only": [],
        "tram_only": [],
        "mixed": [],
        "taxi_mixed": [],
        "taxi_only": [],
        "walking": []
    }

    # Ödeme bilgilerini kontrol et
    if payment_info is None:
        payment_info = {
            "cash": float('inf'),
            "creditCard": float('inf'),
            "kentkart": float('inf')
        }

    total_available_balance = payment_info.get("cash", 0) + payment_info.get("creditCard", 0)
    kentkart_balance = payment_info.get("kentkart", 0)

    # Direkt mesafeyi hesapla
    direct_distance = calculate_distance(start_coord["lat"], start_coord["lng"], end_coord["lat"], end_coord["lng"])

    def is_payment_viable(total_cost, requires_kentkart=True):
        """Ödeme yapılabilirliğini kontrol eder"""
        if requires_kentkart:
            # Toplu taşıma için KentKart gerekli
            return kentkart_balance >= total_cost
        else:
            # Taksi için nakit veya kredi kartı kullanılabilir
            return total_available_balance >= total_cost

    # 3 km'den kısa mesafeler için özel değerlendirme
    if direct_distance <= 3.0:
        # Yürüme seçeneği her zaman mevcut
        walking_time = calculate_walking_time(direct_distance)
        walking_route = {
            "steps": [{
                "mode": "Yürüme",
                "from": {"lat": start_coord["lat"], "lng": start_coord["lng"]},
                "to": {"lat": end_coord["lat"], "lng": end_coord["lng"]},
                "distance": direct_distance,
                "time": walking_time,
                "cost": 0,
                "info": f"{direct_distance:.2f} km yürüyüş ({walking_time} dakika)"
            }],
            "total_distance": direct_distance,
            "total_time": walking_time,
            "total_cost": 0,
            "stops": []
        }
        routes["walking"].append(walking_route)

        # Taksi seçeneği (ödeme kontrolü ile)
        taxi_time = calculate_taxi_time(direct_distance)
        taxi_cost = calculate_taxi_fare(direct_distance, taxi_info)
        if is_payment_viable(taxi_cost, requires_kentkart=False):
            taxi_route = {
                "steps": [{
                    "mode": "Taksi",
                    "from": {"lat": start_coord["lat"], "lng": start_coord["lng"]},
                    "to": {"lat": end_coord["lat"], "lng": end_coord["lng"]},
                    "distance": direct_distance,
                    "time": taxi_time,
                    "cost": taxi_cost,
                    "info": f"{direct_distance:.2f} km taksi yolculuğu ({taxi_time} dakika)"
                }],
                "total_distance": direct_distance,
                "total_time": taxi_time,
                "total_cost": taxi_cost,
                "stops": []
            }
            routes["taxi_only"].append(taxi_route)

        # Toplu taşıma seçenekleri (ödeme kontrolü ile)
        if kentkart_balance >= 7.0:  # Minimum toplu taşıma ücreti
            bus_stops = [s for s in stops if s["type"] == "bus"]
            tram_stops = [s for s in stops if s["type"] == "tram"]
            nearest_bus_starts = find_nearest_stops(start_coord, bus_stops, k=1)
            nearest_bus_ends = find_nearest_stops(end_coord, bus_stops, k=1)
            nearest_tram_starts = find_nearest_stops(start_coord, tram_stops, k=1)
            nearest_tram_ends = find_nearest_stops(end_coord, tram_stops, k=1)

            def is_transit_viable(start_stop, end_stop):
                total_walking = start_stop["distance"] + end_stop["distance"]
                if total_walking > direct_distance * 0.5 or start_stop["distance"] > 0.5 or end_stop["distance"] > 0.5:
                    return False
                return True

            # Otobüs rotası
            if nearest_bus_starts and nearest_bus_ends:
                start_stop = nearest_bus_starts[0]
                end_stop = nearest_bus_ends[0]
                if is_transit_viable(start_stop, end_stop):
                    route = create_bus_route(start_coord, end_coord, start_stop, end_stop, bus_stops, passenger_type)
                    if route and is_payment_viable(route["total_cost"]):
                        routes["bus_only"].append(route)

            # Tramvay rotası
            if nearest_tram_starts and nearest_tram_ends:
                start_stop = nearest_tram_starts[0]
                end_stop = nearest_tram_ends[0]
                if is_transit_viable(start_stop, end_stop):
                    route = create_tram_route(start_coord, end_coord, start_stop, end_stop, tram_stops, passenger_type)
                    if route and is_payment_viable(route["total_cost"]):
                        routes["tram_only"].append(route)

    else:
        # 3 km'den uzun mesafeler için rota hesaplama
        # Taksi seçeneği
        taxi_time = calculate_taxi_time(direct_distance)
        taxi_cost = calculate_taxi_fare(direct_distance, taxi_info)
        if is_payment_viable(taxi_cost, requires_kentkart=False):
            taxi_route = {
                "steps": [{
                    "mode": "Taksi",
                    "from": {"lat": start_coord["lat"], "lng": start_coord["lng"]},
                    "to": {"lat": end_coord["lat"], "lng": end_coord["lng"]},
                    "distance": direct_distance,
                    "time": taxi_time,
                    "cost": taxi_cost,
                    "info": f"{direct_distance:.2f} km taksi yolculuğu ({taxi_time} dakika)"
                }],
                "total_distance": direct_distance,
                "total_time": taxi_time,
                "total_cost": taxi_cost,
                "stops": []
            }
            routes["taxi_only"].append(taxi_route)

        # Toplu taşıma seçenekleri (ödeme kontrolü ile)
        if kentkart_balance >= 7.0:
            bus_stops = [s for s in stops if s["type"] == "bus"]
            tram_stops = [s for s in stops if s["type"] == "tram"]
            nearest_bus_starts = find_nearest_stops(start_coord, bus_stops, k=3)
            nearest_bus_ends = find_nearest_stops(end_coord, bus_stops, k=3)
            nearest_tram_starts = find_nearest_stops(start_coord, tram_stops, k=3)
            nearest_tram_ends = find_nearest_stops(end_coord, tram_stops, k=3)

            # Otobüs rotaları
            for start_stop in nearest_bus_starts:
                for end_stop in nearest_bus_ends:
                    if start_stop["distance"] <= taxi_threshold and end_stop["distance"] <= taxi_threshold:
                        route = create_bus_route(start_coord, end_coord, start_stop, end_stop, bus_stops, passenger_type)
                        if route and is_payment_viable(route["total_cost"]):
                            routes["bus_only"].append(route)

            # Tramvay rotaları
            for start_stop in nearest_tram_starts:
                for end_stop in nearest_tram_ends:
                    if start_stop["distance"] <= taxi_threshold and end_stop["distance"] <= taxi_threshold:
                        route = create_tram_route(start_coord, end_coord, start_stop, end_stop, tram_stops, passenger_type)
                        if route and is_payment_viable(route["total_cost"]):
                            routes["tram_only"].append(route)

            # Karma rotalar
            for bus_start in nearest_bus_starts:
                for tram_end in nearest_tram_ends:
                    if bus_start["distance"] <= taxi_threshold and tram_end["distance"] <= taxi_threshold:
                        route = create_mixed_route(start_coord, end_coord, bus_start, tram_end, stops, passenger_type)
                        if route and is_payment_viable(route["total_cost"]):
                            routes["mixed"].append(route)

            for tram_start in nearest_tram_starts:
                for bus_end in nearest_bus_ends:
                    if tram_start["distance"] <= taxi_threshold and bus_end["distance"] <= taxi_threshold:
                        route = create_mixed_route(start_coord, end_coord, tram_start, bus_end, stops, passenger_type)
                        if route and is_payment_viable(route["total_cost"]):
                            routes["mixed"].append(route)

            # Taksi + Toplu Taşıma kombinasyonları
            taxi_routes = create_taxi_mixed_routes(start_coord, end_coord, stops, taxi_info, passenger_type)
            if taxi_routes:
                viable_taxi_routes = []
                for route in taxi_routes:
                    # Taksi kısmı için nakit/kredi kartı, toplu taşıma kısmı için KentKart kontrolü
                    taxi_steps = [step for step in route["steps"] if step["mode"] == "Taksi"]
                    transit_steps = [step for step in route["steps"] if step["mode"] in ["Bus", "Tram"]]
                    
                    taxi_cost = sum(step["cost"] for step in taxi_steps)
                    transit_cost = sum(step["cost"] for step in transit_steps)
                    
                    if is_payment_viable(taxi_cost, requires_kentkart=False) and is_payment_viable(transit_cost):
                        viable_taxi_routes.append(route)
                
                if viable_taxi_routes:
                    routes["taxi_mixed"] = viable_taxi_routes

    # Her kategori için rotaları sırala
    for route_type in routes:
        if routes[route_type]:
            routes[route_type].sort(key=lambda x: (x["total_cost"], x["total_time"], x["total_distance"]))
            routes[route_type] = routes[route_type][:3]  # Her kategoride en iyi 3 rotayı tut

    return routes

def find_intermediate_stops(start_stop, end_stop, all_stops):
    """İki durak arasındaki ara durakları bulur"""
    intermediate_stops = []
    current = start_stop
    visited = set()

    while current and current['id'] != end_stop['id']:
        visited.add(current['id'])
        next_stop = None
        min_distance = float('inf')

        # Mevcut duraktan gidilebilecek tüm durakları kontrol et
        for next_possible in current.get('nextStops', []):
            if next_possible['stopId'] not in visited:
                # Hedef durağa olan mesafeyi hesapla
                for stop in all_stops:
                    if stop['id'] == next_possible['stopId']:
                        distance = calculate_distance(
                            stop['lat'], stop['lon'],
                            end_stop['lat'], end_stop['lon']
                        )
                        if distance < min_distance:
                            min_distance = distance
                            next_stop = stop
                            break

        if next_stop:
            intermediate_stops.append(next_stop)
            current = next_stop
        else:
            break

    return intermediate_stops

def create_bus_route(start, end, start_stop, end_stop, bus_stops, passenger_type):
    """Sadece otobüs kullanan rota oluşturur."""
    steps = []
    total_distance = 0
    total_time = 0
    total_cost = 0
    all_stops = [start_stop]  # Başlangıç durağını ekle

    # Başlangıç noktasından ilk durağa yürüyüş
    walk_distance = start_stop["distance"]
    walk_time = calculate_walking_time(walk_distance)
    steps.append({
        "mode": "Yürüme",
        "from": {"lat": start["lat"], "lng": start["lng"]},
        "to": {"lat": start_stop["lat"], "lng": start_stop["lon"]},
        "distance": walk_distance,
        "time": walk_time,
        "cost": 0,
        "info": f"{walk_distance:.2f} km yürüyüş ({walk_time} dakika)"
    })
    total_distance += walk_distance
    total_time += walk_time

    # Ara durakları bul
    intermediate_stops = find_intermediate_stops(start_stop, end_stop, bus_stops)
    all_stops.extend(intermediate_stops)  # Ara durakları ekle
    all_stops.append(end_stop)  # Bitiş durağını ekle

    # Otobüs yolculuğu (ara duraklarla birlikte)
    current_stop = start_stop
    for next_stop in intermediate_stops + [end_stop]:
        segment_distance = calculate_distance(
            current_stop["lat"], current_stop["lon"],
            next_stop["lat"], next_stop["lon"]
        )
        segment_time = calculate_bus_time(segment_distance)
        segment_cost = calculate_fare(segment_distance, "bus", passenger_type)

        steps.append({
            "mode": "Bus",
            "from": {"lat": current_stop["lat"], "lng": current_stop["lon"]},
            "to": {"lat": next_stop["lat"], "lng": next_stop["lon"]},
            "distance": segment_distance,
            "time": segment_time,
            "cost": segment_cost,
            "info": f"{segment_distance:.2f} km otobüs yolculuğu ({segment_time} dakika)"
        })
        total_distance += segment_distance
        total_time += segment_time
        total_cost += segment_cost
        current_stop = next_stop

    # Son duraktan varış noktasına yürüyüş
    walk_distance = end_stop["distance"]
    walk_time = calculate_walking_time(walk_distance)
    steps.append({
        "mode": "Yürüme",
        "from": {"lat": end_stop["lat"], "lng": end_stop["lon"]},
        "to": {"lat": end["lat"], "lng": end["lng"]},
        "distance": walk_distance,
        "time": walk_time,
        "cost": 0,
        "info": f"{walk_distance:.2f} km yürüyüş ({walk_time} dakika)"
    })
    total_distance += walk_distance
    total_time += walk_time

    return {
        "steps": steps,
        "total_distance": total_distance,
        "total_time": total_time,
        "total_cost": total_cost,
        "stops": all_stops  # Tüm durakları içerir
    }

def create_tram_route(start, end, start_stop, end_stop, tram_stops, passenger_type):
    """Sadece tramvay kullanan rota oluşturur."""
    steps = []
    total_distance = 0
    total_time = 0
    total_cost = 0
    all_stops = [start_stop]  # Başlangıç durağını ekle

    # Başlangıç noktasından ilk durağa yürüyüş
    walk_distance = start_stop["distance"]
    walk_time = calculate_walking_time(walk_distance)
    steps.append({
        "mode": "Yürüme",
        "from": {"lat": start["lat"], "lng": start["lng"]},
        "to": {"lat": start_stop["lat"], "lng": start_stop["lon"]},
        "distance": walk_distance,
        "time": walk_time,
        "cost": 0,
        "info": f"{walk_distance:.2f} km yürüyüş ({walk_time} dakika)"
    })
    total_distance += walk_distance
    total_time += walk_time

    # Ara durakları bul
    intermediate_stops = find_intermediate_stops(start_stop, end_stop, tram_stops)
    all_stops.extend(intermediate_stops)  # Ara durakları ekle
    all_stops.append(end_stop)  # Bitiş durağını ekle

    # Tramvay yolculuğu (ara duraklarla birlikte)
    current_stop = start_stop
    for next_stop in intermediate_stops + [end_stop]:
        segment_distance = calculate_distance(
            current_stop["lat"], current_stop["lon"],
            next_stop["lat"], next_stop["lon"]
        )
        segment_time = calculate_tram_time(segment_distance)
        segment_cost = calculate_fare(segment_distance, "tram", passenger_type)

        steps.append({
            "mode": "Tram",
            "from": {"lat": current_stop["lat"], "lng": current_stop["lon"]},
            "to": {"lat": next_stop["lat"], "lng": next_stop["lon"]},
            "distance": segment_distance,
            "time": segment_time,
            "cost": segment_cost,
            "info": f"{segment_distance:.2f} km tramvay yolculuğu ({segment_time} dakika)"
        })
        total_distance += segment_distance
        total_time += segment_time
        total_cost += segment_cost
        current_stop = next_stop

    # Son duraktan varış noktasına yürüyüş
    walk_distance = end_stop["distance"]
    walk_time = calculate_walking_time(walk_distance)
    steps.append({
        "mode": "Yürüme",
        "from": {"lat": end_stop["lat"], "lng": end_stop["lon"]},
        "to": {"lat": end["lat"], "lng": end["lng"]},
        "distance": walk_distance,
        "time": walk_time,
        "cost": 0,
        "info": f"{walk_distance:.2f} km yürüyüş ({walk_time} dakika)"
    })
    total_distance += walk_distance
    total_time += walk_time

    return {
        "steps": steps,
        "total_distance": total_distance,
        "total_time": total_time,
        "total_cost": total_cost,
        "stops": all_stops  # Tüm durakları içerir
    }

def create_mixed_route(start, end, start_stop, end_stop, stops, passenger_type):
    """Otobüs ve tramvay karması rota oluşturur."""
    steps = []
    total_distance = 0
    total_time = 0
    total_cost = 0

    # Başlangıç noktasından ilk durağa yürüyüş
    walk_distance = start_stop["distance"]
    walk_time = calculate_walking_time(walk_distance)
    steps.append({
        "mode": "Yürüme",
        "from": {"lat": start["lat"], "lng": start["lng"]},
        "to": {"lat": start_stop["lat"], "lng": start_stop["lon"]},
        "distance": walk_distance,
        "time": walk_time,
        "cost": 0,
        "info": f"{walk_distance:.2f} km yürüyüş ({walk_time} dakika)"
    })
    total_distance += walk_distance
    total_time += walk_time

    # İlk araç yolculuğu
    first_vehicle_distance = calculate_distance(
        start_stop["lat"], start_stop["lon"],
        end_stop["lat"], end_stop["lon"]
    )
    first_vehicle_type = start_stop["type"]
    first_vehicle_time = calculate_bus_time(first_vehicle_distance) if first_vehicle_type == "bus" else calculate_tram_time(first_vehicle_distance)
    first_vehicle_cost = calculate_fare(first_vehicle_distance, first_vehicle_type, passenger_type)
    
    steps.append({
        "mode": "Bus" if first_vehicle_type == "bus" else "Tram",
        "from": {"lat": start_stop["lat"], "lng": start_stop["lon"]},
        "to": {"lat": end_stop["lat"], "lng": end_stop["lon"]},
        "distance": first_vehicle_distance,
        "time": first_vehicle_time,
        "cost": first_vehicle_cost,
        "info": f"{first_vehicle_distance:.2f} km {first_vehicle_type} yolculuğu ({first_vehicle_time} dakika)"
    })
    total_distance += first_vehicle_distance
    total_time += first_vehicle_time
    total_cost += first_vehicle_cost

    # Aktarma yürüyüşü ve ikinci araç
    transfer_stops = find_transfer_stops(end_stop, stops, end)
    if transfer_stops:
        transfer_stop = transfer_stops[0]
        
        # Aktarma yürüyüşü
        transfer_distance = calculate_distance(
            end_stop["lat"], end_stop["lon"],
            transfer_stop["lat"], transfer_stop["lon"]
        )
        transfer_time = calculate_walking_time(transfer_distance)
        steps.append({
            "mode": "Aktarma",
            "from": {"lat": end_stop["lat"], "lng": end_stop["lon"]},
            "to": {"lat": transfer_stop["lat"], "lng": transfer_stop["lon"]},
            "distance": transfer_distance,
            "time": transfer_time,
            "cost": 0,
            "info": f"{transfer_distance:.2f} km aktarma yürüyüşü ({transfer_time} dakika)"
        })
        total_distance += transfer_distance
        total_time += transfer_time

        # İkinci araç yolculuğu
        second_vehicle_distance = calculate_distance(
            transfer_stop["lat"], transfer_stop["lon"],
            end_stop["lat"], end_stop["lon"]
        )
        second_vehicle_type = transfer_stop["type"]
        second_vehicle_time = calculate_bus_time(second_vehicle_distance) if second_vehicle_type == "bus" else calculate_tram_time(second_vehicle_distance)
        second_vehicle_cost = calculate_fare(second_vehicle_distance, second_vehicle_type, passenger_type, is_transfer=True)
        
        steps.append({
            "mode": "Bus" if second_vehicle_type == "bus" else "Tram",
            "from": {"lat": transfer_stop["lat"], "lng": transfer_stop["lon"]},
            "to": {"lat": end_stop["lat"], "lng": end_stop["lon"]},
            "distance": second_vehicle_distance,
            "time": second_vehicle_time,
            "cost": second_vehicle_cost,
            "info": f"{second_vehicle_distance:.2f} km {second_vehicle_type} yolculuğu ({second_vehicle_time} dakika)"
        })
        total_distance += second_vehicle_distance
        total_time += second_vehicle_time
        total_cost += second_vehicle_cost

    # Son duraktan varış noktasına yürüyüş
    walk_distance = end_stop["distance"]
    walk_time = calculate_walking_time(walk_distance)
    steps.append({
        "mode": "Yürüme",
        "from": {"lat": end_stop["lat"], "lng": end_stop["lon"]},
        "to": {"lat": end["lat"], "lng": end["lng"]},
        "distance": walk_distance,
        "time": walk_time,
        "cost": 0,
        "info": f"{walk_distance:.2f} km yürüyüş ({walk_time} dakika)"
    })
    total_distance += walk_distance
    total_time += walk_time

    return {
        "steps": steps,
        "total_distance": total_distance,
        "total_time": total_time,
        "total_cost": total_cost,
        "stops": [start_stop, end_stop]
    }

def create_taxi_mixed_routes(start, end, stops, taxi_info, passenger_type):
    """Taksi ve toplu taşıma karması rotalar oluşturur."""
    routes = []
    direct_distance = calculate_distance(start["lat"], start["lng"], end["lat"], end["lng"])

    # Tüm durakları mesafeye göre sırala
    all_stops = []
    for stop in stops:
        distance_to_start = calculate_distance(start["lat"], start["lng"], stop["lat"], stop["lon"])
        distance_to_end = calculate_distance(stop["lat"], stop["lon"], end["lat"], end["lng"])
        
        # Sadece toplam mesafenin %40'ından daha yakın durakları değerlendir
        if distance_to_start <= direct_distance * 0.4 or distance_to_end <= direct_distance * 0.4:
            all_stops.append({
                **stop,
                "distance_to_start": distance_to_start,
                "distance_to_end": distance_to_end
            })

    # Başlangıç noktasına yakın duraklar için
    start_stops = sorted(all_stops, key=lambda x: x["distance_to_start"])[:5]
    for stop in start_stops:
        # Taksi ile başlangıç
        route = create_taxi_to_transit_route(start, end, stop, stops, taxi_info, passenger_type, "start")
        if route:
            routes.append(route)

    # Bitiş noktasına yakın duraklar için
    end_stops = sorted(all_stops, key=lambda x: x["distance_to_end"])[:5]
    for stop in end_stops:
        # Taksi ile bitiş
        route = create_taxi_to_transit_route(start, end, stop, stops, taxi_info, passenger_type, "end")
        if route:
            routes.append(route)

    return routes

def create_taxi_to_transit_route(start, end, transit_stop, stops, taxi_info, passenger_type, taxi_position):
    """Taksi ve toplu taşıma kombinasyonu rota oluşturur."""
    steps = []
    total_distance = 0
    total_time = 0
    total_cost = 0
    route_stops = []

    if taxi_position == "start":
        # Taksi ile başlangıç
        taxi_distance = calculate_distance(start["lat"], start["lng"], transit_stop["lat"], transit_stop["lon"])
        taxi_time = calculate_taxi_time(taxi_distance)
        taxi_cost = calculate_taxi_fare(taxi_distance, taxi_info)
        
        steps.append({
            "mode": "Taksi",
            "from": {"lat": start["lat"], "lng": start["lng"]},
            "to": {"lat": transit_stop["lat"], "lng": transit_stop["lon"]},
            "distance": taxi_distance,
            "time": taxi_time,
            "cost": taxi_cost,
            "info": f"{taxi_distance:.2f} km taksi yolculuğu ({taxi_time} dakika)"
        })
        total_distance += taxi_distance
        total_time += taxi_time
        total_cost += taxi_cost
        route_stops.append(transit_stop)

        # Toplu taşıma ile devam
        transit_distance = calculate_distance(
            transit_stop["lat"], transit_stop["lon"],
            end["lat"], end["lng"]
        )
        transit_time = calculate_bus_time(transit_distance) if transit_stop["type"] == "bus" else calculate_tram_time(transit_distance)
        transit_cost = calculate_fare(transit_distance, transit_stop["type"], passenger_type)
        
        steps.append({
            "mode": "Bus" if transit_stop["type"] == "bus" else "Tram",
            "from": {"lat": transit_stop["lat"], "lng": transit_stop["lon"]},
            "to": {"lat": end["lat"], "lng": end["lng"]},
            "distance": transit_distance,
            "time": transit_time,
            "cost": transit_cost,
            "info": f"{transit_distance:.2f} km {transit_stop['type']} yolculuğu ({transit_time} dakika)"
        })
        total_distance += transit_distance
        total_time += transit_time
        total_cost += transit_cost

    else:
        # Toplu taşıma ile başlangıç
        transit_distance = calculate_distance(
            start["lat"], start["lng"],
            transit_stop["lat"], transit_stop["lon"]
        )
        transit_time = calculate_bus_time(transit_distance) if transit_stop["type"] == "bus" else calculate_tram_time(transit_distance)
        transit_cost = calculate_fare(transit_distance, transit_stop["type"], passenger_type)
        
        steps.append({
            "mode": "Bus" if transit_stop["type"] == "bus" else "Tram",
            "from": {"lat": start["lat"], "lng": start["lng"]},
            "to": {"lat": transit_stop["lat"], "lng": transit_stop["lon"]},
            "distance": transit_distance,
            "time": transit_time,
            "cost": transit_cost,
            "info": f"{transit_distance:.2f} km {transit_stop['type']} yolculuğu ({transit_time} dakika)"
        })
        total_distance += transit_distance
        total_time += transit_time
        total_cost += transit_cost
        route_stops.append(transit_stop)

        # Taksi ile bitiş
        taxi_distance = calculate_distance(transit_stop["lat"], transit_stop["lon"], end["lat"], end["lng"])
        taxi_time = calculate_taxi_time(taxi_distance)
        taxi_cost = calculate_taxi_fare(taxi_distance, taxi_info)
        
        steps.append({
            "mode": "Taksi",
            "from": {"lat": transit_stop["lat"], "lng": transit_stop["lon"]},
            "to": {"lat": end["lat"], "lng": end["lng"]},
            "distance": taxi_distance,
            "time": taxi_time,
            "cost": taxi_cost,
            "info": f"{taxi_distance:.2f} km taksi yolculuğu ({taxi_time} dakika)"
        })
        total_distance += taxi_distance
        total_time += taxi_time
        total_cost += taxi_cost

    return {
        "steps": steps,
        "total_distance": total_distance,
        "total_time": total_time,
        "total_cost": total_cost,
        "stops": route_stops
    }

def find_transfer_stops(current_stop, all_stops, destination):
    """En uygun aktarma duraklarını bulur."""
    other_type = "tram" if current_stop["type"] == "bus" else "bus"
    transfer_stops = []
    
    for stop in all_stops:
        if stop["type"] == other_type:
            distance = calculate_distance(
                current_stop["lat"], current_stop["lon"],
                stop["lat"], stop["lon"]
            )
            # 1 km'den yakın durakları aktarma için değerlendir
            if distance <= 1.0:
                # Hedef yönünde olan durakları tercih et
                direction_score = calculate_direction_score(current_stop, stop, destination)
                transfer_stops.append({
                    **stop,
                    "transfer_distance": distance,
                    "direction_score": direction_score
                })
    
    # Yön skoru ve mesafeye göre sırala
    transfer_stops.sort(key=lambda x: (x["direction_score"], x["transfer_distance"]))
    return transfer_stops[:3]  # En iyi 3 aktarma noktasını döndür

def calculate_direction_score(current_stop, transfer_stop, destination):
    """Aktarma durağının hedef yönünde olup olmadığını değerlendirir."""
    current_to_dest = calculate_distance(
        current_stop["lat"], current_stop["lon"],
        destination["lat"], destination["lng"]
    )
    transfer_to_dest = calculate_distance(
        transfer_stop["lat"], transfer_stop["lon"],
        destination["lat"], destination["lng"]
    )
    return transfer_to_dest / current_to_dest  # 1'den küçük değerler daha iyi

def calculate_walking_time(distance):
    """Yürüme süresini hesaplar (ortalama 5 km/saat hız)."""
    return int(distance * 12)  # 12 dakika/km

def calculate_bus_time(distance):
    """Otobüs yolculuk süresini hesaplar (ortalama 20 km/saat hız)."""
    return int(distance * 3)  # 3 dakika/km

def calculate_tram_time(distance):
    """Tramvay yolculuk süresini hesaplar (ortalama 25 km/saat hız)."""
    return int(distance * 2.4)  # 2.4 dakika/km

def calculate_taxi_time(distance):
    """Taksi yolculuk süresini hesaplar (ortalama 40 km/saat hız)."""
    return int(distance * 1.5)  # 1.5 dakika/km

def calculate_taxi_fare(distance, taxi_info):
    """Taksi ücretini hesaplar."""
    return taxi_info["openingFee"] + (distance * taxi_info["costPerKm"])

def plan_route(start_coord, end_coord, stops, taxi_info, passenger_type="Genel", payment_info=None, taxi_threshold=3.0):
    """Ana rota planlama fonksiyonu"""
    # Direkt mesafeyi hesapla
    direct_distance = haversine(start_coord["lat"], start_coord["lng"],
                              end_coord["lat"], end_coord["lng"])
    
    # Çok kısa mesafeler için direkt yürüme öner
    if direct_distance <= 1.0:  # 1 km'den kısa mesafeler
        return [{
            "mode": "Yürüme",
            "from": {"lat": start_coord["lat"], "lng": start_coord["lng"]},
            "to": {"lat": end_coord["lat"], "lng": end_coord["lng"]},
            "cost": 0,
            "time": int(direct_distance * 15),
            "info": f"Yürüme (mesafe: {direct_distance:.2f} km)"
        }], [[start_coord["lat"], start_coord["lng"]], 
             [end_coord["lat"], end_coord["lng"]]], []
    
    # Tüm rota alternatiflerini hesapla
    routes = find_routes_by_type(start_coord, end_coord, stops, taxi_info,
                               passenger_type, payment_info, taxi_threshold)
    
    # En uygun rotayı seç
    best_route = None
    best_score = float('infinity')
    
    # Rota değerlendirme fonksiyonu
    def evaluate_route(route):
        if not route:
            return float('infinity')
        
        # Maliyet, süre ve mesafe faktörlerini normalize et
        cost_weight = 0.4
        time_weight = 0.4
        distance_weight = 0.2
        
        normalized_cost = route["total_cost"] / 50  # Maksimum 50 TL baz alınarak
        normalized_time = route["total_time"] / 120  # Maksimum 120 dakika baz alınarak
        normalized_distance = route["total_distance"] / 20  # Maksimum 20 km baz alınarak
        
        return (normalized_cost * cost_weight +
                normalized_time * time_weight +
                normalized_distance * distance_weight)
    
    # Her rota tipini değerlendir
    for route_type, route in routes.items():
        if route:
            if isinstance(route, list):
                for r in route:
                    score = evaluate_route(r)
                    if score < best_score:
                        best_score = score
                        best_route = r
            else:
                score = evaluate_route(route)
                if score < best_score:
                    best_score = score
                    best_route = route
    
    if best_route:
        return best_route["steps"], best_route["polyline"], best_route["stops"]

def calculate_vehicle_time(distance, vehicle_type):
    """Araç süresini hesaplar."""
    if vehicle_type == "bus":
        return int(distance * 2)  # 30 km/saat
    elif vehicle_type == "tram":
        return int(distance * 1.5)  # 40 km/saat
    else:  # taxi
        return int(distance * 1.2)  # 50 km/saat

def calculate_fare(distance, vehicle_type, passenger_type, is_transfer=False):
    """Toplu taşıma ücretini hesaplar."""
    # Temel ücretler (TL)
    base_fares = {
        "bus": 7.0,
        "tram": 7.0,
        "taxi": 15.0  # Açılış ücreti
    }
    
    # Yolcu tipine göre indirim oranları
    discounts = {
        "Genel": 1.0,
        "Öğrenci": 0.5,
        "Öğretmen": 0.5,
        "Yaşlı": 0.5
    }
    
    # Araç tipine göre km başına ücret
    per_km_fares = {
        "bus": 2.0,
        "tram": 2.0,
        "taxi": 5.0
    }
    
    # Temel ücreti al
    base_fare = base_fares.get(vehicle_type, 7.0)
    
    # İndirim oranını al
    discount = discounts.get(passenger_type, 1.0)
    
    # Km başına ücreti al
    per_km = per_km_fares.get(vehicle_type, 2.0)
    
    # Mesafe ücretini hesapla
    distance_fare = distance * per_km
    
    # Toplam ücreti hesapla
    total_fare = (base_fare + distance_fare) * discount
    
    # Aktarma indirimi
    if is_transfer:
        if distance <= 2.0:
            total_fare -= 2.0  # 2 TL indirim
        elif distance <= 5.0:
            total_fare -= 1.0  # 1 TL indirim
    
    # Minimum ücret kontrolü
    if vehicle_type in ["bus", "tram"]:
        total_fare = max(total_fare, 7.0)  # Minimum 7 TL
    else:  # taxi
        total_fare = max(total_fare, 15.0)  # Minimum 15 TL
    
    return round(total_fare, 2)