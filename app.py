from flask import Flask, jsonify, request
from models import db, Car
from schemas import CarSchema
import scraper
import used_scraper
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///instance/dealership.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB and schemas
db.init_app(app)
car_schema = CarSchema()
cars_schema = CarSchema(many=True)

# -------------------- CRUD Endpoints -------------------- #

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
        link=data.get('link')
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

# -------------------- Scraper Endpoints -------------------- #

@app.route('/scrape', methods=['POST'])
def run_scraper_new():
    base_url = 'https://www.claycooley.com/inventory/new-cars/'
    cars = scraper.scrape_all_new_cars(base_url)
    count_added = 0

    for car_data in cars:
        vin = car_data.get('vin')
        if vin:
            existing_car = Car.query.filter_by(vin=vin).first()
        else:
            existing_car = Car.query.filter_by(
                make=car_data['make'],
                model=car_data['model'],
                year=int(car_data['year'])
            ).first()

        if existing_car:
            continue

        new_car = Car(
            make=car_data['make'],
            model=car_data['model'],
            year=int(car_data['year']),
            price=float(car_data.get('price', 0)),
            mileage=int(car_data.get('mileage', 0)),
            status='available',
            vin=vin,
            image_url=car_data.get('image_url'),
            link=car_data.get('link')
        )
        db.session.add(new_car)
        count_added += 1

    db.session.commit()
    return jsonify({"message": f"{count_added} new cars added."})

@app.route('/scrape/used', methods=['POST'])
def run_scraper_used():
    base_url = 'https://www.claycooley.com/inventory/used-vehicles/'
    cars = used_scraper.scrape_all_used_cars(base_url)
    count_added = 0

    for car_data in cars:
        vin = car_data.get('vin')
        if vin:
            existing_car = Car.query.filter_by(vin=vin).first()
        else:
            existing_car = Car.query.filter_by(
                make=car_data['make'],
                model=car_data['model'],
                year=int(car_data['year'])
            ).first()

        if existing_car:
            continue

        new_car = Car(
            make=car_data['make'],
            model=car_data['model'],
            year=int(car_data['year']),
            price=float(car_data.get('price', 0)),
            mileage=int(car_data.get('mileage', 0)),
            status='available',
            vin=vin,
            image_url=car_data.get('image_url'),
            link=car_data.get('link')
        )
        db.session.add(new_car)
        count_added += 1

    db.session.commit()
    return jsonify({"message": f"{count_added} used cars added."})

# -------------------- Scheduled Scraping -------------------- #

def scheduled_scrape_new():
    with app.app_context():
        base_url = 'https://www.claycooley.com/inventory/new-cars/'
        scraper_cars = scraper.scrape_all_new_cars(base_url)
        count_added = 0
        for car_data in scraper_cars:
            vin = car_data.get('vin')
            if vin:
                existing_car = Car.query.filter_by(vin=vin).first()
            else:
                existing_car = Car.query.filter_by(
                    make=car_data['make'],
                    model=car_data['model'],
                    year=int(car_data['year'])
                ).first()
            if existing_car:
                continue
            new_car = Car(
                make=car_data['make'],
                model=car_data['model'],
                year=int(car_data['year']),
                price=float(car_data.get('price', 0)),
                mileage=int(car_data.get('mileage', 0)),
                status='available',
                vin=vin,
                image_url=car_data.get('image_url'),
                link=car_data.get('link')
            )
            db.session.add(new_car)
            count_added += 1
        db.session.commit()
        print(f"Scheduled scraping (new) added {count_added} cars.")

def scheduled_scrape_used():
    with app.app_context():
        base_url = 'https://www.claycooley.com/inventory/used-vehicles/'
        scraper_cars = used_scraper.scrape_all_used_cars(base_url)
        count_added = 0
        for car_data in scraper_cars:
            vin = car_data.get('vin')
            if vin:
                existing_car = Car.query.filter_by(vin=vin).first()
            else:
                existing_car = Car.query.filter_by(
                    make=car_data['make'],
                    model=car_data['model'],
                    year=int(car_data['year'])
                ).first()
            if existing_car:
                continue
            new_car = Car(
                make=car_data['make'],
                model=car_data['model'],
                year=int(car_data['year']),
                price=float(car_data.get('price', 0)),
                mileage=int(car_data.get('mileage', 0)),
                status='available',
                vin=vin,
                image_url=car_data.get('image_url'),
                link=car_data.get('link')
            )
            db.session.add(new_car)
            count_added += 1
        db.session.commit()
        print(f"Scheduled scraping (used) added {count_added} cars.")

# Start scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_scrape_new, trigger='interval', hours=24)
scheduler.add_job(func=scheduled_scrape_used, trigger='interval', hours=24)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# -------------------- Run App -------------------- #

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # Use environment PORT if available (deployment platforms)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
