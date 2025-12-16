"""
Configuration Management for Smart Parking System MVP
GovTech Bhutan - Emerging Technology Division
Budget: ₹300,000 | Timeline: 09.12.25 - 29.12.25
"""

import os
from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================
PROJECT_ROOT = Path(__file__).parent
VIDEO_DIR = PROJECT_ROOT / "videos"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"
CONFIG_DIR = PROJECT_ROOT / "configs"
MODELS_DIR = PROJECT_ROOT / "models"

# Create directories if they don't exist
for directory in [VIDEO_DIR, OUTPUT_DIR, LOGS_DIR, CONFIG_DIR, MODELS_DIR]:
    directory.mkdir(exist_ok=True)

# ============================================================================
# VIDEO INPUT CONFIGURATION
# ============================================================================
# Path to your CCTV video file
VIDEO_SOURCE = "parking_video.mp4.mp4"

# Alternative: Use camera index for live feed (0 = default camera)
# VIDEO_SOURCE = 0

# Video processing settings
FRAME_SKIP = 5  # Process every 6th frame (0=every frame, 5=every 6th) - MAXIMUM FPS BOOST
DISPLAY_WIDTH = 1280  # Display window width
DISPLAY_HEIGHT = 720  # Display window height
PROCESS_SCALE = 0.35  # Scale video to 0.35 for faster processing (smaller = faster)

# ============================================================================
# YOLO MODEL CONFIGURATION
# ============================================================================
# YOLOv8 model size: n (nano), s (small), m (medium), l (large), x (extra large)
# Recommendation: 's' for best speed, 'm' for best accuracy
YOLO_MODEL = "yolov8n.pt"  # NANO model for maximum FPS (3-4x faster than small)
YOLO_DEVICE = "cpu"  # Use "cuda" or "0" for GPU if available
YOLO_IMGSZ = 384  # Input image size (smaller = faster, 384 optimal for nano)

# Detection confidence threshold (0.0 - 1.0)
# Higher = fewer false positives, may miss some vehicles
# Lower = detect more vehicles, more false positives
# CRITICAL: Lowered to 0.30 to detect small/distant parked vehicles (Slot-4 fix)
CONFIDENCE_THRESHOLD = 0.30  # Catches small parked cars that have low confidence

# IoU (Intersection over Union) threshold for NMS (Non-Maximum Suppression)
IOU_THRESHOLD = 0.45

# Vehicle classes to detect (COCO dataset class IDs)
# 2: car, 3: motorcycle, 5: bus, 7: truck
VEHICLE_CLASSES = [2, 3, 5, 7]

# ============================================================================
# PARKING SLOT CONFIGURATION
# ============================================================================
# Path to parking slot configuration file (JSON)
PARKING_SLOTS_CONFIG = str(CONFIG_DIR / "parking_slots.json")

# Minimum IoU between vehicle bbox and parking slot to consider it occupied
# Higher value = vehicle must overlap more with slot to be counted  
# CRITICAL: Lowered to 0.10 to catch vehicles at edges of slots (Slot-4 fix)
SLOT_OCCUPANCY_THRESHOLD = 0.10  # 10% overlap minimum - very lenient for edge cases

# Fallback detection: use center point if IoU is low
# If vehicle center is inside slot polygon, count as occupied even with low IoU
USE_CENTER_POINT_FALLBACK = True  # Enable center-point detection method

# ============================================================================
# DETECTION STABILIZATION SETTINGS (CRITICAL FOR EVALUATION)
# ============================================================================
# Number of consecutive frames a vehicle must be detected before status change
# This prevents flickering and false positives from shadows, people, etc.
# CRITICAL: Increased to 20 frames to filter out moving/passing vehicles on road
MIN_CONSECUTIVE_FRAMES = 20  # Vehicle must be stationary for 20 frames (0.7s at 29fps)

# Minimum time (seconds) between status changes for same slot
# Prevents rapid occupied->vacant->occupied fluctuations
# CRITICAL: Increased to eliminate flickering from moving traffic
DEBOUNCE_TIME = 5.0  # 5 seconds minimum between changes (was 3.0 - too short!)

# Frame buffer size for temporal consistency check
FRAME_BUFFER_SIZE = 10  # Keep last 10 frames for analysis

# Confidence averaging: average confidence over N frames before decision
CONFIDENCE_AVERAGING_FRAMES = 5

# ============================================================================
# ENTRY/EXIT EVENT DETECTION
# ============================================================================
# Enable entry/exit event logging
ENABLE_ENTRY_EXIT_TRACKING = True

# Minimum time (seconds) a vehicle must be in slot to count as valid parking
MIN_PARKING_DURATION = 5.0  # Filter out vehicles just passing through

# Maximum time (seconds) to keep tracking departed vehicles
MAX_TRACKING_TIME = 300.0  # 5 minutes

# ============================================================================
# VISUAL DISPLAY SETTINGS
# ============================================================================
# Colors for slot status (BGR format for OpenCV)
COLOR_VACANT = (0, 255, 0)  # Green
COLOR_OCCUPIED = (0, 0, 255)  # Red
COLOR_UNCERTAIN = (0, 165, 255)  # Orange
COLOR_SLOT_BORDER = (255, 255, 255)  # White

# Opacity for slot overlay (0.0 = transparent, 1.0 = opaque)
SLOT_OVERLAY_ALPHA = 0.3

# Text settings
FONT_SCALE = 0.6
FONT_THICKNESS = 2
TEXT_COLOR = (255, 255, 255)  # White
TEXT_BG_COLOR = (0, 0, 0)  # Black background

# Detection box settings
BBOX_THICKNESS = 2
BBOX_COLOR = (255, 0, 255)  # Magenta for vehicle bounding boxes

# Display FPS and stats on screen
SHOW_FPS = True
SHOW_DETECTION_COUNT = True
SHOW_CONFIDENCE = True

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
# Log file path
LOG_FILE = str(LOGS_DIR / "parking_system.log")

# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Enable detailed event logging (entry/exit timestamps)
EVENT_LOG_FILE = str(LOGS_DIR / "parking_events.csv")

# ============================================================================
# PERFORMANCE OPTIMIZATION
# ============================================================================
# Enable multi-threading for video processing
ENABLE_MULTITHREADING = True

# Number of threads for frame processing
NUM_THREADS = 2

# Frame queue size
FRAME_QUEUE_SIZE = 30

# Enable performance profiling
ENABLE_PROFILING = False

# Target FPS (for processing speed monitoring)
TARGET_FPS = 30

# ============================================================================
# ALERT SETTINGS (OPTIONAL - FUTURE ENHANCEMENT)
# ============================================================================
# Enable alerts for specific conditions
ENABLE_ALERTS = False

# Alert when parking lot is full (all slots occupied)
ALERT_ON_FULL = True

# Alert when specific slots are occupied for too long (hours)
MAX_PARKING_TIME_HOURS = 24

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================
# Use tracking algorithm for better vehicle following
# Options: "sort", "deepsort", "bytetrack", None
TRACKING_ALGORITHM = None  # Disable for MVP, enable if needed

# Save processed video output
SAVE_OUTPUT_VIDEO = True
OUTPUT_VIDEO_PATH = str(OUTPUT_DIR / "parking_detection_output.mp4")
OUTPUT_VIDEO_FPS = 30
OUTPUT_VIDEO_CODEC = "mp4v"  # or "avc1" for H.264

# Save detection snapshots on events
SAVE_SNAPSHOTS = True
SNAPSHOT_DIR = OUTPUT_DIR / "snapshots"
SNAPSHOT_DIR.mkdir(exist_ok=True)

# ============================================================================
# CALIBRATION MODE
# ============================================================================
# Enable slot definition mode (for initial setup)
CALIBRATION_MODE = False

# Instructions for calibration mode
CALIBRATION_INSTRUCTIONS = """
PARKING SLOT CALIBRATION MODE
==============================
Left Click: Add point to current parking slot polygon
Right Click: Complete current parking slot
Press 'c': Clear all points
Press 's': Save parking slot configuration
Press 'q': Quit calibration mode

Define parking slots by clicking corners in order (minimum 4 points per slot).
"""

# ============================================================================
# VALIDATION AND ERROR CHECKING
# ============================================================================
def validate_config():
    """Validate configuration settings before system starts."""
    errors = []
    
    # Check if video source exists (if it's a file path)
    if isinstance(VIDEO_SOURCE, str) and not os.path.exists(VIDEO_SOURCE):
        errors.append(f"Video source not found: {VIDEO_SOURCE}")
    
    # Check threshold ranges
    if not 0.0 <= CONFIDENCE_THRESHOLD <= 1.0:
        errors.append(f"CONFIDENCE_THRESHOLD must be between 0.0 and 1.0, got {CONFIDENCE_THRESHOLD}")
    
    if not 0.0 <= SLOT_OCCUPANCY_THRESHOLD <= 1.0:
        errors.append(f"SLOT_OCCUPANCY_THRESHOLD must be between 0.0 and 1.0, got {SLOT_OCCUPANCY_THRESHOLD}")
    
    # Check frame settings
    if MIN_CONSECUTIVE_FRAMES < 1:
        errors.append(f"MIN_CONSECUTIVE_FRAMES must be >= 1, got {MIN_CONSECUTIVE_FRAMES}")
    
    if DEBOUNCE_TIME < 0:
        errors.append(f"DEBOUNCE_TIME must be >= 0, got {DEBOUNCE_TIME}")
    
    # Check if parking slots config exists (unless in calibration mode)
    if not CALIBRATION_MODE and not os.path.exists(PARKING_SLOTS_CONFIG):
        errors.append(f"Parking slots configuration not found: {PARKING_SLOTS_CONFIG}")
        errors.append("Run in CALIBRATION_MODE=True first to define parking slots.")
    
    return errors

# ============================================================================
# PRESET CONFIGURATIONS FOR DIFFERENT SCENARIOS
# ============================================================================

# High accuracy configuration (slower, more reliable)
def use_high_accuracy_preset():
    global YOLO_MODEL, CONFIDENCE_THRESHOLD, MIN_CONSECUTIVE_FRAMES, DEBOUNCE_TIME
    YOLO_MODEL = "yolov8l.pt"
    CONFIDENCE_THRESHOLD = 0.6
    MIN_CONSECUTIVE_FRAMES = 7
    DEBOUNCE_TIME = 5.0

# Fast processing configuration (faster, may have more false positives)
def use_fast_processing_preset():
    global YOLO_MODEL, CONFIDENCE_THRESHOLD, MIN_CONSECUTIVE_FRAMES, FRAME_SKIP
    YOLO_MODEL = "yolov8n.pt"
    CONFIDENCE_THRESHOLD = 0.4
    MIN_CONSECUTIVE_FRAMES = 3
    FRAME_SKIP = 1

# Balanced configuration (recommended for MVP demo)
def use_balanced_preset():
    global YOLO_MODEL, CONFIDENCE_THRESHOLD, MIN_CONSECUTIVE_FRAMES, DEBOUNCE_TIME
    YOLO_MODEL = "yolov8m.pt"
    CONFIDENCE_THRESHOLD = 0.5
    MIN_CONSECUTIVE_FRAMES = 5
    DEBOUNCE_TIME = 3.0

# Apply balanced preset by default
use_balanced_preset()

if __name__ == "__main__":
    # Run validation when config is imported
    errors = validate_config()
    if errors:
        print("Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration validated successfully!")
        print(f"Video Source: {VIDEO_SOURCE}")
        print(f"YOLO Model: {YOLO_MODEL}")
        print(f"Confidence Threshold: {CONFIDENCE_THRESHOLD}")
        print(f"Min Consecutive Frames: {MIN_CONSECUTIVE_FRAMES}")
        print(f"Debounce Time: {DEBOUNCE_TIME}s")
