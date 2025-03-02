from transport_data import load_data, CityData
from transport_system import *

def main():
    # Veriyi yükle
    file_path = "data.txt"
    city_data = load_data(file_path)
    if city_data is None:
        print("Failed to load city data.")
        return

    start_location = Location(40.7638, 29.9406)
    end_location = Location(40.7760, 29.9495)
    passenger = StudentPassenger("Ali")

    taxi = Taxi("TX1", city_data.taxi['openingFee'], city_data.taxi['costPerKm'])
    transport_modes = [Bus("B1"), Tram("T1"), taxi]

    route = RouteCalculator.calculate_route(start_location, end_location, passenger, transport_modes)
    print(route)

if __name__ == "__main__":
    main()
