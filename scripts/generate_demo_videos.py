import os
import cv2
import numpy as np

os.makedirs("data/sample_videos", exist_ok=True)

def create_pan_zoom_sequence(image_path, target_w=640, target_h=480, num_frames=60):
    img = cv2.imread(image_path)
    if img is None:
        return []
    
    # Resize keeping aspect ratio
    h, w = img.shape[:2]
    frames = []
    
    # Generate dynamic zoom & vertical pan simulating forward vehicle motion
    for i in range(num_frames):
        alpha = i / float(num_frames)
        # Slight zoom from 1.0 to 1.15
        zoom = 1.0 + 0.12 * alpha
        # Center crop with pan
        crop_w = int(w / zoom)
        crop_h = int(h / zoom)
        
        # Pan slightly downward or forward
        start_y = int((h - crop_h) * (0.3 + 0.4 * alpha))
        start_x = int((w - crop_w) * 0.5)
        
        start_y = max(0, min(h - crop_h, start_y))
        start_x = max(0, min(w - crop_w, start_x))
        
        cropped = img[start_y:start_y + crop_h, start_x:start_x + crop_w]
        resized = cv2.resize(cropped, (target_w, target_h))
        frames.append(resized)
    return frames

def generate_pothole_video():
    out_path = "data/sample_videos/demo_potholes.mp4"
    images = [
        "docs/images/pothole_road_damage_detection.jpg",
        "docs/images/pune_road_pothole_detection.jpg",
        "docs/images/pothole_max_detections.jpg",
        "potholes_info/screenshots/real_video/real_video_pothole_prediction_01.jpg",
        "potholes_info/screenshots/real_video/real_video_multi_pothole_01.jpg"
    ]
    
    valid_images = [img for img in images if os.path.exists(img)]
    if not valid_images:
        print("No pothole images found!")
        return
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_path, fourcc, 25, (1280, 720))
    
    for img_path in valid_images:
        frames = create_pan_zoom_sequence(img_path, 1280, 720, num_frames=50)
        for f in frames:
            out.write(f)
            
    out.release()
    print(f"Generated {out_path} ({os.path.getsize(out_path)} bytes)")

def generate_anpr_video():
    out_path = "data/sample_videos/demo_anpr.mp4"
    anpr_dir = "anpr/outputs/anpr_detection_v1/real_images"
    images = []
    if os.path.exists("docs/images/anpr_plate_detection.jpg"):
        images.append("docs/images/anpr_plate_detection.jpg")
    if os.path.exists(anpr_dir):
        for f in sorted(os.listdir(anpr_dir)):
            if f.endswith(('.jpg', '.jpeg', '.png')):
                images.append(os.path.join(anpr_dir, f))
                
    ocr_v2_dir = "anpr/outputs/anpr_ocr_v2/real_images"
    if os.path.exists(ocr_v2_dir):
        for f in sorted(os.listdir(ocr_v2_dir))[:5]:
            if f.endswith(('.jpg', '.jpeg', '.png')):
                images.append(os.path.join(ocr_v2_dir, f))

    if not images:
        print("No ANPR images found!")
        return

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_path, fourcc, 25, (1280, 720))

    for img_path in images:
        frames = create_pan_zoom_sequence(img_path, 1280, 720, num_frames=45)
        for f in frames:
            out.write(f)

    out.release()
    print(f"Generated {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    generate_pothole_video()
    generate_anpr_video()
