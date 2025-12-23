"""
Extract frames from video to create training dataset
This helps you collect images from your parking lot videos
"""

import cv2
import os
from pathlib import Path

# Configuration
VIDEO_PATH = './sample2.mp4'
OUTPUT_DIR = './training_frames'
EXTRACT_EVERY_N_FRAMES = 30  # Extract 1 frame every 30 frames (1 per second if 30fps)
MAX_FRAMES = 300  # Maximum frames to extract

def extract_frames():
    """Extract frames from video for annotation"""
    print(f"📹 Extracting frames from: {VIDEO_PATH}\n")
    
    # Create output directory
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    # Open video
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"❌ Error: Could not open {VIDEO_PATH}")
        return
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video info:")
    print(f"  FPS: {fps}")
    print(f"  Total frames: {total_frames}")
    print(f"  Duration: {total_frames/fps:.1f} seconds")
    print(f"  Extract every: {EXTRACT_EVERY_N_FRAMES} frames")
    print(f"  Max to extract: {MAX_FRAMES}\n")
    
    frame_count = 0
    extracted_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Extract frame if it's time
        if frame_count % EXTRACT_EVERY_N_FRAMES == 0 and extracted_count < MAX_FRAMES:
            filename = f"{OUTPUT_DIR}/frame_{frame_count:06d}.jpg"
            cv2.imwrite(filename, frame)
            extracted_count += 1
            
            if extracted_count % 10 == 0:
                print(f"Extracted {extracted_count} frames...")
        
        frame_count += 1
    
    cap.release()
    
    print(f"\n✅ Extraction complete!")
    print(f"   Extracted: {extracted_count} frames")
    print(f"   Saved to: {OUTPUT_DIR}/")
    print("\nNext steps:")
    print("1. Review frames and delete any without visible license plates")
    print("2. Use Roboflow/LabelImg to annotate the plates")
    print("3. Export annotations in YOLO format")
    print("4. Place in ./plate_training_data/ directory")

def extract_frames_with_plates():
    """Extract frames that likely contain plates (uses current detector)"""
    from ultralytics import YOLO
    
    print(f"📹 Extracting frames with detected plates from: {VIDEO_PATH}\n")
    
    # Create output directory
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    # Load models
    print("Loading models...")
    vehicle_detector = YOLO('yolov8n.pt')
    plate_detector = YOLO('license_plate_detector.pt')
    
    # Open video
    cap = cv2.VideoCapture(VIDEO_PATH)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    
    print(f"Scanning video for plates...\n")
    
    frame_count = 0
    extracted_count = 0
    
    for frame_result in vehicle_detector.predict(source=VIDEO_PATH, stream=True, verbose=False, conf=0.1):
        if extracted_count >= MAX_FRAMES:
            break
        
        # Only process every N frames
        if frame_count % EXTRACT_EVERY_N_FRAMES != 0:
            frame_count += 1
            continue
        
        frame = frame_result.orig_img
        
        # Check for vehicles
        vehicles = [d for d in frame_result.boxes.data.tolist() if int(d[5]) in [2, 3, 5, 7]]
        
        if len(vehicles) > 0:
            # Check for plates in this frame
            plate_results = plate_detector.predict(frame, verbose=False, conf=0.1)
            plates = plate_results[0].boxes.data.tolist()
            
            if len(plates) > 0:
                # This frame has both vehicles and plates!
                filename = f"{OUTPUT_DIR}/plate_frame_{frame_count:06d}.jpg"
                cv2.imwrite(filename, frame)
                extracted_count += 1
                
                print(f"✓ Frame {frame_count}: {len(vehicles)} vehicles, {len(plates)} plates")
        
        frame_count += 1
    
    print(f"\n✅ Extraction complete!")
    print(f"   Extracted: {extracted_count} frames with plates")
    print(f"   Saved to: {OUTPUT_DIR}/")
    print("\nThese frames likely contain license plates - perfect for training!")

if __name__ == "__main__":
    import sys
    
    if "--smart" in sys.argv:
        # Extract only frames with detected plates
        extract_frames_with_plates()
    else:
        # Extract frames uniformly
        extract_frames()
