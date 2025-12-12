# 📋 Распределение TECH работы на 4 участников

## Фокус: Каждый делает свою техническую часть

---

# 👤 УЧАСТНИК 1: ML Engineer (ТЫ)

## 🎯 Твоя зона ответственности:
Machine Learning модель + все данные для визуализаций

---

## 📝 Полный список задач:

### 1. ML Модель
- [ ] Скачать датасет RDD2022
- [ ] Fine-tune YOLOv8n на детекцию дефектов
  - Target: accuracy > 70%
  - Speed: 30+ FPS
- [ ] Создать inference скрипт для обработки:
  - Одного изображения
  - Папки изображений
  - Видео (покадрово)
- [ ] Оптимизация модели (если нужно)

### 2. Сбор данных по Бишкеку
- [ ] Собрать 100-200 изображений дорог Бишкека:
  - Google Street View (автоматический скрипт)
  - Яндекс.Карты панорамы
  - Или попросить у Участника 4
- [ ] Обработать все через модель
- [ ] Получить детекции с координатами

### 3. Аналитика и scoring алгоритмы

#### Severity Score (Оценка серьезности):
```python
def calculate_severity(defect):
    """
    Оценка серьезности дефекта: 1-10
    """
    # Факторы:
    size_score = defect['bbox_area'] / image_area * 10  # размер
    type_score = {
        'pothole': 9,
        'alligator_crack': 7,
        'transverse_crack': 5,
        'longitudinal_crack': 4
    }[defect['type']]
    
    confidence_factor = defect['confidence']
    
    severity = (size_score * 0.6 + type_score * 0.4) * confidence_factor
    return min(10, severity)
```

#### Priority Score (Приоритет ремонта):
```python
def calculate_priority(street_defects):
    """
    Приоритет ремонта улицы: 1-10
    """
    avg_severity = mean([d['severity'] for d in street_defects])
    defect_count = len(street_defects)
    
    # Эмулируем трафик по типу дороги
    traffic_score = {
        'main_avenue': 10,    # Chui, Manas
        'major_street': 7,
        'minor_street': 4
    }
    
    priority = (
        avg_severity * 0.5 +
        min(defect_count / 10, 10) * 0.3 +
        traffic_score * 0.2
    )
    return priority
```

#### Road Quality Index:
```python
def calculate_road_quality(street):
    """
    Качество дороги: 0-100 (100 = идеально)
    """
    defects_per_km = street['defect_count'] / street['length_km']
    avg_severity = street['avg_severity']
    
    quality = 100 - (defects_per_km * 5 + avg_severity * 3)
    return max(0, min(100, quality))
```

### 4. Генерация датасетов для Frontend

#### CSV для карты с маркерами:
```csv
lat,lon,defect_type,severity,confidence,image_path,street_name,district
42.8746,74.5698,pothole,9.2,0.89,img001.jpg,Chui Ave,Sverdlovsky
42.8750,74.5702,longitudinal_crack,5.4,0.76,img002.jpg,Manas Ave,Leninsky
42.8755,74.5710,transverse_crack,6.1,0.82,img003.jpg,Ibraimov St,Pervomaysky
...
```

#### JSON для heatmap:
```json
{
  "heatmap_data": [
    [42.8746, 74.5698, 0.92],  // lat, lon, intensity (0-1)
    [42.8750, 74.5702, 0.54],
    [42.8755, 74.5710, 0.61],
    ...
  ]
}
```

#### JSON для districts (для Choropleth):
```json
{
  "districts": [
    {
      "name": "Sverdlovsky",
      "defect_count": 347,
      "defect_density": 8.5,  // per km
      "avg_severity": 7.2,
      "quality_index": 42,
      "repair_cost_estimate": 8500000
    },
    {
      "name": "Leninsky",
      "defect_count": 289,
      "defect_density": 6.8,
      "avg_severity": 6.4,
      "quality_index": 53,
      "repair_cost_estimate": 6200000
    },
    ...
  ]
}
```

#### JSON для top worst roads:
```json
{
  "worst_roads": [
    {
      "rank": 1,
      "street_name": "Chui Avenue",
      "district": "Sverdlovsky",
      "defect_count": 45,
      "avg_severity": 8.3,
      "quality_index": 32,
      "priority_score": 9.2,
      "repair_cost": 1350000,
      "defects": [
        {"type": "pothole", "count": 23},
        {"type": "crack", "count": 22}
      ]
    },
    {
      "rank": 2,
      "street_name": "Manas Avenue",
      ...
    },
    ...  // топ-20
  ]
}
```

#### JSON для статистики (dashboard):
```json
{
  "total_stats": {
    "total_defects": 1247,
    "critical_defects": 156,
    "total_repair_cost": 42500000,
    "priority_roads_count": 23,
    "defects_by_type": {
      "pothole": 562,
      "longitudinal_crack": 301,
      "transverse_crack": 234,
      "alligator_crack": 150
    },
    "defects_by_severity": {
      "high": 335,
      "medium": 678,
      "low": 234
    }
  }
}
```

### 5. Визуализации для презентации
- [ ] Confusion matrix модели
- [ ] 10 лучших примеров детекции (до/после)
- [ ] График: Defects by Type (для слайда)
- [ ] График: Severity Distribution (для слайда)
- [ ] Heatmap изображение города (для слайда)
- [ ] Model performance chart (accuracy, speed)

### 6. GitHub структура (для HR)
```
ml/
├── README.md                    # Подробная документация
│   - Описание проекта
│   - Как установить
│   - Как использовать
│   - Архитектура модели
│   - Результаты (метрики)
│
├── requirements.txt             # Зависимости
├── train.py                     # Обучение модели
├── inference.py                 # Детекция на изображениях
├── analytics.py                 # Scoring алгоритмы
├── data_generator.py            # Генерация датасетов для frontend
│
├── utils/
│   ├── preprocessing.py         # Препроцессинг изображений
│   ├── scoring.py               # Severity/Priority scoring
│   └── visualization.py         # Визуализации
│
├── notebooks/
│   └── exploration.ipynb        # Jupyter анализ данных
│
├── data/                        # НЕ коммитить (в .gitignore)
│   ├── raw/                     # Исходные изображения
│   ├── processed/               # Обработанные
│   └── annotations/             # Аннотации
│
├── models/                      # НЕ коммитить (в .gitignore)
│   └── best.pt                  # Обученная модель
│
├── output/                      # Датасеты для frontend
│   ├── defects.csv
│   ├── heatmap.json
│   ├── districts.json
│   ├── worst_roads.json
│   └── stats.json
│
└── visualizations/              # Для презентации
    ├── confusion_matrix.png
    ├── detection_examples/
    └── charts/
```

### 7. Документация (важно для HR!)

#### Хороший README.md:
```markdown
# RoadDoctor ML - Road Defect Detection

## Overview
AI-powered system for automatic detection of road defects using YOLOv8.

## Model Performance
- **Accuracy:** 76.3%
- **Precision:** 0.78
- **Recall:** 0.74
- **F1-Score:** 0.76
- **Inference Speed:** 35 FPS (GPU)

## Dataset
- Training: RDD2022 (47,420 images)
- Fine-tuning: Bishkek roads (150 images)
- Classes: 4 (pothole, longitudinal_crack, transverse_crack, alligator_crack)

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
from inference import RoadDefectDetector

detector = RoadDefectDetector('models/best.pt')
results = detector.detect('path/to/image.jpg')
```

## Architecture
[Diagram showing Camera → Preprocessing → YOLOv8 → Postprocessing → Output]

## Results
- Processed 150 images of Bishkek roads
- Detected 1,247 defects
- Generated priority repair list for 23 streets

## Author
[Your Name] - ML Engineer
```

### 8. Красивые коммиты (для HR)
```bash
# Хорошие примеры:
git commit -m "Add YOLOv8 training pipeline with data augmentation"
git commit -m "Implement severity scoring algorithm"
git commit -m "Add heatmap data generation for visualization"
git commit -m "Optimize inference speed: 20 FPS → 35 FPS"
git commit -m "Generate analytics datasets for frontend integration"

# Плохие примеры (не делать!):
git commit -m "update"
git commit -m "fix"
git commit -m "changes"
```

---

## 📦 Твой стек:
- **Python 3.9+**
- **YOLOv8** (ultralytics)
- **OpenCV** (обработка изображений)
- **NumPy, Pandas** (данные)
- **Matplotlib, Seaborn** (визуализации)
- **GeoPandas** (геоданные, опционально)
- **Jupyter** (анализ)

---

## ⏱️ Примерное время:
- **День 1:** 8ч - датасет, начало обучения модели
- **День 2:** 8ч - inference, сбор данных Бишкека, scoring алгоритмы
- **День 3:** 8ч - генерация всех датасетов, визуализации для презентации
- **День 4:** 4ч - финальная документация, помощь команде, презентационные материалы

---

## 🎯 Output (что передаешь команде):
✅ Обученная модель (best.pt)  
✅ 5 JSON/CSV файлов с данными  
✅ Визуализации для презентации (10+ изображений)  
✅ Документированный код на GitHub  
✅ README.md с метриками  

---
---

# 👤 УЧАСТНИК 2: Backend Developer

## 🎯 Твоя зона ответственности:
API сервер + интеграция ML модели

---

## 📝 Полный список задач:

### 1. Настройка Backend проекта
- [ ] FastAPI проект структура
- [ ] Виртуальное окружение
- [ ] Установка зависимостей:
```bash
pip install fastapi uvicorn python-multipart sqlalchemy pillow python-jose[cryptography]
```

### 2. Интеграция ML модели

#### Загрузка модели при старте:
```python
# main.py
from fastapi import FastAPI
from ultralytics import YOLO
import os

app = FastAPI()

# Загрузка модели при старте сервера
@app.on_event("startup")
async def load_model():
    global model
    model_path = os.path.join("models", "best.pt")
    model = YOLO(model_path)
    print(f"Model loaded from {model_path}")
```

#### Endpoint для детекции:
```python
from fastapi import File, UploadFile
import cv2
import numpy as np

@app.post("/api/detect")
async def detect_defects(file: UploadFile = File(...)):
    """
    Загрузить изображение и получить детекции
    """
    # Читаем изображение
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Детекция
    results = model(image)
    
    # Парсинг результатов
    detections = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            
            detections.append({
                "type": model.names[cls],
                "confidence": conf,
                "bbox": [x1, y1, x2, y2],
                "severity": calculate_severity(box, image.shape)
            })
    
    # Сохраняем результат с bbox
    result_image = results[0].plot()
    result_path = f"results/{file.filename}"
    cv2.imwrite(result_path, result_image)
    
    return {
        "detections": detections,
        "result_image_url": f"/static/{result_path}"
    }
```

### 3. Endpoints для данных визуализаций

#### Загрузка данных от Участника 1:
```python
import json
import pandas as pd

# При старте сервера загружаем все данные
@app.on_event("startup")
async def load_datasets():
    global defects_data, heatmap_data, districts_data, worst_roads_data, stats_data
    
    # Загрузка CSV
    defects_data = pd.read_csv("data/defects.csv").to_dict('records')
    
    # Загрузка JSON
    with open("data/heatmap.json") as f:
        heatmap_data = json.load(f)
    
    with open("data/districts.json") as f:
        districts_data = json.load(f)
    
    with open("data/worst_roads.json") as f:
        worst_roads_data = json.load(f)
    
    with open("data/stats.json") as f:
        stats_data = json.load(f)
```

#### GET Endpoints:
```python
@app.get("/api/defects")
async def get_all_defects():
    """
    Получить все дефекты для карты
    """
    return {"defects": defects_data}

@app.get("/api/heatmap")
async def get_heatmap_data():
    """
    Получить данные для heatmap
    """
    return heatmap_data

@app.get("/api/districts")
async def get_districts():
    """
    Получить статистику по районам
    """
    return districts_data

@app.get("/api/worst-roads")
async def get_worst_roads(limit: int = 20):
    """
    Получить топ худших дорог
    """
    return {
        "worst_roads": worst_roads_data["worst_roads"][:limit]
    }

@app.get("/api/stats")
async def get_statistics():
    """
    Получить общую статистику для dashboard
    """
    return stats_data
```

### 4. Фильтрация данных

#### Endpoint с фильтрами:
```python
from typing import Optional, List

@app.get("/api/defects/filter")
async def filter_defects(
    defect_type: Optional[str] = None,
    min_severity: Optional[float] = None,
    district: Optional[str] = None
):
    """
    Фильтровать дефекты по параметрам
    """
    filtered = defects_data.copy()
    
    if defect_type:
        filtered = [d for d in filtered if d['defect_type'] == defect_type]
    
    if min_severity:
        filtered = [d for d in filtered if d['severity'] >= min_severity]
    
    if district:
        filtered = [d for d in filtered if d['district'] == district]
    
    return {"defects": filtered, "count": len(filtered)}
```

### 5. CORS настройка (для Frontend)
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6. Статичные файлы (для изображений)
```python
from fastapi.staticfiles import StaticFiles

# Раздача статичных файлов
app.mount("/static", StaticFiles(directory="results"), name="static")
```

### 7. База данных (опционально, если время есть)

#### SQLite для хранения дефектов:
```python
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./road_defects.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Defect(Base):
    __tablename__ = "defects"
    
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    defect_type = Column(String)
    severity = Column(Float)
    confidence = Column(Float)
    image_path = Column(String)
    street_name = Column(String)
    district = Column(String)

Base.metadata.create_all(bind=engine)

# Endpoint для добавления дефекта
@app.post("/api/defects/add")
async def add_defect(defect: dict):
    db = SessionLocal()
    new_defect = Defect(**defect)
    db.add(new_defect)
    db.commit()
    db.refresh(new_defect)
    db.close()
    return {"message": "Defect added", "id": new_defect.id}
```

### 8. Swagger документация (автоматическая в FastAPI)
```python
# Доступна по адресу: http://localhost:8000/docs
# Автоматически генерируется из кода!

# Можно добавить описания:
@app.get("/api/stats", 
    summary="Get statistics",
    description="Returns overall statistics for dashboard",
    response_description="Statistics object with counts and totals")
async def get_statistics():
    return stats_data
```

### 9. Деплой

#### Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Запуск
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Railway.app деплой:
```bash
# 1. Создать account на railway.app
# 2. New Project → Deploy from GitHub
# 3. Выбрать репозиторий
# 4. Railway автоматически детектит Python и деплоит
# 5. Получить public URL
```

### 10. Тестирование

#### Тесты endpoints:
```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_get_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    assert "total_defects" in response.json()["total_stats"]

def test_get_defects():
    response = client.get("/api/defects")
    assert response.status_code == 200
    assert len(response.json()["defects"]) > 0

def test_filter_defects():
    response = client.get("/api/defects/filter?defect_type=pothole")
    assert response.status_code == 200
    defects = response.json()["defects"]
    assert all(d["defect_type"] == "pothole" for d in defects)
```

### 11. Логирование
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/api/stats")
async def get_statistics():
    logger.info("Stats endpoint called")
    return stats_data
```

---

## 📦 Твой стек:
- **FastAPI** (веб-фреймворк)
- **Uvicorn** (ASGI сервер)
- **SQLAlchemy** (ORM, опционально)
- **Pillow** (обработка изображений)
- **YOLOv8** (интеграция ML)
- **Pandas** (обработка данных)

---

## 📂 Структура:
```
backend/
├── main.py                      # Главный файл приложения
├── requirements.txt             # Зависимости
├── Dockerfile                   # Для деплоя
│
├── api/
│   ├── routes.py               # API endpoints
│   └── models.py               # Pydantic models
│
├── ml/
│   └── detector.py             # Обертка для ML модели
│
├── data/                        # Данные от Участника 1
│   ├── defects.csv
│   ├── heatmap.json
│   ├── districts.json
│   ├── worst_roads.json
│   └── stats.json
│
├── models/                      # ML модель
│   └── best.pt
│
├── results/                     # Результаты детекций
│   └── detected_images/
│
├── tests/
│   └── test_api.py
│
└── README.md
```

---

## ⏱️ Примерное время:
- **День 1:** 6ч - setup, базовые endpoints, интеграция ML
- **День 2:** 8ч - все endpoints для визуализаций, тестирование
- **День 3:** 6ч - деплой, оптимизация, документация
- **День 4:** 4ч - финальные тесты, помощь Frontend

---

## 🎯 Output (что передаешь команде):
✅ Рабочий API с документацией  
✅ Задеплоенный сервер (public URL)  
✅ Swagger docs (для Frontend разработчика)  
✅ Все endpoints протестированы  

---
---

# 👤 УЧАСТНИК 3: Frontend Developer

## 🎯 Твоя зона ответственности:
Web приложение с картой и dashboard

---

## 📝 Полный список задач:

### 1. Setup проекта
```bash
npx create-react-app road-doctor-frontend
cd road-doctor-frontend
npm install leaflet react-leaflet axios recharts leaflet.heat
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 2. Интерактивная карта

#### Базовая карта с маркерами:
```jsx
// components/Map.jsx
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { useEffect, useState } from 'react';
import axios from 'axios';
import L from 'leaflet';

const Map = () => {
  const [defects, setDefects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Загрузка дефектов с backend
    axios.get('http://backend-url/api/defects')
      .then(res => {
        setDefects(res.data.defects);
        setLoading(false);
      });
  }, []);

  // Кастомные иконки для разных типов
  const getIcon = (type, severity) => {
    const color = severity > 7 ? 'red' : severity > 4 ? 'orange' : 'yellow';
    const size = severity > 7 ? 30 : severity > 4 ? 25 : 20;
    
    return L.divIcon({
      className: 'custom-icon',
      html: `<div style="
        background-color: ${color};
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        border: 2px solid white;
      "></div>`,
      iconSize: [size, size]
    });
  };

  return (
    <MapContainer 
      center={[42.8746, 74.5698]} 
      zoom={12} 
      style={{ height: '100vh', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {defects.map((defect, idx) => (
        <Marker 
          key={idx}
          position={[defect.lat, defect.lon]}
          icon={getIcon(defect.defect_type, defect.severity)}
        >
          <Popup>
            <div className="p-2">
              <h3 className="font-bold">{defect.defect_type}</h3>
              <p>Severity: {defect.severity.toFixed(1)}/10</p>
              <p>Street: {defect.street_name}</p>
              <p>Confidence: {(defect.confidence * 100).toFixed(0)}%</p>
              {defect.image_path && (
                <img src={`http://backend-url/static/${defect.image_path}`} 
                     alt="defect" className="mt-2 w-full" />
              )}
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default Map;
```

#### Heatmap слой:
```jsx
// components/Heatmap.jsx
import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';
import axios from 'axios';

const HeatmapLayer = () => {
  const map = useMap();

  useEffect(() => {
    axios.get('http://backend-url/api/heatmap')
      .then(res => {
        const heatData = res.data.heatmap_data;
        
        // Создать heatmap layer
        const heat = L.heatLayer(heatData, {
          radius: 25,
          blur: 15,
          maxZoom: 17,
          max: 1.0,
          gradient: {
            0.0: 'green',
            0.5: 'yellow',
            0.7: 'orange',
            1.0: 'red'
          }
        }).addTo(map);

        return () => {
          map.removeLayer(heat);
        };
      });
  }, [map]);

  return null;
};

// Использование:
// <HeatmapLayer /> внутри <MapContainer>
```

#### Toggle между Markers и Heatmap:
```jsx
const [viewMode, setViewMode] = useState('markers'); // 'markers' or 'heatmap'

<div className="absolute top-4 right-4 z-1000 bg-white p-2 rounded shadow">
  <button 
    className={`px-4 py-2 ${viewMode === 'markers' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
    onClick={() => setViewMode('markers')}
  >
    Markers
  </button>
  <button 
    className={`px-4 py-2 ${viewMode === 'heatmap' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
    onClick={() => setViewMode('heatmap')}
  >
    Heatmap
  </button>
</div>

{viewMode === 'markers' ? <MarkersLayer /> : <HeatmapLayer />}
```

### 3. Фильтры

#### Sidebar с фильтрами:
```jsx
// components/Filters.jsx
const Filters = ({ onFilterChange }) => {
  const [filters, setFilters] = useState({
    types: {
      pothole: true,
      longitudinal_crack: true,
      transverse_crack: true,
      alligator_crack: true
    },
    minSeverity: 0,
    district: 'all'
  });

  const handleChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  return (
    <div className="w-64 bg-white p-4 shadow-lg h-full overflow-y-auto">
      <h2 className="text-xl font-bold mb-4">Filters</h2>
      
      {/* Type filters */}
      <div className="mb-4">
        <h3 className="font-semibold mb-2">Defect Type</h3>
        {Object.keys(filters.types).map(type => (
          <label key={type} className="flex items-center mb-2">
            <input 
              type="checkbox" 
              checked={filters.types[type]}
              onChange={(e) => handleChange('types', {
                ...filters.types,
                [type]: e.target.checked
              })}
              className="mr-2"
            />
            {type.replace('_', ' ')}
          </label>
        ))}
      </div>

      {/* Severity slider */}
      <div className="mb-4">
        <h3 className="font-semibold mb-2">Min Severity: {filters.minSeverity}</h3>
        <input 
          type="range" 
          min="0" 
          max="10" 
          step="0.5"
          value={filters.minSeverity}
          onChange={(e) => handleChange('minSeverity', parseFloat(e.target.value))}
          className="w-full"
        />
      </div>

      {/* District filter */}
      <div className="mb-4">
        <h3 className="font-semibold mb-2">District</h3>
        <select 
          value={filters.district}
          onChange={(e) => handleChange('district', e.target.value)}
          className="w-full p-2 border rounded"
        >
          <option value="all">All Districts</option>
          <option value="Sverdlovsky">Sverdlovsky</option>
          <option value="Leninsky">Leninsky</option>
          <option value="Pervomaysky">Pervomaysky</option>
          <option value="Oktyabrsky">Oktyabrsky</option>
        </select>
      </div>
    </div>
  );
};
```

### 4. Dashboard

#### Stats Cards:
```jsx
// components/Dashboard.jsx
import { useEffect, useState } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [worstRoads, setWorstRoads] = useState([]);

  useEffect(() => {
    // Загрузка статистики
    axios.get('http://backend-url/api/stats')
      .then(res => setStats(res.data.total_stats));
    
    // Загрузка худших дорог
    axios.get('http://backend-url/api/worst-roads?limit=10')
      .then(res => setWorstRoads(res.data.worst_roads));
  }, []);

  if (!stats) return <div>Loading...</div>;

  return (
    <div className="p-8">
      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <StatCard 
          title="Total Defects" 
          value={stats.total_defects}
          icon="🚨"
          color="blue"
        />
        <StatCard 
          title="Critical" 
          value={stats.critical_defects}
          icon="🔴"
          color="red"
        />
        <StatCard 
          title="Repair Cost" 
          value={`${(stats.total_repair_cost / 1000000).toFixed(1)}M som`}
          icon="💰"
          color="green"
        />
        <StatCard 
          title="Priority Roads" 
          value={stats.priority_roads_count}
          icon="🎯"
          color="orange"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        {/* Pie Chart - Defects by Type */}
        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-xl font-bold mb-4">Defects by Type</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={Object.entries(stats.defects_by_type).map(([name, value]) => ({ name, value }))}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {Object.keys(stats.defects_by_type).map((_, idx) => (
                  <Cell key={idx} fill={['#EF4444', '#F59E0B', '#10B981', '#3B82F6'][idx]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Bar Chart - Severity Distribution */}
        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-xl font-bold mb-4">Severity Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={Object.entries(stats.defects_by_severity).map(([name, value]) => ({ name, value }))}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top 10 Worst Roads */}
      <div className="bg-white p-6 rounded shadow">
        <h3 className="text-xl font-bold mb-4">Top 10 Worst Roads</h3>
        <div className="space-y-3">
          {worstRoads.map((road, idx) => (
            <div key={idx} className="flex items-center">
              <span className="w-8 text-lg font-bold">{idx + 1}</span>
              <div className="flex-1">
                <div className="flex justify-between mb-1">
                  <span className="font-semibold">{road.street_name}</span>
                  <span className="text-sm text-gray-600">{road.district}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-6">
                  <div 
                    className="h-6 rounded-full flex items-center justify-center text-white text-sm font-bold"
                    style={{ 
                      width: `${road.priority_score * 10}%`,
                      backgroundColor: road.priority_score > 8 ? '#EF4444' : road.priority_score > 6 ? '#F59E0B' : '#10B981'
                    }}
                  >
                    {road.priority_score.toFixed(1)}
                  </div>
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>{road.defect_count} defects</span>
                  <span>Quality: {road.quality_index}/100</span>
                  <span>{(road.repair_cost / 1000).toFixed(0)}K som</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, color }) => (
  <div className={`bg-white p-6 rounded shadow border-l-4 border-${color}-500`}>
    <div className="flex items-center justify-between">
      <div>
        <p className="text-gray-600 text-sm">{title}</p>
        <p className="text-3xl font-bold mt-2">{value}</p>
      </div>
      <div className="text-4xl">{icon}</div>
    </div>
  </div>
);
```

### 5. Priority Planner Page

```jsx
// pages/PriorityPlanner.jsx
const PriorityPlanner = () => {
  const [roads, setRoads] = useState([]);
  const [selectedBudget, setSelectedBudget] = useState(10000000); // 10M som

  useEffect(() => {
    axios.get('http://backend-url/api/worst-roads?limit=20')
      .then(res => setRoads(res.data.worst_roads));
  }, []);

  // Расчет сколько дорог можно отремонтировать с бюджетом
  const getRepairablePlan = (budget) => {
    let remaining = budget;
    const plan = [];
    
    for (const road of roads) {
      if (remaining >= road.repair_cost) {
        plan.push(road);
        remaining -= road.repair_cost;
      }
    }
    
    return { plan, remaining };
  };

  const { plan, remaining } = getRepairablePlan(selectedBudget);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Priority Repair Planner</h1>
      
      {/* Budget Selector */}
      <div className="bg-white p-6 rounded shadow mb-6">
        <h3 className="text-xl font-semibold mb-4">Select Budget</h3>
        <input 
          type="range"
          min="5000000"
          max="50000000"
          step="1000000"
          value={selectedBudget}
          onChange={(e) => setSelectedBudget(parseInt(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between mt-2">
          <span className="text-2xl font-bold">{(selectedBudget / 1000000).toFixed(0)}M som</span>
          <span className="text-gray-600">Remaining: {(remaining / 1000000).toFixed(1)}M som</span>
        </div>
      </div>

      {/* Repair Plan */}
      <div className="bg-white p-6 rounded shadow">
        <h3 className="text-xl font-semibold mb-4">
          Recommended Repair Plan ({plan.length} roads)
        </h3>
        
        <div className="space-y-4">
          {plan.map((road, idx) => (
            <div key={idx} className="border-l-4 border-blue-500 pl-4 py-3 bg-gray-50">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h4 className="font-bold text-lg">
                    {idx + 1}. {road.street_name}
                    <span className="ml-2 text-sm text-gray-600">({road.district})</span>
                  </h4>
                  <div className="grid grid-cols-3 gap-4 mt-2 text-sm">
                    <div>
                      <span className="text-gray-600">Defects:</span>
                      <span className="ml-2 font-semibold">{road.defect_count}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Priority:</span>
                      <span className="ml-2 font-semibold text-red-600">{road.priority_score.toFixed(1)}/10</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Cost:</span>
                      <span className="ml-2 font-semibold">{(road.repair_cost / 1000).toFixed(0)}K som</span>
                    </div>
                  </div>
                </div>
                <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                  View on Map
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Impact Summary */}
        <div className="mt-6 p-4 bg-blue-50 rounded">
          <h4 className="font-bold mb-2">Impact of This Plan:</h4>
          <ul className="space-y-1 text-sm">
            <li>🚗 <strong>{plan.reduce((sum, r) => sum + r.defect_count, 0)} defects</strong> will be fixed</li>
            <li>😊 Approximately <strong>{(plan.length * 2500).toLocaleString()} people</strong> benefit daily</li>
            <li>💰 Citizens save <strong>~{(plan.length * 1.35).toFixed(1)}M som/year</strong> on car repairs</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
```

### 6. Impact Calculator (Креативная фича!)

```jsx
// components/ImpactCalculator.jsx
const ImpactCalculator = () => {
  const [roadsToFix, setRoadsToFix] = useState(20);

  const calculate = (numRoads) => {
    return {
      carsSaved: numRoads * 270,
      moneySaved: numRoads * 1.35, // в миллионах
      timeSaved: numRoads * 2250, // в часах
      peopleBenefit: numRoads * 2500
    };
  };

  const impact = calculate(roadsToFix);

  return (
    <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-8 rounded-lg shadow-xl text-white">
      <h2 className="text-3xl font-bold mb-6">💰 Citizen Impact Calculator</h2>
      
      <p className="text-lg mb-4">
        If we repair <strong>TOP {roadsToFix} priority roads:</strong>
      </p>

      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="bg-white bg-opacity-20 p-6 rounded">
          <div className="text-5xl mb-2">🚗</div>
          <div className="text-3xl font-bold">{impact.carsSaved.toLocaleString()}</div>
          <div>Cars saved from damage / year</div>
        </div>

        <div className="bg-white bg-opacity-20 p-6 rounded">
          <div className="text-5xl mb-2">💵</div>
          <div className="text-3xl font-bold">{impact.moneySaved.toFixed(1)}M som</div>
          <div>Money saved by citizens / year</div>
        </div>

        <div className="bg-white bg-opacity-20 p-6 rounded">
          <div className="text-5xl mb-2">⏱️</div>
          <div className="text-3xl font-bold">{impact.timeSaved.toLocaleString()}</div>
          <div>Hours saved (less traffic) / year</div>
        </div>

        <div className="bg-white bg-opacity-20 p-6 rounded">
          <div className="text-5xl mb-2">😊</div>
          <div className="text-3xl font-bold">{impact.peopleBenefit.toLocaleString()}</div>
          <div>Happier citizens daily</div>
        </div>
      </div>

      {/* Slider */}
      <div>
        <label className="block mb-2 font-semibold">
          Select number of roads to repair: {roadsToFix}
        </label>
        <input 
          type="range"
          min="5"
          max="50"
          value={roadsToFix}
          onChange={(e) => setRoadsToFix(parseInt(e.target.value))}
          className="w-full h-3 bg-white bg-opacity-30 rounded-lg cursor-pointer"
        />
        <div className="flex justify-between text-sm mt-1">
          <span>5</span>
          <span>50</span>
        </div>
      </div>
    </div>
  );
};
```

### 7. Navigation & Layout

```jsx
// App.jsx
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100">
        {/* Header */}
        <header className="bg-white shadow">
          <div className="container mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <img src="/logo.svg" alt="Logo" className="h-10" />
              <h1 className="text-2xl font-bold text-blue-600">RoadDoctor</h1>
            </div>
            
            <nav className="flex space-x-6">
              <Link to="/" className="hover:text-blue-600 font-semibold">Map</Link>
              <Link to="/dashboard" className="hover:text-blue-600 font-semibold">Dashboard</Link>
              <Link to="/priority" className="hover:text-blue-600 font-semibold">Priority Planner</Link>
            </nav>
          </div>
        </header>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<MapPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/priority" element={<PriorityPlanner />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
```

### 8. Деплой на Vercel

```bash
# 1. Установить Vercel CLI
npm i -g vercel

# 2. Build проекта
npm run build

# 3. Деплой
vercel

# 4. Или через GitHub:
# - Push код в GitHub
# - Зайти на vercel.com
# - Import GitHub repository
# - Автоматический деплой!
```

---

## 📦 Твой стек:
- **React** (UI)
- **Leaflet.js** (карты)
- **Recharts** (графики)
- **Axios** (HTTP)
- **Tailwind CSS** (стили)
- **React Router** (навигация)

---

## 📂 Структура:
```
frontend/
├── public/
│   ├── index.html
│   └── logo.svg
│
├── src/
│   ├── App.jsx
│   ├── index.jsx
│   │
│   ├── pages/
│   │   ├── MapPage.jsx
│   │   ├── Dashboard.jsx
│   │   └── PriorityPlanner.jsx
│   │
│   ├── components/
│   │   ├── Map.jsx
│   │   ├── Heatmap.jsx
│   │   ├── Filters.jsx
│   │   ├── StatCard.jsx
│   │   └── ImpactCalculator.jsx
│   │
│   ├── services/
│   │   └── api.js           # Axios config
│   │
│   └── styles/
│       └── globals.css
│
├── package.json
└── tailwind.config.js
```

---

## ⏱️ Примерное время:
- **День 1:** 8ч - setup, карта с маркерами, фильтры
- **День 2:** 10ч - heatmap, dashboard, графики
- **День 3:** 8ч - Priority Planner, Impact Calculator, стилизация
- **День 4:** 4ч - финальный polish, деплой, тестирование

---

## 🎯 Output (что передаешь команде):
✅ Рабочее веб-приложение  
✅ Интерактивная карта с маркерами  
✅ Heatmap визуализация  
✅ Dashboard с графиками  
✅ Priority Planner  
✅ Impact Calculator  
✅ Задеплоено на Vercel (public URL)  

---
---

# 👤 УЧАСТНИК 4: Data Collector + QA

## 🎯 Твоя зона ответственности:
Сбор данных по Бишкеку + тестирование всего + помощь команде

---

## 📝 Полный список задач:

### 1. Сбор изображений дорог Бишкека (КРИТИЧЕСКИ ВАЖНО!)

#### Метод 1: Google Street View (Автоматический)
```python
# google_streetview_scraper.py
import requests
import time

API_KEY = "YOUR_GOOGLE_API_KEY"  # Получить на console.cloud.google.com

# Главные улицы Бишкека с координатами
bishkek_streets = [
    {"name": "Chui Avenue", "coords": [
        (42.8746, 74.5698),
        (42.8750, 74.5750),
        (42.8755, 74.5800),
        # ... каждые 50 метров
    ]},
    {"name": "Manas Avenue", "coords": [...]},
    {"name": "Ibraimov Street", "coords": [...]},
    # ... добавить 20-30 главных улиц
]

def download_streetview(lat, lon, heading, filename):
    """
    Скачать панораму Google Street View
    """
    url = f"https://maps.googleapis.com/maps/api/streetview?size=640x640&location={lat},{lon}&heading={heading}&key={API_KEY}"
    
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    time.sleep(0.5)  # Не превышать rate limit

# Скачать изображения для всех точек
for street in bishkek_streets:
    for idx, (lat, lon) in enumerate(street['coords']):
        # 4 направления (север, юг, запад, восток)
        for heading in [0, 90, 180, 270]:
            filename = f"data/bishkek/{street['name']}_{idx}_{heading}.jpg"
            download_streetview(lat, lon, heading, filename)

# Результат: 500-1000+ изображений
```

#### Метод 2: Яндекс.Карты (Ручной сбор)
- Открыть Яндекс.Карты панорамы Бишкека
- Скриншоты дорог (особенно с дефектами)
- Записать координаты каждого изображения

#### Метод 3: Съемка на телефон (Если возможно)
- [ ] Договориться с таксистом/водителем автобуса
- [ ] Установить телефон на крепление
- [ ] Записать 30-60 минут видео проезда по городу
- [ ] Извлечь кадры: 1 кадр каждые 2 секунды = 900-1800 изображений

```python
# extract_frames_from_video.py
import cv2

def extract_frames(video_path, output_folder, interval=2):
    """
    Извлечь кадры из видео
    interval: интервал в секундах
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval)
    
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            filename = f"{output_folder}/frame_{saved_count:04d}.jpg"
            cv2.imwrite(filename, frame)
            saved_count += 1
        
        frame_count += 1
    
    cap.release()
    print(f"Extracted {saved_count} frames")

extract_frames("bishkek_roads.mp4", "data/frames", interval=2)
```

### 2. Добавление GPS координат к изображениям

```python
# add_gps_metadata.py
import piexif
from PIL import Image

def add_gps_to_image(image_path, lat, lon):
    """
    Добавить GPS координаты в EXIF
    """
    img = Image.open(image_path)
    
    # Конвертировать координаты в формат EXIF
    def to_deg(value, loc):
        if value < 0:
            loc_value = loc[0]
        else:
            loc_value = loc[1]
        
        abs_value = abs(value)
        deg = int(abs_value)
        min = int((abs_value - deg) * 60)
        sec = int((abs_value - deg - min/60) * 3600 * 100)
        
        return (deg, 1), (min, 1), (sec, 100), loc_value
    
    lat_deg = to_deg(lat, ["S", "N"])
    lon_deg = to_deg(lon, ["W", "E"])
    
    exif_dict = piexif.load(img.info.get("exif", b""))
    gps_ifd = {
        piexif.GPSIFD.GPSLatitude: (lat_deg[0], lat_deg[1], lat_deg[2]),
        piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
        piexif.GPSIFD.GPSLongitude: (lon_deg[0], lon_deg[1], lon_deg[2]),
        piexif.GPSIFD.GPSLongitudeRef: lon_deg[3],
    }
    exif_dict["GPS"] = gps_ifd
    
    exif_bytes = piexif.dump(exif_dict)
    img.save(image_path, exif=exif_bytes)

# Добавить координаты к каждому изображению
# (lat, lon из bishkek_streets выше)
```

### 3. Сбор статистики по Бишкеку

#### Найти и задокументировать:
- [ ] **Дороги:**
  - Общая длина дорог: ~1,200 км
  - Источник: сайт мэрии Бишкека
  
- [ ] **Бюджет:**
  - Бюджет на ремонт дорог 2024: ? млн сомов
  - Источник: госбюджет КР
  
- [ ] **Проблемы:**
  - Количество жалоб граждан на ямы: ? в год
  - Стоимость средного ремонта машины: ~5,000-15,000 сом
  - ДТП из-за плохих дорог: ? в год
  
- [ ] **Экономика:**
  - Потери из-за пробок: ? млн сомов/год
  - Траты на бензин: +20% из-за пробок

Сохранить всё в:
```
data/research/
├── bishkek_statistics.md
├── sources.txt
└── calculations.xlsx
```

### 4. Тестирование (QA)

#### ML модель (помощь Участнику 1):
- [ ] Протестировать детекцию на 20 случайных изображениях
- [ ] Визуально проверить: правильно ли найдены дефекты?
- [ ] Записать примеры:
  - True Positive (правильно нашли)
  - False Positive (нашли то чего нет)
  - False Negative (пропустили дефект)
- [ ] Сообщить о проблемах

#### Backend API (помощь Участнику 2):
```bash
# Тестирование endpoints
curl http://localhost:8000/api/stats
curl http://localhost:8000/api/defects
curl http://localhost:8000/api/heatmap
curl http://localhost:8000/api/worst-roads

# Проверить:
# - Все endpoints возвращают 200 OK
# - Данные в правильном формате
# - Нет ошибок в console
```

#### Frontend (помощь Участнику 3):
- [ ] **Карта:**
  - Загружаются ли маркеры?
  - Работает ли heatmap toggle?
  - Popup показывается при клике?
  
- [ ] **Dashboard:**
  - Все графики отображаются?
  - Цифры правильные?
  - Топ-10 дорог показывается?
  
- [ ] **Фильтры:**
  - Работает фильтрация по типу?
  - Slider severity работает?
  - Фильтр по району работает?
  
- [ ] **Responsive:**
  - Открыть на телефоне
  - Всё ли читаемо?
  - Кнопки кликабельны?
  
- [ ] **Браузеры:**
  - Chrome ✓
  - Firefox ✓
  - Safari ✓

#### Создать список багов:
```
bugs.md:

1. [HIGH] Heatmap не показывается на iOS Safari
2. [MEDIUM] Popup обрезается на мобильном
3. [LOW] Некоторые тексты не влезают в карточки
...
```

### 5. Организация данных для команды

#### Структура папок:
```
shared-data/
├── images/
│   ├── bishkek_roads/        # Для Участника 1
│   │   ├── chui_ave_001.jpg
│   │   ├── chui_ave_002.jpg
│   │   └── ...
│   └── metadata.csv          # Файл с координатами
│       # filename, lat, lon, street_name, district
│
├── research/
│   ├── statistics.md         # Для презентации
│   ├── sources.txt
│   └── competitor_analysis.md
│
└── testing/
    ├── bugs.md
    ├── test_results.md
    └── screenshots/
```

### 6. Помощь с презентацией (совместно с командой)

#### Сбор материалов:
- [ ] Скриншоты приложения (высокое качество):
  - Карта с маркерами
  - Heatmap
  - Dashboard
  - Priority Planner
  - До/После детекции
  
- [ ] Создать сравнительные таблицы:
```
| Metric              | Manual | Our System |
|---------------------|--------|------------|
| Time to scan city   | 3 mo   | 2 weeks    |
| Cost                | 15M    | 2M         |
| Coverage            | 60%    | 100%       |
| Update frequency    | Yearly | Real-time  |
```

- [ ] Подготовить demo-сценарий:
```
demo_script.md:

СЦЕНА 1: Загрузка изображения (15 сек)
1. Открыть приложение
2. Кликнуть "Upload Image"
3. Выбрать фото дороги с ямой
4. Показать результат детекции

СЦЕНА 2: Карта (20 сек)
1. Открыть Map view
2. Zoom на центр Бишкека
3. Показать маркеры
4. Кликнуть на красный маркер
5. Показать popup с деталями

СЦЕНА 3: Heatmap (15 сек)
1. Toggle на Heatmap
2. Показать красные зоны
3. Объяснить: "Это худшие районы"

СЦЕНА 4: Dashboard (20 сек)
1. Переключиться на Dashboard
2. Показать KPI карточки
3. Показать Top 10 worst roads
4. Объяснить priority scores

СЦЕНА 5: Priority Planner (20 сек)
1. Открыть Priority Planner
2. Показать топ-20 дорог
3. Изменить budget slider
4. Показать impact calculator
```

### 7. Backup и contingency planning

#### Создать backup:
- [ ] Скачать всё приложение локально
- [ ] Записать демо-видео (полное)
- [ ] Сделать статичные скриншоты всех страниц
- [ ] PDF с презентацией на 3 флешках
- [ ] Распечатать ключевые слайды

#### Emergency план:
```
emergency_plan.md:

ЕСЛИ НЕ РАБОТАЕТ ИНТЕРНЕТ:
- Использовать демо-видео
- Показывать статичные скриншоты
- Объяснять вербально

ЕСЛИ НЕ РАБОТАЕТ ПРОЕКТОР:
- Показывать с ноутбука (большой экран)
- Раздать распечатанные слайды жюри

ЕСЛИ СЛОМАЛСЯ КОД:
- Использовать backup версию
- Показывать скриншоты
- Объяснять как должно работать

ЕСЛИ ЗАБЫЛ ТЕКСТ:
- Иметь скрипт в телефоне
- Использовать слайды как подсказки
- Импровизировать (знать суть)
```

### 8. Координация команды

#### Daily standups:
- [ ] Организовать встречи в 10:00 и 20:00
- [ ] Записывать прогресс каждого
- [ ] Отслеживать блокеры
- [ ] Помогать где нужно

#### Создать чеклисты:
```
day1_checklist.md:

Участник 1:
[ ] Датасет скачан
[ ] Обучение запущено
[ ] Inference скрипт работает

Участник 2:
[ ] Backend работает локально
[ ] Базовые endpoints созданы
[ ] ML модель интегрирована

Участник 3:
[ ] React проект создан
[ ] Карта отображается
[ ] Загрузка данных работает

Участник 4:
[ ] Собрано 50+ изображений Бишкека
[ ] Добавлены GPS координаты
[ ] Статистика собрана
```
---

## 📦 Твой стек:
- **Python** (скрипты для сбора данных)
- **Google Maps API**
- **Excel/Google Sheets** (организация данных)
- **Markdown** (документация)
- **Browser DevTools** (тестирование)

---

## 📂 Структура:
```
participant4-work/
├── data-collection/
│   ├── google_streetview_scraper.py
│   ├── extract_frames_from_video.py
│   ├── add_gps_metadata.py
│   └── collected-images/          # 150+ изображений
│
├── research/
│   ├── bishkek_statistics.md
│   ├── sources.txt
│   └── competitor_analysis.md
│
├── testing/
│   ├── bugs.md
│   ├── test_cases.md
│   ├── test_results.md
│   └── screenshots/
│
├── coordination/
│   ├── daily_standups.md
│   ├── checklists/
│   └── project_log.md
│
└── backup/
    ├── demo-video-full.mp4
    ├── screenshots/
    └── emergency_plan.md
```

---

## ⏱️ Примерное время:
- **День 1:** 8ч - сбор изображений, GPS, статистика
- **День 2:** 8ч - продолжение сбора, начало тестирования
- **День 3:** 8ч - полное тестирование, баг-репорты, помощь команде
- **День 4:** 8ч - финальная проверка всего, backup материалы, координация

---

## 🎯 Output (что передаешь команде):
✅ 150+ изображений дорог Бишкека с GPS  
✅ Статистика и исследование  
✅ Полный QA отчет с багами  
✅ Backup материалы (видео, скриншоты)  
✅ Emergency план  
✅ Координация команды (standups, checklists)  

---
---

# 🤝 ИНТЕГРАЦИЯ МЕЖДУ УЧАСТНИКАМИ

## Ключевые точки передачи данных:

### Участник 1 → Участник 2:
```
ml/models/best.pt          # Обученная модель
ml/output/defects.csv      # Данные для карты
ml/output/heatmap.json     # Данные для heatmap
ml/output/districts.json   # Данные по районам
ml/output/worst_roads.json # Топ худших дорог
ml/output/stats.json       # Статистика
```

### Участник 2 → Участник 3:
```
Backend URL: https://your-backend.railway.app
API Documentation: https://your-backend.railway.app/docs

Endpoints:
GET /api/defects
GET /api/heatmap
GET /api/districts
GET /api/worst-roads
GET /api/stats
POST /api/detect (upload image)
```

### Участник 4 → Участник 1:
```
data/bishkek_roads/        # Папка с изображениями
data/metadata.csv          # GPS координаты
data/research/             # Статистика для презентации
```

### Участник 4 → Все:
```
testing/bugs.md            # Баг-репорты
testing/test_results.md    # Результаты тестов
backup/                    # Backup материалы
```

---

# 📊 КОНТРОЛЬНЫЕ ТОЧКИ (Milestones)

## Конец Дня 1 (10 декабря, 20:00):
- **Участник 1:** ✅ Датасет готов, модель обучается
- **Участник 2:** ✅ Backend работает, базовые endpoints
- **Участник 3:** ✅ React app, карта показывает тестовые данные
- **Участник 4:** ✅ 50+ изображений собрано, GPS добавлен

## Конец Дня 2 (11 декабря, 20:00):
- **Участник 1:** ✅ Модель обучена, все датасеты сгенерированы
- **Участник 2:** ✅ Все endpoints работают, ML интегрирована
- **Участник 3:** ✅ Карта + heatmap + dashboard базовый
- **Участник 4:** ✅ 150+ изображений, начато тестирование

## Конец Дня 3 (12 декабря, 20:00):
- **Участник 1:** ✅ Визуализации готовы, документация
- **Участник 2:** ✅ Задеплоено на Railway
- **Участник 3:** ✅ Всё работает, задеплоено на Vercel
- **Участник 4:** ✅ Полный QA, backup готов

## Конец Дня 4 (13 декабря, 20:00):
- **Все:** ✅ Всё работает end-to-end
- **Все:** ✅ Презентация и питч готовы
- **Все:** ✅ Готовы к выступлению!

---

# 💬 КОММУНИКАЦИЯ

## Telegram группа:
```
Правила:
1. Быстрые ответы (< 1 час)
2. @ упоминания для срочного
3. Если блокер - пишем сразу
4. Делимся progress (скриншоты!)
5. Поддерживаем друг друга 💪

Примеры хороших сообщений:
"@Участник2 готов defects.csv, где залить?"
"Модель обучена! Accuracy 76.3% 🎉"
"@all Standup в 20:00, не забудьте!"
```

## GitHub:
```
Ветки:
main           # Production
dev            # Development
feature/ml     # Участник 1
feature/backend # Участник 2
feature/frontend # Участник 3
feature/data   # Участник 4

Коммиты:
✅ "Add severity scoring algorithm"
✅ "Implement heatmap endpoint"
✅ "Add priority planner component"
❌ "update"
❌ "fix"
```

---

# 🎯 КРИТЕРИИ УСПЕХА

## Минимум (MVP):
- [ ] ML модель работает (70%+ accuracy)
- [ ] 100+ изображений Бишкека обработаны
- [ ] Карта с маркерами работает
- [ ] Heatmap работает
- [ ] Dashboard с базовой статистикой
- [ ] Всё задеплоено и доступно

## Хорошо:
- [ ] Всё выше +
- [ ] Priority Planner работает
- [ ] Impact Calculator работает
- [ ] Красивый дизайн
- [ ] Мобильная версия работает

## Отлично (победа!):
- [ ] Всё выше +
- [ ] Код на GitHub чистый и документированный
- [ ] 0 критических багов
- [ ] Презентация killer
- [ ] Live demo работает без глюков

---

**Удачи команде! Каждый делает свою техническую часть, презентацию и питч потом вместе подготовите! 🚀💪**
