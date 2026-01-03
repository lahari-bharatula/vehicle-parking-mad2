🚗 Vehicle Parking Management System

A web-based Vehicle Parking Management System designed to manage parking slots, reservations, and dashboards for different user roles.
This project demonstrates a full-stack application architecture, with a deployed frontend demo and a backend implemented using Flask.

🔗 Live Demo (Frontend)

👉 Live Site:

https://lahari-bharatula.github.io/vehicle-parking-mad2/#/


⚠️ Note:
This live demo showcases the frontend only.
Backend services (Flask API & database) are not deployed and are replaced with demo/mock data for presentation purposes.

🧠 Project Overview

The system supports multiple roles and features commonly required in a parking management application:

👤 User Roles

Admin

View overall parking statistics

Monitor slot usage

Access summary dashboards

User

Login and access parking-related views

View booking/slot information

🛠️ Tech Stack
Frontend

Vue.js 3

Vite

Vue Router

Pinia (state management)

Chart.js (dashboard visualizations)

HTML / CSS / JavaScript

Backend (not deployed)

Flask

SQLite

REST-style APIs

📁 Project Structure
vehicle-parking-mad2/
├── frontend/
│   ├── src/
│   ├── dist/              # Production build (used for GitHub Pages)
│   ├── vite.config.js
│   └── package.json
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── database/
│
└── README.md

🚀 Deployment Details

The frontend is deployed using GitHub Pages

Built using vite build

Deployed via gh-pages branch

Routing handled using hash-based routing (createWebHashHistory) to support static hosting