from flask import Flask, render_template, request, jsonify
import json
from route_planner import plan_route, find_routes_by_type

app = Flask(__name__)

def load_data():
    with open("data.txt", "r", encoding="utf-8") as file:
        return json.load(file)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_stops", methods=["GET"])
def get_stops():
    # Her istek için veriyi yeniden yükle
    data = load_data()
    return jsonify(data["duraklar"])

@app.route("/process_coordinates", methods=["POST"])
def process_coordinates():
    try:
        # Her istek için veriyi yeniden yükle
        data = load_data()
        
        request_data = request.get_json()
        
        if not request_data or 'start' not in request_data or 'end' not in request_data:
            return jsonify({'error': 'Başlangıç ve bitiş koordinatları gerekli'}), 400
            
        start_coord = request_data['start']
        end_coord = request_data['end']
        passenger_type = request_data.get('passengerType', 'Genel')
        payment_info = request_data.get('paymentInfo', {})
        
        taxi_info = data["taxi"]  # Taksi bilgilerini data.txt'den al
        
        routes = find_routes_by_type(start_coord, end_coord, data["duraklar"], taxi_info, passenger_type, payment_info)
        
        # Her rota tipi için en iyi rotayı seç
        best_routes = []
        for route_type, route_list in routes.items():
            if route_list:
                if isinstance(route_list, list):
                    # En iyi rotayı ekle
                    route = route_list[0]
                    route['type'] = route_type
                    best_routes.append(route)
                else:
                    route_list['type'] = route_type
                    best_routes.append(route_list)
        
        return jsonify({
            'message': 'Rotalar hesaplandı!',
            'routes': best_routes
        })
        
    except Exception as e:
        print(f"Hata: {str(e)}")
        return jsonify({'error': 'Rota hesaplanırken bir hata oluştu'}), 500

if __name__ == "__main__":
    app.run(debug=True)