#!/usr/bin/env python3
"""
Исправление аннотаций: конвертация полигонов в bounding boxes
"""

import sys
from pathlib import Path

def polygon_to_bbox(polygon_coords):
    """Конвертирует полигон в bounding box"""
    # Полигон: [x1, y1, x2, y2, x3, y3, ...]
    # Преобразуем в пары координат
    coords = []
    for i in range(0, len(polygon_coords), 2):
        if i + 1 < len(polygon_coords):
            coords.append((polygon_coords[i], polygon_coords[i + 1]))
    
    if not coords:
        return None
    
    # Находим min/max
    x_coords = [c[0] for c in coords]
    y_coords = [c[1] for c in coords]
    
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    width = x_max - x_min
    height = y_max - y_min
    
    return x_center, y_center, width, height

def fix_annotation_file(label_file):
    """Исправляет файл аннотации, конвертируя полигоны в bbox"""
    with open(label_file, 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    changed = False
    
    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue
        
        class_id = int(parts[0])
        values = [float(x) for x in parts[1:]]
        
        # Если 5 значений - это уже правильный bbox
        if len(values) == 4:
            fixed_lines.append(line)
        # Если больше 4 - это полигон, нужно конвертировать
        elif len(values) > 4 and len(values) % 2 == 0:
            # Полигон: пары координат (x1, y1, x2, y2, ...)
            bbox = polygon_to_bbox(values)
            if bbox:
                fixed_line = f"{class_id} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n"
                fixed_lines.append(fixed_line)
                changed = True
            else:
                print(f"  ⚠️  Не удалось конвертировать полигон в {label_file.name}")
        else:
            # Неправильный формат, пропускаем
            print(f"  ⚠️  Пропущена строка с неправильным форматом: {len(values)} значений")
            continue
    
    if changed:
        with open(label_file, 'w') as f:
            f.writelines(fixed_lines)
        return True
    return False

def fix_dataset(dataset_path):
    """Исправляет все аннотации в датасете"""
    dataset_path = Path(dataset_path)
    
    print("=" * 70)
    print("🔧 Исправление аннотаций: полигоны → bounding boxes")
    print("=" * 70)
    print(f"Путь: {dataset_path}\n")
    
    fixed_count = 0
    total_count = 0
    
    for split in ['train', 'val', 'test']:
        labels_dir = dataset_path / split / 'labels'
        if not labels_dir.exists():
            continue
        
        print(f"\n{split.upper()}:")
        label_files = list(labels_dir.glob('*.txt'))
        
        for label_file in label_files:
            total_count += 1
            if fix_annotation_file(label_file):
                fixed_count += 1
                print(f"  ✅ Исправлен: {label_file.name}")
    
    print("\n" + "=" * 70)
    print(f"✅ Исправлено файлов: {fixed_count} из {total_count}")
    print("=" * 70)
    
    return fixed_count

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python fix_annotations.py <path_to_dataset>")
        print("\nПример:")
        print("  python fix_annotations.py data/urban_tech")
        sys.exit(1)
    
    dataset_path = sys.argv[1]
    fix_dataset(dataset_path)

