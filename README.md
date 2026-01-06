<p align="center">
  <img src="https://img.shields.io/badge/Proudly%20Sri%20Lankan-%F0%9F%87%B1%F0%9F%87%B0-green" />
  <img src="https://img.shields.io/badge/AI-Powered-blueviolet" />
  <img src="https://img.shields.io/badge/IoT%20Enabled-yellow" />
</p>

# <h1>Smart System for Seaweed Cultivation & Harvest Management </h1>

Empowering Sri Lankan seaweed farmers with **AI, IoT,** and **predictive analytics**.Automate species identification, monitor environments, predict harvest readiness, and add value through traceable post-harvest management.

---

## System Architecture Diagram

<p align="center">
  <img src="main system diagram.png" width="80%" alt="Integrated Smart Seaweed Farming System Architecture"/>
</p>

---

## Why This Project Matters

- Seaweed is a sustainable resource for food, cosmetics, and pharmaceuticals.
- Sri Lanka’s coasts are ideal, but current farming is traditional and inefficient.
- **This system introduces digital transformation:**
  - 🌱 **AI-powered species identification** (_Kappaphycus alvarezii_, _Gracilaria edulis_)
  - 🌡️ **IoT environmental monitoring** for indoor/outdoor decisions
  - 📊 **Predictive harvest modeling** for better yield & income
  - 📦 **Traceable packaging & AI-driven recommendations**

---

## Key Modules

### 1️⃣ AI Seaweed Identification
- Identifies local seaweed species and rejects non-seaweed
- Linked to knowledge base (traits, uses, nutrition)
- Tech: TensorFlow, PyTorch, OpenCV, React.js, Node.js, MongoDB  
- _First localized AI model for Sri Lankan species!_

### 2️⃣ Environmental Suitability & Micro-Site Recommendation
- Monitors temp, pH, salinity & light via IoT
- Recommends indoor/outdoor, ranks micro-sites
- Tech: ESP32, Node.js, React.js, MongoDB, Chart.js, D3.js  
- _Pioneering micro-site ranking in Sri Lanka!_

### 3️⃣ Growth Monitoring & Harvest Prediction
- Real-time weight-based tracking
- Logistic Growth Model for harvest readiness
- Tech: ESP32, HX711, Python (Flask), React.js, MongoDB  
- _First weight based harvest prediction for local seaweed!_

### 4️⃣ Packaging & Delivery with AI Prescription Calculator
- QR-based traceability, smart packaging
- Suggests food & medicinal uses, accurate ingredient ratios
- Tech: Node.js, React.js, MongoDB, TensorFlow, PyTorch  
- _First all-in-one traceable post-harvest tool!_

---

##  Feature Highlights

- AI-powered species recognition
- IoT-backed environment monitoring
- Predictive harvest scheduling
- QR-based transparent packaging
- Value-added medical & food guidance

---

## Tech Stack

| Frontend   | Backend            | Database | AI/ML               | IoT & Sensors                   | Visualization    |
|------------|--------------------|----------|---------------------|-------------------------------|------------------|
| React.js   | Node.js, Express   | MongoDB  | TensorFlow, PyTorch | ESP32, temp/pH/salinity/light | Chart.js, D3.js  |
| TypeScript | Python (Flask)     |          | OpenCV              | HX711 load cell               |                  |

---

## Getting Started

```sh
git clone https://github.com/ishendulara/Smart-System-for-Seaweed-Cultivation-and-Harvest-Management.git

# Backend
cd backend
npm install

# Frontend
cd ../frontend
npm install

# Start backend
npm start

# Start frontend
npm start
```

App runs at [http://localhost:3000](http://localhost:3000)

---

## Research Highlights

- First integrated smart seaweed farming system in Sri Lanka
- Closes gaps in species ID, monitoring, prediction, and post-harvest management
- Supports coastal women, small farmers, and sustainable aquaculture

---

## Contributing

Found a bug, idea, or want to collaborate?  
Raise an [issue](https://github.com/ishendulara/Smart-System-for-Seaweed-Cultivation-and-Harvest-Management/issues) or submit a PR!

---

<p align="center" style="font-size:18px;">
  <b>Smart farming, sustainable oceans.<br>
  Proudly crafted in Sri Lanka 🇱🇰</b>
</p>
