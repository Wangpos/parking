"""
Quick Test for Automatic Parking Detection Mode
Tests basic functionality without video processing
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)

print("="*70)
print("AUTOMATIC MODE - QUICK TEST")
print("="*70)

# Test 1: Import modules
print("\n[1/5] Testing imports...")
try:
    from automatic_detector import (
        AutomaticParkingDetector,
        ParkingZone,
        TrackedVehicle,
        SUPERVISION_AVAILABLE
    )
    print("✓ automatic_detector imports successful")
except Exception as e:
    print(f"✗ Failed to import automatic_detector: {e}")
    sys.exit(1)

# Test 2: Check supervision availability
print("\n[2/5] Checking tracking library...")
if SUPERVISION_AVAILABLE:
    print("✓ Supervision library available - tracking enabled")
else:
    print("⚠️  Supervision not available - tracking disabled")

# Test 3: Initialize detector
print("\n[3/5] Initializing detector...")
try:
    # Use nano model for quick test
    detector = AutomaticParkingDetector(
        model_path="yolov8n.pt",
        confidence_threshold=0.25,
        device="cpu"
    )
    print("✓ Detector initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize detector: {e}")
    print("   Note: YOLOv8 will auto-download on first run")
    sys.exit(1)

# Test 4: Test parking zone
print("\n[4/5] Testing parking zone...")
try:
    zone = ParkingZone([(0, 0), (100, 0), (100, 100), (0, 100)])
    
    # Test point inside
    assert zone.contains_point((50, 50)) == True
    
    # Test bbox inside
    assert zone.contains_bbox((40, 40, 60, 60)) == True
    
    print("✓ Parking zone functionality working")
except Exception as e:
    print(f"✗ Parking zone test failed: {e}")
    sys.exit(1)

# Test 5: Test tracked vehicle
print("\n[5/5] Testing vehicle tracking...")
try:
    import numpy as np
    import cv2
    from datetime import datetime
    
    # Create test vehicle
    vehicle = TrackedVehicle(
        tracker_id=1,
        class_name="car",
        bbox=(100, 100, 200, 200),
        confidence=0.85
    )
    
    # Test speed calculation
    speed = vehicle.get_speed_pixels_per_second()
    assert speed >= 0
    
    # Test parking check
    is_parked = vehicle.check_if_parked(speed_threshold=3.0, time_threshold=5.0)
    
    print("✓ Vehicle tracking functionality working")
except Exception as e:
    print(f"✗ Vehicle tracking test failed: {e}")
    sys.exit(1)

# Success
print("\n" + "="*70)
print("ALL TESTS PASSED! ✓")
print("="*70)
print("\nAutomatic mode is ready to use!")
print("\nTo run with video:")
print("  python main_automatic.py --video path/to/video.mp4")
print("\nTo define parking zone:")
print("  python main_automatic.py --define-zone")
print("\nFor help:")
print("  python main_automatic.py --help")
print("="*70 + "\n")
