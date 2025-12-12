"""
Data Generator for Frontend Integration
Generates mock data simulating road defects in Bishkek

Output files:
- output/defects.csv: All defects with coordinates
- output/heatmap.json: Heatmap data for visualization
- output/districts.json: Statistics by district
- output/worst_roads.json: Top worst roads ranked
- output/stats.json: Overall statistics for dashboard
"""

import json
import csv
import random
import os
from collections import defaultdict
import sys

# Add utils to path
sys.path.append(os.path.dirname(__file__))
from utils.scoring import (
    calculate_severity, calculate_priority,
    calculate_road_quality, estimate_repair_cost,
    categorize_severity
)


# Bishkek city center coordinates
BISHKEK_CENTER = (42.8746, 74.5698)

# Districts of Bishkek
DISTRICTS = ['Sverdlovsky', 'Leninsky', 'Pervomaysky', 'Oktyabrsky']

# Major streets in Bishkek
STREETS = [
    {'name': 'Chui Avenue', 'district': 'Sverdlovsky', 'traffic': 'main_avenue', 'length_km': 4.5},
    {'name': 'Manas Avenue', 'district': 'Leninsky', 'traffic': 'main_avenue', 'length_km': 5.2},
    {'name': 'Ibraimov Street', 'district': 'Pervomaysky', 'traffic': 'major_street', 'length_km': 3.8},
    {'name': 'Abdrakhmanov Street', 'district': 'Sverdlovsky', 'traffic': 'major_street', 'length_km': 4.1},
    {'name': 'Erkindik Boulevard', 'district': 'Oktyabrsky', 'traffic': 'high', 'length_km': 3.5},
    {'name': 'Frunze Street', 'district': 'Leninsky', 'traffic': 'major_street', 'length_km': 6.0},
    {'name': 'Akhunbaev Street', 'district': 'Sverdlovsky', 'traffic': 'medium', 'length_km': 4.3},
    {'name': 'Toktogul Street', 'district': 'Pervomaysky', 'traffic': 'medium', 'length_km': 3.2},
    {'name': 'Moskovskaya Street', 'district': 'Oktyabrsky', 'traffic': 'major_street', 'length_km': 5.5},
    {'name': 'Sovietskaya Street', 'district': 'Leninsky', 'traffic': 'medium', 'length_km': 2.8},
    {'name': 'Logvinenko Street', 'district': 'Sverdlovsky', 'traffic': 'medium', 'length_km': 3.1},
    {'name': 'Bokonbaev Street', 'district': 'Pervomaysky', 'traffic': 'high', 'length_km': 4.7},
    {'name': 'Jibek Jolu Street', 'district': 'Oktyabrsky', 'traffic': 'medium', 'length_km': 3.9},
    {'name': 'Tynystanov Street', 'district': 'Leninsky', 'traffic': 'low', 'length_km': 2.5},
    {'name': 'Panfilov Street', 'district': 'Sverdlovsky', 'traffic': 'medium', 'length_km': 3.7},
    {'name': 'Razzakov Street', 'district': 'Pervomaysky', 'traffic': 'medium', 'length_km': 3.3},
    {'name': 'Isanov Street', 'district': 'Oktyabrsky', 'traffic': 'low', 'length_km': 2.9},
    {'name': 'Kievskaya Street', 'district': 'Leninsky', 'traffic': 'medium', 'length_km': 4.2},
    {'name': 'Gorky Street', 'district': 'Sverdlovsky', 'traffic': 'low', 'length_km': 2.6},
    {'name': 'Togolok Moldo Street', 'district': 'Pervomaysky', 'traffic': 'low', 'length_km': 3.0}
]

# Defect types
DEFECT_TYPES = ['pothole', 'longitudinal_crack', 'transverse_crack', 'alligator_crack']


def generate_random_coordinate(base_lat, base_lon, radius_km=0.05):
    """Generate random coordinate near base point"""
    # Approximate: 1 degree latitude/longitude ~ 111 km
    lat_offset = random.uniform(-radius_km, radius_km) / 111
    lon_offset = random.uniform(-radius_km, radius_km) / (111 * abs(np.cos(np.radians(base_lat))))

    return (
        round(base_lat + lat_offset, 6),
        round(base_lon + lon_offset, 6)
    )


def generate_defects_for_street(street, num_defects=None):
    """Generate mock defects for a street"""
    if num_defects is None:
        # Generate random number based on traffic (worse roads have more defects)
        if street['traffic'] == 'main_avenue':
            num_defects = random.randint(30, 50)
        elif street['traffic'] in ['major_street', 'high']:
            num_defects = random.randint(20, 35)
        else:
            num_defects = random.randint(10, 25)

    defects = []
    base_lat, base_lon = BISHKEK_CENTER

    # Distribute coordinates along the street
    for i in range(num_defects):
        lat, lon = generate_random_coordinate(base_lat, base_lon, radius_km=0.02)

        # Random defect type
        defect_type = random.choice(DEFECT_TYPES)

        # Random bbox area and confidence
        bbox_area = random.uniform(5000, 25000)
        confidence = random.uniform(0.65, 0.95)

        # Calculate severity
        defect_dict = {
            'bbox_area': bbox_area,
            'class_name': defect_type,
            'confidence': confidence
        }
        severity = calculate_severity(defect_dict, image_area=640*640)

        defect = {
            'lat': lat,
            'lon': lon,
            'defect_type': defect_type,
            'severity': severity,
            'confidence': round(confidence, 2),
            'image_path': f'img_{street["name"].replace(" ", "_")}_{i:03d}.jpg',
            'street_name': street['name'],
            'district': street['district']
        }

        defects.append(defect)

    return defects


def generate_all_data():
    """Generate all data for frontend"""
    print("=" * 60)
    print("Generating Mock Data for RoadDoctor Frontend")
    print("=" * 60)

    # Create output directory
    os.makedirs('output', exist_ok=True)

    all_defects = []
    street_stats = []

    # Generate defects for each street
    print("\n📍 Generating defects for streets...")
    for street in STREETS:
        defects = generate_defects_for_street(street)
        all_defects.extend(defects)

        # Calculate street statistics
        severities = [d['severity'] for d in defects]
        avg_severity = sum(severities) / len(severities) if severities else 0

        priority_score = calculate_priority(defects, street['traffic'])
        quality_index = calculate_road_quality({
            'defect_count': len(defects),
            'length_km': street['length_km'],
            'avg_severity': avg_severity
        })
        repair_cost = estimate_repair_cost(len(defects), avg_severity, street['length_km'])

        # Count defects by type
        defect_breakdown = {}
        for dtype in DEFECT_TYPES:
            count = sum(1 for d in defects if d['defect_type'] == dtype)
            defect_breakdown[dtype] = count

        street_stat = {
            'street_name': street['name'],
            'district': street['district'],
            'defect_count': len(defects),
            'avg_severity': round(avg_severity, 1),
            'priority_score': priority_score,
            'quality_index': quality_index,
            'repair_cost': repair_cost,
            'length_km': street['length_km'],
            'defect_breakdown': defect_breakdown
        }

        street_stats.append(street_stat)
        print(f"  ✓ {street['name']}: {len(defects)} defects, Priority: {priority_score}")

    print(f"\n✓ Total defects generated: {len(all_defects)}")

    # 1. Generate defects.csv
    print("\n📄 Generating output/defects.csv...")
    with open('output/defects.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'lat', 'lon', 'defect_type', 'severity', 'confidence',
            'image_path', 'street_name', 'district'
        ])
        writer.writeheader()
        writer.writerows(all_defects)
    print("✓ defects.csv created")

    # 2. Generate heatmap.json
    print("\n🔥 Generating output/heatmap.json...")
    heatmap_data = []
    for defect in all_defects:
        intensity = defect['severity'] / 10  # Normalize to 0-1
        heatmap_data.append([defect['lat'], defect['lon'], round(intensity, 2)])

    with open('output/heatmap.json', 'w') as f:
        json.dump({'heatmap_data': heatmap_data}, f, indent=2)
    print("✓ heatmap.json created")

    # 3. Generate districts.json
    print("\n🗺️  Generating output/districts.json...")
    district_stats = defaultdict(lambda: {
        'defect_count': 0,
        'total_severity': 0,
        'total_cost': 0
    })

    for stat in street_stats:
        district = stat['district']
        district_stats[district]['defect_count'] += stat['defect_count']
        district_stats[district]['total_severity'] += stat['avg_severity'] * stat['defect_count']
        district_stats[district]['total_cost'] += stat['repair_cost']

    districts_output = []
    for district in DISTRICTS:
        stats = district_stats[district]
        defect_count = stats['defect_count']
        avg_severity = stats['total_severity'] / defect_count if defect_count > 0 else 0

        # Estimate total road length in district (rough estimate)
        district_length = sum(s['length_km'] for s in STREETS if s['district'] == district)

        districts_output.append({
            'name': district,
            'defect_count': defect_count,
            'defect_density': round(defect_count / district_length, 1) if district_length > 0 else 0,
            'avg_severity': round(avg_severity, 1),
            'quality_index': calculate_road_quality({
                'defect_count': defect_count,
                'length_km': district_length,
                'avg_severity': avg_severity
            }),
            'repair_cost_estimate': stats['total_cost']
        })

    with open('output/districts.json', 'w') as f:
        json.dump({'districts': districts_output}, f, indent=2)
    print("✓ districts.json created")

    # 4. Generate worst_roads.json
    print("\n⚠️  Generating output/worst_roads.json...")
    sorted_roads = sorted(street_stats, key=lambda x: x['priority_score'], reverse=True)

    worst_roads = []
    for rank, road in enumerate(sorted_roads[:20], 1):
        worst_roads.append({
            'rank': rank,
            'street_name': road['street_name'],
            'district': road['district'],
            'defect_count': road['defect_count'],
            'avg_severity': road['avg_severity'],
            'quality_index': road['quality_index'],
            'priority_score': road['priority_score'],
            'repair_cost': road['repair_cost'],
            'defects': [
                {'type': dtype, 'count': count}
                for dtype, count in road['defect_breakdown'].items()
            ]
        })

    with open('output/worst_roads.json', 'w') as f:
        json.dump({'worst_roads': worst_roads}, f, indent=2)
    print("✓ worst_roads.json created")

    # 5. Generate stats.json
    print("\n📊 Generating output/stats.json...")

    # Calculate overall stats
    total_defects = len(all_defects)
    critical_defects = sum(1 for d in all_defects if d['severity'] >= 7)
    total_cost = sum(s['repair_cost'] for s in street_stats)
    priority_roads = sum(1 for s in street_stats if s['priority_score'] >= 7)

    # Defects by type
    defects_by_type = {dtype: 0 for dtype in DEFECT_TYPES}
    for defect in all_defects:
        defects_by_type[defect['defect_type']] += 1

    # Defects by severity category
    defects_by_severity = {'high': 0, 'medium': 0, 'low': 0}
    for defect in all_defects:
        category = categorize_severity(defect['severity'])
        defects_by_severity[category] += 1

    stats_output = {
        'total_stats': {
            'total_defects': total_defects,
            'critical_defects': critical_defects,
            'total_repair_cost': total_cost,
            'priority_roads_count': priority_roads,
            'defects_by_type': defects_by_type,
            'defects_by_severity': defects_by_severity
        }
    }

    with open('output/stats.json', 'w') as f:
        json.dump(stats_output, f, indent=2)
    print("✓ stats.json created")

    # Print summary
    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETE!")
    print("=" * 60)
    print(f"Total Defects: {total_defects}")
    print(f"Critical Defects: {critical_defects}")
    print(f"Total Repair Cost: {total_cost:,} KGS")
    print(f"Priority Roads: {priority_roads}")
    print(f"\nFiles generated in 'output/' directory:")
    print("  - defects.csv")
    print("  - heatmap.json")
    print("  - districts.json")
    print("  - worst_roads.json")
    print("  - stats.json")
    print("\n✓ Ready for backend integration!")


# Add numpy import for coordinate calculation
import numpy as np


if __name__ == "__main__":
    generate_all_data()
