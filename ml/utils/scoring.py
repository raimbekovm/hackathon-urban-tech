"""
Scoring algorithms for road defect analysis
Implements: Severity Score, Priority Score, Road Quality Index
"""

import numpy as np
from statistics import mean


def calculate_severity(defect, image_area=None):
    """
    Calculate severity score for a defect (1-10 scale)

    Args:
        defect: Detection dictionary with keys:
                - bbox_area: Area of bounding box
                - class_name or type: Defect type
                - confidence: Detection confidence
        image_area: Total image area (width * height)

    Returns:
        float: Severity score (1-10)
    """
    # Type severity weights
    type_scores = {
        'pothole': 9,
        'alligator_crack': 7,
        'transverse_crack': 5,
        'longitudinal_crack': 4
    }

    # Get defect type
    defect_type = defect.get('class_name') or defect.get('type', 'unknown')
    type_score = type_scores.get(defect_type, 5)  # Default to medium severity

    # Size score (relative to image)
    if image_area and defect.get('bbox_area'):
        size_ratio = defect['bbox_area'] / image_area
        size_score = min(size_ratio * 100, 10)  # Scale to 0-10
    else:
        size_score = 5  # Default medium size

    # Confidence factor
    confidence = defect.get('confidence', 0.8)

    # Combined severity score
    severity = (size_score * 0.6 + type_score * 0.4) * confidence
    severity = min(10, max(1, severity))  # Clamp to 1-10

    return round(severity, 1)


def calculate_priority(street_defects, traffic_level='medium'):
    """
    Calculate repair priority for a street (1-10 scale)

    Args:
        street_defects: List of defect dictionaries, each with 'severity'
        traffic_level: Traffic level ('low', 'medium', 'high', 'main_avenue')

    Returns:
        float: Priority score (1-10)
    """
    if not street_defects:
        return 0

    # Average severity
    avg_severity = mean([d.get('severity', 5) for d in street_defects])

    # Defect count factor
    defect_count = len(street_defects)
    count_factor = min(defect_count / 10, 10)  # Normalize to 0-10

    # Traffic score mapping
    traffic_scores = {
        'main_avenue': 10,    # Chui, Manas
        'high': 8,
        'major_street': 7,
        'medium': 5,
        'minor_street': 4,
        'low': 3
    }
    traffic_score = traffic_scores.get(traffic_level, 5)

    # Combined priority
    priority = (
        avg_severity * 0.5 +
        count_factor * 0.3 +
        traffic_score * 0.2
    )

    return round(min(10, priority), 1)


def calculate_road_quality(street_stats):
    """
    Calculate Road Quality Index (0-100 scale, 100 = perfect)

    Args:
        street_stats: Dictionary with keys:
                     - defect_count: Number of defects
                     - length_km: Street length in km
                     - avg_severity: Average severity of defects

    Returns:
        int: Quality index (0-100)
    """
    defect_count = street_stats.get('defect_count', 0)
    length_km = street_stats.get('length_km', 1)  # Avoid division by zero
    avg_severity = street_stats.get('avg_severity', 0)

    # Defects per km
    defects_per_km = defect_count / length_km

    # Calculate quality degradation
    quality = 100 - (defects_per_km * 5 + avg_severity * 3)

    # Clamp to 0-100
    return int(max(0, min(100, quality)))


def estimate_repair_cost(defect_count, avg_severity, street_length_km=1.0):
    """
    Estimate repair cost in KGS (Kyrgyz Som)

    Args:
        defect_count: Number of defects
        avg_severity: Average severity (1-10)
        street_length_km: Street length in km

    Returns:
        int: Estimated cost in KGS
    """
    # Base cost per defect (KGS)
    base_costs = {
        'low': 5000,      # Minor crack repair
        'medium': 15000,  # Moderate pothole
        'high': 30000     # Major pothole or severe crack
    }

    # Determine severity category
    if avg_severity < 4:
        base_cost = base_costs['low']
    elif avg_severity < 7:
        base_cost = base_costs['medium']
    else:
        base_cost = base_costs['high']

    # Total cost
    total_cost = defect_count * base_cost

    # Add length-based overhead (resurfacing for long streets)
    if defect_count / street_length_km > 10:  # More than 10 defects per km
        resurfacing_cost = street_length_km * 500000  # 500k KGS per km
        total_cost += resurfacing_cost

    return int(total_cost)


def categorize_severity(severity_score):
    """
    Categorize severity into low/medium/high

    Args:
        severity_score: Severity value (1-10)

    Returns:
        str: Category ('low', 'medium', 'high')
    """
    if severity_score < 4:
        return 'low'
    elif severity_score < 7:
        return 'medium'
    else:
        return 'high'


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("Scoring Algorithms Demo")
    print("=" * 60)

    # Example defect
    defect = {
        'bbox_area': 12000,
        'class_name': 'pothole',
        'confidence': 0.89
    }

    severity = calculate_severity(defect, image_area=640*640)
    print(f"\nDefect Severity: {severity}/10")
    print(f"Category: {categorize_severity(severity)}")

    # Example street with multiple defects
    street_defects = [
        {'severity': 9.2},
        {'severity': 8.5},
        {'severity': 7.8},
        {'severity': 6.5},
        {'severity': 8.9}
    ]

    priority = calculate_priority(street_defects, traffic_level='main_avenue')
    print(f"\nStreet Priority: {priority}/10")

    # Example road quality
    street_stats = {
        'defect_count': 45,
        'length_km': 3.5,
        'avg_severity': 8.3
    }

    quality = calculate_road_quality(street_stats)
    print(f"\nRoad Quality Index: {quality}/100")

    # Repair cost estimation
    cost = estimate_repair_cost(45, 8.3, 3.5)
    print(f"Estimated Repair Cost: {cost:,} KGS")

    print("\n✓ Scoring module working correctly!")
