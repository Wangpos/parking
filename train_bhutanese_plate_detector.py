"""
Train Custom YOLO Model for Bhutanese License Plate Detection
This script fine-tunes YOLOv8 specifically for Bhutanese license plates
"""

from ultralytics import YOLO
import os
import shutil
from pathlib import Path

# ======================== CONFIGURATION ========================
PROJECT_NAME = "bhutan_plate_detector"
EPOCHS = 100  # Training iterations
BATCH_SIZE = 16  # Adjust based on your GPU memory
IMAGE_SIZE = 640  # YOLO input size
PRETRAINED_MODEL = 'yolov8n.pt'  # Start with nano model (fast)
DEVICE = 0  # GPU device (0) or 'cpu'

# Data paths
DATA_DIR = "./plate_training_data"
TRAIN_IMAGES_DIR = f"{DATA_DIR}/images/train"
VAL_IMAGES_DIR = f"{DATA_DIR}/images/val"
TRAIN_LABELS_DIR = f"{DATA_DIR}/labels/train"
VAL_LABELS_DIR = f"{DATA_DIR}/labels/val"
# ================================================================

def setup_dataset_structure():
    """Create the directory structure for YOLO training"""
    print("📁 Setting up dataset structure...")
    
    dirs = [
        TRAIN_IMAGES_DIR,
        VAL_IMAGES_DIR,
        TRAIN_LABELS_DIR,
        VAL_LABELS_DIR
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")
    
    print("\n✅ Directory structure ready!\n")

def create_dataset_yaml():
    """Create dataset.yaml configuration file"""
    yaml_content = f"""# Bhutanese License Plate Dataset Configuration
path: {os.path.abspath(DATA_DIR)}
train: images/train
val: images/val

# Classes
nc: 1  # number of classes
names: ['license_plate']  # class names

# Bhutanese plate characteristics:
# - Formats: BP-X-YNNNN, BT-X-YNNNN, BG-X-YNNNN
# - Colors: Red, Yellow, Blue, Green, White backgrounds
# - Contains Bhutanese script (Dzongkha) at top
# - Typically rectangular with specific aspect ratio
"""
    
    yaml_path = f"{DATA_DIR}/dataset.yaml"
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"✓ Created {yaml_path}\n")
    return yaml_path

def train_model(yaml_path):
    """Train the YOLO model on Bhutanese plates"""
    print("🚀 Starting training...\n")
    print("=" * 60)
    print(f"Project: {PROJECT_NAME}")
    print(f"Epochs: {EPOCHS}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Image size: {IMAGE_SIZE}")
    print(f"Device: {DEVICE}")
    print("=" * 60)
    print()
    
    # Load pretrained model
    model = YOLO(PRETRAINED_MODEL)
    
    # Training configuration optimized for license plates
    results = model.train(
        data=yaml_path,
        epochs=EPOCHS,
        batch=BATCH_SIZE,
        imgsz=IMAGE_SIZE,
        device=DEVICE,
        project=PROJECT_NAME,
        name='bhutan_plates',
        
        # Augmentation settings (important for plates!)
        hsv_h=0.015,  # Hue augmentation
        hsv_s=0.7,    # Saturation (helps with different plate colors)
        hsv_v=0.4,    # Value/brightness
        degrees=5,    # Slight rotation (plates can be at angles)
        translate=0.1,  # Translation
        scale=0.5,    # Scale variation
        shear=2,      # Shear transformation
        perspective=0.0,  # Perspective (plates are usually flat)
        flipud=0.0,   # No vertical flip (plates have orientation)
        fliplr=0.0,   # No horizontal flip (text direction matters)
        mosaic=1.0,   # Mosaic augmentation
        mixup=0.0,    # No mixup (keep plates clear)
        
        # Training parameters
        patience=20,  # Early stopping patience
        save=True,
        save_period=10,  # Save checkpoint every 10 epochs
        cache=False,  # Set True if you have enough RAM
        workers=8,
        
        # Loss weights
        box=7.5,      # Box loss weight (important for precise localization)
        cls=0.5,      # Class loss weight (only 1 class)
        dfl=1.5,      # Distribution focal loss
        
        # Other
        verbose=True,
        plots=True    # Generate training plots
    )
    
    print("\n✅ Training complete!")
    print(f"Best model saved to: {PROJECT_NAME}/bhutan_plates/weights/best.pt")
    return results

def validate_model(model_path):
    """Validate the trained model"""
    print("\n📊 Validating model...")
    model = YOLO(model_path)
    
    metrics = model.val()
    
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    print(f"mAP50: {metrics.box.map50:.4f}")
    print(f"mAP50-95: {metrics.box.map:.4f}")
    print(f"Precision: {metrics.box.mp:.4f}")
    print(f"Recall: {metrics.box.mr:.4f}")
    print("=" * 60)

def export_model(model_path):
    """Export model for deployment"""
    print("\n📦 Exporting model...")
    model = YOLO(model_path)
    
    # Export to different formats
    model.export(format='onnx')  # ONNX format
    print("✓ Exported to ONNX format")

def create_annotation_guide():
    """Create a guide for annotating images"""
    guide = """
# 📝 How to Annotate Bhutanese License Plates

## Step 1: Collect Images
Collect 300-500 images of Bhutanese vehicles with visible license plates:
- Various angles (front, slight angles)
- Different lighting conditions (day, night, shadows)
- Different plate types (BP, BT, BG, etc.)
- Different colors (red, yellow, blue, green, white)
- Different distances (close-up, medium, far)
- Different weather conditions

## Step 2: Use Labeling Tool
I recommend using one of these tools:

### Option A: Roboflow (Easiest - Online)
1. Go to https://roboflow.com
2. Create free account
3. Create new project: "Bhutanese Plates"
4. Upload your images
5. Draw boxes around license plates
6. Export in YOLOv8 format
7. Download and place in ./plate_training_data/

### Option B: LabelImg (Offline - Desktop)
1. Install: `pip install labelImg`
2. Run: `labelImg`
3. Open directory with images
4. Draw boxes (press 'w' to start)
5. Save (press 's')
6. Choose YOLO format
7. Label class: 'license_plate'

### Option C: CVAT (Advanced - Online/Self-hosted)
1. Go to https://cvat.org
2. Create account
3. Upload images
4. Create task with 1 label: 'license_plate'
5. Annotate all plates
6. Export as YOLO 1.1 format

## Step 3: Annotation Tips
✓ Draw tight boxes around the entire plate (include borders)
✓ Include the Bhutanese script at the top
✓ Don't include too much surrounding area
✓ Ensure the box is rectangular and aligned
✓ Mark partially visible plates too (if >50% visible)
✗ Don't include too much vehicle body
✗ Don't miss small or distant plates

## Step 4: Data Split
- Training set: 80% of images (e.g., 240 images)
- Validation set: 20% of images (e.g., 60 images)

Place in:
- Train images: ./plate_training_data/images/train/
- Train labels: ./plate_training_data/labels/train/
- Val images: ./plate_training_data/images/val/
- Val labels: ./plate_training_data/labels/val/

## Step 5: Label Format
Each image (e.g., img1.jpg) needs a label file (img1.txt):
```
0 0.5 0.5 0.3 0.15
```
Format: class_id center_x center_y width height (all normalized 0-1)

Example for a plate at:
- Image: 1920x1080
- Plate box: x1=800, y1=500, x2=1100, y2=600
- Center_x = (800+1100)/2 / 1920 = 0.494
- Center_y = (500+600)/2 / 1080 = 0.509
- Width = (1100-800) / 1920 = 0.156
- Height = (600-500) / 1080 = 0.093
- Label: `0 0.494 0.509 0.156 0.093`

## Quick Start with Sample Images
You can extract frames from your video to start:
```python
python extract_frames_for_training.py
```
Then annotate those frames!
"""
    
    with open("ANNOTATION_GUIDE.md", 'w') as f:
        f.write(guide)
    
    print("✓ Created ANNOTATION_GUIDE.md")

def main():
    """Main training pipeline"""
    print("\n" + "=" * 60)
    print("  BHUTANESE LICENSE PLATE DETECTOR TRAINING")
    print("=" * 60)
    print()
    
    # Check if dataset exists
    if not os.path.exists(TRAIN_IMAGES_DIR) or len(os.listdir(TRAIN_IMAGES_DIR)) == 0:
        print("⚠️  No training data found!")
        print("\nPlease follow these steps:\n")
        print("1. Run this script to create dataset structure:")
        print("   python train_bhutanese_plate_detector.py --setup")
        print("\n2. Collect and annotate images (see ANNOTATION_GUIDE.md)")
        print("\n3. Run training:")
        print("   python train_bhutanese_plate_detector.py --train")
        print()
        
        response = input("Create dataset structure now? (y/n): ")
        if response.lower() == 'y':
            setup_dataset_structure()
            create_dataset_yaml()
            create_annotation_guide()
            
            print("\n✅ Setup complete!")
            print("\nNext steps:")
            print("1. Read ANNOTATION_GUIDE.md")
            print("2. Collect 300-500 images of Bhutanese vehicles")
            print("3. Annotate license plates using Roboflow/LabelImg")
            print("4. Place data in ./plate_training_data/")
            print("5. Run: python train_bhutanese_plate_detector.py --train")
        return
    
    # Count training images
    train_count = len([f for f in os.listdir(TRAIN_IMAGES_DIR) if f.endswith(('.jpg', '.png'))])
    val_count = len([f for f in os.listdir(VAL_IMAGES_DIR) if f.endswith(('.jpg', '.png'))])
    
    print(f"📊 Dataset Statistics:")
    print(f"  Training images: {train_count}")
    print(f"  Validation images: {val_count}")
    print(f"  Total: {train_count + val_count}")
    print()
    
    if train_count < 50:
        print("⚠️  WARNING: Less than 50 training images!")
        print("   Recommended: 300+ images for good accuracy")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Create dataset YAML
    yaml_path = create_dataset_yaml()
    
    # Train model
    results = train_model(yaml_path)
    
    # Validate
    best_model_path = f"{PROJECT_NAME}/bhutan_plates/weights/best.pt"
    validate_model(best_model_path)
    
    # Export
    export_model(best_model_path)
    
    print("\n" + "=" * 60)
    print("🎉 ALL DONE!")
    print("=" * 60)
    print(f"\n📁 Your trained model: {best_model_path}")
    print("\nTo use it in main.py, replace:")
    print("  plate_detector = YOLO('license_plate_detector.pt')")
    print("With:")
    print(f"  plate_detector = YOLO('{best_model_path}')")
    print()

if __name__ == "__main__":
    import sys
    
    if "--setup" in sys.argv:
        setup_dataset_structure()
        create_dataset_yaml()
        create_annotation_guide()
        print("\n✅ Setup complete! Read ANNOTATION_GUIDE.md for next steps.")
    elif "--train" in sys.argv:
        main()
    else:
        main()
