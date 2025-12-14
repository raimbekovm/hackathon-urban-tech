#!/usr/bin/env python3
"""
Prepare demo photos with bounding boxes for upload demo
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLASS_NAMES = {
    0: 'alligator_crack',
    1: 'longitudinal_crack',
    2: 'pothole',
    3: 'transverse_crack'
}

CLASS_COLORS = {
    0: (0, 0, 255),      # Blue
    1: (255, 0, 0),      # Red
    2: (255, 165, 0),    # Orange
    3: (0, 255, 0)       # Green
}

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
    return detections

def draw_boxes(image_path, label_path, output_path):
    """Draw ALL YOLO bounding boxes on image"""
    detections = parse_yolo_label(label_path)
    if not detections:
        print(f"No detections found in {label_path}")
        return False

    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except:
        font = ImageFont.load_default()

    for detection in detections:
        x_center = detection['x_center'] * img_width
        y_center = detection['y_center'] * img_height
        box_width = detection['width'] * img_width
        box_height = detection['height'] * img_height

        x1 = int(x_center - box_width / 2)
        y1 = int(y_center - box_height / 2)
        x2 = int(x_center + box_width / 2)
        y2 = int(y_center + box_height / 2)

        color = CLASS_COLORS.get(detection['class_id'], (255, 255, 0))
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

        label_text = detection['class_name'].replace('_', ' ').title()
        text_bbox = draw.textbbox((x1, y1 - 20), label_text, font=font)
        draw.rectangle(text_bbox, fill=color)
        draw.text((x1, y1 - 20), label_text, fill=(255, 255, 255), font=font)

    img.save(output_path, quality=95)
    print(f"✓ Saved {output_path.name} with {len(detections)} boxes")
    return True

def main():
    base_path = Path(__file__).parent
    demo_path = base_path / 'demo_upload'
    output_path = base_path / 'data' / 'demo_annotated'

    output_path.mkdir(parents=True, exist_ok=True)

    print("🎨 Generating demo photos with bounding boxes...\n")

    # Process demo_diverse_defects
    draw_boxes(
        demo_path / 'demo_diverse_defects.jpg',
        demo_path / 'demo_diverse_defects.txt',
        output_path / 'demo_diverse_defects.jpg'
    )

    # Process demo_many_potholes
    draw_boxes(
        demo_path / 'demo_many_potholes.jpg',
        demo_path / 'demo_many_potholes.txt',
        output_path / 'demo_many_potholes.jpg'
    )

    print(f"\n✅ Demo photos ready in {output_path}/")
    print("\n📝 For demo presentation, upload one of these:")
    print("   1. demo_diverse_defects.jpg - 5 boxes, 3 different classes")
    print("   2. demo_many_potholes.jpg - 17 boxes, all potholes")

if __name__ == '__main__':
    main()
