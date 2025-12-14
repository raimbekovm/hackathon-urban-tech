#!/usr/bin/env python3
"""
Generate real defect data from annotated images
Creates CSV with random Bishkek coordinates and real image paths
"""

import os
import csv
import random
import shutil
from pathlib import Path

# Class mapping
CLASS_NAMES = {
    0: 'longitudinal_crack',
    1: 'transverse_crack',
    2: 'alligator_crack',
    3: 'pothole'
}

# Bishkek coordinates - different districts
# Format: (center_lat, center_lon, radius_km, district_name)
BISHKEK_ZONES = [
    (42.8746, 74.5698, 0.02, "Свердловский район"),  # Center
    (42.8900, 74.5850, 0.015, "Первомайский район"),  # North
    (42.8600, 74.5600, 0.015, "Ленинский район"),     # Southwest
    (42.8500, 74.5900, 0.015, "Октябрьский район"),   # South
    (42.8850, 74.5650, 0.015, "Свердловский район"),  # Northwest
    (42.8650, 74.5750, 0.012, "Ленинский район"),     # Center-West
    (42.8800, 74.5800, 0.012, "Первомайский район"),  # North-Center
]

# Street names for each zone
STREETS_BY_ZONE = {
    "Свердловский район": [
        "Чуйский проспект", "Киевская улица", "Московская улица",
        "Токтогула улица", "Байтик Баатыра улица"
    ],
    "Первомайский район": [
        "Жибек Жолу проспект", "Ала-Арчинская улица", "Уметалиева улица",
        "Куренкеева улица", "Мичурина улица"
    ],
    "Ленинский район": [
        "Льва Толстого улица", "Абдыкадырова улица", "Чокморова улица",
        "Димитрова улица", "Московская улица"
    ],
    "Октябрьский район": [
        "Фрунзе улица", "Ибраимова улица", "Панфилова улица",
        "Тыныстанова улица", "Боконбаева улица"
    ]
}

def generate_random_coordinate(zone):
    """Generate random coordinate within zone"""
    center_lat, center_lon, radius, district = zone

    # Random offset within radius
    angle = random.uniform(0, 2 * 3.14159)
    distance = random.uniform(0, radius)

    lat = center_lat + distance * cos(angle)
    lon = center_lon + distance * sin(angle)

    return lat, lon, district

def cos(angle):
    """Simple cosine approximation"""
    import math
    return math.cos(angle)

def sin(angle):
    """Simple sine approximation"""
    import math
    return math.sin(angle)

def parse_yolo_label(label_path):
    """Parse YOLO label file and return list of detections"""
    detections = []

    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])

                detections.append({
                    'class_id': class_id,
                    'class_name': CLASS_NAMES.get(class_id, 'unknown'),
                    'x_center': x_center,
                    'y_center': y_center,
                    'width': width,
                    'height': height
                })

    return detections

def calculate_severity(bbox_width, bbox_height, defect_type):
    """Calculate defect severity based on size and type"""
    # Size factor (larger = more severe)
    size_factor = (bbox_width + bbox_height) / 2.0 * 10

    # Type severity weights
    type_weights = {
        'pothole': 1.2,
        'alligator_crack': 1.1,
        'longitudinal_crack': 0.8,
        'transverse_crack': 0.9,
        'unknown': 1.0
    }

    type_factor = type_weights.get(defect_type, 1.0)

    # Calculate severity (1-10 scale)
    severity = min(10.0, max(1.0, size_factor * type_factor))

    return round(severity, 1)

def main():
    print("🚀 Generating real defect data from annotated images...\n")

    # Paths
    base_path = Path(__file__).parent
    dataset_path = base_path / 'data' / 'urban_tech'
    output_path = base_path / 'output'
    output_path.mkdir(exist_ok=True)

    # Output CSV path
    csv_path = output_path / 'defects.csv'

    # Collect all images and labels
    image_label_pairs = []

    # Train set
    train_images = dataset_path / 'train' / 'images'
    train_labels = dataset_path / 'train' / 'labels'

    for img_file in train_images.glob('*.jpg'):
        label_file = train_labels / (img_file.stem + '.txt')
        if label_file.exists():
            image_label_pairs.append((img_file, label_file, 'train'))

    # Test set
    test_images = dataset_path / 'test' / 'images'
    test_labels = dataset_path / 'test' / 'labels'

    for img_file in test_images.glob('*.jpg'):
        label_file = test_labels / (img_file.stem + '.txt')
        if label_file.exists():
            image_label_pairs.append((img_file, label_file, 'test'))

    print(f"Found {len(image_label_pairs)} images with labels\n")

    # Generate defects CSV
    all_defects = []
    defect_id = 1

    for img_path, label_path, split in image_label_pairs:
        # Parse labels
        detections = parse_yolo_label(label_path)

        if not detections:
            continue

        # Assign random zone to this image
        zone = random.choice(BISHKEK_ZONES)

        for detection in detections:
            # Generate random coordinates in zone
            lat, lon, district = generate_random_coordinate(zone)

            # Get random street name for district
            streets = STREETS_BY_ZONE.get(district, ["Unknown Street"])
            street_name = random.choice(streets)

            # Calculate severity
            severity = calculate_severity(
                detection['width'],
                detection['height'],
                detection['class_name']
            )

            # Random confidence (high for real annotations)
            confidence = round(random.uniform(0.85, 0.98), 2)

            # Relative path to image from frontend
            relative_img_path = f"ml/data/urban_tech/{split}/images/{img_path.name}"

            all_defects.append({
                'lat': round(lat, 6),
                'lon': round(lon, 6),
                'defect_type': detection['class_name'],
                'severity': severity,
                'confidence': confidence,
                'image_path': relative_img_path,
                'street_name': street_name,
                'district': district
            })

            print(f"  [{defect_id}] {detection['class_name']} on {street_name} (severity: {severity})")
            defect_id += 1

    # Write CSV
    print(f"\n📝 Writing {len(all_defects)} defects to {csv_path}")

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'lat', 'lon', 'defect_type', 'severity', 'confidence',
            'image_path', 'street_name', 'district'
        ])
        writer.writeheader()
        writer.writerows(all_defects)

    # Generate stats.json
    print("\n📊 Generating statistics...")

    total_defects = len(all_defects)
    critical_defects = sum(1 for d in all_defects if d['severity'] >= 7)

    # Calculate total repair cost (rough estimate)
    total_cost = sum(d['severity'] * 5000 + random.randint(2000, 8000) for d in all_defects)

    stats = {
        "total_stats": {
            "total_defects": total_defects,
            "critical_defects": critical_defects,
            "total_repair_cost": int(total_cost)
        }
    }

    import json
    with open(output_path / 'stats.json', 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"  Total defects: {total_defects}")
    print(f"  Critical defects: {critical_defects}")
    print(f"  Estimated repair cost: {total_cost:,} KGS")

    # Generate worst roads
    print("\n🏆 Calculating worst roads...")

    from collections import defaultdict
    roads_data = defaultdict(lambda: {
        'defects': [],
        'lat_sum': 0,
        'lon_sum': 0,
        'count': 0
    })

    for defect in all_defects:
        road_key = (defect['street_name'], defect['district'])
        roads_data[road_key]['defects'].append(defect)
        roads_data[road_key]['lat_sum'] += defect['lat']
        roads_data[road_key]['lon_sum'] += defect['lon']
        roads_data[road_key]['count'] += 1

    worst_roads = []
    for (street, district), data in roads_data.items():
        defect_count = data['count']
        avg_severity = sum(d['severity'] for d in data['defects']) / defect_count
        avg_lat = data['lat_sum'] / defect_count
        avg_lon = data['lon_sum'] / defect_count

        # Priority score
        priority_score = min(10.0, avg_severity * 0.6 + (defect_count / 5) * 0.4)

        worst_roads.append({
            'street_name': street,
            'district': district,
            'defect_count': defect_count,
            'avg_severity': round(avg_severity, 1),
            'priority_score': round(priority_score, 1),
            'lat': round(avg_lat, 6),
            'lon': round(avg_lon, 6)
        })

    # Sort by priority
    worst_roads.sort(key=lambda x: x['priority_score'], reverse=True)

    # Add ranks
    for i, road in enumerate(worst_roads[:10], 1):
        road['rank'] = i

    with open(output_path / 'worst_roads.json', 'w') as f:
        json.dump({'worst_roads': worst_roads[:10]}, f, indent=2)

    print(f"  Top worst road: {worst_roads[0]['street_name']} ({worst_roads[0]['defect_count']} defects)")

    # Generate heatmap
    print("\n🔥 Generating heatmap data...")

    heatmap_data = [[d['lat'], d['lon'], min(1.0, d['severity'] / 10.0)] for d in all_defects]

    with open(output_path / 'heatmap.json', 'w') as f:
        json.dump({'heatmap_data': heatmap_data}, f)

    print(f"  Heatmap points: {len(heatmap_data)}")

    # Generate districts summary
    print("\n📍 Generating districts summary...")

    district_stats = defaultdict(lambda: {
        'defect_count': 0,
        'total_severity': 0,
        'lat_sum': 0,
        'lon_sum': 0
    })

    for defect in all_defects:
        d = defect['district']
        district_stats[d]['defect_count'] += 1
        district_stats[d]['total_severity'] += defect['severity']
        district_stats[d]['lat_sum'] += defect['lat']
        district_stats[d]['lon_sum'] += defect['lon']

    districts = []
    for district, stats_data in district_stats.items():
        count = stats_data['defect_count']
        districts.append({
            'district': district,
            'defect_count': count,
            'avg_severity': round(stats_data['total_severity'] / count, 1),
            'lat': round(stats_data['lat_sum'] / count, 6),
            'lon': round(stats_data['lon_sum'] / count, 6)
        })

    with open(output_path / 'districts.json', 'w') as f:
        json.dump({'districts': districts}, f, indent=2)

    print(f"  Districts analyzed: {len(districts)}")

    print("\n✅ Done! Generated files:")
    print(f"   - {csv_path}")
    print(f"   - {output_path}/stats.json")
    print(f"   - {output_path}/worst_roads.json")
    print(f"   - {output_path}/heatmap.json")
    print(f"   - {output_path}/districts.json")
    print("\n🚀 Refresh your browser to see real annotated defects!")

if __name__ == '__main__':
    main()
