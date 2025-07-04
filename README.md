#  Personal Finance Tracker

A simple Flask-based web application to help users track their daily, monthly, and yearly expenses.

---

## Features

- Add expenses with descriptions and price
-  Automatically calculates:
  - Total spent today
  - Total spent this month
  - Total spent this year
-  Stores data in an SQL database

---

##  Tech Stack

- **Backend**: Python, Flask  
- **Database**: SQLite (can be switched to PostgreSQL/MySQL)  
- **Frontend**: HTML + basic styling (can be extended with Bootstrap or Tailwind)

---

## Project Structure

project/
│
├── app.py # Main Flask app
├── templates/
│ └── index.html # HTML form and dashboard
├── static/ # (Optional) for CSS/JS
├── database.db # SQLite database
└── README.md # You're here!
