import json
from typing import List, Dict, Optional

class Transfer:
    def __init__(self, transferStopId: str, transferSure: int, transferUcret: float):
        self.transferStopId = transferStopId
        self.transferSure = transferSure
        self.transferUcret = transferUcret

class NextStop:
    def __init__(self, stopId: str, mesafe: float, sure: int, ucret: float):
        self.stopId = stopId
        self.mesafe = mesafe
        self.sure = sure
        self.ucret = ucret

class Stop:
    def __init__(self, id: str, name: str, type: str, lat: float, lon: float, sonDurak: bool, nextStops: List[NextStop], transfer: Optional[Transfer]):
        self.id = id
        self.name = name
        self.type = type
        self.lat = lat
        self.lon = lon
        self.sonDurak = sonDurak
        self.nextStops = nextStops
        self.transfer = transfer

class CityData:
    def __init__(self, city: str, taxi: Dict[str, float], duraklar: List[Stop]):
        self.city = city
        self.taxi = taxi
        self.duraklar = duraklar

def load_data(file_path: str) -> Optional[CityData]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        duraklar = []
        for durak in data['duraklar']:
            nextStops = [NextStop(**next_stop) for next_stop in durak.get('nextStops', [])]
            transfer = Transfer(**durak['transfer']) if durak['transfer'] else None
            duraklar.append(Stop(id=durak['id'], name=durak['name'], type=durak['type'], lat=durak['lat'], lon=durak['lon'], sonDurak=durak['sonDurak'], nextStops=nextStops, transfer=transfer))

        return CityData(city=data['city'], taxi=data['taxi'], duraklar=duraklar)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
    return None
