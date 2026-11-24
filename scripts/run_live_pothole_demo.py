#!/usr/bin/env python3
"""
SIH 2026 - Live Pothole & Road Damage Detection Prototype
=========================================================
Runs real-time YOLOv8 road defect detection on video or live webcam.
Designed for live classroom and hackathon demonstrations.
"""

import os
import sys
import time
import argparse
import cv2
from ultralytics import YOLO

def run_pothole_demo(source="data/sample_videos/demo_potholes.mp4", conf=0.35, loop=True):
    model_path = "models/pothole.pt"
    if not os.path.exists(model_path):
        print(f"[ERROR] Model weights not found at {model_path}")
        sys.exit(1)

    print(f"[AI] Loading YOLOv8 Road Damage Model from {model_path}...")
    model = YOLO(model_path)
    
    # Class colors (BGR)
    # 0: longitudinal_crack, 1: transverse_crack, 2: alligator_crack, 3: pothole, 4: manhole, 5: waterlogging
    colors = {
        0: (255, 120, 0),    # Blue
        1: (0, 200, 100),    # Green
        2: (0, 220, 255),    # Yellow
        3: (0, 0, 255),      # Red (Pothole)
        4: (220, 50, 200),   # Purple (Manhole)
        5: (255, 255, 0)     # Cyan
    }

    is_cam = source.isdigit() or source == "0"
    src_val = int(source) if is_cam else source

    print("\n" + "="*60)
    print("🚦 SIH 2026 LIVE ROAD DAMAGE & POTHOLE DETECTOR DEMO")
    print(f" Source: {source} (Press 'q' or 'ESC' on the preview window to exit)")
    print("="*60 + "\n")

    win_title = "SIH 2026: Live Pothole & Road Defect Detection (Press Q to Exit)"
    cv2.namedWindow(win_title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_title, 1280, 720)

    while True:
        cap = cv2.VideoCapture(src_val)
        if not cap.isOpened():
            print(f"[ERROR] Unable to open source: {source}")
            break

        prev_time = time.time()
        fps = 30.0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break  # Video reached end

            # Compute live processing FPS
            curr_time = time.time()
            dt = curr_time - prev_time
            prev_time = curr_time
            if dt > 0:
                fps = 0.85 * fps + 0.15 * (1.0 / dt)

            # YOLO inference
            results = model.predict(frame, conf=conf, imgsz=640, verbose=False)[0]

            defect_counts = {}
            for box in results.boxes:
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = model.names.get(cls_id, f"Class_{cls_id}").upper()
                confidence = float(box.conf[0].cpu().numpy())
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].cpu().numpy()]

                defect_counts[cls_name] = defect_counts.get(cls_name, 0) + 1
                color = colors.get(cls_id, (0, 255, 0))

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                # Draw label banner
                label = f"{cls_name} {int(confidence*100)}%"
                (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
                cv2.rectangle(frame, (x1, y1 - lh - 6), (x1 + lw + 6, y1), color, -1)
                cv2.putText(frame, label, (x1 + 3, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

            # Draw HUD Overlays
            h, w = frame.shape[:2]
            # Top banner
            cv2.rectangle(frame, (0, 0), (w, 52), (20, 20, 25), -1)
            cv2.putText(frame, "SIH 2026: Mobile Road Defect Intelligence (BUS-101)", (15, 22), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 220, 255), 2)
            
            summary_text = f"FPS: {fps:.1f} | Detections: {len(results.boxes)}"
            if defect_counts:
                summary_text += " | " + ", ".join([f"{k}: {v}" for k, v in defect_counts.items()])
            else:
                summary_text += " | Road Condition: Normal"

            cv2.putText(frame, summary_text, (15, 44), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)

            # Show OpenCV preview window
            cv2.imshow(win_title, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                cap.release()
                cv2.destroyAllWindows()
                return

        cap.release()
        if not loop or is_cam:
            break
        print("[DEMO] Looping video presentation...")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live Pothole Detection Demo")
    parser.add_argument("--source", type=str, default="data/sample_videos/demo_potholes.mp4", 
                        help="Path to video file or 0 for webcam")
    parser.add_argument("--conf", type=float, default=0.35, help="Detection confidence threshold")
    parser.add_argument("--no-loop", action="store_true", help="Do not loop video")
    args = parser.parse_args()

    run_pothole_demo(source=args.source, conf=args.conf, loop=not args.no_loop)
