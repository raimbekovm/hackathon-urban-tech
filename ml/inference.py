"""
YOLOv8 Inference Script for Road Defect Detection
Supports: single image, folder of images, video
"""

import os
import cv2
from pathlib import Path
from ultralytics import YOLO
import numpy as np


class RoadDefectDetector:
    """Road defect detector using YOLOv8"""

    def __init__(self, model_path='models/best.pt'):
        """
        Initialize detector

        Args:
            model_path: Path to trained YOLOv8 model
        """
        if not os.path.exists(model_path):
            print(f"⚠️  Model not found at {model_path}")
            print("Using pretrained YOLOv8n as placeholder...")
            model_path = 'yolov8n.pt'

        self.model = YOLO(model_path)
        print(f"✓ Model loaded from: {model_path}")

        # Class names
        self.class_names = {
            0: 'pothole',
            1: 'longitudinal_crack',
            2: 'transverse_crack',
            3: 'alligator_crack'
        }

    def detect_image(self, image_path, save_path=None, conf_threshold=0.25):
        """
        Detect defects in a single image

        Args:
            image_path: Path to input image
            save_path: Path to save result (optional)
            conf_threshold: Confidence threshold

        Returns:
            List of detections with bbox, confidence, class
        """
        # Run inference
        results = self.model(image_path, conf=conf_threshold)

        # Parse detections
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls = int(box.cls[0].cpu().numpy())

                detection = {
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'confidence': conf,
                    'class': cls,
                    'class_name': self.class_names.get(cls, f'class_{cls}'),
                    'bbox_area': (x2 - x1) * (y2 - y1)
                }
                detections.append(detection)

        # Save annotated image
        if save_path:
            annotated = results[0].plot()
            cv2.imwrite(save_path, annotated)
            print(f"✓ Saved annotated image: {save_path}")

        return detections

    def detect_folder(self, input_folder, output_folder=None, conf_threshold=0.25):
        """
        Detect defects in all images in a folder

        Args:
            input_folder: Path to folder with images
            output_folder: Path to save annotated images
            conf_threshold: Confidence threshold

        Returns:
            Dictionary mapping image_path -> detections
        """
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []

        for ext in image_extensions:
            image_files.extend(Path(input_folder).glob(f'*{ext}'))
            image_files.extend(Path(input_folder).glob(f'*{ext.upper()}'))

        print(f"Found {len(image_files)} images in {input_folder}")

        if output_folder:
            os.makedirs(output_folder, exist_ok=True)

        all_detections = {}

        for img_path in image_files:
            save_path = None
            if output_folder:
                save_path = os.path.join(output_folder, img_path.name)

            detections = self.detect_image(str(img_path), save_path, conf_threshold)
            all_detections[str(img_path)] = detections

            print(f"  {img_path.name}: {len(detections)} defects detected")

        return all_detections

    def detect_video(self, video_path, output_path=None, conf_threshold=0.25, frame_skip=30):
        """
        Detect defects in video (frame by frame)

        Args:
            video_path: Path to input video
            output_path: Path to save annotated video
            conf_threshold: Confidence threshold
            frame_skip: Process every Nth frame (for speed)

        Returns:
            List of detections per frame
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"❌ Could not open video: {video_path}")
            return []

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"Video: {width}x{height} @ {fps} FPS, {total_frames} frames")

        # Setup output video writer
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_detections = []
        frame_num = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Process every Nth frame
            if frame_num % frame_skip == 0:
                # Run inference
                results = self.model(frame, conf=conf_threshold)
                annotated_frame = results[0].plot()

                # Parse detections
                detections = []
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        cls = int(box.cls[0].cpu().numpy())

                        detections.append({
                            'frame': frame_num,
                            'bbox': [float(x1), float(y1), float(x2), float(y2)],
                            'confidence': conf,
                            'class_name': self.class_names.get(cls, f'class_{cls}')
                        })

                frame_detections.append({
                    'frame': frame_num,
                    'detections': detections
                })

                if writer:
                    writer.write(annotated_frame)

                if frame_num % 100 == 0:
                    print(f"Processed frame {frame_num}/{total_frames}")

            frame_num += 1

        cap.release()
        if writer:
            writer.release()
            print(f"✓ Saved annotated video: {output_path}")

        return frame_detections


def main():
    """Example usage"""
    detector = RoadDefectDetector('models/best.pt')

    # Example 1: Detect in single image
    # detections = detector.detect_image(
    #     'data/test_image.jpg',
    #     save_path='output/result.jpg'
    # )
    # print(f"Found {len(detections)} defects")

    # Example 2: Detect in folder
    # all_detections = detector.detect_folder(
    #     'data/bishkek_roads',
    #     output_folder='output/detected'
    # )

    # Example 3: Detect in video
    # frame_detections = detector.detect_video(
    #     'data/bishkek_drive.mp4',
    #     output_path='output/annotated_video.mp4',
    #     frame_skip=30  # Process every 30th frame
    # )

    print("\n✓ Inference module ready!")
    print("Import and use RoadDefectDetector class for detection")


if __name__ == "__main__":
    main()
