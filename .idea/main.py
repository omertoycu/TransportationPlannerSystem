from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

def load_data():
    with open("data.txt", "r", encoding="utf-8") as file:
        return json.load(file)

data = load_data()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_stops", methods=["GET"])
def get_stops():
    return jsonify(data["duraklar"])

@app.route("/process_coordinates", methods=["POST"])
def process_coordinates():
    coords = request.json
    print(f"Mevcut Konum: {coords['start']}, Hedef Konum: {coords['end']}")
    return jsonify({"message": "Koordinatlar alındı!"})

if __name__ == "__main__":
    app.run(debug=True)
