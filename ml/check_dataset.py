#!/usr/bin/env python3
"""
Проверка формата датасета для YOLO
Использование: python check_dataset.py path/to/dataset
"""

import sys
from pathlib import Path
from collections import Counter

def check_dataset(dataset_path):
    """Проверяет структуру и формат датасета YOLO"""
    dataset_path = Path(dataset_path)
    
    print("=" * 70)
    print("🔍 Проверка датасета YOLO")
    print("=" * 70)
    print(f"Путь: {dataset_path}\n")
    
    # Проверка структуры
    required_dirs = ['train/images', 'train/labels']
    optional_dirs = ['val/images', 'val/labels', 'test/images', 'test/labels']
    
    print("📁 Проверка структуры папок:")
    all_ok = True
    
    for dir_path in required_dirs:
        full_path = dataset_path / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} - НЕ НАЙДЕНО!")
            all_ok = False
    
    for dir_path in optional_dirs:
        full_path = dataset_path / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path} (опционально)")
    
    if not all_ok:
        print("\n❌ Обязательные папки отсутствуют!")
        return False
    
    # Проверка соответствия изображений и аннотаций
    print("\n📊 Статистика данных:")
    
    for split in ['train', 'val', 'test']:
        images_dir = dataset_path / split / 'images'
        labels_dir = dataset_path / split / 'labels'
        
        if not images_dir.exists():
            continue
        
        image_files = {f.stem for f in images_dir.glob('*') 
                      if f.suffix.lower() in ['.jpg', '.jpeg', '.png']}
        label_files = {f.stem for f in labels_dir.glob('*.txt')}
        
        print(f"\n{split.upper()}:")
        print(f"  Изображений: {len(image_files)}")
        print(f"  Аннотаций: {len(label_files)}")
        
        # Проверка соответствия
        missing_labels = image_files - label_files
        missing_images = label_files - image_files
        
        if missing_labels:
            print(f"  ⚠️  Изображения без аннотаций: {len(missing_labels)}")
            if len(missing_labels) <= 5:
                for img in list(missing_labels)[:5]:
                    print(f"     - {img}")
        
        if missing_images:
            print(f"  ⚠️  Аннотации без изображений: {len(missing_images)}")
            if len(missing_images) <= 5:
                for lbl in list(missing_images)[:5]:
                    print(f"     - {lbl}")
        
        if not missing_labels and not missing_images:
            print(f"  ✅ Все файлы соответствуют")
    
    # Проверка формата аннотаций
    print("\n📝 Проверка формата аннотаций:")
    
    sample_labels = list((dataset_path / 'train' / 'labels').glob('*.txt'))
    if not sample_labels:
        print("  ❌ Нет файлов аннотаций для проверки")
        return False
    
    class_counts = Counter()
    errors = []
    
    for label_file in sample_labels[:100]:  # Проверяем первые 100
        try:
            with open(label_file) as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) != 5:
                        errors.append(f"{label_file.name}:{line_num} - неправильное количество значений ({len(parts)})")
                        continue
                    
                    try:
                        class_id, x, y, w, h = map(float, parts)
                        class_id = int(class_id)
                        
                        # Проверка диапазонов
                        if not (0 <= class_id <= 4):
                            errors.append(f"{label_file.name}:{line_num} - класс {class_id} вне диапазона 0-4")
                        
                        if not (0 <= x <= 1 and 0 <= y <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                            errors.append(f"{label_file.name}:{line_num} - значения вне диапазона 0-1")
                        
                        class_counts[class_id] += 1
                    except ValueError:
                        errors.append(f"{label_file.name}:{line_num} - неверный формат чисел")
        except Exception as e:
            errors.append(f"{label_file.name} - ошибка чтения: {e}")
    
    if errors:
        print(f"  ⚠️  Найдено {len(errors)} ошибок:")
        for error in errors[:10]:
            print(f"     - {error}")
        if len(errors) > 10:
            print(f"     ... и еще {len(errors) - 10} ошибок")
    else:
        print(f"  ✅ Формат аннотаций корректен")
    
    # Статистика классов
    print("\n🏷️  Распределение классов:")
    class_names = {
        0: 'longitudinal_crack',
        1: 'transverse_crack',
        2: 'alligator_crack',
        3: 'pothole',
        4: 'other_damage'
    }
    
    for class_id in sorted(class_counts.keys()):
        name = class_names.get(class_id, f'unknown_{class_id}')
        count = class_counts[class_id]
        print(f"  {class_id} ({name}): {count} объектов")
    
    # Итог
    print("\n" + "=" * 70)
    if errors:
        print("⚠️  Датасет имеет ошибки, но может быть использован")
        print("   Рекомендуется исправить ошибки перед обучением")
    else:
        print("✅ Датасет готов к использованию!")
    print("=" * 70)
    
    return len(errors) == 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python check_dataset.py <path_to_dataset>")
        print("\nПример:")
        print("  python check_dataset.py data/bishkek_annotated")
        sys.exit(1)
    
    dataset_path = sys.argv[1]
    success = check_dataset(dataset_path)
    sys.exit(0 if success else 1)

