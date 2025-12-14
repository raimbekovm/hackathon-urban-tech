# 🚀 RoadDoctor - Development Branch

> **Live Demo:** [https://raimbekovm.github.io/hackathon-urban-tech/](https://raimbekovm.github.io/hackathon-urban-tech/)
> **Main Branch:** [Production Frontend](https://github.com/raimbekovm/hackathon-urban-tech/tree/main)

This is the **development branch** containing the complete RoadDoctor system: ML pipeline, training notebooks, datasets, and frontend application.

## 📋 What's in This Branch

This branch contains the **full development environment** with:

✅ **Complete ML Pipeline** - Detection, analysis, and data processing
✅ **Frontend Application** - Interactive dashboard with all visualization modes
✅ **Training Notebooks** - Kaggle notebooks for model fine-tuning
✅ **Custom Datasets** - Annotated Bishkek road images
✅ **Documentation** - Setup guides and API references

## 📁 Directory Structure

```
dev/
├── frontend/                    # Web dashboard application
│   ├── index.html              # Main page
│   ├── app.js                  # Application logic
│   └── README.md               # Frontend-specific docs
│
├── ml/                         # Machine learning pipeline
│   ├── data/                   # Training and test data
│   │   ├── bishkek_roads/     # 45 real street images
│   │   ├── portfolio_samples/  # 9 annotated examples (showcase)
│   │   │   ├── images/        # Sample photos
│   │   │   ├── labels/        # YOLO annotations
│   │   │   └── README.md      # Annotation documentation
│   │   └── urban_tech/        # Full training dataset
│   │       ├── train/         # Training images & labels
│   │       ├── test/          # Test images & labels
│   │       └── data.yaml      # Dataset configuration
│   │
│   ├── notebooks/             # Jupyter/Kaggle notebooks
│   │   └── train_rdd2022_kaggle.ipynb  # YOLOv8 training
│   │
│   ├── output/                # Generated detection results
│   │   ├── defects.csv       # All defects with coordinates
│   │   ├── worst_roads.json  # Priority-ranked roads
│   │   ├── heatmap.json      # Heatmap intensity data
│   │   ├── stats.json        # Statistical summaries
│   │   └── districts.json    # District aggregations
│   │
│   ├── utils/                # Helper functions
│   │   ├── scoring.py        # Severity & priority algorithms
│   │   └── visualization.py  # Chart generation
│   │
│   ├── process_real_data.py  # Main ML pipeline
│   ├── get_street_names.py   # Reverse geocoding script
│   └── README.md             # ML documentation
│
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
pip
Git
```

### 1. Clone and Setup
```bash
# Clone repository and switch to dev branch
git clone https://github.com/raimbekovm/hackathon-urban-tech.git
cd hackathon-urban-tech
git checkout dev

# Set up ML environment
cd ml
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run ML Pipeline
```bash
# Process road images and detect defects
python process_real_data.py

# Add real street names via geocoding (optional)
python get_street_names.py
```

This generates output files in `ml/output/`:
- `defects.csv` - All detected defects
- `worst_roads.json` - Priority-ranked roads
- `heatmap.json` - Heatmap data
- `stats.json` - Statistics
- `districts.json` - District summaries

### 3. Launch Frontend
```bash
# Go back to root and start server
cd ..
python3 -m http.server 8000

# Open in browser
open http://localhost:8000/frontend/
```

## 🎯 Development Workflow

### Working with Datasets

#### Portfolio Samples (9 images)
Example annotations for showcase:
```bash
ls ml/data/portfolio_samples/images/
# Screenshot_001.jpg ... Screenshot_009.jpg

ls ml/data/portfolio_samples/labels/
# Screenshot_001.txt ... Screenshot_009.txt
```

#### Full Training Dataset
Complete dataset for model training:
```bash
# View dataset structure
cat ml/data/urban_tech/data.yaml

# Training data
ls ml/data/urban_tech/train/images/
ls ml/data/urban_tech/train/labels/
```

### Training Model on Kaggle

1. Upload `ml/notebooks/train_rdd2022_kaggle.ipynb` to Kaggle
2. Enable GPU accelerator
3. Update dataset paths
4. Run all cells (50 epochs, ~2 hours)
5. Download trained weights

### Processing New Images

Add new road images to `ml/data/bishkek_roads/`:
```bash
# Add your images
cp /path/to/images/*.jpg ml/data/bishkek_roads/

# Run detection
cd ml
python process_real_data.py

# Update with street names
python get_street_names.py
```

### Updating Frontend Data

After running ML pipeline, data is automatically available:
```bash
# Frontend reads from ml/output/
frontend/app.js → loads ../ml/output/defects.csv
frontend/app.js → loads ../ml/output/worst_roads.json
# etc.
```

## 🛠️ Technology Stack

### ML Pipeline
- **YOLOv8n** - Object detection (Ultralytics)
- **OpenCV** - Image processing
- **Pandas** - Data manipulation
- **Roboflow** - Dataset annotation
- **Nominatim** - Reverse geocoding (OpenStreetMap)

### Frontend
- **Leaflet.js** - Interactive maps
- **Leaflet.heat** - Heatmap plugin
- **Chart.js** - Data visualization
- **Vanilla JS** - No frameworks

## 📊 Data Annotations

### Annotation Format
YOLO format (.txt files):
```
class_id x_center y_center width height
```

Example:
```
0 0.673745 0.704904 0.258170 0.353179  # longitudinal_crack
3 0.486070 0.422343 0.084577 0.179837  # pothole
```

### Classes
- `0` - longitudinal_crack (Продольная трещина)
- `1` - transverse_crack (Поперечная трещина)
- `2` - alligator_crack (Сетка трещин)
- `3` - pothole (Яма)

### Annotation Statistics
- **Total images**: 45
- **Training set**: 39 images
- **Test set**: 6 images
- **Total objects**: 172
  - Longitudinal cracks: 67
  - Transverse cracks: 11
  - Alligator cracks: 63
  - Potholes: 31

See `ml/data/portfolio_samples/ANNOTATION_EXAMPLES.md` for details.

## 🔧 Configuration

### Dataset Config (`ml/data/urban_tech/data.yaml`)
```yaml
path: /kaggle/working/urban_tech
train: train/images
val: valid/images
test: test/images

names:
  0: longitudinal_crack
  1: transverse_crack
  2: alligator_crack
  3: pothole
```

### Model Training Parameters
```python
model = YOLO('yolov8n.pt')
results = model.train(
    data='data.yaml',
    epochs=50,
    imgsz=640,
    batch=16,
    name='road_defects'
)
```

## 📈 ML Pipeline Workflow

1. **Image Collection** → Screenshots from Google Maps Street View
2. **Annotation** → Manual labeling in Roboflow (YOLO format)
3. **Training** → YOLOv8 fine-tuning on Kaggle GPU
4. **Inference** → Detect defects in new images
5. **Post-processing** → Severity scoring, priority ranking
6. **Geocoding** → Add street names via Nominatim API
7. **Export** → Generate JSON/CSV for frontend

## 🧪 Testing

### Test ML Pipeline
```bash
cd ml
python -c "from utils.scoring import calculate_severity; print(calculate_severity(100, 80, 'pothole', 0.95))"
# Expected: ~8.5 (high severity)
```

### Test Frontend Locally
```bash
python3 -m http.server 8000
open http://localhost:8000/frontend/
```

## 🚀 Deployment

### Deploy to GitHub Pages
```bash
# Merge dev to main
git checkout main
git merge dev

# Push to trigger GitHub Actions
git push origin main

# GitHub Actions automatically deploys to gh-pages
```

### Manual Deployment
```bash
# Use provided script
./update-gh-pages.sh
```

## 📝 Development Guidelines

### Adding New Features

1. **Create feature branch**
   ```bash
   git checkout -b feature/new-visualization
   ```

2. **Make changes**
   - Update ML pipeline or frontend
   - Test locally
   - Update documentation

3. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: add new visualization mode"
   git push origin feature/new-visualization
   ```

4. **Create pull request** to dev branch

### Code Style

- **Python**: PEP 8
- **JavaScript**: ESLint recommended
- **Commits**: Conventional Commits format
  - `feat:` - New features
  - `fix:` - Bug fixes
  - `docs:` - Documentation
  - `chore:` - Maintenance

## 🐛 Troubleshooting

### Common Issues

**Q: ML pipeline shows "No defects detected"**
A: Check if images are in correct folder and model weights are downloaded

**Q: Frontend shows 404 errors**
A: Verify relative paths in `app.js` are correct (`../ml/output/`)

**Q: Geocoding is slow**
A: Nominatim has 1 request/second rate limit - this is normal

**Q: Training fails on Kaggle**
A: Ensure dataset paths match Kaggle file structure

See `DEBUG.md` for detailed troubleshooting.

## 👥 Team & Contributors

**Urban Tech Hackathon 2025**
- ML Engineering & Dataset Annotation
- Frontend Development & UI/UX
- Data Science & Analytics
- Project Management

## 📄 License

MIT License - Developed for Urban Tech Hackathon 2025

## 🔗 Related Links

- [Live Demo](https://raimbekovm.github.io/hackathon-urban-tech/)
- [Main Branch (Production)](https://github.com/raimbekovm/hackathon-urban-tech/tree/main)
- [GitHub Pages Branch](https://github.com/raimbekovm/hackathon-urban-tech/tree/gh-pages)
- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [RDD2022 Dataset](https://github.com/sekilab/RoadDamageDetector)

---

**Development Status:** Active
**Last Updated:** December 2025
**Built with ❤️ for making Bishkek roads safer**
