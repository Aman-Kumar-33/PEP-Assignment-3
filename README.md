# 🍔 Smart Food Stall Web Application

A lightweight, portable full-stack web application designed to eliminate long queues at campus food stalls through digital pre-ordering and peak-time analytics.

---

## 🎯 Project Purpose

During short university breaks, dozens of students rush to the same food stalls simultaneously, leading to crowd congestion, stressed stall owners, and delayed orders.

The **Smart Food Stall** solves this by creating a two-sided platform:

* **For Students:** A clean interface to browse menus, pre-order food, select specific pickup time slots, and track the live preparation status of their food.
* **For Stall Owners:** A centralized admin dashboard to manage incoming orders, update statuses dynamically (Pending ➔ Preparing ➔ Ready), and add new items to their menu.
* **For Campus Management:** An analytics dashboard that tracks and visualizes peak demand times, passively encouraging students to order during off-peak hours to distribute the crowd.

---

## ⚙️ How the Code Works

This project is built using **Python** and **Flask** for the backend, with standard **HTML**, **CSS**, and **JavaScript** for the frontend. To make the project 100% portable and easy to run without complex database setups, it utilizes a local JSON file as its database.

### 1️⃣ Data Management (`data.json`)

Instead of an SQL server, all data (users, stalls, menus, and live orders) is stored in `data.json`.

The backend uses two helper functions:

* `load_data()` – Reads the JSON file and converts it into Python dictionaries.
* `save_data(data)` – Writes updated Python dictionaries back to the JSON file, acting as persistent storage.

---

### 2️⃣ Backend Routing (`app.py`)

Flask handles HTTP requests and routes users to different views:

* `/` (Home) – Loads available stalls.
* `/menu/<stall_id>` – Dynamically generates the menu for a specific stall.
* `/place_order` (POST) – Processes form submissions, generates a unique Order ID, logs selected food items into `order_details`, and saves them to the JSON file.
* `/manage/<stall_id>` – Admin dashboard that joins orders, student names, and food items together for stall owners to process.
* `/analytics` – Reads historical orders, tallies them by `time_slot`, and passes aggregated data to the frontend.

---

### 3️⃣ Frontend & UI (`templates/`)

* **Jinja2 Templating** – Securely injects Python variables directly into HTML (e.g., dynamically coloring order status badges).
* **Chart.js** – Used on the Analytics page to render an interactive bar chart of peak order times.
* **Auto-Refreshing** – The "My Orders" page includes a lightweight JavaScript script that polls the server every 5 seconds, providing real-time updates when admins change order statuses.

---

## 🚀 How to Run the Program (Local Setup)

Because this app uses a local JSON database, setup is extremely fast. No external database configuration is required.

---

### ✅ Prerequisites

Make sure you have **Python 3** installed on your computer.

---

## 📦 Installation Steps

### 1️⃣ Clone the Repository (or Download ZIP)

```bash
git clone https://github.com/YourUsername/smart-food-stall.git
cd smart-food-stall
```

---

### 2️⃣ Create a Virtual Environment

This keeps project dependencies isolated from your main system.

```bash
python -m venv venv
```

---

### 3️⃣ Activate the Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

**Mac/Linux:**

```bash
source venv/bin/activate
```

---

### 4️⃣ Install Required Packages

```bash
pip install Flask
# If deploying to a production server like Render, also install gunicorn:
# pip install gunicorn
```

---

### 5️⃣ Run the Application

```bash
python app.py
```

---

### 6️⃣ Open in Browser

Navigate to:

```
http://127.0.0.1:5000
```

**Student Perspective:**

* Place an order from the home page
* Or go to:

```
http://127.0.0.1:5000/my_orders/1
```

**Stall Admin Perspective:**

```
http://127.0.0.1:5000/manage/1
```

---

## 🧠 Key Advantages

* No external database required
* Fully portable project
* Beginner-friendly architecture
* Real-time order tracking
* Crowd distribution via analytics

---

Built to simplify campus food ordering and eliminate long queues efficiently.
