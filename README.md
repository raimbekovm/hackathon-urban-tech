# 🚀 RoadDoctor - AI-Powered Road Defect Detection System

Real-time road damage detection and monitoring system for Bishkek using computer vision and interactive mapping.

## 📋 Overview

RoadDoctor is an intelligent road infrastructure monitoring platform that automatically detects and prioritizes road defects using YOLOv8-based computer vision. The system processes real street imagery from Bishkek, identifies various types of road damage, and provides an interactive web dashboard for visualization and decision-making.

**Problem**: Municipal authorities struggle to efficiently monitor 300+ km of roads and prioritize maintenance work.

**Solution**: Automated defect detection from camera-equipped vehicles + ML analysis + priority-based repair scheduling.

**Impact**: Data-driven road maintenance, optimized budget allocation, improved road safety.

## ✨ Features

- 🤖 **YOLOv8-based Detection**: Identifies 4+ types of road defects with confidence scoring
- 🗺️ **Interactive Map Dashboard**: Real-time visualization of detected defects across Bishkek
- 📊 **Statistical Analysis**: Comprehensive metrics including severity scores, repair costs, and quality indices
- 🔥 **Heatmap Visualization**: Identify worst affected areas at a glance
- 🎯 **Priority Ranking**: Smart algorithm ranks roads for repair based on severity, count, and traffic
- 📍 **Geocoding Integration**: Automatic street name and district mapping via reverse geocoding
- ⚠️ **Critical Alerts**: Pulsating markers highlight defects requiring immediate attention

## 🛠️ Technology Stack

### Machine Learning
- **YOLOv8n**: Object detection model for road defect identification
- **Python 3.x**: Core ML pipeline
- **OpenCV**: Image processing
- **Pandas**: Data manipulation and analysis
- **Nominatim API**: Reverse geocoding for street names

### Frontend
- **Leaflet.js**: Interactive mapping library
- **Leaflet.heat**: Heatmap visualization
- **Chart.js**: Statistical charts and graphs
- **Vanilla JavaScript**: Fast, framework-free implementation

### Defect Types
- Potholes
- Longitudinal cracks
- Transverse cracks
- Alligator cracks
- Other road damage

## 📊 Current Results

- **138 defects** detected from real Bishkek street imagery
- **40 unique streets** analyzed across multiple districts
- **Top affected street**: Абдыкадырова улица (13 defects)
- **6 districts** covered: Ленинский, Первомайский, and more
- Detection confidence: 82-95% average

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
pip
Web browser
```

### 1. Clone the Repository
```bash
git clone https://github.com/raimbekovm/hackathon-urban-tech.git
cd hackathon-urban-tech
```

### 2. Set Up ML Environment
```bash
cd ml
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Process Data (Optional - outputs already generated)
```bash
# Run the ML pipeline
python process_real_data.py

# Add street names via reverse geocoding
python get_street_names.py
```

This generates:
- `ml/output/defects.csv` - All detected defects
- `ml/output/worst_roads.json` - Priority-ranked roads
- `ml/output/heatmap.json` - Heatmap intensity data
- `ml/output/stats.json` - Statistical summaries
- `ml/output/districts.json` - District-level aggregations

### 4. Launch Web Dashboard
```bash
cd ..
python3 -m http.server 8000
```

Open browser: **http://localhost:8000/frontend/**

## 📁 Project Structure

```
hackathon-urban-tech/
├── frontend/               # Web dashboard
│   ├── index.html         # Main page
│   ├── app.js             # Application logic
│   └── README.md          # Frontend documentation
├── ml/                    # Machine learning pipeline
│   ├── output/            # Generated data files
│   ├── utils/             # Scoring algorithms
│   ├── process_real_data.py   # Main ML pipeline
│   ├── get_street_names.py    # Reverse geocoding
│   └── notebooks/         # Training notebooks
└── README.md              # This file
```

## 🎯 Dashboard Modes

### 1. All Defects View
Individual markers for each detected defect, color-coded by type:
- 🔴 Red: Potholes
- 🟠 Orange: Longitudinal cracks
- 🟢 Green: Transverse cracks
- 🟣 Purple: Alligator cracks
- ⚫ Gray: Other damage

### 2. Heatmap View
Density-based visualization showing concentration of defects:
- Green zones: Good road condition
- Yellow zones: Moderate issues
- Orange zones: Poor condition
- Red zones: Critical - immediate repair needed

### 3. Critical Defects View
Filters and highlights defects with severity ≥7/10:
- Pulsating animation for visibility
- Priority repair recommendations
- Estimated repair costs

### 4. Map Styles
- Streets view (CartoDB Voyager)
- Satellite imagery (Esri World Imagery)

## 🧮 Scoring Algorithms

### Severity Score (1-10)
```
severity = (size_factor × 0.6 + type_factor × 0.4) × confidence
```

### Priority Score (1-10)
```
priority = severity × 0.5 + defect_count × 0.3 + traffic_weight × 0.2
```

### Road Quality Index (0-100)
```
quality = 100 - (defects_per_km × 5 + avg_severity × 3)
```

## 🔧 Development

### Training Custom Model
Use the Kaggle notebook for training on RDD2022 dataset:
```bash
# Upload ml/notebooks/train_rdd2022_kaggle.ipynb to Kaggle
# Enable GPU acceleration
# Run all cells (50 epochs, ~2 hours)
```

### Adding New Detection Classes
1. Update model training with new labels
2. Add color mapping in `frontend/app.js`
3. Update defect type names in `DEFECT_NAMES`

## 📈 Roadmap

- [ ] Deploy to production server
- [ ] Mobile application for field workers
- [ ] Real-time detection from bus cameras
- [ ] Historical trend analysis
- [ ] PDF report generation
- [ ] Integration with municipal systems

## 👥 Team

**Urban Tech Hackathon 2025**
- ML Engineer: Road defect detection pipeline
- Full Stack: Interactive dashboard and visualization
- Data Scientist: Scoring algorithms and analytics
- Project Manager: Coordination and presentation

## 📄 License

This project was developed for the Urban Tech Hackathon 2025.

## 🙏 Acknowledgments

- RDD2022 Dataset for training data
- OpenStreetMap/Nominatim for geocoding services
- CartoDB and Esri for map tiles
- Ultralytics YOLOv8 team

---

**Built with ❤️ for making Bishkek roads safer**
