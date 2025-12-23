#!/usr/bin/env python3
"""Quick diagnostic - Test if YOLO models work"""
import cv2
from ultralytics import YOLO
import sys

print("="*60)
print("DIAGNOSTIC TEST - License Plate Detection System")
print("="*60)

# Test 1: Check video file
print("\n1️⃣  Testing video file...")
video_path = './sample.mp4'
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"   ❌ ERROR: Cannot open {video_path}")
    sys.exit(1)

ret, frame = cap.read()
if not ret:
    print("   ❌ ERROR: Cannot read first frame")
    sys.exit(1)

print(f"   ✅ Video OK: {frame.shape[1]}x{frame.shape[0]}")
cap.release()

# Test 2: Load vehicle detector
print("\n2️⃣  Loading vehicle detector (yolov8n.pt)...")
try:
    vehicle_detector = YOLO('yolov8n.pt')
    print("   ✅ Vehicle detector loaded")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    sys.exit(1)

# Test 3: Test vehicle detection on first frame
print("\n3️⃣  Testing vehicle detection on first frame...")
results = vehicle_detector(frame, conf=0.1, verbose=False)[0]
all_detections = results.boxes.data.tolist()
print(f"   Total detections (all classes): {len(all_detections)}")

vehicles = [2, 3, 5, 7]  # car, motorcycle, bus, truck
vehicle_count = 0
for det in all_detections:
    x1, y1, x2, y2, conf, cls = det
    class_id = int(cls)
    if class_id in vehicles:
        vehicle_count += 1
        print(f"     • Class {class_id} (vehicle): confidence={conf:.3f}")
    else:
        if len(all_detections) < 20:  # Only show if not too many
            print(f"     • Class {class_id} (other): confidence={conf:.3f}")

if vehicle_count == 0:
    print("   ⚠️  NO VEHICLES DETECTED!")
    print("   Trying lower confidence (0.05)...")
    results2 = vehicle_detector(frame, conf=0.05, verbose=False)[0]
    for det in results2.boxes.data.tolist():
        x1, y1, x2, y2, conf, cls = det
        if int(cls) in vehicles:
            print(f"     • Class {int(cls)}: conf={conf:.3f}")
            vehicle_count += 1
else:
    print(f"   ✅ Found {vehicle_count} vehicles")

# Test 4: Load plate detector
print("\n4️⃣  Loading license plate detector...")
try:
    plate_detector = YOLO('license_plate_detector.pt')
    print("   ✅ Plate detector loaded")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    sys.exit(1)

# Test 5: Test plate detection
print("\n5️⃣  Testing plate detection on first frame...")
plate_results = plate_detector(frame, conf=0.1, verbose=False)[0]
plates_found = len(plate_results.boxes.data)
print(f"   Plates detected: {plates_found}")

if plates_found > 0:
    for i, plate in enumerate(plate_results.boxes.data.tolist()[:5]):  # Show first 5
        x1, y1, x2, y2, pconf, pcls = plate
        print(f"     • Plate {i+1}: confidence={pconf:.3f}")
else:
    print("   ⚠️  NO PLATES DETECTED")
    print("   Trying lower confidence (0.05)...")
    plate_results2 = plate_detector(frame, conf=0.05, verbose=False)[0]
    plates_found2 = len(plate_results2.boxes.data)
    print(f"   Plates at conf=0.05: {plates_found2}")

print("\n" + "="*60)
if vehicle_count > 0 and plates_found > 0:
    print("✅ SYSTEM OK - Both models are detecting!")
elif vehicle_count > 0:
    print("⚠️  VEHICLE DETECTION OK, but plate detector not finding plates")
elif plates_found > 0:
    print("⚠️  PLATE DETECTION OK, but vehicle detector not finding vehicles") 
else:
    print("❌ CRITICAL: Neither model is detecting anything!")
    print("   Possible issues:")
    print("   - Models not trained properly")
    print("   - Video content doesn't match expected input")
    print("   - Confidence thresholds too high")
print("="*60)
