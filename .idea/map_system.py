from typing import List, Dict
import folium

class MapSystem:
    def __init__(self):
        self.stops = {}
        self.routes = []

    def add_stop(self, stop):
        self.stops[stop.id] = stop

    def add_route(self, start_stop_id, end_stop_id, distance, duration, cost):
        self.routes.append({
            "start": start_stop_id,
            "end": end_stop_id,
            "distance": distance,
            "duration": duration,
            "cost": cost
        })

class MapVisualizer:
    @staticmethod
    def visualize(map_system):
        # Harita görselleştirme kodu burada olacak
        map_center = [40.7638, 29.9406]  # Başlangıç noktası haritanın merkezi olarak ayarlanır
        transport_map = folium.Map(location=map_center, zoom_start=13)

        for stop_id, stop in map_system.stops.items():
            folium.Marker(
                location=[stop.lat, stop.lon],
                popup=f"{stop.name} (ID: {stop.id}, Tip: {stop.type})",
                icon=folium.Icon(color='blue' if stop.type == 'bus' else 'green')
            ).add_to(transport_map)

        for route in map_system.routes:
            start_stop = map_system.stops[route['start']]
            end_stop = map_system.stops[route['end']]
            folium.PolyLine(
                locations=[[start_stop.lat, start_stop.lon], [end_stop.lat, end_stop.lon]],
                color='blue' if start_stop.type == 'bus' else 'green',
                weight=2.5,
                opacity=1
            ).add_to(transport_map)

        transport_map.save("transport_map.html")
        print("Harita 'transport_map.html' dosyasına kaydedildi.")

class RouteFinder:
    @staticmethod
    def find_route(start_location, end_location, map_system):
        # Rota bulma algoritması burada olacak
        route = f"Rota {start_location.latitude}, {start_location.longitude} -> {end_location.latitude}, {end_location.longitude} arası hesaplanıyor..."
        return route
