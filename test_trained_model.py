"""
Test your newly trained Bhutanese plate detector
Compare it with the original model
"""

from ultralytics import YOLO
import cv2
import numpy as np

# Configuration
TEST_VIDEO = './sample2.mp4'
ORIGINAL_MODEL = 'license_plate_detector.pt'
TRAINED_MODEL = 'bhutan_plate_detector/bhutan_plates/weights/best.pt'

def test_model(model_path, model_name):
    """Test a plate detector model"""
    print(f"\n{'='*60}")
    print(f"Testing: {model_name}")
    print(f"Model: {model_path}")
    print(f"{'='*60}\n")
    
    # Load models
    vehicle_detector = YOLO('yolov8n.pt')
    plate_detector = YOLO(model_path)
    
    # Open video
    cap = cv2.VideoCapture(TEST_VIDEO)
    
    total_plates = 0
    total_vehicles = 0
    frames_with_plates = 0
    frame_count = 0
    
    # Test on first 100 frames
    for frame_result in vehicle_detector.predict(source=TEST_VIDEO, stream=True, verbose=False, conf=0.1):
        if frame_count >= 100:
            break
        
        frame = frame_result.orig_img
        
        # Count vehicles
        vehicles = [d for d in frame_result.boxes.data.tolist() if int(d[5]) in [2, 3, 5, 7]]
        total_vehicles += len(vehicles)
        
        # Detect plates
        plate_results = plate_detector.predict(frame, verbose=False, conf=0.1)
        plates = plate_results[0].boxes.data.tolist()
        
        if len(plates) > 0:
            frames_with_plates += 1
            total_plates += len(plates)
        
        frame_count += 1
        
        if frame_count % 20 == 0:
            print(f"Frame {frame_count}: {len(vehicles)} vehicles, {len(plates)} plates")
    
    cap.release()
    
    # Results
    print(f"\n{'='*60}")
    print(f"RESULTS - {model_name}")
    print(f"{'='*60}")
    print(f"Frames processed: {frame_count}")
    print(f"Total vehicles detected: {total_vehicles}")
    print(f"Total plates detected: {total_plates}")
    print(f"Frames with plates: {frames_with_plates}/{frame_count} ({frames_with_plates/frame_count*100:.1f}%)")
    print(f"Avg plates per frame: {total_plates/frame_count:.2f}")
    print(f"Detection rate: {total_plates/total_vehicles*100:.1f}% (plates per vehicle)")
    print(f"{'='*60}\n")
    
    return {
        'frames': frame_count,
        'vehicles': total_vehicles,
        'plates': total_plates,
        'frames_with_plates': frames_with_plates,
        'detection_rate': total_plates/total_vehicles if total_vehicles > 0 else 0
    }

def compare_models():
    """Compare original vs trained model"""
    print("\n" + "="*60)
    print("  BHUTANESE PLATE DETECTOR COMPARISON")
    print("="*60)
    
    # Test original model
    try:
        original_results = test_model(ORIGINAL_MODEL, "Original Model")
    except Exception as e:
        print(f"❌ Could not test original model: {e}")
        original_results = None
    
    # Test trained model
    try:
        trained_results = test_model(TRAINED_MODEL, "Trained Model (Bhutanese)")
    except Exception as e:
        print(f"❌ Could not test trained model: {e}")
        print(f"   Did you train the model yet?")
        print(f"   Run: python train_bhutanese_plate_detector.py --train")
        trained_results = None
    
    # Comparison
    if original_results and trained_results:
        print("\n" + "="*60)
        print("  COMPARISON")
        print("="*60)
        print(f"{'Metric':<30} {'Original':<15} {'Trained':<15} {'Improvement':<15}")
        print("-"*60)
        
        metrics = [
            ('Total Plates Detected', 'plates'),
            ('Frames with Plates', 'frames_with_plates'),
            ('Detection Rate (%)', 'detection_rate')
        ]
        
        for metric_name, metric_key in metrics:
            orig = original_results[metric_key]
            trained = trained_results[metric_key]
            
            if metric_key == 'detection_rate':
                orig *= 100
                trained *= 100
                improvement = f"+{trained - orig:.1f}%"
                print(f"{metric_name:<30} {orig:<15.1f} {trained:<15.1f} {improvement:<15}")
            else:
                improvement = f"+{trained - orig}"
                print(f"{metric_name:<30} {orig:<15} {trained:<15} {improvement:<15}")
        
        print("="*60)

def test_on_single_image(image_path):
    """Test both models on a single image"""
    print(f"\nTesting on image: {image_path}\n")
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Could not load image: {image_path}")
        return
    
    # Test both models
    original = YOLO(ORIGINAL_MODEL)
    trained = YOLO(TRAINED_MODEL)
    
    print("Original model:")
    orig_results = original.predict(img, conf=0.1, verbose=True)
    
    print("\nTrained model:")
    trained_results = trained.predict(img, conf=0.1, verbose=True)
    
    # Visualize
    orig_img = orig_results[0].plot()
    trained_img = trained_results[0].plot()
    
    # Side by side
    combined = np.hstack([orig_img, trained_img])
    cv2.imshow('Left: Original | Right: Trained', combined)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1].endswith(('.jpg', '.png')):
        # Test on single image
        test_on_single_image(sys.argv[1])
    else:
        # Compare on video
        compare_models()
