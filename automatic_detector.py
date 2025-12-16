"""
Automatic Parking Detection System (Mode 2)
Zero-configuration parking detection with vehicle tracking
GovTech Bhutan - Smart Parking MVP

Features:
- Automatic vehicle detection (near + far range)
- Vehicle tracking with persistent IDs (prevents timer resets)
- Smart parking classification (parked vs moving)
- Automatic capacity estimation
- Optional parking zone definition
- Handles large vehicles (trucks, buses)
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Dict, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
import logging
import json
from pathlib import Path
import time

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from supervision import Detections
    from supervision.tracker.byte_tracker.core import ByteTrack
    SUPERVISION_AVAILABLE = True
except ImportError:
    SUPERVISION_AVAILABLE = False
    print("⚠️  supervision not installed. Run: pip install supervision filterpy")


@dataclass
class TrackedVehicle:
    """Represents a tracked vehicle with history."""
    tracker_id: int
    class_name: str
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    confidence: float
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    positions: deque = field(default_factory=lambda: deque(maxlen=150))  # Last 150 positions (5 sec)
    is_parked: bool = False
    parked_stable_since: Optional[datetime] = None  # Track stable parked state
    stationary_since: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize position history."""
        center = self.get_center()
        self.positions.append((center, datetime.now()))
    
    def get_center(self) -> Tuple[int, int]:
        """Get center point of bounding box."""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    def get_area(self) -> int:
        """Get bounding box area."""
        x1, y1, x2, y2 = self.bbox
        return (x2 - x1) * (y2 - y1)
    
    def update(self, bbox: Tuple[int, int, int, int], confidence: float):
        """Update vehicle position and tracking data."""
        self.bbox = bbox
        self.confidence = confidence
        self.last_seen = datetime.now()
        center = self.get_center()
        self.positions.append((center, datetime.now()))
    
    def get_speed_pixels_per_second(self) -> float:
        """Calculate speed in pixels per second with smoothing."""
        if len(self.positions) < 5:
            return 0.0
        
        # Get positions from last 5 seconds for better accuracy
        current_time = datetime.now()
        recent_positions = [
            (pos, timestamp) for pos, timestamp in self.positions
            if (current_time - timestamp).total_seconds() <= 5.0
        ]
        
        if len(recent_positions) < 5:
            return 0.0
        
        # Calculate position variance (lower = more stationary)
        positions_only = [pos for pos, _ in recent_positions]
        x_coords = [p[0] for p in positions_only]
        y_coords = [p[1] for p in positions_only]
        
        x_variance = np.var(x_coords)
        y_variance = np.var(y_coords)
        total_variance = x_variance + y_variance
        
        # If variance is very low, vehicle is stationary
        if total_variance < 100:  # Less than 10px movement
            return 0.0
        
        # Calculate distance between first and last position (ignores jitter)
        first_pos = recent_positions[0][0]
        last_pos = recent_positions[-1][0]
        dx = last_pos[0] - first_pos[0]
        dy = last_pos[1] - first_pos[1]
        distance = np.sqrt(dx**2 + dy**2)
        
        # Calculate time span
        time_span = (recent_positions[-1][1] - recent_positions[0][1]).total_seconds()
        
        if time_span == 0:
            return 0.0
        
        return distance / time_span
    
    def get_stationary_duration(self) -> float:
        """Get how long vehicle has been stationary (in seconds)."""
        if self.stationary_since:
            return (datetime.now() - self.stationary_since).total_seconds()
        return 0.0
    
    def check_if_parked(self, speed_threshold: float = 8.0, time_threshold: float = 5.0) -> bool:
        """
        Determine if vehicle is parked with hysteresis and occlusion handling.
        
        Args:
            speed_threshold: Max speed in pixels/second to consider stationary (default: 8.0)
            time_threshold: Min seconds stationary to consider parked (default: 5.0)
        
        Returns:
            True if vehicle is parked
        """
        # OCCLUSION HANDLING: If not enough position data, maintain current status
        if len(self.positions) < 5:
            # During occlusion, keep previous status
            return self.is_parked
        
        speed = self.get_speed_pixels_per_second()
        
        # HYSTERESIS: If already marked as parked, use stricter threshold to un-park
        if self.is_parked:
            # Need sustained movement (>15 px/s for 3+ seconds) to un-park
            if speed > 15.0 and self.parked_stable_since:
                stable_duration = (datetime.now() - self.parked_stable_since).total_seconds()
                if stable_duration > 3.0:
                    self.is_parked = False
                    self.stationary_since = None
                    self.parked_stable_since = None
                    return False
            # Still parked
            return True
        
        # Not parked yet - check if should transition to parked
        if speed < speed_threshold:
            if self.stationary_since is None:
                self.stationary_since = datetime.now()
        else:
            # Moving - reset stationary timer
            self.stationary_since = None
            return False
        
        # Check if stationary long enough to mark as parked
        stationary_duration = self.get_stationary_duration()
        if stationary_duration >= time_threshold:
            self.is_parked = True
            self.parked_stable_since = datetime.now()
            return True
        
        return False


class ParkingZone:
    """Defines a parking zone polygon."""
    
    def __init__(self, points: Optional[List[Tuple[int, int]]] = None):
        """
        Initialize parking zone.
        
        Args:
            points: List of (x, y) points defining polygon boundary
        """
        self.points = np.array(points) if points else None
    
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if point is inside parking zone."""
        if self.points is None:
            return True  # No zone defined = everything is parking area
        
        return cv2.pointPolygonTest(self.points, point, False) >= 0
    
    def contains_bbox(self, bbox: Tuple[int, int, int, int], threshold: float = 0.5) -> bool:
        """
        Check if bounding box overlaps with parking zone.
        
        Args:
            bbox: Bounding box as (x1, y1, x2, y2)
            threshold: Minimum overlap ratio to consider inside zone
        
        Returns:
            True if bbox is in parking zone
        """
        if self.points is None:
            return True
        
        x1, y1, x2, y2 = bbox
        
        # Check center point
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        return self.contains_point((center_x, center_y))
    
    def draw(self, frame: np.ndarray, color: Tuple[int, int, int] = (255, 255, 0), thickness: int = 2):
        """Draw parking zone on frame."""
        if self.points is not None and len(self.points) > 0:
            cv2.polylines(frame, [self.points], True, color, thickness)


class AutomaticParkingDetector:
    """
    Automatic parking detection system with zero configuration.
    
    Features:
    - Enhanced vehicle detection (near + far range)
    - Vehicle tracking (persistent IDs)
    - Smart parking classification
    - Automatic capacity estimation
    """
    
    def __init__(
        self,
        model_path: str = "yolov8s.pt",
        confidence_threshold: float = 0.3,
        device: str = "auto",
        parking_zone: Optional[ParkingZone] = None,
        process_size: int = 640,
        enable_half_precision: bool = True
    ):
        """
        Initialize automatic parking detector.
        
        Args:
            model_path: Path to YOLO model (yolov8s.pt for balanced speed/accuracy)
            confidence_threshold: Detection confidence threshold (0.2-0.3 for far range)
            device: Device to run model on ("auto", "cpu", or "cuda")
            parking_zone: Optional ParkingZone object
            process_size: Image size for processing (640 for speed, 1280 for accuracy)
            enable_half_precision: Use FP16 for 2x speedup on GPU
        """
        self.logger = logging.getLogger('AutoParkingDetector')
        
        # Auto-detect best device
        if device == "auto":
            if TORCH_AVAILABLE and torch.cuda.is_available():
                self.device = "cuda"
                self.logger.info("[OK] GPU (CUDA) detected and will be used")
            else:
                self.device = "cpu"
                self.logger.info("[WARNING] Using CPU (GPU not available)")
        else:
            self.device = device
        
        # Load YOLO model
        self.logger.info(f"Loading YOLO model: {model_path}")
        try:
            self.model = YOLO(model_path)
            self.model.fuse()  # Optimize for inference
            
            # Move model to device
            if self.device == "cuda" and TORCH_AVAILABLE:
                self.model.to('cuda')
                self.logger.info("[OK] Model moved to GPU")
            
            self.logger.info("[OK] YOLO model loaded successfully")
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to load YOLO model: {e}")
            raise
        
        self.confidence_threshold = confidence_threshold
        self.process_size = process_size
        self.enable_half_precision = enable_half_precision and self.device == "cuda"
        
        # Vehicle classes: car, motorcycle, bus, truck
        self.vehicle_classes = [2, 3, 5, 7]
        self.person_class = [0]  # person class - tracked separately
        
        # Initialize tracker
        if SUPERVISION_AVAILABLE:
            self.tracker = ByteTrack(
                track_activation_threshold=0.25,
                lost_track_buffer=120,  # Keep tracks for 120 frames (4 sec) for occlusion
                minimum_matching_threshold=0.8,
                frame_rate=30
            )
            self.logger.info("[OK] ByteTrack tracker initialized")
        else:
            self.tracker = None
            self.logger.warning("[WARNING] Tracking disabled (supervision not available)")
        
        # Parking zone
        self.parking_zone = parking_zone or ParkingZone()
        
        # Tracked vehicles
        self.tracked_vehicles: Dict[int, TrackedVehicle] = {}
        
        # Capacity estimation
        self.max_parked_observed = 0
        self.estimated_capacity = 0
        self.capacity_buffer = 2
        
        # Statistics
        self.frame_count = 0
        self.total_detections = 0
        
        # Performance tracking
        self.fps_history = deque(maxlen=30)
        self.process_times = deque(maxlen=30)
        self.last_results = None  # Cache last results for frame skipping
        self.last_person_detections = []  # Store person detections for visualization
        self.person_detect_counter = 0  # For alternating person detection
        
        self.logger.info("[OK] Automatic parking detector initialized")
        self.logger.info(f"  - Confidence: {confidence_threshold}")
        self.logger.info(f"  - Device: {self.device}")
        self.logger.info(f"  - Process Size: {process_size}")
        self.logger.info(f"  - Half Precision: {self.enable_half_precision}")
        self.logger.info(f"  - Parking Zone: {'Defined' if parking_zone and parking_zone.points is not None else 'Full Frame'}")
    
    def detect_vehicles(self, frame: np.ndarray, resize_for_speed: bool = True) -> List[Dict]:
        """
        Detect vehicles with optimized processing.
        
        Args:
            frame: Input video frame
            resize_for_speed: If True, resize frame for faster processing
        
        Returns:
            List of detection dictionaries
        """
        detections = []
        
        try:
            # Optionally resize frame for faster processing
            if resize_for_speed and self.process_size < max(frame.shape[:2]):
                scale_factor = self.process_size / max(frame.shape[:2])
                process_frame = cv2.resize(frame, None, fx=scale_factor, fy=scale_factor)
            else:
                process_frame = frame
                scale_factor = 1.0
            
            # Optimized detection - detect both vehicles AND persons
            # First detect vehicles
            vehicle_results = self.model.predict(
                process_frame,
                conf=self.confidence_threshold,
                iou=0.55,  # Balanced IoU - prevents duplicates while catching close vehicles
                classes=self.vehicle_classes,
                verbose=False,
                device=self.device,
                imgsz=self.process_size,
                max_det=150,  # Increased for comprehensive coverage
                half=self.enable_half_precision
            )
            
            # Detect persons only every 3rd frame for speed optimization
            self.person_detect_counter += 1
            if self.person_detect_counter % 3 == 0:
                person_results = self.model.predict(
                    process_frame,
                    conf=max(0.3, self.confidence_threshold),  # Higher confidence for persons
                    iou=0.6,  # Higher IoU for person NMS
                    classes=self.person_class,
                    verbose=False,
                    device=self.device,
                    imgsz=self.process_size,
                    max_det=50,  # Reduced for speed
                    half=self.enable_half_precision
                )
            else:
                # Reuse previous person detections for speed
                person_results = []
            
            # Combine results (vehicles only for tracking)
            results = vehicle_results
            
            # Process PERSON detections separately (for visualization only)
            person_detections = []
            if person_results:  # Only if detection was performed this frame
                for result in person_results:
                    boxes = result.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                        if scale_factor != 1.0:
                            x1 = int(x1 / scale_factor)
                            y1 = int(y1 / scale_factor)
                            x2 = int(x2 / scale_factor)
                            y2 = int(y2 / scale_factor)
                        
                        confidence = float(box.conf[0])
                        person_detections.append({
                            'bbox': (x1, y1, x2, y2),
                            'confidence': confidence,
                            'class': 'person'
                        })
                # Store updated person detections
                self.last_person_detections = person_detections
            # Else: keep previous person detections for display
            
            # Process VEHICLE detections (for tracking)
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Extract bounding box (xyxy format)
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    
                    # Scale back to original size if resized
                    if scale_factor != 1.0:
                        x1 = int(x1 / scale_factor)
                        y1 = int(y1 / scale_factor)
                        x2 = int(x2 / scale_factor)
                        y2 = int(y2 / scale_factor)
                    
                    # Get confidence and class
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                    # Map class ID to name
                    class_names = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
                    class_name = class_names.get(class_id, "vehicle")
                    
                    detection = {
                        'bbox': (x1, y1, x2, y2),
                        'confidence': confidence,
                        'class_id': class_id,
                        'class_name': class_name
                    }
                    
                    detections.append(detection)
            
            self.total_detections += len(detections)
            
        except Exception as e:
            self.logger.error(f"Error during detection: {e}")
        
        return detections
    
    def update_tracking(self, frame: np.ndarray, detections: List[Dict]) -> List[TrackedVehicle]:
        """
        Update vehicle tracking.
        
        Args:
            frame: Current video frame
            detections: List of detections from detect_vehicles()
        
        Returns:
            List of tracked vehicles
        """
        if not self.tracker or not SUPERVISION_AVAILABLE:
            # Fallback: no tracking, create temporary vehicles
            vehicles = []
            for det in detections:
                vehicle = TrackedVehicle(
                    tracker_id=-1,
                    class_name=det['class_name'],
                    bbox=det['bbox'],
                    confidence=det['confidence']
                )
                vehicles.append(vehicle)
            return vehicles
        
        # Convert detections to Supervision format
        if len(detections) == 0:
            # Update tracker with empty detections
            tracked_detections = self.tracker.update_with_detections(
                Detections.empty()
            )
            return []
        
        # Prepare arrays for Supervision
        xyxy = np.array([det['bbox'] for det in detections])
        confidence = np.array([det['confidence'] for det in detections])
        class_id = np.array([det['class_id'] for det in detections])
        
        # Create Detections object
        supervision_detections = Detections(
            xyxy=xyxy,
            confidence=confidence,
            class_id=class_id
        )
        
        # Update tracker
        tracked_detections = self.tracker.update_with_detections(supervision_detections)
        
        # Update tracked vehicles
        current_frame_ids = set()
        
        for i in range(len(tracked_detections)):
            if tracked_detections.tracker_id is None:
                continue
            
            tracker_id = int(tracked_detections.tracker_id[i])
            bbox = tuple(map(int, tracked_detections.xyxy[i]))
            confidence = float(tracked_detections.confidence[i])
            class_id = int(tracked_detections.class_id[i])
            
            # Map class name
            class_names = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
            class_name = class_names.get(class_id, "vehicle")
            
            current_frame_ids.add(tracker_id)
            
            # Update or create tracked vehicle
            if tracker_id in self.tracked_vehicles:
                self.tracked_vehicles[tracker_id].update(bbox, confidence)
            else:
                self.tracked_vehicles[tracker_id] = TrackedVehicle(
                    tracker_id=tracker_id,
                    class_name=class_name,
                    bbox=bbox,
                    confidence=confidence
                )
        
        # Remove lost tracks (not seen for 5 seconds)
        current_time = datetime.now()
        to_remove = []
        for tracker_id, vehicle in self.tracked_vehicles.items():
            if tracker_id not in current_frame_ids:
                time_since_seen = (current_time - vehicle.last_seen).total_seconds()
                if time_since_seen > 5.0:
                    to_remove.append(tracker_id)
        
        for tracker_id in to_remove:
            del self.tracked_vehicles[tracker_id]
        
        return list(self.tracked_vehicles.values())
    
    def classify_parking_status(
        self,
        vehicles: List[TrackedVehicle],
        speed_threshold: float = 8.0,
        time_threshold: float = 5.0
    ) -> Tuple[List[TrackedVehicle], List[TrackedVehicle]]:
        """
        Classify vehicles as parked or moving.
        
        Args:
            vehicles: List of tracked vehicles
            speed_threshold: Max speed (pixels/sec) to consider stationary (default: 5.0)
            time_threshold: Min time (seconds) stationary to consider parked (default: 3.0)
        
        Returns:
            Tuple of (parked_vehicles, moving_vehicles)
        """
        parked = []
        moving = []
        
        for vehicle in vehicles:
            # Check if in parking zone
            if not self.parking_zone.contains_bbox(vehicle.bbox):
                continue  # Ignore vehicles outside parking zone
            
            # Check if parked
            if vehicle.check_if_parked(speed_threshold, time_threshold):
                parked.append(vehicle)
            else:
                moving.append(vehicle)
        
        return parked, moving
    
    def update_capacity_estimation(self, parked_count: int):
        """
        Update automatic capacity estimation.
        
        Args:
            parked_count: Current number of parked vehicles
        """
        if parked_count > self.max_parked_observed:
            self.max_parked_observed = parked_count
            self.estimated_capacity = parked_count + self.capacity_buffer
    
    def process_frame(self, frame: np.ndarray, force_detect: bool = True) -> Dict:
        """
        Process a single frame with performance optimization.
        
        Args:
            frame: Input video frame
            force_detect: If False, return cached results (for frame skipping)
        
        Returns:
            Dictionary with detection results
        """
        start_time = time.time()
        
        self.frame_count += 1
        
        if not force_detect and self.last_results is not None:
            # Return cached results for skipped frames
            self.last_results['frame'] = frame
            return self.last_results
        
        # Detect vehicles
        detections = self.detect_vehicles(frame)
        
        # Update tracking
        tracked_vehicles = self.update_tracking(frame, detections)
        
        # Classify parking status
        parked_vehicles, moving_vehicles = self.classify_parking_status(tracked_vehicles)
        
        # Update capacity
        parked_count = len(parked_vehicles)
        self.update_capacity_estimation(parked_count)
        
        # Calculate statistics
        available = max(0, self.estimated_capacity - parked_count)
        occupancy_percent = (parked_count / self.estimated_capacity * 100) if self.estimated_capacity > 0 else 0
        
        # Track performance
        process_time = time.time() - start_time
        self.process_times.append(process_time)
        fps = 1.0 / process_time if process_time > 0 else 0
        self.fps_history.append(fps)
        
        results = {
            'frame': frame,
            'parked_vehicles': parked_vehicles,
            'moving_vehicles': moving_vehicles,
            'person_detections': getattr(self, 'last_person_detections', []),  # Add person detections
            'total_tracked': len(tracked_vehicles),
            'parked_count': parked_count,
            'moving_count': len(moving_vehicles),
            'capacity': self.estimated_capacity,
            'available': available,
            'occupancy_percent': occupancy_percent,
            'detections_count': len(detections),
            'fps': fps,
            'avg_fps': sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0,
            'process_time': process_time * 1000  # Convert to ms
        }
        
        # Cache results
        self.last_results = results
        
        return results
    
    def draw_results(self, frame: np.ndarray, results: Dict) -> np.ndarray:
        """
        Draw detection results on frame.
        
        Args:
            frame: Input frame
            results: Results from process_frame()
        
        Returns:
            Annotated frame
        """
        output_frame = frame.copy()
        
        # Draw parking zone
        self.parking_zone.draw(output_frame, color=(255, 255, 0), thickness=2)
        
        # Draw parked vehicles (GREEN)
        for vehicle in results['parked_vehicles']:
            x1, y1, x2, y2 = vehicle.bbox
            
            # Draw bounding box
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"ID:{vehicle.tracker_id} {vehicle.class_name.upper()}"
            parked_time = vehicle.get_stationary_duration()
            label += f" ({parked_time:.0f}s)"
            
            cv2.putText(
                output_frame, label, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )
        
        # Draw moving vehicles (PURPLE)
        for vehicle in results['moving_vehicles']:
            x1, y1, x2, y2 = vehicle.bbox
            
            # Draw bounding box
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
            
            # Draw label
            speed = vehicle.get_speed_pixels_per_second()
            label = f"ID:{vehicle.tracker_id} MOVING ({speed:.1f}px/s)"
            
            cv2.putText(
                output_frame, label, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2
            )
        
        # Draw persons (YELLOW/ORANGE) - visualized separately, not tracked
        person_detections = results.get('person_detections', [])
        for person in person_detections:
            x1, y1, x2, y2 = person['bbox']
            confidence = person['confidence']
            
            # Draw bounding box in yellow/orange
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 165, 255), 2)
            
            # Draw label
            label = f"PERSON ({confidence:.2f})"
            cv2.putText(
                output_frame, label, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2
            )
        
        # Draw statistics panel
        panel_height = 235  # Increased for pedestrian count
        overlay = output_frame.copy()
        cv2.rectangle(overlay, (10, 10), (450, panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, output_frame, 0.3, 0, output_frame)
        
        # Text
        y_offset = 35
        avg_fps = results.get('avg_fps', 0)
        process_time = results.get('process_time', 0)
        person_count = len(results.get('person_detections', []))
        
        stats_lines = [
            f"MODE: AUTOMATIC DETECTION",
            f"FPS: {avg_fps:.1f} | Process: {process_time:.1f}ms",
            f"CAPACITY: {results['capacity']} (auto-detected)",
            f"PARKED: {results['parked_count']}",
            f"AVAILABLE: {results['available']}",
            f"OCCUPANCY: {results['occupancy_percent']:.1f}%",
            f"MOVING VEHICLES: {results['moving_count']} (not counted)",
            f"PEDESTRIANS: {person_count} (monitored)"
        ]
        
        for line in stats_lines:
            cv2.putText(
                output_frame, line, (20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
            )
            y_offset += 25
        
        # Occupancy status
        if results['occupancy_percent'] >= 90:
            status = "FULL"
            status_color = (0, 0, 255)
        elif results['occupancy_percent'] >= 70:
            status = "NEARLY FULL"
            status_color = (0, 165, 255)
        else:
            status = "AVAILABLE"
            status_color = (0, 255, 0)
        
        cv2.putText(
            output_frame, f"STATUS: {status}", (20, panel_height - 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2
        )
        
        return output_frame


class ParkingZoneDefiner:
    """Interactive tool to define parking zone polygon."""
    
    def __init__(self, frame: np.ndarray):
        """
        Initialize zone definer.
        
        Args:
            frame: Sample frame to draw on
        """
        self.frame = frame.copy()
        self.points = []
        self.finished = False
        
        cv2.namedWindow("Define Parking Zone")
        cv2.setMouseCallback("Define Parking Zone", self._mouse_callback)
    
    def _mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))
            print(f"Point {len(self.points)}: ({x}, {y})")
    
    def run(self) -> Optional[ParkingZone]:
        """
        Run interactive zone definition.
        
        Returns:
            ParkingZone object or None if cancelled
        """
        print("\n" + "="*60)
        print("PARKING ZONE DEFINITION")
        print("="*60)
        print("Instructions:")
        print("  - Click to add points defining parking area boundary")
        print("  - Press ENTER when done (minimum 3 points)")
        print("  - Press ESC to cancel")
        print("="*60 + "\n")
        
        while not self.finished:
            display_frame = self.frame.copy()
            
            # Draw points
            for i, point in enumerate(self.points):
                cv2.circle(display_frame, point, 5, (0, 255, 0), -1)
                cv2.putText(
                    display_frame, str(i+1), (point[0]+10, point[1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
                )
            
            # Draw polygon
            if len(self.points) > 1:
                cv2.polylines(display_frame, [np.array(self.points)], False, (255, 255, 0), 2)
            
            # Draw instructions
            cv2.putText(
                display_frame, f"Points: {len(self.points)} | ENTER=Done | ESC=Cancel",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
            )
            
            cv2.imshow("Define Parking Zone", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 13:  # ENTER
                if len(self.points) >= 3:
                    self.finished = True
                    print(f"\n✓ Parking zone defined with {len(self.points)} points")
                else:
                    print("\n⚠️  Need at least 3 points!")
            elif key == 27:  # ESC
                print("\n✗ Cancelled")
                cv2.destroyAllWindows()
                return None
        
        cv2.destroyAllWindows()
        return ParkingZone(self.points)


def save_parking_zone(zone: ParkingZone, filepath: str = "configs/parking_zone.json"):
    """Save parking zone to JSON file."""
    if zone.points is not None:
        data = {
            'points': zone.points.tolist(),
            'created_at': datetime.now().isoformat()
        }
        
        Path(filepath).parent.mkdir(exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Parking zone saved to {filepath}")


def load_parking_zone(filepath: str = "configs/parking_zone.json") -> Optional[ParkingZone]:
    """Load parking zone from JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        points = data.get('points')
        if points:
            print(f"✓ Parking zone loaded from {filepath}")
            return ParkingZone(points)
    except FileNotFoundError:
        print(f"ℹ️  No parking zone file found at {filepath}")
    except Exception as e:
        print(f"⚠️  Error loading parking zone: {e}")
    
    return None
