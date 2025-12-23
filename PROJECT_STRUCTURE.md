# Project Structure & Component Analysis

## 📁 Workspace Overview

```
parking/
├── Core Processing Files
│   ├── main.py                          ⭐ Main pipeline (vehicle + plate detection)
│   ├── util.py                          ⭐ OCR & format validation (NEEDS IMPROVEMENT)
│   ├── visualize.py                     📊 Creates output video with annotations
│   └── analyze_video.py                 📺 Video metadata analysis
│
├── Supporting Modules
│   └── sort/
│       ├── __init__.py
│       └── sort.py                      🔄 Vehicle tracking algorithm (SORT)
│
├── Machine Learning Models
│   ├── yolov8n.pt                       🚗 Vehicle detector (YOLO)
│   └── license_plate_detector.pt        📋 License plate detector (custom YOLO)
│
├── Test Scripts
│   ├── test_ocr.py                      🧪 Test OCR preprocessing
│   ├── test_plate_detector.py           🧪 Test plate detection
│   └── test_full_pipeline.py            🧪 Test complete pipeline
│
├── Configuration Files
│   ├── requirements.txt                 📦 Dependencies
│   └── requirements_alternative.txt     📦 Alternative deps
│
├── Input/Output Files
│   ├── sample.mp4                       🎬 Sample video input
│   ├── sample2.mp4                      🎬 Alternative sample
│   ├── output_with_plates.mp4           🎬 Processed output video
│   ├── test.csv                         📊 Detected plates data
│   └── test_interpolated.csv            📊 Smoothed data
│
├── Data & Artifacts
│   ├── plate_crops/                     🖼️ Cropped plate images
│   ├── first_detected_plate.jpg         🖼️ Sample plate image
│   ├── __pycache__/                     🔧 Python cache
│   └── env/                             🐍 Virtual environment
│
├── Documentation
│   ├── README.md                        📖 Project overview
│   ├── instruction.md                   📖 Setup instructions
│   ├── SYSTEM_STATUS.md                 ✅ Current status
│   ├── DETECTION_IMPROVEMENT_GUIDE.md   🔧 (NEW) Detailed improvements
│   └── QUICK_FIX_GUIDE.md              🔧 (NEW) Quick action plan
│
└── Other
    ├── .git/                            📝 Version control
    ├── .gitignore                       📝 Git config
    └── LICENSE                          ⚖️ License
```

---

## 🔄 Data Flow Pipeline

```
Video Input (sample.mp4)
    ↓
[YOLO Vehicle Detector] (yolov8n.pt)
    ↓ Detects cars, buses, motorcycles, trucks
[SORT Tracker]
    ↓ Assigns stable vehicle IDs across frames
[YOLO Plate Detector] (license_plate_detector.pt)
    ↓ Detects license plate regions
[Plate Cropping]
    ↓ Extract rectangular region containing plate
[OCR Preprocessing] ⚠️ MAIN PROBLEM HERE
    ↓ util.py → read_license_plate()
    ├─ Method 1: Red channel extraction
    ├─ Method 2: Inverted red channel
    ├─ Method 3: Upscaling + CLAHE
    ├─ Method 4: Adaptive threshold
    ├─ Method 5: Inverted adaptive
    └─ Method 6: HSV value channel
[EasyOCR Text Recognition] ⚠️ CONFIDENCE TOO LOW
    ↓ Character recognition from image
[Format Validation] ⚠️ ACCEPTS PARTIAL READS
    ↓ Check if format matches BP-X-YNNNN
[Temporal Voting] ❌ MISSING
    ↓ (Should verify consistency across frames)
[CSV Output]
    ↓ test.csv with detected plates
[Visualization]
    ↓ Create output video with boxes & text
[Video Output] (output_with_plates.mp4)
```

---

## 📝 Component Responsibilities

### **1. main.py** ⭐

**Role:** Orchestrates the entire pipeline

**What it does:**

- Loads YOLOv8 vehicle and plate detector models
- Processes video frame by frame
- Calls tracker for vehicle IDs
- Calls util.py for OCR
- Writes output video with annotations
- Saves results to CSV

**Current Issues:**

- ⚠️ `MIN_PLATE_CONFIDENCE = 0.05` (too low)
- ⚠️ No validation of OCR confidence before storing
- ⚠️ No temporal voting across frames
- ✅ Vehicle detection and tracking works well

**Lines to focus on:**

- Line 15: Confidence threshold
- Lines 45-65: Vehicle detection loop
- Lines 75+: Plate detection loop

---

### **2. util.py** ⭐⭐⭐ (PRIORITY - NEEDS MOST WORK)

**Role:** OCR and license plate validation

**Key Functions:**

#### `read_license_plate(license_plate_crop)`

**What it does:**

- Attempts to read text from plate image using 6 preprocessing methods
- Returns text and confidence score

**Current Preprocessing Methods:**

1. Red channel extraction
2. Inverted red channel
3. Upscaling (4x) + CLAHE
4. Adaptive threshold
5. Inverted adaptive threshold
6. HSV value channel

**Missing Methods:**

- ❌ Deskewing (straighten rotated plates)
- ❌ Morphological operations (clean noise)
- ❌ Bilateral filtering (smooth while preserving edges)
- ❌ Specific optimization for red Bhutanese plates

**Problems:**

- OCR confidence threshold is 0.3 (should be 0.5+)
- Accepts partial reads
- No validation of output format

**Lines to improve:**

- Lines 180-270: Preprocessing methods
- Line 290+: Candidate selection and scoring

#### `license_complies_format(text)`

**What it does:**

- Validates if text looks like a Bhutanese license plate

**Current Issues:**

- ⚠️ Too lenient - accepts "3225" or partial reads
- ⚠️ Doesn't enforce Bhutanese format (BP-X-YNNNN)
- ⚠️ Returns True for almost anything with 4+ characters and mixed digits/letters

**Should enforce:**

- Format: `^(BP|BT)-\d-[A-Z]\d{4}$`
- Examples: BP-1-C3275, BT-2-A1234
- Reject: Partial reads, wrong format, too short

#### `format_license(text)`

**What it does:**

- Converts raw OCR text to standardized format

**Current Issues:**

- Tries to "fix" text instead of rejecting invalid formats
- Converts I→1, O→0 even if they're wrong
- Adds BP prefix to things that aren't plates

---

### **3. sort.py** ✅ (Works well)

**Role:** Vehicle tracking across frames

**What it does:**

- Maintains stable vehicle IDs
- Tracks movement over time
- Handles occlusion and temporary disappearance

**Status:** Working well, no changes needed

---

### **4. visualize.py** ✅ (Works well)

**Role:** Creates final output video

**What it does:**

- Reads interpolated CSV
- Draws vehicle bounding boxes
- Displays license plate text
- Creates output video

**Status:** Works fine, depends on accurate OCR from main.py

---

### **5. Test Scripts** 🧪

#### `test_plate_detector.py`

- Tests if YOLO plate detector finds plates in video
- Useful for debugging detection issues

#### `test_ocr.py`

- Tests OCR preprocessing on sample images
- Useful for finding best preprocessing method

#### `test_full_pipeline.py`

- Tests complete pipeline on first N frames
- Good for debugging end-to-end issues

---

## 📊 File Relationships

```
Input Video
    ↓
main.py (orchestrator)
    ├→ vehicle_detector (yolov8n.pt)
    ├→ tracker (sort/sort.py)
    ├→ plate_detector (license_plate_detector.pt)
    └→ read_license_plate() from util.py
            ├→ EasyOCR reader
            ├→ license_complies_format()
            └→ format_license()
    ↓
Output: test.csv (raw results)
    ↓
add_missing_data.py (interpolation)
    ↓
Output: test_interpolated.csv
    ↓
visualize.py (creates video)
    ↓
Output: output_with_plates.mp4
```

---

## 🎯 What Each Component Does for Correct Detection

### **For Vehicle Detection (Working ✅):**

1. YOLOv8n model scans frame
2. Finds objects matching vehicle classes (car=2, motorcycle=3, bus=5, truck=7)
3. Returns bounding boxes with confidence scores
4. SORT tracker assigns stable IDs

**No changes needed** - This works well!

### **For License Plate Detection (Mostly working ⚠️):**

1. Custom YOLO model scans frame
2. Finds rectangular regions that look like plates
3. Returns bounding boxes with confidence scores
4. Currently accepts low confidence (0.05)

**Minor change needed:**

- Increase `MIN_PLATE_CONFIDENCE` from 0.05 to 0.4

### **For License Plate Recognition (Major problem ❌):**

1. Crop plate region from frame
2. **Apply preprocessing** (CURRENT METHODS SUBOPTIMAL)
   - Red channel extraction
   - Upscaling
   - Thresholding
   - etc.
3. **Run EasyOCR** with low confidence (0.3)
4. **Accept anything** that vaguely matches format
5. **No temporal voting** across frames

**Major changes needed:**

1. Better preprocessing (deskewing, morphology, bilateral filter)
2. Higher OCR confidence threshold (0.5+)
3. Strict format validation (reject partials)
4. Temporal voting (consensus across frames)

---

## 🔍 Bhutanese License Plate Characteristics

### **Format:**

```
BP-1-C3275
├─ BP = Bhutan Private (or BT for Taxi)
├─ 1 = Region code (0-9)
├─ C = Vehicle category (A-Z)
└─ 3275 = Registration number (4 digits)
```

### **Physical Appearance:**

- **Color:** Yellow background with RED text and red border
- **Size:** Standard (roughly 520x110 mm)
- **Material:** Reflective aluminum
- **Text:** Bold, sans-serif font

### **Common OCR Confusions:**

- O (letter) ↔ 0 (zero)
- I (letter) ↔ 1 (one)
- S ↔ 5
- B ↔ 8
- Z ↔ 2
- G ↔ 6
- A ↔ 4

**Your preprocessing must handle these!**

---

## 🚦 Current Issues Summary

| Component         | Status      | Issue                                           | Priority  |
| ----------------- | ----------- | ----------------------------------------------- | --------- |
| Vehicle Detection | ✅ Works    | None                                            | N/A       |
| Vehicle Tracking  | ✅ Works    | None                                            | N/A       |
| Plate Detection   | ⚠️ Works OK | Low confidence threshold                        | 🔴 High   |
| OCR Preprocessing | ❌ Poor     | Not optimized for red plates, missing deskewing | 🔴 High   |
| OCR Recognition   | ❌ Poor     | Too low confidence threshold (0.3)              | 🔴 High   |
| Format Validation | ❌ Loose    | Accepts partial/invalid reads                   | 🔴 High   |
| Temporal Voting   | ❌ Missing  | No frame-to-frame consistency                   | 🟡 Medium |
| Output Video      | ✅ Works    | Depends on accurate OCR                         | 🟢 Low    |

---

## 📚 Key Files to Understand

1. **Start here:** Read `main.py` lines 1-100 (configuration + main loop)
2. **Then:** Read `util.py` lines 180-270 (preprocessing methods)
3. **Then:** Read `util.py` lines 75-115 (format validation)
4. **Finally:** Understand the data flow in `main.py` lines 45-85 (detection loop)

---

## ✅ Summary

Your system is **80% built correctly**. The remaining **20% that matters** is:

- **OCR preprocessing** (how you prepare the image before reading it)
- **Confidence thresholds** (being more strict about what you accept)
- **Format validation** (rejecting obviously wrong reads)
- **Temporal voting** (checking consistency across frames)

All these live in `util.py` and need improvement. The good news: **No need to rewrite the whole system!** Just improve the plate reading quality.
