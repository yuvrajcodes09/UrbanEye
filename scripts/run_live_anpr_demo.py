#!/usr/bin/env python3
"""
SIH 2026 - Live ANPR (Automatic Number Plate Recognition) Prototype
===================================================================
Runs real-time YOLOv8 license plate localization & OCR on video or live webcam.
Designed for live classroom and hackathon demonstrations.
"""

import os
import sys
import time
import argparse
import cv2
import numpy as np
from ultralytics import YOLO

# Graceful EasyOCR check
OCR_AVAILABLE = False
try:
    import easyocr
    ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    OCR_AVAILABLE = True
except Exception:
    ocr_reader = None

def run_anpr_demo(source="data/sample_videos/demo_anpr.mp4", conf=0.25, loop=True):
    model_path = "models/anpr/best.pt"
    if not os.path.exists(model_path):
        print(f"[ERROR] ANPR model weights not found at {model_path}")
        sys.exit(1)

    print(f"[AI] Loading YOLOv8 ANPR Plate Localizer from {model_path}...")
    model = YOLO(model_path)

    is_cam = source.isdigit() or source == "0"
    src_val = int(source) if is_cam else source

    print("\n" + "="*60)
    print("🚗 SIH 2026 LIVE AUTOMATIC NUMBER PLATE RECOGNITION (ANPR) DEMO")
    print(f" Source: {source} (Press 'q' or 'ESC' on the preview window to exit)")
    print("="*60 + "\n")

    total_plates_tracked = 0

    win_title = "SIH 2026: Live ANPR License Plate Tracking (Press Q to Exit)"
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
                break

            curr_time = time.time()
            dt = curr_time - prev_time
            prev_time = curr_time
            if dt > 0:
                fps = 0.85 * fps + 0.15 * (1.0 / dt)

            # YOLO inference
            results = model.predict(frame, conf=conf, imgsz=640, verbose=False)[0]

            plates_in_frame = len(results.boxes)
            total_plates_tracked += plates_in_frame

            for box in results.boxes:
                confidence = float(box.conf[0].cpu().numpy())
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].cpu().numpy()]
                
                plate_text = "PLATE"
                # Optional EasyOCR if enabled
                if OCR_AVAILABLE and ocr_reader is not None:
                    h, w = frame.shape[:2]
                    crop = frame[max(0, y1-5):min(h, y2+5), max(0, x1-5):min(w, x2+5)]
                    if crop.size > 0:
                        ocr_res = ocr_reader.readtext(crop, detail=0)
                        if ocr_res:
                            plate_text = "".join(c for c in "".join(ocr_res) if c.isalnum()).upper()

                # High contrast green box around plate
                color = (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                # Label badge
                badge = f"{plate_text} ({int(confidence*100)}%)"
                (lw, lh), _ = cv2.getTextSize(badge, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
                cv2.rectangle(frame, (x1, y1 - lh - 6), (x1 + lw + 6, y1), (0, 180, 0), -1)
                cv2.putText(frame, badge, (x1 + 3, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

            # HUD Overlays
            h, w = frame.shape[:2]
            cv2.rectangle(frame, (0, 0), (w, 52), (20, 25, 20), -1)
            cv2.putText(frame, "SIH 2026: Automatic Number Plate Recognition (ANPR)", (15, 22), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 120), 2)

            status_str = f"FPS: {fps:.1f} | Active Plates in Frame: {plates_in_frame}"
            if OCR_AVAILABLE:
                status_str += " | OCR: EasyOCR Active"
            else:
                status_str += " | Mode: Edge YOLO Plate Localization"

            cv2.putText(frame, status_str, (15, 44), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)

            # Show preview
            cv2.imshow(win_title, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                cap.release()
                cv2.destroyAllWindows()
                return

        cap.release()
        if not loop or is_cam:
            break
        print("[DEMO] Looping ANPR presentation...")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live ANPR Detection Demo")
    parser.add_argument("--source", type=str, default="data/sample_videos/demo_anpr.mp4", 
                        help="Path to video file or 0 for webcam")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--no-loop", action="store_true", help="Do not loop video")
    args = parser.parse_args()

    run_anpr_demo(source=args.source, conf=args.conf, loop=not args.no_loop)
