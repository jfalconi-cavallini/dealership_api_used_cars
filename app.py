from flask import Flask, jsonify, request
from models import db, Car
from schemas import CarSchema
import used_scraper
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()
car_schema = CarSchema()
cars_schema = CarSchema(many=True)

@app.route('/health')
def health():
    return {"ok": True}, 200

@app.route('/cars', methods=['GET'])
def get_cars():
    cars = Car.query.all()
    return jsonify(cars_schema.dump(cars))

@app.route('/cars/<int:car_id>', methods=['GET'])
def get_car(car_id):
    car = Car.query.get_or_404(car_id)
    return jsonify(car_schema.dump(car))

@app.route('/cars', methods=['POST'])
def add_car():
    data = request.json
    new_car = Car(
        make=data['make'],
        model=data['model'],
        year=data['year'],
        price=data['price'],
        mileage=data.get('mileage', 0),
        status=data.get('status', 'available'),
        vin=data.get('vin'),
        image_url=data.get('image_url'),
        link=data.get('link'),
        exterior_color=data.get('exterior_color'),
        interior_color=data.get('interior_color')
    )
    db.session.add(new_car)
    db.session.commit()
    return jsonify(car_schema.dump(new_car)), 201


@app.route('/cars/<int:car_id>', methods=['PUT'])
def update_car(car_id):
    car = Car.query.get_or_404(car_id)
    data = request.json
    for field in data:
        setattr(car, field, data[field])
    db.session.commit()
    return jsonify(car_schema.dump(car))

@app.route('/cars/<int:car_id>', methods=['DELETE'])
def delete_car(car_id):
    car = Car.query.get_or_404(car_id)
    db.session.delete(car)
    db.session.commit()
    return jsonify({"message": "Car deleted"})

# -------------------- Safe DB Add -------------------- #
def safe_int(val, default=0):
    """Convert val to int, return default if conversion fails"""
    try:
        return int(val)
    except (TypeError, ValueError):
        return default

def add_cars_to_db(cars_list):
    """Add a list of car dicts to the database safely."""
    count_added = 0
    for car_data in cars_list:
        vin = car_data.get('vin')
        if vin:
            existing_car = Car.query.filter_by(vin=vin).first()
        else:
            existing_car = Car.query.filter_by(
                make=car_data.get('make', ''),
                model=car_data.get('model', ''),
                year=safe_int(car_data.get('year', 0))
            ).first()

        if existing_car:
            continue

        new_car = Car(
            make=car_data.get('make', ''),
            model=car_data.get('model', ''),
            year=safe_int(car_data.get('year', 0)),
            price=float(car_data.get('price', 0)),
            mileage=safe_int(car_data.get('mileage', 0)),
            status='available',
            vin=vin,
            image_url=car_data.get('image_url'),
            link=car_data.get('link'),
            exterior_color=car_data.get('exterior_color'),
            interior_color=car_data.get('interior_color')
        )


        db.session.add(new_car)
        count_added += 1

    db.session.commit()
    print(f"{count_added} cars added to the database.")
    return count_added


@app.route('/scrape/used', methods=['POST'])
def run_scraper_used():
    base_url = 'https://www.claycooley.com/inventory/used-vehicles/'
    cars = used_scraper.scrape_all_used_cars(base_url)
    count_added = add_cars_to_db(cars)
    return jsonify({"message": f"{count_added} used cars added."})

# -------------------- Scheduled Scraping -------------------- #
def scheduled_scrape(func):
    with app.app_context():
        count_added = add_cars_to_db(func())
        print(f"Scheduled scraping added {count_added} cars.")

scheduler = BackgroundScheduler()
scheduler.add_job(lambda: scheduled_scrape(
    lambda: used_scraper.scrape_all_used_cars('https://www.claycooley.com/inventory/used-vehicles/')), 
    trigger='interval', hours=24
)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# -------------------- Run App -------------------- #
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
