"""
Main Launcher for Automatic Parking Detection Mode
Zero-configuration smart parking system
GovTech Bhutan - Smart Parking MVP

Usage:
    # Run with default video
    python main_automatic.py
    
    # Run with specific video
    python main_automatic.py --video path/to/video.mp4
    
    # Define parking zone first
    python main_automatic.py --define-zone
    
    # Run with webcam
    python main_automatic.py --video 0
    
    # Save output video
    python main_automatic.py --save-output
"""

import cv2
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

from automatic_detector import (
    AutomaticParkingDetector,
    ParkingZone,
    ParkingZoneDefiner,
    save_parking_zone,
    load_parking_zone
)


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/automatic_mode.log')
        ]
    )


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Smart Parking System - Automatic Mode',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default video
  python main_automatic.py
  
  # Run with specific video file
  python main_automatic.py --video path/to/parking_video.mp4
  
  # Define parking zone interactively
  python main_automatic.py --define-zone
  
  # Run with webcam
  python main_automatic.py --video 0
  
  # Save annotated output video
  python main_automatic.py --save-output
  
  # Use smaller model for faster processing
  python main_automatic.py --model yolov8n.pt
        """
    )
    
    parser.add_argument(
        '--video', '-v',
        type=str,
        default='parking_video.mp4.mp4',
        help='Path to video file or camera index (default: parking_video.mp4.mp4)'
    )
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        default='yolov8s.pt',
        help='YOLO model to use (default: yolov8s.pt for balanced speed/accuracy)'
    )
    
    parser.add_argument(
        '--confidence', '-c',
        type=float,
        default=0.15,
        help='Detection confidence threshold (default: 0.15, lower=more detections)'
    )
    
    parser.add_argument(
        '--device', '-d',
        type=str,
        default='auto',
        help='Device to run on: auto, cpu, or cuda (default: auto - uses GPU if available)'
    )
    
    parser.add_argument(
        '--define-zone',
        action='store_true',
        help='Interactively define parking zone before running'
    )
    
    parser.add_argument(
        '--no-zone',
        action='store_true',
        help='Disable parking zone (process entire frame)'
    )
    
    parser.add_argument(
        '--save-output',
        action='store_true',
        help='Save annotated video to output folder'
    )
    
    parser.add_argument(
        '--frame-skip',
        type=int,
        default=1,
        help='Process every Nth frame (0=all frames, 1=every 2nd, 2=every 3rd) - default: 1 for 2x speed'
    )
    
    parser.add_argument(
        '--speed-threshold',
        type=float,
        default=8.0,
        help='Max speed (pixels/sec) to consider vehicle stationary (default: 8.0)'
    )
    
    parser.add_argument(
        '--time-threshold',
        type=float,
        default=5.0,
        help='Min seconds stationary to consider parked (default: 5.0)'
    )
    
    parser.add_argument(
        '--preset',
        type=str,
        choices=['fast', 'balanced', 'accurate'],
        default='balanced',
        help='Performance preset: fast (yolov8n, skip 2), balanced (yolov8s, skip 1), accurate (yolov8m, skip 0)'
    )
    
    parser.add_argument(
        '--process-size',
        type=int,
        default=640,
        help='Processing resolution (default: 640 for speed, 1280 for accuracy)'
    )
    
    parser.add_argument(
        '--show-fps',
        action='store_true',
        help='Display FPS counter on screen'
    )
    
    return parser.parse_args()


def apply_preset(args):
    """Apply performance preset configurations."""
    if args.preset == 'fast':
        args.model = 'yolov8n.pt'
        args.frame_skip = 2  # Process every 3rd frame
        args.process_size = 640
        args.confidence = 0.2  # Lower for better coverage
        args.speed_threshold = 10.0  # Very lenient
        args.time_threshold = 3.0  # Quick detection
        print("\n[FAST] preset: Optimized for speed (15-25 FPS)")
    elif args.preset == 'balanced':
        args.model = 'yolov8s.pt'
        args.frame_skip = 1  # Process every 2nd frame
        args.process_size = 640
        args.confidence = 0.15  # Lower to catch all vehicles
        args.speed_threshold = 8.0  # Lenient for stationary detection
        args.time_threshold = 5.0  # Stable parking detection
        print("\n[BALANCED] preset: Good speed and accuracy (10-20 FPS)")
    elif args.preset == 'accurate':
        args.model = 'yolov8m.pt'
        args.frame_skip = 0  # Process all frames
        args.process_size = 1280
        args.confidence = 0.1  # Very low for complete coverage
        args.speed_threshold = 5.0  # Stricter for accuracy
        args.time_threshold = 8.0  # Very stable detection
        print("\n[ACCURATE] preset: Maximum accuracy (5-15 FPS)")


def get_video_source(video_arg):
    """
    Get video source from argument.
    
    Args:
        video_arg: Video path or camera index
        
    Returns:
        Video source (str or int)
    """
    # Check if it's a camera index
    if video_arg.isdigit():
        return int(video_arg)
    
    # Check if file exists
    video_path = Path(video_arg)
    if not video_path.exists():
        # Try in videos folder
        video_path = Path('videos') / video_arg
        if not video_path.exists():
            print(f"✗ Video file not found: {video_arg}")
            sys.exit(1)
    
    return str(video_path)


def main():
    """Main execution function."""
    # Setup
    setup_logging()
    logger = logging.getLogger('AutomaticMode')
    args = parse_arguments()
    
    # Apply preset if not using custom settings
    apply_preset(args)
    
    print("\n" + "="*70)
    print("SMART PARKING SYSTEM - AUTOMATIC DETECTION MODE")
    print("="*70)
    print("Features:")
    print("  [OK] Zero-configuration vehicle detection")
    print("  [OK] Automatic capacity estimation")
    print("  [OK] Vehicle tracking (prevents timer resets)")
    print("  [OK] Smart parking classification (parked vs moving)")
    print("  [OK] Far-range detection (detects distant vehicles)")
    print("  [OK] Performance optimized for real-time processing")
    print("="*70)
    print(f"\nPerformance Settings:")
    print(f"  - Model: {args.model}")
    print(f"  - Device: {args.device.upper()}")
    print(f"  - Frame Skip: Every {args.frame_skip + 1}{'st' if args.frame_skip == 0 else ('nd' if args.frame_skip == 1 else 'rd')} frame")
    print(f"  - Process Size: {args.process_size}px")
    print(f"  - Confidence: {args.confidence}")
    print(f"\nParking Detection Settings:")
    print(f"  - Speed Threshold: {args.speed_threshold} pixels/sec")
    print(f"  - Time Threshold: {args.time_threshold} seconds")
    print("="*70 + "\n")
    
    # Get video source
    video_source = get_video_source(args.video)
    logger.info(f"Video source: {video_source}")
    
    # Open video
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print(f"✗ Failed to open video source: {video_source}")
        sys.exit(1)
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"✓ Video loaded: {width}x{height} @ {fps} FPS ({total_frames} frames)")
    
    # Define parking zone
    parking_zone = None
    
    if args.no_zone:
        print("[INFO] Parking zone disabled - processing entire frame")
        parking_zone = ParkingZone()
    elif args.define_zone:
        print("\nDefining parking zone...")
        # Read first frame
        ret, first_frame = cap.read()
        if ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to start
            
            # Interactive zone definition
            zone_definer = ParkingZoneDefiner(first_frame)
            parking_zone = zone_definer.run()
            
            if parking_zone:
                save_parking_zone(parking_zone)
            else:
                print("[WARNING] No parking zone defined, using entire frame")
                parking_zone = ParkingZone()
    else:
        # Try to load existing zone
        parking_zone = load_parking_zone()
        if parking_zone is not None:
            print("[WARNING] Existing parking zone loaded from previous session")
            print("          If detection seems wrong, use --no-zone to disable")
            print("          Or use --define-zone to redefine the zone")
        else:
            print("[INFO] No parking zone defined - processing entire frame")
            print("       (Run with --define-zone to define one if needed)")
            parking_zone = ParkingZone()
    
    # Initialize detector
    print(f"\nInitializing detector with model: {args.model}")
    print("This may take a moment on first run (downloading model)...\n")
    
    try:
        detector = AutomaticParkingDetector(
            model_path=args.model,
            confidence_threshold=args.confidence,
            device=args.device,
            parking_zone=parking_zone,
            process_size=args.process_size,
            enable_half_precision=True
        )
        
        # Store thresholds for processing
        detector.speed_threshold = args.speed_threshold
        detector.time_threshold = args.time_threshold
        
        print("[OK] Detector initialized successfully\n")
    except Exception as e:
        print(f"[ERROR] Failed to initialize detector: {e}")
        sys.exit(1)
    
    # Setup output video writer
    output_writer = None
    if args.save_output:
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = output_dir / f'automatic_mode_{timestamp}.mp4'
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        print(f"✓ Output will be saved to: {output_path}\n")
    
    # Processing info
    print("="*70)
    print("CONTROLS:")
    print("  SPACE  - Pause/Resume")
    print("  Q/ESC  - Quit")
    print("  S      - Save screenshot")
    print("  F      - Toggle FPS display")
    print("="*70)
    print(f"\nTarget FPS: 15-30 (Current preset: {args.preset.upper()})")
    print("Processing video...\n")
    print("="*70 + "\n")
    
    # Processing loop
    frame_count = 0
    paused = False
    show_fps = args.show_fps
    
    try:
        while True:
            if not paused:
                # Read frame
                ret, frame = cap.read()
                
                if not ret:
                    print("\n✓ End of video reached")
                    break
                
                frame_count += 1
                
                # Frame skipping for performance
                should_process = (frame_count % (args.frame_skip + 1) == 0)
                
                # Process frame (or use cached results) with custom thresholds
                if should_process:
                    results = detector.process_frame(frame, force_detect=True)
                    # Apply custom thresholds
                    parked, moving = detector.classify_parking_status(
                        list(detector.tracked_vehicles.values()),
                        speed_threshold=args.speed_threshold,
                        time_threshold=args.time_threshold
                    )
                    results['parked_vehicles'] = parked
                    results['moving_vehicles'] = moving
                    results['parked_count'] = len(parked)
                    results['moving_count'] = len(moving)
                    detector.update_capacity_estimation(len(parked))
                    results['capacity'] = detector.estimated_capacity
                    results['available'] = max(0, detector.estimated_capacity - len(parked))
                    results['occupancy_percent'] = (len(parked) / detector.estimated_capacity * 100) if detector.estimated_capacity > 0 else 0
                    detector.last_results = results
                else:
                    results = detector.last_results if detector.last_results else detector.process_frame(frame, force_detect=True)
                
                # Draw results
                annotated_frame = detector.draw_results(frame, results)
                
                # Optionally show FPS
                if show_fps:
                    fps_text = f"FPS: {results.get('avg_fps', 0):.1f}"
                    cv2.putText(
                        annotated_frame, fps_text, (10, annotated_frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                    )
                
                # Write to output video
                if output_writer:
                    output_writer.write(annotated_frame)
                
                # Display
                cv2.imshow('Automatic Parking Detection', annotated_frame)
                
                # Print stats every 30 processed frames
                if should_process and detector.frame_count % 30 == 0:
                    avg_fps = results.get('avg_fps', 0)
                    print(f"Frame {frame_count}/{total_frames} | "
                          f"FPS: {avg_fps:.1f} | "
                          f"Parked: {results['parked_count']} | "
                          f"Capacity: {results['capacity']} | "
                          f"Occupancy: {results['occupancy_percent']:.1f}%")
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # Q or ESC
                print("\n⚠️  Stopped by user")
                break
            elif key == ord(' '):  # SPACE
                paused = not paused
                status = "PAUSED" if paused else "RESUMED"
                print(f"\n{status}")
            elif key == ord('s'):  # S
                # Save screenshot
                screenshot_dir = Path('output/screenshots')
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                screenshot_path = screenshot_dir / f'screenshot_{timestamp}.jpg'
                cv2.imwrite(str(screenshot_path), annotated_frame)
                print(f"✓ Screenshot saved: {screenshot_path}")
            elif key == ord('f'):  # F
                show_fps = not show_fps
                print(f"\nFPS display: {'ON' if show_fps else 'OFF'}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user (Ctrl+C)")
    
    finally:
        # Cleanup
        cap.release()
        if output_writer:
            output_writer.release()
        cv2.destroyAllWindows()
        
        # Final statistics
        print("\n" + "="*70)
        print("FINAL STATISTICS")
        print("="*70)
        print(f"Total Frames Processed: {detector.frame_count}")
        print(f"Total Detections: {detector.total_detections}")
        print(f"Average FPS: {sum(detector.fps_history) / len(detector.fps_history):.1f}" if detector.fps_history else "N/A")
        print(f"Average Process Time: {sum(detector.process_times) / len(detector.process_times) * 1000:.1f}ms" if detector.process_times else "N/A")
        print(f"Estimated Capacity: {detector.estimated_capacity}")
        print(f"Max Parked Observed: {detector.max_parked_observed}")
        print(f"Currently Tracked Vehicles: {len(detector.tracked_vehicles)}")
        print("="*70 + "\n")
        
        print("[OK] Automatic parking detection completed")


if __name__ == '__main__':
    main()
