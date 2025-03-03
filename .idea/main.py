import os
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer
from transport_data import load_data
from transport_system import Location, StudentPassenger, Bus, Tram, Taxi
from map_system import MapSystem, MapVisualizer, RouteFinder

def main():
    # Veriyi yükle
    file_path = "data.txt"
    city_data = load_data(file_path)
    if city_data is None:
        print("Failed to load city data.")
        return

    map_system = MapSystem()
    for stop in city_data.duraklar:
        map_system.add_stop(stop)
        for next_stop in stop.nextStops:
            map_system.add_route(stop.id, next_stop.stopId, next_stop.mesafe, next_stop.sure, next_stop.ucret)

    start_location = Location(40.7638, 29.9406)
    end_location = Location(40.7760, 29.9495)
    passenger = StudentPassenger("Ali")

    taxi = Taxi("TX1", city_data.taxi['openingFee'], city_data.taxi['costPerKm'])
    transport_modes = [Bus("B1"), Tram("T1"), taxi]

    route = RouteFinder.find_route(start_location, end_location, map_system)
    print(route)
    MapVisualizer.visualize(map_system)

    # Harita dosyasını sunmak için bir HTTP sunucusu başlat
    PORT = 8000
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)

    # Varsayılan web tarayıcısında harita dosyasını aç
    webbrowser.open(f"http://localhost:{PORT}/transport_map.html")

    # Sunucuyu başlat
    print(f"Sunucu {PORT} portunda çalışıyor...")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
