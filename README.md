# ClayCooley Car Inventory REST API

A full-featured REST API that scrapes live used car inventory data from [Clay Cooley](https://www.claycooley.com/) and provides endpoints for CRUD operations. The API also supports scheduled daily updates to keep the inventory current.

## 🔗 Live Demo

Try the API in action (GET all cars): https://web-production-bf935.up.railway.app/cars

---

## 🏗 Tech Stack

- **Backend Framework:** Flask
- **Database:** SQLite with SQLAlchemy ORM
- **Data Scraping:** BeautifulSoup + Requests
- **Scheduling:** APScheduler for automated daily scraping
- **Data Serialization:** Marshmallow (for JSON responses)

---

## 🚀 Features

- **Full CRUD functionality:**

  - `GET /cars` – Retrieve all cars
  - `GET /cars/<id>` – Retrieve a single car
  - `POST /cars` – Add a new car manually
  - `PUT /cars/<id>` – Update an existing car
  - `DELETE /cars/<id>` – Delete a car

- **Live Inventory Scraper:**

  - `POST /scrape` – Trigger live scraping of Clay Cooley’s inventory
  - Scraper extracts: make, model, year, VIN, price, mileage, image, and link

- **Scheduled Updates:**

  - Automatically runs every 24 hours to fetch the latest inventory

- **Database Integrity:**
  - Prevents duplicate entries based on VIN or combination of make/model/year

---

## 📦 Installation

1. **Clone the repository**

```bash
git clone https://github.com/<your-username>/claycooley-api.git
cd claycooley-api

2. **Create a Virtual Environment**
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

3. **Install dependencies**
pip install -r requirements.txt

4. **Run the API**
python3 app.py

The api will be available at http://localhost:8080

---

## 🧪 Testing Endpoints

1. **GET all cars**
curl http://localhost:8080/cars

2. **POST new car**
curl -X POST http://localhost:8080/cars \
-H "Content-Type: application/json" \
-d '{"make":"Toyota","model":"Camry","year":2025,"price":30000}'

3. **Trigger scraper**
curl -X POST http://localhost:8080/scrape

---
## 🔮 Future Enhancements
- Add user authentication and role-based access
- Improve scraper resilience with retries and error handling
- Add advanced filtering and sorting options
- Switch to a more scalable database (PostgreSQL or MySQL)
- Implement REST API versioning for better maintainability
- Combine with Car Management System
```
