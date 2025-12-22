"""Test if the license plate detector model is working"""
import cv2
from ultralytics import YOLO
import sys

# Load video
video_path = './sample2.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: Could not open video {video_path}")
    sys.exit(1)

# Load plate detector
print("Loading license plate detector...")
plate_detector = YOLO('license_plate_detector.pt')
print("✓ Model loaded\n")

# Test on first 10 frames
frame_count = 0
total_plates = 0

print("Testing plate detection on first 10 frames...")
print("="*60)

while frame_count < 10:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detect plates
    results = plate_detector(frame, verbose=False)[0]
    plates = results.boxes.data.tolist()
    
    print(f"\nFrame {frame_count}:")
    print(f"  Plates detected by YOLO: {len(plates)}")
    
    if len(plates) > 0:
        total_plates += len(plates)
        for i, plate in enumerate(plates):
            x1, y1, x2, y2, conf, cls = plate
            print(f"  Plate {i+1}: bbox=({int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}), conf={conf:.2f}")
            
            # Save the first plate image for inspection
            if frame_count == 0 and i == 0:
                plate_crop = frame[int(y1):int(y2), int(x1):int(x2)]
                cv2.imwrite('first_detected_plate.jpg', plate_crop)
                print(f"  Saved first plate to: first_detected_plate.jpg")
    
    frame_count += 1

cap.release()

print("\n" + "="*60)
print(f"SUMMARY:")
print(f"Frames tested: {frame_count}")
print(f"Total plates detected: {total_plates}")
print("="*60)

if total_plates == 0:
    print("\n⚠ WARNING: No plates detected!")
    print("This could mean:")
    print("  1. The license_plate_detector.pt model is not trained properly")
    print("  2. The video doesn't contain visible license plates")
    print("  3. The detection confidence threshold is too high")
else:
    print(f"\n✓ Plate detector is working! Found {total_plates} plates")
    print("If OCR is failing, check the OCR preprocessing")
