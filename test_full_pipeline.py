"""Test the full pipeline on a few frames"""
from ultralytics import YOLO
import cv2
import numpy as np
from sort.sort import Sort
from util import get_car, read_license_plate

# Load models
print("Loading models...")
vehicle_detector = YOLO('yolov8n.pt')
plate_detector = YOLO('license_plate_detector.pt')
print("✓ Models loaded\n")

# Load video
video_path = './sample2.mp4'
cap = cv2.VideoCapture(video_path)

# Initialize tracker
tracker = Sort()

frame_num = 0
max_frames = 5  # Only process 5 frames

print(f"Processing first {max_frames} frames...\n")
print("="*70)

while frame_num < max_frames:
    ret, frame = cap.read()
    if not ret:
        break
    
    print(f"\n==== FRAME {frame_num} ====")
    
    # Detect vehicles
    vehicle_results = vehicle_detector(frame, verbose=False)[0]
    detections = []
    for det in vehicle_results.boxes.data.tolist():
        x1, y1, x2, y2, conf, cls = det
        if int(cls) in [2, 3, 5, 7]:  # car, motorcycle, bus, truck
            detections.append([x1, y1, x2, y2, conf])
    
    print(f"Vehicles detected: {len(detections)}")
    
    # Track vehicles
    tracks = tracker.update(np.asarray(detections))
    print(f"Tracked vehicles: {len(tracks)}")
    
    if len(tracks) > 0:
        for track in tracks:
            print(f"  Vehicle ID {int(track[4])}: ({int(track[0])}, {int(track[1])}, {int(track[2])}, {int(track[3])})")
    
    # Detect plates
    plate_results = plate_detector(frame, conf=0.2, verbose=False)[0]  # Lower confidence
    plates = plate_results.boxes.data.tolist()
    
    print(f"\nPlates detected by YOLO: {len(plates)}")
    
    for i, plate in enumerate(plates):
        px1, py1, px2, py2, pconf, pcls = plate
        print(f"\n  Plate {i+1}:")
        print(f"    BBox: ({int(px1)}, {int(py1)}, {int(px2)}, {int(py2)})")
        print(f"    Confidence: {pconf:.2f}")
        
        # Match to vehicle
        car = get_car(plate, tracks)
        car_id = int(car[4]) if car[4] != -1 else -1
        
        print(f"    Matched to vehicle: {car_id}")
        
        # If no match, use first vehicle
        if car_id == -1 and len(tracks) > 0:
            print(f"    ⚠ Using first vehicle instead")
            car = tracks[0]
            car_id = int(car[4])
        
        if car_id != -1:
            # Crop plate
            pad = 5
            y1p = max(0, int(py1) - pad)
            y2p = min(frame.shape[0], int(py2) + pad)
            x1p = max(0, int(px1) - pad)
            x2p = min(frame.shape[1], int(px2) + pad)
            crop = frame[y1p:y2p, x1p:x2p, :]
            
            if crop.size > 0:
                # OCR - pass original BGR crop, preprocessing is done inside read_license_plate
                print(f"    Running OCR...")
                text, score = read_license_plate(crop)
                
                if text:
                    print(f"    \u2713 OCR SUCCESS: '{text}' (confidence: {score:.2f})")
                else:
                    print(f"    \u2717 OCR FAILED: No text detected")
    
    frame_num += 1

cap.release()

print("\n" + "="*70)
print("Test complete!")
