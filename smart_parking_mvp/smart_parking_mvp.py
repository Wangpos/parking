"""
SMART PARKING SYSTEM MVP - GovTech PoC
Strictly aligned with Terms of Reference requirements

Core Features (70% Weight):
✓ Vehicle presence detection (YOLO)
✓ Slot availability (occupied/vacant)
✓ Parking duration tracking
✓ Real-time performance (GPU-accelerated)
✓ Clear visualization

Scope: Feasibility demonstration, not perfection
"""
from ultralytics import YOLO
import cv2
import numpy as np
import json
import os
import sys
import time
from datetime import datetime
from shapely.geometry import Polygon, box as shapely_box
import torch


# ============================================================================
# PARKING SLOT CLASS
# ============================================================================

class ParkingSlot:
    """Represents one parking slot with occupancy tracking"""
    
    def __init__(self, slot_id, points):
        self.id = slot_id
        self.points = points  # 4 corner points
        self.polygon = Polygon(points)
        
        # Occupancy state
        self.is_occupied = False
        self.occupied_since = None
        self.last_vacant = time.time()
        self.occupying_vehicle_id = None  # Track which vehicle is parked
        
        # Simple counters for stability
        self.vacant_frames = 0
        self.occupied_frames = 0
        
        # Statistics
        self.total_occupancies = 0
        self.total_duration = 0.0
    
    def check_overlap(self, bbox):
        """
        Check if vehicle bounding box overlaps with this slot
        Returns overlap ratio (0.0 to 1.0)
        """
        x1, y1, x2, y2 = bbox
        vehicle_box = shapely_box(x1, y1, x2, y2)
        
        if not self.polygon.intersects(vehicle_box):
            return 0.0
        
        intersection = self.polygon.intersection(vehicle_box).area
        vehicle_area = vehicle_box.area
        
        return intersection / vehicle_area if vehicle_area > 0 else 0.0
    
    def mark_occupied(self, vehicle_id=None):
        """Mark slot as occupied by a specific vehicle"""
        if not self.is_occupied:
            self.is_occupied = True
            self.occupied_since = time.time()
            self.occupying_vehicle_id = vehicle_id
            self.total_occupancies += 1
        elif vehicle_id and self.occupying_vehicle_id and vehicle_id != self.occupying_vehicle_id:
            # Different vehicle - reset timer
            if self.occupied_since:
                duration = time.time() - self.occupied_since
                self.total_duration += duration
            self.occupied_since = time.time()
            self.occupying_vehicle_id = vehicle_id
            self.total_occupancies += 1
        
        self.is_occupied = True
        self.vacant_frames = 0
    
    def mark_vacant(self):
        """Mark slot as vacant"""
        if self.is_occupied:
            if self.occupied_since:
                duration = time.time() - self.occupied_since
                self.total_duration += duration
            self.is_occupied = False
            self.occupied_since = None
            self.occupying_vehicle_id = None
            self.last_vacant = time.time()
        self.occupied_frames = 0
    
    def get_duration(self):
        """Get current parking duration in seconds"""
        if not self.is_occupied or not self.occupied_since:
            return 0
        return time.time() - self.occupied_since


# ============================================================================
# SMART PARKING SYSTEM MVP
# ============================================================================

class SmartParkingMVP:
    """
    Core parking system for GovTech PoC
    Focused on: detection, occupancy, duration, visualization
    """
    
    def __init__(self, slots_json, model_path='yolov8m.pt'):
        print("="*70)
        print("SMART PARKING SYSTEM MVP - GovTech PoC")
        print("="*70)
        
        # GPU check
        if torch.cuda.is_available():
            self.device = 'cuda'
            print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA: {torch.version.cuda}")
            print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        else:
            self.device = 'cpu'
            print("⚠️  Running on CPU (slower)")
        
        # Load YOLO
        print(f"\nLoading YOLO model: {model_path}")
        self.model = YOLO(model_path)
        if self.device == 'cuda':
            self.model.to('cuda')
        print("✅ Model loaded")
        
        # Load parking slots
        print(f"\nLoading slots: {slots_json}")
        with open(slots_json, 'r') as f:
            data = json.load(f)
        
        self.slots = [ParkingSlot(s['id'], s['points']) for s in data['slots']]
        print(f"✅ Loaded {len(self.slots)} parking slots")
        
        # Configuration
        self.overlap_threshold = 0.4  # 40% overlap = truly parked (ignore passing vehicles)
        self.conf_threshold = 0.25  # Lower for consistent detection = stable IDs
        self.iou_threshold = 0.3  # Lower for tracker matching (IoU between tracks)
        
        # Vehicle tracking history for type smoothing
        self.vehicle_type_history = {}  # track_id -> list of recent types
        self.history_window = 10  # Keep last 10 classifications
        
        # Vehicle position tracking for movement detection
        self.vehicle_positions = {}  # track_id -> list of (x, y, timestamp)
        self.position_history_window = 5  # Keep last 5 positions
        self.stationary_threshold = 10  # pixels
        
        # Vehicle classes (COCO dataset)
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        
        # Statistics
        self.frame_count = 0
        self.start_time = time.time()
        
        print("\nConfiguration:")
        print(f"  Overlap threshold: {self.overlap_threshold*100:.0f}%")
        print(f"  Detection confidence: {self.conf_threshold}")
        print(f"  Tracker IoU: {self.iou_threshold}")
        print(f"  Tracker: ByteTrack (stable IDs)")
        print("="*70 + "\n")
    
    def process_frame(self, frame):
        """Process one frame: detect vehicles, update occupancy"""
        self.frame_count += 1
        
        # Downscale 4K to 1080p for processing speed
        h, w = frame.shape[:2]
        if w > 1920:
            scale = 1920 / w
            process_frame = cv2.resize(frame, None, fx=scale, fy=scale)
            scale_back = 1.0 / scale
        else:
            process_frame = frame
            scale_back = 1.0
        
        # YOLO detection with TRACKING for persistent IDs
        # ByteTrack configuration for MAXIMUM stability
        results = self.model.track(
            source=process_frame,
            device=self.device,
            half=True if self.device == 'cuda' else False,
            imgsz=960,
            conf=self.conf_threshold,
            iou=0.3,  # Lower IOU for tracker matching (more lenient)
            classes=self.vehicle_classes,
            persist=True,  # Persistent tracking
            tracker='bytetrack.yaml',  # Use ByteTrack config
            verbose=False
        )
        
        # Extract vehicle bounding boxes with IDs and types
        vehicles = []
        if results[0].boxes is not None and len(results[0].boxes) > 0:
            for box in results[0].boxes:
                # Get tracking ID
                if box.id is None:
                    continue
                
                track_id = int(box.id.item())
                
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                # Scale back to original resolution
                if scale_back != 1.0:
                    x1 = int(x1 * scale_back)
                    y1 = int(y1 * scale_back)
                    x2 = int(x2 * scale_back)
                    y2 = int(y2 * scale_back)
                
                # Get vehicle type with smoothing
                cls = int(box.cls.item())
                vehicle_type_map = {2: 'Car', 3: 'Motorcycle', 5: 'Bus', 7: 'Truck'}
                raw_type = vehicle_type_map.get(cls, 'Vehicle')
                
                # Update type history for this vehicle
                if track_id not in self.vehicle_type_history:
                    self.vehicle_type_history[track_id] = []
                
                self.vehicle_type_history[track_id].append(raw_type)
                
                # Keep only recent history
                if len(self.vehicle_type_history[track_id]) > self.history_window:
                    self.vehicle_type_history[track_id].pop(0)
                
                # Use majority vote for stable type
                type_counts = {}
                for t in self.vehicle_type_history[track_id]:
                    type_counts[t] = type_counts.get(t, 0) + 1
                vehicle_type = max(type_counts.items(), key=lambda x: x[1])[0]
                
                conf = float(box.conf.item())
                
                # Calculate vehicle center for movement tracking
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                
                # Track position history
                if track_id not in self.vehicle_positions:
                    self.vehicle_positions[track_id] = []
                
                self.vehicle_positions[track_id].append((center_x, center_y, time.time()))
                
                # Keep only recent positions
                if len(self.vehicle_positions[track_id]) > self.position_history_window:
                    self.vehicle_positions[track_id].pop(0)
                
                # Check if vehicle is stationary
                is_stationary = self.is_vehicle_stationary(track_id)
                
                vehicles.append({
                    'id': track_id,
                    'type': vehicle_type,
                    'bbox': (x1, y1, x2, y2),
                    'confidence': conf,
                    'is_stationary': is_stationary
                })
        
        # Clean up history for vehicles no longer in frame
        current_ids = {v['id'] for v in vehicles}
        old_ids = set(self.vehicle_type_history.keys()) - current_ids
        for old_id in old_ids:
            if old_id in self.vehicle_type_history:
                del self.vehicle_type_history[old_id]
            if old_id in self.vehicle_positions:
                del self.vehicle_positions[old_id]
        
        # Update slot occupancy
        self.update_occupancy(vehicles)
        
        return vehicles
    
    def is_vehicle_stationary(self, vehicle_id):
        """Check if vehicle is stationary based on position history"""
        if vehicle_id not in self.vehicle_positions:
            return False
        
        positions = self.vehicle_positions[vehicle_id]
        
        # Need at least 3 positions to determine movement
        if len(positions) < 3:
            return False
        
        # Calculate max displacement from first to last position
        first_x, first_y, _ = positions[0]
        last_x, last_y, _ = positions[-1]
        
        displacement = ((last_x - first_x)**2 + (last_y - first_y)**2)**0.5
        
        return displacement < self.stationary_threshold
    
    def update_occupancy(self, vehicles):
        """
        Simple and accurate occupancy detection:
        - RED = vehicle with 40%+ overlap (truly parked)
        - GREEN = less than 20% overlap (vehicle left)
        - Immediate response when vehicle leaves
        """
        for slot in self.slots:
            best_overlap = 0.0
            best_vehicle = None
            
            # Find best matching vehicle
            for vehicle in vehicles:
                bbox = vehicle['bbox']
                overlap = slot.check_overlap(bbox)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_vehicle = vehicle
            
            if slot.is_occupied:
                # Currently RED - turn GREEN when vehicle leaves
                if best_overlap < 0.2:  # Less than 20% = vehicle leaving/left
                    slot.vacant_frames += 1
                    # More aggressive - only 1 frame needed if overlap is very low
                    frames_needed = 1 if best_overlap < 0.05 else 2
                    if slot.vacant_frames >= frames_needed:
                        slot.mark_vacant()
                else:
                    # Vehicle still there with good overlap
                    slot.vacant_frames = 0
                    if best_vehicle and best_vehicle['id'] != slot.occupying_vehicle_id:
                        # Different vehicle replaced the old one
                        slot.mark_occupied(best_vehicle['id'])
            else:
                # Currently GREEN - turn RED when vehicle parks
                if best_overlap > self.overlap_threshold:  # 40%+ overlap = parked
                    slot.occupied_frames += 1
                    if slot.occupied_frames >= 2:  # Need 2 frames to confirm parking
                        if best_vehicle:
                            slot.mark_occupied(best_vehicle['id'])
                else:
                    slot.occupied_frames = 0
    
    def draw_visualization(self, frame, vehicles):
        """Draw visualization overlay for MVP demo"""
        vis = frame.copy()
        
        # Draw parking slots
        for slot in self.slots:
            # Color based on occupancy
            if slot.is_occupied:
                color = (0, 0, 255)  # RED = occupied
                thickness = 3
            else:
                color = (0, 255, 0)  # GREEN = vacant
                thickness = 2
            
            # Draw slot polygon
            points = np.array(slot.points, dtype=np.int32)
            cv2.polylines(vis, [points], True, color, thickness)
            
            # Semi-transparent fill
            overlay = vis.copy()
            cv2.fillPoly(overlay, [points], color)
            cv2.addWeighted(overlay, 0.15, vis, 0.85, 0, vis)
            
            # Slot label
            center = np.mean(points, axis=0).astype(int)
            
            # Slot ID
            label = f"#{slot.id}"
            
            # Duration if occupied
            if slot.is_occupied:
                duration = slot.get_duration()
                label += f" {self.format_duration(duration)}"
            
            # Label background
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(vis, (center[0] - w//2 - 5, center[1] - h - 5),
                         (center[0] + w//2 + 5, center[1] + 5), (0, 0, 0), -1)
            
            # Label text
            cv2.putText(vis, label, (center[0] - w//2, center[1]),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw vehicle bounding boxes with ID only
        for vehicle in vehicles:
            x1, y1, x2, y2 = map(int, vehicle['bbox'])
            vehicle_id = vehicle['id']
            
            # Simple cyan color for all vehicles
            color = (255, 255, 0)  # Yellow
            
            # Draw bounding box
            cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)
            
            # Vehicle label with ID only
            label = f"ID:{vehicle_id}"
            
            # Label background
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(vis, (x1, y1 - h - 10), (x1 + w + 10, y1), color, -1)
            
            # Label text
            cv2.putText(vis, label, (x1 + 5, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Draw statistics dashboard
        self.draw_dashboard(vis, vehicles)
        
        return vis
    
    def draw_dashboard(self, frame, vehicles):
        """Draw statistics dashboard"""
        # Calculate stats
        total_slots = len(self.slots)
        occupied = sum(1 for s in self.slots if s.is_occupied)
        vacant = total_slots - occupied
        occupancy_rate = (occupied / total_slots * 100) if total_slots > 0 else 0
        
        # Vehicle stats
        total_vehicles = len(vehicles)
        
        # FPS
        elapsed = time.time() - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        # GPU info
        if self.device == 'cuda':
            gpu_mem = torch.cuda.memory_allocated(0) / 1024**3
            gpu_info = f"GPU: {gpu_mem:.1f}GB"
        else:
            gpu_info = "CPU Mode"
        
        # Dashboard
        stats = [
            "SMART PARKING MVP",
            f"FPS: {fps:.1f} | {gpu_info}",
            "",
            f"CAPACITY: {occupied}/{total_slots} ({occupancy_rate:.0f}%)",
            f"Vacant: {vacant}",
            f"Vehicles: {total_vehicles}",
            "",
            "GREEN = Vacant",
            "RED = Occupied"
        ]
        
        # Background
        max_width = 420
        height = len(stats) * 35 + 20
        cv2.rectangle(frame, (10, 10), (max_width, height), (0, 0, 0), -1)
        
        # Text
        y = 40
        for stat in stats:
            if stat == "":
                y += 15
                continue
            
            if "SMART PARKING" in stat:
                color = (0, 255, 255)
                scale = 0.8
            elif occupied == total_slots and "CAPACITY" in stat:
                color = (0, 0, 255)
                scale = 0.7
            elif "GREEN" in stat:
                color = (0, 255, 0)
                scale = 0.6
            elif "RED" in stat:
                color = (0, 0, 255)
                scale = 0.6
            else:
                color = (255, 255, 255)
                scale = 0.7
            
            cv2.putText(frame, stat, (20, y),
                       cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2)
            y += 35
    
    def format_duration(self, seconds):
        """Format duration as Xm Ys"""
        if seconds < 60:
            return f"{int(seconds)}s"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m{secs:02d}s"
    
    def run(self, video_source, output_video=None):
        """Run the parking system on video"""
        print("Starting Smart Parking MVP...")
        print(f"Video: {video_source}\n")
        
        # Open video
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            print("[ERROR] Cannot open video")
            return
        
        # Video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Resolution: {frame_width}x{frame_height}")
        print(f"FPS: {fps}")
        
        # Video writer (optional)
        writer = None
        if output_video:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))
            print(f"Recording to: {output_video}")
        
        # Display setup
        max_display_width = 1280
        display_scale = min(max_display_width / frame_width, 1.0)
        display_width = int(frame_width * display_scale)
        display_height = int(frame_height * display_scale)
        
        print(f"Display: {display_width}x{display_height}\n")
        print("Controls:")
        print("  Q - Quit")
        print("  S - Save snapshot")
        print("  SPACE - Pause/Resume")
        print("\n" + "="*70 + "\n")
        
        window_name = 'Smart Parking MVP - GovTech PoC'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, display_width, display_height)
        
        paused = False
        
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    print("\n[END] Video finished")
                    break
                
                # Process frame
                vehicles = self.process_frame(frame)
                
                # Visualize
                annotated = self.draw_visualization(frame, vehicles)
                
                # Write to output video
                if writer:
                    writer.write(annotated)
                
                # Store for display
                current_frame = annotated.copy()
            else:
                annotated = current_frame
            
            # Resize for display
            if display_scale < 1.0:
                display_frame = cv2.resize(annotated, (display_width, display_height))
            else:
                display_frame = annotated
            
            # Show
            cv2.imshow(window_name, display_frame)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n[QUIT] User stopped")
                break
            
            elif key == ord('s'):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'output/snapshots/parking_{timestamp}.jpg'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                cv2.imwrite(filename, annotated)
                print(f"[SAVED] {filename}")
            
            elif key == ord(' '):
                paused = not paused
                print("[PAUSED]" if paused else "[RESUMED]")
        
        # Cleanup
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        
        # Final report
        self.print_report()
    
    def print_report(self):
        """Print final statistics"""
        print("\n" + "="*70)
        print("FINAL REPORT")
        print("="*70)
        
        total_slots = len(self.slots)
        occupied = sum(1 for s in self.slots if s.is_occupied)
        
        print(f"\nCapacity: {occupied}/{total_slots} occupied")
        print(f"\nSlot Statistics:")
        
        for slot in self.slots:
            avg_duration = slot.total_duration / slot.total_occupancies if slot.total_occupancies > 0 else 0
            status = "OCCUPIED" if slot.is_occupied else "VACANT"
            
            print(f"  Slot #{slot.id}: {status}")
            print(f"    Total uses: {slot.total_occupancies}")
            print(f"    Avg duration: {self.format_duration(avg_duration)}")
        
        print("\n" + "="*70)


# ============================================================================
# SLOT MAPPER - 2-CLICK ANGLE-AWARE SYSTEM
# ============================================================================

def map_parking_slots(video_path, output_json='configs/parking_slots.json'):
    """
    Minimal-interaction slot mapper for angled parking
    
    Process:
    1. User clicks & drags along ONE parking line direction
    2. System calculates angle and perpendicular automatically
    3. System generates N angled slot polygons
    4. Perfect alignment with painted lines
    """
    print("="*70)
    print("PARKING SLOT MAPPER - 2-Click System")
    print("="*70)
    
    # Load video
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("[ERROR] Cannot read video")
        return None
    
    orig_frame = frame.copy()
    print(f"\nVideo: {video_path}")
    print(f"Resolution: {frame.shape[1]}x{frame.shape[0]}")
    
    # Resize for display
    max_width = 1280
    display_scale = 1.0
    if frame.shape[1] > max_width:
        display_scale = max_width / frame.shape[1]
        frame = cv2.resize(frame, None, fx=display_scale, fy=display_scale)
    
    print(f"Display scale: {display_scale:.2f}x\n")
    
    # STEP 1: Define parking direction
    print("="*70)
    print("STEP 1: Define Parking Direction")
    print("="*70)
    print("Click and DRAG along ONE parking slot line")
    print("  - Start at one end of the line")
    print("  - Drag to the other end")
    print("  - This defines slot angle and direction")
    print("\nPress ENTER when satisfied | R to redraw")
    print("="*70 + "\n")
    
    drawing = False
    line_start = None
    line_end = None
    line_defined = False
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal drawing, line_start, line_end, line_defined
        
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            line_start = (x, y)
            line_end = (x, y)
            line_defined = False
        
        elif event == cv2.EVENT_MOUSEMOVE and drawing:
            line_end = (x, y)
        
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            line_end = (x, y)
            line_defined = True
            
            dx = line_end[0] - line_start[0]
            dy = line_end[1] - line_start[1]
            angle = np.degrees(np.arctan2(dy, dx))
            length = int(np.sqrt(dx**2 + dy**2) / display_scale)
            
            print(f"\n✓ Direction: {length}px at {angle:.1f}°")
            print("Press ENTER to continue\n")
    
    window_name = 'Draw Line Along Parking Direction'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, mouse_callback)
    
    while True:
        display = frame.copy()
        
        if line_start and line_end:
            color = (0, 255, 0) if line_defined else (0, 255, 255)
            thickness = 3 if line_defined else 2
            
            cv2.line(display, line_start, line_end, color, thickness)
            
            if line_defined:
                cv2.arrowedLine(display, line_start, line_end, (0, 255, 0), 3, tipLength=0.05)
            
            cv2.circle(display, line_start, 8, (255, 0, 0), -1)
            cv2.circle(display, line_end, 8, (0, 0, 255), -1)
        
        # Enhanced visual instructions - MUCH CLEARER
        box_height = 200
        cv2.rectangle(display, (10, 10), (750, box_height), (0, 0, 0), -1)
        cv2.rectangle(display, (10, 10), (750, box_height), (0, 255, 255), 3)
        
        y_pos = 50
        instructions = [
            ("STEP 1: DEFINE PARKING DIRECTION", (0, 255, 255), 0.9, True),
            ("", (255, 255, 255), 0.7, False),
            ("1. CLICK at START of a parking slot line", (255, 255, 255), 0.7, False),
            ("2. DRAG to END of the same line", (255, 255, 255), 0.7, False),
            ("3. RELEASE mouse button", (255, 255, 255), 0.7, False),
            ("", (255, 255, 255), 0.7, False),
            ("Press ENTER when satisfied | R to redraw", (0, 255, 0), 0.7, True)
        ]
        
        for text, color, scale, bold in instructions:
            if text == "":
                y_pos += 20
                continue
            thickness = 2 if bold else 1
            cv2.putText(display, text, (25, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness)
            y_pos += 35
        
        # Draw example diagram if no line yet
        if not line_start or not line_defined:
            # Example box
            ex_x = display.shape[1] - 320
            ex_y = 10
            ex_w = 310
            ex_h = 180
            
            cv2.rectangle(display, (ex_x, ex_y), (ex_x + ex_w, ex_y + ex_h), (0, 0, 0), -1)
            cv2.rectangle(display, (ex_x, ex_y), (ex_x + ex_w, ex_y + ex_h), (0, 255, 255), 2)
            
            cv2.putText(display, "EXAMPLE:", (ex_x + 10, ex_y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Draw example parking slots
            slots_y = ex_y + 60
            for i in range(3):
                offset = i * 85
                # Angled rectangle representing parking slot
                pts = np.array([
                    [ex_x + 20 + offset, slots_y],
                    [ex_x + 70 + offset, slots_y - 10],
                    [ex_x + 70 + offset, slots_y + 70],
                    [ex_x + 20 + offset, slots_y + 80]
                ], np.int32)
                cv2.polylines(display, [pts], True, (100, 100, 100), 1)
            
            # Draw example direction line with arrow
            arrow_start = (ex_x + 35, slots_y + 35)
            arrow_end = (ex_x + 220, slots_y + 15)
            cv2.arrowedLine(display, arrow_start, arrow_end, (0, 255, 0), 3, tipLength=0.1)
            
            cv2.putText(display, "Draw line like this", (ex_x + 30, ex_y + ex_h - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.imshow(window_name, display)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == 13 and line_defined:  # ENTER
            break
        elif key == ord('r') or key == ord('R'):
            line_start = None
            line_end = None
            line_defined = False
            print("✓ Reset")
    
    cv2.destroyAllWindows()
    
    if not line_defined:
        return None
    
    # STEP 2: Calculate vectors
    orig_x1 = int(line_start[0] / display_scale)
    orig_y1 = int(line_start[1] / display_scale)
    orig_x2 = int(line_end[0] / display_scale)
    orig_y2 = int(line_end[1] / display_scale)
    
    dx = orig_x2 - orig_x1
    dy = orig_y2 - orig_y1
    length = np.sqrt(dx**2 + dy**2)
    
    # Direction vector (along slots)
    dir_vec = np.array([dx, dy]) / length
    
    # Perpendicular vector (across slots)
    perp_vec = np.array([-dy, dx]) / length
    
    angle = np.degrees(np.arctan2(dy, dx))
    
    print(f"\n✓ Angle: {angle:.2f}°\n")
    
    # STEP 3: Get parameters with clear explanations
    print("="*70)
    print("STEP 2: Slot Configuration")
    print("="*70)
    print("\nThe line you drew defines the DIRECTION of parking slots.")
    print("Now specify the SIZE and COUNT:\n")
    
    print("1. SLOT LENGTH (along the line you drew)")
    print("   - This is how LONG each parking slot is")
    print("   - Typical car slot: 300-500 pixels")
    print("   - Just press ENTER for default (300)")
    slot_length = int(input("   Enter length [300]: ") or "300")
    print(f"   ✓ Slot length: {slot_length} pixels\n")
    
    print("2. SLOT WIDTH (perpendicular to the line)")
    print("   - This is how WIDE each parking slot is")
    print("   - Typical car slot: 150-250 pixels")
    print("   - Just press ENTER for default (200)")
    slot_width = int(input("   Enter width [200]: ") or "200")
    print(f"   ✓ Slot width: {slot_width} pixels\n")
    
    print("3. NUMBER OF SLOTS")
    print("   - How many parking slots to generate?")
    print("   - Count the parking slots in your video")
    print("   - Just press ENTER for default (9)")
    num_slots = int(input("   Enter number [9]: ") or "9")
    print(f"   ✓ Generating {num_slots} slots\n")
    
    print("4. SPACING between slots")
    print("   - Gap between parking slots (painted lines)")
    print("   - Typical spacing: 30-80 pixels")
    print("   - Just press ENTER for default (50)")
    spacing = int(input("   Enter spacing [50]: ") or "50")
    print(f"   ✓ Spacing: {spacing} pixels\n")
    
    print("5. SLOT POSITION relative to your line:")
    print("   1 = Slots on LEFT side of line")
    print("   2 = Slots on RIGHT side of line")
    print("   3 = Slots CENTERED on line")
    print("   - Just press ENTER for default (1)")
    side = int(input("   Choose position [1]: ") or "1")
    print(f"   ✓ Position: {'Left' if side==1 else 'Right' if side==2 else 'Centered'}\n")
    
    # STEP 4: Generate slots
    print(f"\n✓ Generating {num_slots} angled slots...\n")
    
    slots = []
    start_point = np.array([orig_x1, orig_y1], dtype=float)
    
    for i in range(num_slots):
        slot_center = start_point + dir_vec * i * (slot_length + spacing)
        
        if side == 1:
            offset = perp_vec * slot_width
        elif side == 2:
            offset = -perp_vec * slot_width
        else:
            offset = perp_vec * (slot_width / 2)
            slot_center = slot_center - offset
            offset = perp_vec * slot_width
        
        half_length = slot_length / 2
        
        c1 = slot_center - dir_vec * half_length
        c2 = slot_center + dir_vec * half_length
        c3 = c2 + offset
        c4 = c1 + offset
        
        points = [
            [int(c1[0]), int(c1[1])],
            [int(c2[0]), int(c2[1])],
            [int(c3[0]), int(c3[1])],
            [int(c4[0]), int(c4[1])]
        ]
        
        slots.append({'id': i + 1, 'points': points})
        print(f"  ✓ Slot-{i + 1}")
    
    # Save
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump({'slots': slots, 'total_slots': len(slots)}, f, indent=2)
    
    print(f"\n✅ Saved {len(slots)} slots to: {output_json}")
    
    # Preview
    preview = orig_frame.copy()
    if preview.shape[1] > 1280:
        preview = cv2.resize(preview, None, fx=1280/preview.shape[1], fy=1280/preview.shape[1])
    
    scale = preview.shape[1] / orig_frame.shape[1]
    for slot in slots:
        pts = np.array([[int(p[0]*scale), int(p[1]*scale)] for p in slot['points']], np.int32)
        cv2.polylines(preview, [pts], True, (0, 255, 0), 2)
        overlay = preview.copy()
        cv2.fillPoly(overlay, [pts], (0, 255, 0))
        cv2.addWeighted(overlay, 0.15, preview, 0.85, 0, preview)
        center = np.mean(pts, axis=0).astype(int)
        cv2.putText(preview, str(slot['id']), tuple(center),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    cv2.imwrite('parking_slots_preview.jpg', preview)
    print("✅ Preview: parking_slots_preview.jpg\n")
    
    cv2.namedWindow('Generated Slots - Press any key', cv2.WINDOW_NORMAL)
    cv2.imshow('Generated Slots - Press any key', preview)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return slots


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("="*70)
        print("SMART PARKING SYSTEM MVP - GovTech PoC")
        print("="*70)
        print("\nUsage:")
        print("  1. Define parking slots:")
        print("     python smart_parking_mvp.py --map <video_file>")
        print("\n  2. Run parking detection:")
        print("     python smart_parking_mvp.py --run <video_file>")
        print("\nExample:")
        print("  python smart_parking_mvp.py --map parking.mp4")
        print("  python smart_parking_mvp.py --run parking.mp4")
        print("="*70)
        return
    
    mode = sys.argv[1]
    
    if mode == '--map':
        # Slot mapping mode
        if len(sys.argv) < 3:
            print("[ERROR] Video file required")
            return
        
        video_file = sys.argv[2]
        if not os.path.exists(video_file):
            print(f"[ERROR] Video not found: {video_file}")
            return
        
        map_parking_slots(video_file)
    
    elif mode == '--run':
        # Detection mode
        if len(sys.argv) < 3:
            print("[ERROR] Video file required")
            return
        
        video_file = sys.argv[2]
        if not os.path.exists(video_file):
            print(f"[ERROR] Video not found: {video_file}")
            return
        
        slots_json = 'configs/parking_slots.json'
        if not os.path.exists(slots_json):
            print(f"[ERROR] Slots not found: {slots_json}")
            print("Run --map first to define parking slots")
            return
        
        # Optional output video
        output_video = sys.argv[3] if len(sys.argv) > 3 else None
        
        # Run system
        system = SmartParkingMVP(slots_json)
        system.run(video_file, output_video)
    
    else:
        print(f"[ERROR] Unknown mode: {mode}")
        print("Use --map or --run")


if __name__ == "__main__":
    main()
