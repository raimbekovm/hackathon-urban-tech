#!/usr/bin/env python3
"""
Generate real defect data from annotated images - ONE DEFECT PER IMAGE
Uses real street names via Nominatim API
Distributes evenly across all Bishkek
"""

import os
import csv
import random
import time
import json
from pathlib import Path
import requests

# Class mapping
CLASS_NAMES = {
    0: 'longitudinal_crack',
    1: 'transverse_crack',
    2: 'alligator_crack',
    3: 'pothole'
}

# Bishkek bounding box - full city coverage
BISHKEK_BOUNDS = {
    'north': 42.92,   # Северная граница
    'south': 42.82,   # Южная граница
    'east': 74.65,    # Восточная граница
    'west': 74.52     # Западная граница
}

def get_street_name(lat, lon):
    """Get real street name from coordinates using Nominatim"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'addressdetails': 1,
            'accept-language': 'ru'
        }
        headers = {
            'User-Agent': 'RoadDoctor/1.0 (Hackathon)'
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})

            street = (
                address.get('road') or
                address.get('street') or
                address.get('pedestrian') or
                address.get('suburb') or
                address.get('neighbourhood') or
                'Unknown Street'
            )

            district = (
                address.get('suburb') or
                address.get('city_district') or
                address.get('neighbourhood') or
                'Unknown District'
            )

            print(f"  ✓ ({lat:.4f}, {lon:.4f}) → {street}, {district}")
            return street, district
        else:
            print(f"  ✗ Error {response.status_code}")
            return 'Unknown Street', 'Unknown District'

    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return 'Unknown Street', 'Unknown District'

def generate_random_coordinate():
    """Generate random coordinate anywhere in Bishkek"""
    lat = random.uniform(BISHKEK_BOUNDS['south'], BISHKEK_BOUNDS['north'])
    lon = random.uniform(BISHKEK_BOUNDS['west'], BISHKEK_BOUNDS['east'])
    return lat, lon

def parse_yolo_label(label_path):
    """Parse YOLO label file and return FIRST detection only"""
    with open(label_path, 'r') as f:
        line = f.readline().strip()
        if not line:
            return None

        parts = line.split()
        if len(parts) >= 5:
            class_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])

            return {
                'class_id': class_id,
                'class_name': CLASS_NAMES.get(class_id, 'unknown'),
                'x_center': x_center,
                'y_center': y_center,
                'width': width,
                'height': height
            }
    return None

def calculate_severity(bbox_width, bbox_height, defect_type):
    """Calculate defect severity based on size and type"""
    size_factor = (bbox_width + bbox_height) / 2.0 * 10

    type_weights = {
        'pothole': 1.2,
        'alligator_crack': 1.1,
        'longitudinal_crack': 0.8,
        'transverse_crack': 0.9,
        'unknown': 1.0
    }

    type_factor = type_weights.get(defect_type, 1.0)
    severity = min(10.0, max(1.0, size_factor * type_factor))

    return round(severity, 1)

def main():
    print("🚀 Generating real defect data - ONE DEFECT PER IMAGE...\n")

    # Paths
    base_path = Path(__file__).parent
    dataset_path = base_path / 'data' / 'portfolio_samples'
    output_path = base_path / 'output'
    output_path.mkdir(exist_ok=True)

    csv_path = output_path / 'defects.csv'

    # Collect all images and labels
    image_label_pairs = []

    # Portfolio samples (no train/test split)
    images_dir = dataset_path / 'images'
    labels_dir = dataset_path / 'labels'

    for img_file in sorted(images_dir.glob('*.jpg')):
        label_file = labels_dir / (img_file.stem + '.txt')
        if label_file.exists():
            image_label_pairs.append((img_file, label_file, 'portfolio'))

    print(f"Found {len(image_label_pairs)} images with labels\n")
    print("Generating coordinates and fetching street names...\n")

    # Generate defects CSV - ONE PER IMAGE
    all_defects = []

    for idx, (img_path, label_path, split) in enumerate(image_label_pairs, 1):
        # Parse FIRST detection only
        detection = parse_yolo_label(label_path)

        if not detection:
            print(f"  [{idx}] No detection in {img_path.name}")
            continue

        # Generate random coordinates in Bishkek
        lat, lon = generate_random_coordinate()

        # Get real street name via API
        print(f"  [{idx}/{len(image_label_pairs)}] ", end='')
        street_name, district = get_street_name(lat, lon)

        # Calculate severity
        severity = calculate_severity(
            detection['width'],
            detection['height'],
            detection['class_name']
        )

        # Random confidence (high for real annotations)
        confidence = round(random.uniform(0.85, 0.98), 2)

        # Relative path to image from web root
        relative_img_path = f"ml/data/portfolio_samples/images/{img_path.name}"

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

        # Rate limit: 1 request per second
        if idx < len(image_label_pairs):
            time.sleep(1.1)

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
    total_cost = sum(d['severity'] * 5000 + random.randint(2000, 8000) for d in all_defects)

    stats = {
        "total_stats": {
            "total_defects": total_defects,
            "critical_defects": critical_defects,
            "total_repair_cost": int(total_cost)
        }
    }

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

    worst_roads.sort(key=lambda x: x['priority_score'], reverse=True)

    for i, road in enumerate(worst_roads[:10], 1):
        road['rank'] = i

    with open(output_path / 'worst_roads.json', 'w') as f:
        json.dump({'worst_roads': worst_roads[:10]}, f, indent=2)

    if worst_roads:
        print(f"  Top worst road: {worst_roads[0]['street_name']} ({worst_roads[0]['defect_count']} defects)")
    else:
        print("  No roads found")

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
    print("\n🚀 Refresh your browser to see {len(all_defects)} real defects with photos!")

if __name__ == '__main__':
    main()
