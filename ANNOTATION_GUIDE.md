
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
