#!/usr/bin/env python3
"""
Generate defect data with annotated bounding boxes
- 45 real images with YOLO boxes drawn
- Clustered points for heatmap visibility
- 10 critical defects
- Real street names via Nominatim
"""

import os
import csv
import random
import time
import json
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont

# Class mapping and colors (FIXED)
CLASS_NAMES = {
    0: 'alligator_crack',      # было longitudinal_crack
    1: 'longitudinal_crack',   # было transverse_crack
    2: 'pothole',              # было alligator_crack
    3: 'transverse_crack'      # было pothole
}

CLASS_COLORS = {
    0: (0, 0, 255),      # Blue for alligator_crack
    1: (255, 0, 0),      # Red for longitudinal_crack
    2: (255, 165, 0),    # Orange for pothole
    3: (0, 255, 0)       # Green for transverse_crack
}

# Bishkek zones for clustering
BISHKEK_ZONES = [
    {'name': 'Center', 'lat': 42.876, 'lon': 74.612, 'radius': 0.015},
    {'name': 'North', 'lat': 42.910, 'lon': 74.590, 'radius': 0.015},
    {'name': 'South', 'lat': 42.830, 'lon': 74.580, 'radius': 0.015},
    {'name': 'East', 'lat': 42.870, 'lon': 74.640, 'radius': 0.015},
    {'name': 'West', 'lat': 42.860, 'lon': 74.540, 'radius': 0.015},
]

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

def generate_zone_coordinate(zone):
    """Generate coordinate within a zone with small variation"""
    lat = zone['lat'] + random.uniform(-zone['radius'], zone['radius'])
    lon = zone['lon'] + random.uniform(-zone['radius'], zone['radius'])
    return lat, lon

def parse_yolo_label(label_path):
    """Parse YOLO label file and return ALL detections"""
    detections = []
    with open(label_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
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
    return detections if detections else None

def draw_yolo_box_on_image(image_path, label_path, output_path):
    """Draw ALL YOLO bounding boxes on image"""
    # Parse all detections
    detections = parse_yolo_label(label_path)
    if not detections:
        return False

    # Open image
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    img_width, img_height = img.size

    # Try to use a better font, fallback to default
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except:
        font = ImageFont.load_default()

    # Draw each detection
    for detection in detections:
        # Convert YOLO format to pixel coordinates
        x_center = detection['x_center'] * img_width
        y_center = detection['y_center'] * img_height
        box_width = detection['width'] * img_width
        box_height = detection['height'] * img_height

        # Calculate corners
        x1 = int(x_center - box_width / 2)
        y1 = int(y_center - box_height / 2)
        x2 = int(x_center + box_width / 2)
        y2 = int(y_center + box_height / 2)

        # Get color for class
        color = CLASS_COLORS.get(detection['class_id'], (255, 255, 0))

        # Draw rectangle
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

        # Draw label
        label_text = detection['class_name'].replace('_', ' ').title()

        # Draw text background
        text_bbox = draw.textbbox((x1, y1 - 20), label_text, font=font)
        draw.rectangle(text_bbox, fill=color)
        draw.text((x1, y1 - 20), label_text, fill=(255, 255, 255), font=font)

    # Save annotated image
    img.save(output_path, quality=95)
    return True

def calculate_severity(bbox_width, bbox_height, defect_type, force_critical=False):
    """Calculate defect severity based on size and type"""
    if force_critical:
        # Critical defects: 7.0 to 9.5
        return round(random.uniform(7.0, 9.5), 1)

    size_factor = (bbox_width + bbox_height) / 2.0 * 10

    type_weights = {
        'pothole': 1.2,
        'alligator_crack': 1.1,
        'longitudinal_crack': 0.8,
        'transverse_crack': 0.9,
        'unknown': 1.0
    }

    type_factor = type_weights.get(defect_type, 1.0)
    severity = min(6.5, max(1.0, size_factor * type_factor))

    return round(severity, 1)

def main():
    print("🚀 Generating defect data with bounding boxes...\n")

    # Paths
    base_path = Path(__file__).parent
    source_dataset = Path('/tmp/urban_tech_full')
    output_dataset = base_path / 'data' / 'urban_tech_annotated'
    output_path = base_path / 'output'

    # Create output directories
    output_dataset.mkdir(parents=True, exist_ok=True)
    (output_dataset / 'images').mkdir(exist_ok=True)
    output_path.mkdir(exist_ok=True)

    csv_path = output_path / 'defects.csv'

    # Collect all images and labels from source
    image_label_pairs = []

    # Train set
    train_images = source_dataset / 'train' / 'images'
    train_labels = source_dataset / 'train' / 'labels'

    if train_images.exists():
        for img_file in sorted(train_images.glob('*.jpg')):
            label_file = train_labels / (img_file.stem + '.txt')
            if label_file.exists():
                image_label_pairs.append((img_file, label_file, 'train'))

    # Test set
    test_images = source_dataset / 'test' / 'images'
    test_labels = source_dataset / 'test' / 'labels'

    if test_images.exists():
        for img_file in sorted(test_images.glob('*.jpg')):
            label_file = test_labels / (img_file.stem + '.txt')
            if label_file.exists():
                image_label_pairs.append((img_file, label_file, 'test'))

    print(f"Found {len(image_label_pairs)} images with labels\n")

    if len(image_label_pairs) == 0:
        print("❌ No images found! Check source path.")
        return

    # Exclude demo photos (for upload demo feature)
    DEMO_PHOTOS = [
        'Screenshot-2025-12-12-at-22_11_11_png.rf.22264ac682b70f7a8c043ae1e038aa64.jpg',
        'Screenshot-2025-12-12-at-21_53_25_png.rf.556655d102e355fc528a9f86930c376f.jpg'
    ]

    # Filter out demo photos
    image_label_pairs = [
        (img, lbl, split) for (img, lbl, split) in image_label_pairs
        if img.name not in DEMO_PHOTOS
    ]

    print(f"After excluding demo photos: {len(image_label_pairs)} images\n")

    # Mark 10 random indices as critical
    critical_indices = random.sample(range(len(image_label_pairs)), min(10, len(image_label_pairs)))

    print("Drawing bounding boxes on images and generating data...\n")

    all_defects = []
    zone_index = 0

    for idx, (img_path, label_path, split) in enumerate(image_label_pairs, 1):
        # Parse all detections
        detections = parse_yolo_label(label_path)

        if not detections:
            print(f"  [{idx}] No detection in {img_path.name}")
            continue

        # Output annotated image path
        output_img_path = output_dataset / 'images' / img_path.name

        # Draw ALL boxes on image
        print(f"  [{idx}/{len(image_label_pairs)}] Drawing {len(detections)} boxes on {img_path.name}...", end=' ')
        if draw_yolo_box_on_image(img_path, label_path, output_img_path):
            print("✓")
        else:
            print("✗ Failed")
            continue

        # Use first detection for data generation (one marker per image)
        first_detection = detections[0]

        # Generate coordinates in zones (for clustering)
        zone = BISHKEK_ZONES[zone_index % len(BISHKEK_ZONES)]
        lat, lon = generate_zone_coordinate(zone)
        zone_index += 1

        # Get real street name via API
        print(f"  [{idx}/{len(image_label_pairs)}] ", end='')
        street_name, district = get_street_name(lat, lon)

        # Calculate severity
        is_critical = idx - 1 in critical_indices
        severity = calculate_severity(
            first_detection['width'],
            first_detection['height'],
            first_detection['class_name'],
            force_critical=is_critical
        )

        # Random confidence
        confidence = round(random.uniform(0.85, 0.98), 2)

        # Relative path to annotated image
        relative_img_path = f"ml/data/urban_tech_annotated/images/{img_path.name}"

        all_defects.append({
            'lat': round(lat, 6),
            'lon': round(lon, 6),
            'defect_type': first_detection['class_name'],
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
    print(f"   - {len(all_defects)} annotated images in {output_dataset}/images/")
    print(f"\n🚀 Refresh your browser to see {len(all_defects)} defects with annotated photos!")

if __name__ == '__main__':
    main()
