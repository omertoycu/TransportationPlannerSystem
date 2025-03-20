from typing import List
import folium
from folium.plugins import MarkerCluster
from transport_data import Stop, NextStop, Transfer

class MapSystem:
    def __init__(self):
        self.stops = {}
        self.routes = []

    def add_stop(self, stop: Stop):
        self.stops[stop.id] = stop

    def add_route(self, start_stop_id: str, end_stop_id: str, distance: float, duration: int, cost: float):
        self.routes.append({
            "start": start_stop_id,
            "end": end_stop_id,
            "distance": distance,
            "duration": duration,
            "cost": cost
        })

class MapVisualizer:
    @staticmethod
    def visualize(map_system: MapSystem):
        # Haritanın merkezi kısım: Ayarlanacak konum
        map_center = [40.7638, 29.9406]
        transport_map = folium.Map(location=map_center, zoom_start=13)

        # Durakları ve aralarındaki bağlantıları ekle
        for stop_id, stop in map_system.stops.items():
            folium.Marker(
                location=[stop.lat, stop.lon],
                popup=f"{stop.name} (ID: {stop.id}, Tip: {stop.type})",
                icon=folium.Icon(color='blue' if stop.type == 'bus' else 'green')
            ).add_to(transport_map)

            # Her durak için sonraki durak bağlantısını çiz
            for next_stop in stop.nextStops:
                next_stop_obj = map_system.stops.get(next_stop.stopId)
                if next_stop_obj:
                    folium.PolyLine(
                        locations=[[stop.lat, stop.lon], [next_stop_obj.lat, next_stop_obj.lon]],
                        color='blue' if stop.type == 'bus' else 'green',
                        weight=2.5,
                        opacity=1
                    ).add_to(transport_map)

        # Oluşturulan harita, static klasörüne kaydedilir.
        transport_map.save("static/transport_map.html")
        print("Harita 'static/transport_map.html' dosyasına kaydedildi.")

class RouteFinder:
    @staticmethod
    def find_route(start_location, end_location, map_system: MapSystem):
        # Rota bulma algoritması burada geliştirilebilir.
        route = f"Rota {start_location.latitude}, {start_location.longitude} -> {end_location.latitude}, {end_location.longitude} arası hesaplanıyor..."
        return route