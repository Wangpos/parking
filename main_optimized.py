"""
Optimized License Plate Detection System
Efficiently detects vehicles, tracks them, and recognizes Bhutanese license plates
"""

from ultralytics import YOLO
import cv2
import numpy as np
from sort.sort import Sort
from util import get_car, read_license_plate, write_csv

# ======================== CONFIGURATION ========================
VIDEO_PATH = './sample2.mp4'
OUTPUT_CSV = './test.csv'
PROCESS_EVERY_N_FRAMES = 2  # Process license plates every N frames (1=all, 2=every other, etc.)
VEHICLE_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck

# Display settings
SHOW_VIDEO = True
SHOW_VEHICLE_BOXES = True
SHOW_CONFIDENCE_SCORES = False  # Show confidence scores on video
FONT_SCALE = 1.2
FONT_THICKNESS = 2
# ================================================================


class LicensePlateDetector:
    """Main class for license plate detection and tracking"""
    
    def __init__(self):
        # Initialize models
        print("Loading models...")
        self.vehicle_model = YOLO('yolov8n.pt')
        self.plate_model = YOLO('license_plate_detector.pt')
        
        # Initialize tracker
        self.tracker = Sort()
        
        # Storage
        self.results = {}
        self.plate_cache = {}  # Store best plate reading per vehicle
        
        print("✓ Models loaded successfully\n")
    
    def preprocess_plate(self, plate_img):
        """Enhanced preprocessing for better OCR accuracy"""
        # Convert to grayscale
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        
        # Upscale 3x for better OCR
        h, w = gray.shape
        upscaled = cv2.resize(gray, (w * 3, h * 3), interpolation=cv2.INTER_CUBIC)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(upscaled)
        
        # Denoise while preserving edges
        filtered = cv2.bilateralFilter(enhanced, 11, 17, 17)
        
        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            filtered, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 2
        )
        
        # Clean up with morphology
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    def draw_plate_number(self, frame, vehicle_bbox, plate_text):
        """Draw license plate number on the vehicle"""
        x1, y1, x2, y2 = map(int, vehicle_bbox[:4])
        
        # Calculate text size
        (text_w, text_h), _ = cv2.getTextSize(
            plate_text, cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, FONT_THICKNESS
        )
        
        # Position above vehicle
        text_x = x1 + 10
        text_y = y1 - 20
        
        # Keep text on screen
        if text_y < text_h + 20:
            text_y = y1 + text_h + 30
        
        # Draw white background
        cv2.rectangle(frame,
                     (text_x - 10, text_y - text_h - 10),
                     (text_x + text_w + 10, text_y + 10),
                     (255, 255, 255), -1)
        
        # Draw green text
        cv2.putText(frame, plate_text,
                   (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, (0, 200, 0), FONT_THICKNESS)
    
    def process_video(self):
        """Main processing loop"""
        frame_count = 0
        plates_detected = 0
        
        print(f"Processing video: {VIDEO_PATH}")
        print(f"Detection interval: Every {PROCESS_EVERY_N_FRAMES} frame(s)\n")
        
        # Create window if showing video
        if SHOW_VIDEO:
            cv2.namedWindow('License Plate Detection', cv2.WINDOW_NORMAL)
        
        # Process video with YOLO streaming
        for frame_result in self.vehicle_model.predict(
            source=VIDEO_PATH, 
            stream=True, 
            verbose=False
        ):
            original_frame = frame_result.orig_img
            display_frame = original_frame.copy()
            
            # Store results for this frame
            self.results[frame_count] = {}
            
            # ==================== VEHICLE DETECTION ====================
            vehicle_detections = []
            for detection in frame_result.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = detection
                if int(class_id) in VEHICLE_CLASSES:
                    vehicle_detections.append([x1, y1, x2, y2, score])
                    
                    if SHOW_VEHICLE_BOXES:
                        cv2.rectangle(display_frame, (int(x1), int(y1)), 
                                    (int(x2), int(y2)), (0, 255, 0), 2)
            
            # ==================== VEHICLE TRACKING ====================
            tracked_vehicles = self.tracker.update(np.asarray(vehicle_detections))
            
            # Draw vehicle IDs and cached plates
            for track in tracked_vehicles:
                x1, y1, x2, y2, track_id = track
                track_id = int(track_id)
                
                # Draw vehicle ID
                if SHOW_CONFIDENCE_SCORES:
                    cv2.putText(display_frame, f'ID:{track_id}', 
                               (int(x1), int(y2) + 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                
                # Display cached license plate
                if track_id in self.plate_cache:
                    self.draw_plate_number(display_frame, track, 
                                         self.plate_cache[track_id]['text'])
            
            # ==================== LICENSE PLATE DETECTION ====================
            if frame_count % PROCESS_EVERY_N_FRAMES == 0:
                plate_detections = self.plate_model(original_frame, verbose=False)[0]
                
                for plate_detection in plate_detections.boxes.data.tolist():
                    px1, py1, px2, py2, p_score, p_class = plate_detection
                    
                    # Match plate to vehicle
                    car_bbox = get_car(plate_detection, tracked_vehicles)
                    car_id = int(car_bbox[4]) if car_bbox[4] != -1 else -1
                    
                    if car_id != -1:
                        # Crop plate with padding
                        padding = 5
                        y1_p = max(0, int(py1) - padding)
                        y2_p = min(original_frame.shape[0], int(py2) + padding)
                        x1_p = max(0, int(px1) - padding)
                        x2_p = min(original_frame.shape[1], int(px2) + padding)
                        
                        plate_crop = original_frame[y1_p:y2_p, x1_p:x2_p, :]
                        
                        if plate_crop.size == 0:
                            continue
                        
                        # Preprocess and read plate
                        processed_plate = self.preprocess_plate(plate_crop)
                        plate_text, text_score = read_license_plate(processed_plate)
                        
                        if plate_text is not None:
                            plates_detected += 1
                            print(f"✓ Frame {frame_count}: '{plate_text}' "
                                  f"(Vehicle ID: {car_id}, Confidence: {text_score:.2f})")
                            
                            # Update cache if better score
                            if (car_id not in self.plate_cache or 
                                text_score > self.plate_cache[car_id]['text_score']):
                                self.plate_cache[car_id] = {
                                    'text': plate_text,
                                    'text_score': text_score,
                                    'bbox': [px1, py1, px2, py2],
                                    'bbox_score': p_score
                                }
                            
                            # Store in results
                            self.results[frame_count][car_id] = {
                                'car': {'bbox': list(car_bbox[:4])},
                                'license_plate': {
                                    'bbox': [px1, py1, px2, py2],
                                    'text': plate_text,
                                    'bbox_score': p_score,
                                    'text_score': text_score
                                }
                            }
                            
                            # Draw green box around detected plate
                            cv2.rectangle(display_frame, (int(px1), int(py1)), 
                                        (int(px2), int(py2)), (0, 255, 0), 2)
            
            else:
                # Use cached plates for skipped frames
                for track in tracked_vehicles:
                    car_id = int(track[4])
                    if car_id in self.plate_cache:
                        self.results[frame_count][car_id] = {
                            'car': {'bbox': list(track[:4])},
                            'license_plate': {
                                'bbox': self.plate_cache[car_id]['bbox'],
                                'text': self.plate_cache[car_id]['text'],
                                'bbox_score': self.plate_cache[car_id]['bbox_score'],
                                'text_score': self.plate_cache[car_id]['text_score']
                            }
                        }
            
            # ==================== DISPLAY ====================
            if SHOW_VIDEO:
                # Add frame info
                info_text = f"Frame: {frame_count} | Plates: {plates_detected} | Press 'q' to quit"
                cv2.putText(display_frame, info_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow('License Plate Detection', display_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n⚠ Detection stopped by user")
                    break
            
            frame_count += 1
        
        # Cleanup
        if SHOW_VIDEO:
            cv2.destroyAllWindows()
        
        # Summary
        print(f"\n{'='*60}")
        print(f"PROCESSING COMPLETE")
        print(f"{'='*60}")
        print(f"Total frames processed: {frame_count}")
        print(f"License plates detected: {plates_detected}")
        print(f"Unique vehicles tracked: {len(self.plate_cache)}")
        print(f"{'='*60}\n")
        
        # Save results
        write_csv(self.results, OUTPUT_CSV)


def main():
    """Entry point"""
    detector = LicensePlateDetector()
    detector.process_video()
    
    print("✅ All done! Check test.csv for results.")
    print("\nNext steps:")
    print("  1. Run: python add_missing_data.py  (to interpolate missing frames)")
    print("  2. Run: python visualize.py         (to create output video)")


if __name__ == "__main__":
    main()
