"""
Utility Functions for Smart Parking System MVP
GovTech Bhutan - Emerging Technology Division
Includes: Logging, timestamps, performance monitoring, event tracking
"""

import logging
import time
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import config


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(log_file: str = None, log_level: str = None) -> logging.Logger:
    """
    Configure logging for the parking system.
    
    Args:
        log_file: Path to log file (default from config)
        log_level: Logging level (default from config)
        
    Returns:
        Configured logger instance
    """
    log_file = log_file or config.LOG_FILE
    log_level = log_level or config.LOG_LEVEL
    
    # Create logs directory if it doesn't exist
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also print to console
        ]
    )
    
    logger = logging.getLogger('SmartParking')
    logger.info("="*60)
    logger.info("Smart Parking System Initialized")
    logger.info(f"GovTech Bhutan MVP - Budget: ₹3,00,000")
    logger.info(f"Evaluation Date: 29.12.2025")
    logger.info("="*60)
    
    return logger


# ============================================================================
# TIMESTAMP UTILITIES
# ============================================================================

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def get_formatted_timestamp(dt: datetime = None) -> str:
    """Get formatted timestamp for display."""
    dt = dt or datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def calculate_duration(start_time: datetime, end_time: datetime = None) -> timedelta:
    """Calculate duration between two timestamps."""
    end_time = end_time or datetime.now()
    return end_time - start_time


def format_duration(duration: timedelta) -> str:
    """Format duration as human-readable string."""
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO format timestamp string to datetime object."""
    return datetime.fromisoformat(timestamp_str)


# ============================================================================
# EVENT LOGGING
# ============================================================================

class EventLogger:
    """Log parking events (entry/exit) to CSV file."""
    
    def __init__(self, log_file: str = None):
        """
        Initialize event logger.
        
        Args:
            log_file: Path to CSV log file (default from config)
        """
        self.log_file = log_file or config.EVENT_LOG_FILE
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Create CSV file with headers if it doesn't exist
        if not Path(self.log_file).exists():
            self._create_log_file()
    
    def _create_log_file(self):
        """Create CSV file with headers."""
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Timestamp', 'Slot_ID', 'Slot_Name', 'Event_Type', 
                'Duration', 'Confidence', 'Details'
            ])
    
    def log_entry(self, slot_id: int, slot_name: str, confidence: float = None, details: str = ""):
        """Log vehicle entry event."""
        self._log_event(slot_id, slot_name, 'ENTRY', confidence=confidence, details=details)
    
    def log_exit(self, slot_id: int, slot_name: str, duration: str = None, details: str = ""):
        """Log vehicle exit event."""
        self._log_event(slot_id, slot_name, 'EXIT', duration=duration, details=details)
    
    def log_status_change(self, slot_id: int, slot_name: str, new_status: str, confidence: float = None):
        """Log parking slot status change."""
        event_type = f'STATUS_CHANGE_{new_status.upper()}'
        self._log_event(slot_id, slot_name, event_type, confidence=confidence)
    
    def _log_event(self, slot_id: int, slot_name: str, event_type: str, 
                   duration: str = "", confidence: float = None, details: str = ""):
        """Internal method to log event to CSV."""
        timestamp = get_formatted_timestamp()
        confidence_str = f"{confidence:.2f}" if confidence is not None else ""
        
        try:
            with open(self.log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp, slot_id, slot_name, event_type,
                    duration, confidence_str, details
                ])
        except Exception as e:
            logging.error(f"Error writing to event log: {e}")
    
    def get_recent_events(self, limit: int = 10) -> List[Dict]:
        """Get most recent events from log file."""
        events = []
        try:
            with open(self.log_file, 'r') as f:
                reader = csv.DictReader(f)
                events = list(reader)[-limit:]
        except Exception as e:
            logging.error(f"Error reading event log: {e}")
        return events


# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

class PerformanceMonitor:
    """Monitor and track system performance metrics."""
    
    def __init__(self, window_size: int = 30):
        """
        Initialize performance monitor.
        
        Args:
            window_size: Number of frames to average for FPS calculation
        """
        self.window_size = window_size
        self.frame_times: List[float] = []
        self.processing_times: List[float] = []
        self.detection_counts: List[int] = []
        self.start_time = time.time()
        self.frame_count = 0
        self.last_frame_time = time.time()
    
    def start_frame(self):
        """Mark the start of frame processing."""
        self.last_frame_time = time.time()
    
    def end_frame(self, detection_count: int = 0):
        """
        Mark the end of frame processing.
        
        Args:
            detection_count: Number of detections in this frame
        """
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        
        self.frame_times.append(frame_time)
        self.detection_counts.append(detection_count)
        self.frame_count += 1
        
        # Keep only recent frames
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
            self.detection_counts.pop(0)
    
    def get_fps(self) -> float:
        """Calculate current frames per second."""
        if len(self.frame_times) < 2:
            return 0.0
        avg_frame_time = np.mean(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
    
    def get_average_processing_time(self) -> float:
        """Get average frame processing time in milliseconds."""
        if len(self.frame_times) == 0:
            return 0.0
        return np.mean(self.frame_times) * 1000  # Convert to ms
    
    def get_average_detections(self) -> float:
        """Get average number of detections per frame."""
        if len(self.detection_counts) == 0:
            return 0.0
        return np.mean(self.detection_counts)
    
    def get_uptime(self) -> timedelta:
        """Get system uptime."""
        return timedelta(seconds=time.time() - self.start_time)
    
    def get_stats(self) -> Dict:
        """Get all performance statistics."""
        return {
            'fps': self.get_fps(),
            'avg_processing_time_ms': self.get_average_processing_time(),
            'avg_detections': self.get_average_detections(),
            'total_frames': self.frame_count,
            'uptime': format_duration(self.get_uptime())
        }
    
    def print_stats(self):
        """Print performance statistics to console."""
        stats = self.get_stats()
        print(f"\n{'='*50}")
        print(f"PERFORMANCE STATISTICS")
        print(f"{'='*50}")
        print(f"FPS: {stats['fps']:.1f}")
        print(f"Avg Processing Time: {stats['avg_processing_time_ms']:.1f} ms")
        print(f"Avg Detections/Frame: {stats['avg_detections']:.1f}")
        print(f"Total Frames Processed: {stats['total_frames']}")
        print(f"System Uptime: {stats['uptime']}")
        print(f"{'='*50}\n")


# ============================================================================
# DETECTION STABILIZATION
# ============================================================================

class DetectionStabilizer:
    """Stabilize detection results to prevent flickering and false positives."""
    
    def __init__(self, min_consecutive_frames: int = None, debounce_time: float = None):
        """
        Initialize detection stabilizer.
        
        Args:
            min_consecutive_frames: Minimum consecutive detections required
            debounce_time: Minimum time between status changes (seconds)
        """
        self.min_consecutive_frames = min_consecutive_frames or config.MIN_CONSECUTIVE_FRAMES
        self.debounce_time = debounce_time or config.DEBOUNCE_TIME
        
        # Track detection history per slot
        self.slot_detection_history: Dict[int, List[bool]] = {}
        self.slot_last_change_time: Dict[int, float] = {}
        self.slot_confidence_history: Dict[int, List[float]] = {}
    
    def update(self, slot_id: int, is_detected: bool, confidence: float = 1.0) -> Tuple[bool, bool]:
        """
        Update detection state for a slot and determine if status should change.
        
        Args:
            slot_id: Parking slot ID
            is_detected: Whether vehicle is detected in current frame
            confidence: Detection confidence (0.0 - 1.0)
            
        Returns:
            Tuple of (should_update_status, new_status)
        """
        current_time = time.time()
        
        # Initialize history for new slot
        if slot_id not in self.slot_detection_history:
            self.slot_detection_history[slot_id] = []
            self.slot_confidence_history[slot_id] = []
            self.slot_last_change_time[slot_id] = 0
        
        # Add current detection to history
        self.slot_detection_history[slot_id].append(is_detected)
        self.slot_confidence_history[slot_id].append(confidence)
        
        # Keep only recent history
        max_history = self.min_consecutive_frames * 2
        if len(self.slot_detection_history[slot_id]) > max_history:
            self.slot_detection_history[slot_id].pop(0)
            self.slot_confidence_history[slot_id].pop(0)
        
        # Get recent detections
        recent_detections = self.slot_detection_history[slot_id][-self.min_consecutive_frames:]
        
        # Check if we have enough consecutive frames
        if len(recent_detections) < self.min_consecutive_frames:
            return False, is_detected
        
        # Check if all recent frames agree
        all_detected = all(recent_detections)
        none_detected = not any(recent_detections)
        
        if not (all_detected or none_detected):
            # Mixed results, not stable yet
            return False, is_detected
        
        # Determine new status
        new_status = all_detected
        
        # Check debounce time
        time_since_last_change = current_time - self.slot_last_change_time[slot_id]
        if time_since_last_change < self.debounce_time:
            # Too soon to change status again
            return False, new_status
        
        # Status change is stable and allowed
        self.slot_last_change_time[slot_id] = current_time
        return True, new_status
    
    def get_average_confidence(self, slot_id: int, window: int = 5) -> float:
        """Get average confidence for a slot over recent frames."""
        if slot_id not in self.slot_confidence_history:
            return 0.0
        
        recent_confidences = self.slot_confidence_history[slot_id][-window:]
        if not recent_confidences:
            return 0.0
        
        return np.mean(recent_confidences)
    
    def reset_slot(self, slot_id: int):
        """Reset detection history for a specific slot."""
        if slot_id in self.slot_detection_history:
            del self.slot_detection_history[slot_id]
            del self.slot_confidence_history[slot_id]
            del self.slot_last_change_time[slot_id]
    
    def reset_all(self):
        """Reset all detection history."""
        self.slot_detection_history.clear()
        self.slot_last_change_time.clear()
        self.slot_confidence_history.clear()


# ============================================================================
# VIDEO UTILITIES
# ============================================================================

def resize_frame(frame: np.ndarray, width: int = None, height: int = None) -> np.ndarray:
    """
    Resize frame while maintaining aspect ratio.
    
    Args:
        frame: Input frame
        width: Target width (optional)
        height: Target height (optional)
        
    Returns:
        Resized frame
    """
    if width is None and height is None:
        return frame
    
    h, w = frame.shape[:2]
    
    if width is not None:
        aspect = width / w
        new_height = int(h * aspect)
        return cv2.resize(frame, (width, new_height))
    else:
        aspect = height / h
        new_width = int(w * aspect)
        return cv2.resize(frame, (new_width, height))


def draw_info_panel(frame: np.ndarray, stats: Dict, y_offset: int = 10) -> np.ndarray:
    """
    Draw information panel on frame with system statistics.
    
    Args:
        frame: Frame to draw on
        stats: Dictionary of statistics to display
        y_offset: Y-axis offset for panel
        
    Returns:
        Frame with info panel
    """
    import cv2
    
    # Panel background
    panel_height = len(stats) * 30 + 20
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, y_offset), (400, y_offset + panel_height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Draw statistics
    y_pos = y_offset + 25
    for key, value in stats.items():
        text = f"{key}: {value}"
        cv2.putText(frame, text, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX,
                   0.6, (255, 255, 255), 2)
        y_pos += 30
    
    return frame


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

def validate_bbox(bbox: Tuple[int, int, int, int], frame_shape: Tuple[int, int]) -> bool:
    """
    Validate if bounding box is within frame boundaries.
    
    Args:
        bbox: Bounding box as (x, y, w, h)
        frame_shape: Frame shape as (height, width)
        
    Returns:
        True if valid, False otherwise
    """
    x, y, w, h = bbox
    frame_h, frame_w = frame_shape[:2]
    
    return (0 <= x < frame_w and 
            0 <= y < frame_h and 
            w > 0 and h > 0 and
            x + w <= frame_w and 
            y + h <= frame_h)


def clamp_bbox(bbox: Tuple[int, int, int, int], frame_shape: Tuple[int, int]) -> Tuple[int, int, int, int]:
    """
    Clamp bounding box to frame boundaries.
    
    Args:
        bbox: Bounding box as (x, y, w, h)
        frame_shape: Frame shape as (height, width)
        
    Returns:
        Clamped bounding box
    """
    x, y, w, h = bbox
    frame_h, frame_w = frame_shape[:2]
    
    x = max(0, min(x, frame_w - 1))
    y = max(0, min(y, frame_h - 1))
    w = max(1, min(w, frame_w - x))
    h = max(1, min(h, frame_h - y))
    
    return (x, y, w, h)


if __name__ == "__main__":
    # Test utilities
    print("Testing Smart Parking Utilities\n")
    
    # Test logging
    logger = setup_logging()
    logger.info("Logging system initialized")
    
    # Test timestamp utilities
    print(f"\nCurrent Timestamp: {get_formatted_timestamp()}")
    start = datetime.now()
    time.sleep(0.1)
    duration = calculate_duration(start)
    print(f"Duration: {format_duration(duration)}")
    
    # Test event logger
    event_logger = EventLogger()
    event_logger.log_entry(1, "Slot A-01", confidence=0.95)
    print("\n✓ Event logged")
    
    # Test performance monitor
    perf = PerformanceMonitor()
    for i in range(10):
        perf.start_frame()
        time.sleep(0.033)  # Simulate ~30 FPS
        perf.end_frame(detection_count=3)
    
    perf.print_stats()
    
    # Test detection stabilizer
    stabilizer = DetectionStabilizer(min_consecutive_frames=3, debounce_time=1.0)
    print("\nTesting Detection Stabilizer:")
    for i in range(5):
        should_update, status = stabilizer.update(slot_id=1, is_detected=True, confidence=0.9)
        print(f"Frame {i+1}: should_update={should_update}, status={status}")
    
    print("\n✓ All utility tests completed successfully!")
