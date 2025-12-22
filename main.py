"""
License Plate Detection System - Optimized Version
Detects vehicles, tracks them, and recognizes Bhutanese license plates in real-time
"""

from ultralytics import YOLO
import cv2
import numpy as np
from sort.sort import Sort
from util import get_car, read_license_plate, write_csv

# ======================== CONFIGURATION ========================
VIDEO_PATH = './sample.mp4'
OUTPUT_VIDEO_PATH = './output_with_plates.mp4'
CSV_OUTPUT_PATH = './test.csv'
PROCESS_EVERY_N_FRAMES = 1  # Process every frame for maximum detection
VEHICLES = [2, 3, 5, 7]  # COCO classes: car, motorcycle, bus, truck
FONT_SCALE = 1.2
MIN_PLATE_CONFIDENCE = 0.05  # Very low threshold - show partial detections
DEBUG_MODE = False  # Show debug output and save plate crops
SAVE_PLATE_CROPS = False  # Save detected plate images for debugging
SHOW_PARTIAL_PLATES = True  # Show partial/low confidence plates
# ================================================================

# Initialize
results = {}
plate_cache = {}
tracker = Sort()

# Load models
print("Loading models...")
vehicle_detector = YOLO('yolov8n.pt')
plate_detector = YOLO('license_plate_detector.pt')
print("✓ Models loaded\n")

# Setup video writer
print(f"Processing: {VIDEO_PATH}\n")
cap_test = cv2.VideoCapture(VIDEO_PATH)
if not cap_test.isOpened():
    print(f"❌ Error: Could not open video {VIDEO_PATH}")
    exit(1)

fps = int(cap_test.get(cv2.CAP_PROP_FPS))
width = int(cap_test.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap_test.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap_test.get(cv2.CAP_PROP_FRAME_COUNT))
cap_test.release()

print(f"Video: {width}x{height} @ {fps}fps, {total_frames} frames")
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(OUTPUT_VIDEO_PATH, fourcc, fps, (width, height))

# Process video
frame_num = 0
plates_found = 0

for frame_result in vehicle_detector.predict(source=VIDEO_PATH, stream=True, verbose=False):
    results[frame_num] = {}
    original = frame_result.orig_img
    display = original.copy()
    
    # Detect vehicles
    detections = []
    for det in frame_result.boxes.data.tolist():
        x1, y1, x2, y2, conf, cls = det
        if int(cls) in VEHICLES:
            detections.append([x1, y1, x2, y2, conf])
            cv2.rectangle(display, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
    
    # Track vehicles
    tracks = tracker.update(np.asarray(detections))
    
    # Draw tracked vehicles with plates
    for track in tracks:
        x1, y1, x2, y2, vid = track
        vid = int(vid)
        
        # Show cached plate if available
        if vid in plate_cache:
            plate_data = plate_cache[vid]
            plate_text = plate_data['text']
            is_partial = plate_data.get('is_partial', False)
            
            # Create display text with indicator for partial reads
            if is_partial:
                display_text = f"Car {vid} | {plate_text}?"
            else:
                display_text = f"Car {vid} | {plate_text}"
            
            # Calculate position
            (tw, th), _ = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
            tx = int(x1) + 5
            ty = int(y1) - 15
            if ty < th + 20:
                ty = int(y1) + th + 30
            
            # Use different color for partial reads
            text_color = (0, 255, 255) if is_partial else (0, 255, 0)  # Yellow for partial, green for confident
            
            # Draw background rectangle (semi-transparent look with solid color)
            cv2.rectangle(display, (tx - 5, ty - th - 8), (tx + tw + 5, ty + 8), (0, 0, 0), -1)
            
            # Draw text
            cv2.putText(display, display_text, (tx, ty), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
    
    # Detect license plates (every N frames)
    if frame_num % PROCESS_EVERY_N_FRAMES == 0:
        plates = plate_detector(original, conf=0.2, verbose=False)[0]  # Lower confidence to detect more plates
        
        if DEBUG_MODE and len(plates.boxes.data) > 0:
            print(f"\nFrame {frame_num}: YOLO detected {len(plates.boxes.data)} plate(s)")
        
        for plate in plates.boxes.data.tolist():
            px1, py1, px2, py2, pconf, pcls = plate
            
            # Match to vehicle - try multiple methods
            car = get_car(plate, tracks)
            car_id = int(car[4]) if car[4] != -1 else -1
            
            # If no direct match, find closest vehicle by distance
            if car_id == -1 and len(tracks) > 0:
                # Find closest vehicle to plate
                plate_center_x = (px1 + px2) / 2
                plate_center_y = (py1 + py2) / 2
                
                min_dist = float('inf')
                closest_vehicle = None
                
                for track in tracks:
                    vx1, vy1, vx2, vy2, vid = track
                    vehicle_center_x = (vx1 + vx2) / 2
                    vehicle_center_y = (vy1 + vy2) / 2
                    
                    dist = ((plate_center_x - vehicle_center_x)**2 + 
                           (plate_center_y - vehicle_center_y)**2) ** 0.5
                    
                    if dist < min_dist:
                        min_dist = dist
                        closest_vehicle = track
                
                if closest_vehicle is not None:
                    car = closest_vehicle
                    car_id = int(car[4])
            
            # Process plate if we have a vehicle
            if car_id != -1:
                # Crop with padding
                pad = 5
                y1p = max(0, int(py1) - pad)
                y2p = min(original.shape[0], int(py2) + pad)
                x1p = max(0, int(px1) - pad)
                x2p = min(original.shape[1], int(px2) + pad)
                crop = original[y1p:y2p, x1p:x2p, :]
                
                if crop.size == 0:
                    if DEBUG_MODE:
                        print(f"  ⚠ Empty crop for car {car_id}")
                    continue
                
                # Save original crop for debugging
                if SAVE_PLATE_CROPS and frame_num % 10 == 0:  # Save every 10th frame
                    cv2.imwrite(f'plate_crops/car{car_id}_frame{frame_num}.jpg', crop)
                
                # Read plate - pass original crop, preprocessing will be done in util.py
                if DEBUG_MODE:
                    print(f"  Running OCR on plate for car {car_id}...")
                text, score = read_license_plate(crop)
                
                if DEBUG_MODE:
                    if text:
                        print(f"  OCR Result: '{text}' (score: {score:.2f})")
                    else:
                        print(f"  OCR Result: No text detected")
                
                # Accept any detection, even partial/low confidence
                if text:
                    # Mark as partial if low confidence
                    is_partial = score < 0.3
                    display_text = f"{text}" if not is_partial else f"{text}?"
                    
                    # Update cache with best score OR longer text
                    should_update = False
                    if car_id not in plate_cache:
                        should_update = True
                    elif score > plate_cache[car_id]['text_score']:
                        should_update = True
                    elif len(text) > len(plate_cache[car_id]['text']) and score >= MIN_PLATE_CONFIDENCE:
                        should_update = True  # Prefer longer/more complete reads
                    
                    if should_update:
                        plates_found += 1
                        print(f"✓ Car {car_id} → Plate: {display_text} (Confidence: {score:.2f})")
                        
                        plate_cache[car_id] = {
                            'text': text,
                            'text_score': score,
                            'bbox': [px1, py1, px2, py2],
                            'bbox_score': pconf,
                            'is_partial': is_partial
                        }
                    
                    # Save result
                    results[frame_num][car_id] = {
                        'car': {'bbox': list(car[:4])},
                        'license_plate': {
                            'bbox': [px1, py1, px2, py2],
                            'text': text,
                            'bbox_score': pconf,
                            'text_score': score
                        }
                    }
                    
                    # Draw yellow box around plate for visibility
                    cv2.rectangle(display, (int(px1), int(py1)), (int(px2), int(py2)), (0, 255, 255), 2)
    
    else:
        # Use cached plates
        for track in tracks:
            cid = int(track[4])
            if cid in plate_cache:
                results[frame_num][cid] = {
                    'car': {'bbox': list(track[:4])},
                    'license_plate': {
                        'bbox': plate_cache[cid]['bbox'],
                        'text': plate_cache[cid]['text'],
                        'bbox_score': plate_cache[cid]['bbox_score'],
                        'text_score': plate_cache[cid]['text_score']
                    }
                }
    
    # Write frame to output video
    video_writer.write(display)
    
    # Display
    info = f"Frame: {frame_num}/{total_frames} | Plates: {plates_found} | Vehicles: {len(plate_cache)} | Press 'q' to quit"
    cv2.putText(display, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imshow('License Plate Detection', display)
    
    # Show progress
    if frame_num % 30 == 0:
        progress = (frame_num / total_frames) * 100
        print(f"Progress: {frame_num}/{total_frames} ({progress:.1f}%)")
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\n⚠ Stopped by user")
        break
    
    frame_num += 1

video_writer.release()
cv2.destroyAllWindows()

# Summary
print(f"\n{'='*60}")
print(f"PROCESSING COMPLETE")
print(f"{'='*60}")
print(f"Total frames: {frame_num}")
print(f"Plates detected: {plates_found}")
print(f"Unique vehicles: {len(plate_cache)}")
print(f"\nUnique license plates found:")
for vid, data in plate_cache.items():
    print(f"  Vehicle {vid}: {data['text']} (confidence: {data['text_score']:.2f})")
print(f"{'='*60}\n")

# Save results
print(f"Saving results...")
write_csv(results, CSV_OUTPUT_PATH)
print(f"✅ Output video saved to: {OUTPUT_VIDEO_PATH}")
print(f"✅ CSV data saved to: {CSV_OUTPUT_PATH}")
print(f"\n🎉 All done!")