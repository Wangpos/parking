# License Plate Detection & Recognition - Comprehensive Analysis & Improvement Guide

## Current System Status: ✅ PARTIALLY WORKING

Your system is detecting vehicles and license plates, but has **challenges with accurate OCR recognition**. Based on the video feed image you showed, here are the specific issues and solutions needed.

---

## 📊 CURRENT PIPELINE ANALYSIS

### **What's Working:**

1. ✅ **Vehicle Detection** - YOLOv8n detects vehicles (cars, motorcycles, buses, trucks)
2. ✅ **Vehicle Tracking** - SORT algorithm tracks vehicles across frames with stable IDs
3. ✅ **License Plate Detection** - custom `license_plate_detector.pt` model detects plates
4. ✅ **Data Persistence** - Results saved to CSV with interpolation for smoothing

### **What Needs Improvement:**

1. ❌ **OCR Accuracy** - EasyOCR struggles with Bhutanese red/pink license plates
2. ⚠️ **Low Confidence Threshold** - Currently accepts very low quality detections
3. ⚠️ **Character Recognition** - Letters vs Numbers confusion (O/0, I/1, etc.)
4. ⚠️ **Partial Plate Recognition** - Accepting incomplete reads instead of waiting for full plate view

---

## 🎯 ISSUES IN YOUR VIDEO FEED

From the screenshot showing parking lot detection, here are the specific problems:

### **Issue 1: Character Misrecognition**

- **What's happening**: Plates like "222S" are being read as "2225" or partial characters
- **Root cause**: EasyOCR confidence is too low (0.3 threshold), accepting poor quality reads
- **Impact**: Wrong plate numbers recorded

### **Issue 2: Partial Plate Detection**

- **What's happening**: Plates at angles or partially visible are detected but OCR fails
- **Root cause**: Not enough preprocessing to handle rotated/skewed plates
- **Impact**: Missing plate reads or incomplete numbers

### **Issue 3: Red/Pink Plate Color Issues**

- **What's happening**: Bhutanese red/pink license plates have poor contrast in OCR
- **Root cause**: EasyOCR not optimized for the red plate color scheme
- **Impact**: Character segmentation fails

### **Issue 4: Lighting Variations**

- **What's happening**: Different lighting conditions cause different OCR results
- **Root cause**: No adaptive lighting/contrast enhancement
- **Impact**: Same plate gets different readings in different frames

---

## ✅ SOLUTIONS & IMPROVEMENTS NEEDED

### **PRIORITY 1: Improve OCR Preprocessing (Critical)**

**Current Problems in `util.py`:**

```python
# Current: 6 preprocessing methods, but some are suboptimal
# Problems:
# - Red channel extraction not optimal for Bhutanese plates
# - HSV value channel not helping
# - Upscaling factor (4x) may be too aggressive
```

**What needs to be done:**

1. **Add Morphological Operations**

   ```python
   # After threshold, clean up noise
   kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
   morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
   morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)
   ```

2. **Improve Red Channel Detection**

   ```python
   # For red Bhutanese plates specifically
   # Create red mask using HSV
   hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
   lower_red = np.array([0, 100, 100])
   upper_red = np.array([10, 255, 255])
   mask = cv2.inRange(hsv, lower_red, upper_red)
   # Apply mask to extract only red plate area
   ```

3. **Add Deskewing (Most Important for Angled Plates)**

   ```python
   # Detect and correct skewed plates
   # Use contour analysis to find rotation angle
   # Rotate image to align text horizontally
   ```

4. **Add Bilateral Filtering**
   ```python
   # Removes noise while preserving edges
   filtered = cv2.bilateralFilter(gray, 9, 75, 75)
   ```

### **PRIORITY 2: Increase Confidence Thresholds**

**Current Issue:**

```python
MIN_PLATE_CONFIDENCE = 0.05  # TOO LOW - shows everything including noise
```

**Solution:**

- **For plate detection**: Increase from 0.05 to **0.3-0.4** (high quality only)
- **For OCR**: Increase from 0.3 to **0.5-0.6** (only accept confident reads)
- **For format validation**: Reject partial reads, require complete plates

### **PRIORITY 3: Add Character Validation & Correction**

**Current dictionaries exist but not fully leveraged:**

```python
dict_char_to_int = {'O': '0', 'I': '1', 'J': '3', 'A': '4', 'G': '6', 'S': '5'}
```

**What's needed:**

1. **Position-specific correction** - Know Bhutanese format: BP-1-C3275

   - Position 0-1: Letters (BP/BT)
   - Position 2: Digit (0-9)
   - Position 3: Letter (A-Z)
   - Position 4-7: Digits (0-9)

2. **Confidence-weighted voting** - Multiple reads of same plate, keep consensus

   ```python
   # If same vehicle appears in 5 frames with plates:
   # Frame 1: "322S"
   # Frame 2: "322S"
   # Frame 3: "3225"
   # Frame 4: "322S"
   # Frame 5: "322S"
   # → Accept "322S" (4 out of 5 agreement)
   ```

3. **Format Enforcement**
   - Must match: `BP-\d-[A-Z]\d{4}` or `BT-\d-[A-Z]\d{4}`
   - Reject anything not matching this pattern

### **PRIORITY 4: Improve Plate Detection Confidence**

**Current:**

```python
# Accepting plates with very low confidence
results[frame_num] = {}
detections = []
for det in frame_result.boxes.data.tolist():
    # No minimum confidence threshold for plates!
```

**Solution:**

- Set minimum plate detection confidence to **0.4-0.5**
- Skip frames where no high-confidence plates detected
- Focus on vehicles with multiple consecutive detections

### **PRIORITY 5: Add Temporal Consistency**

**Current Issue:** Each frame is processed independently

**Solution - Add Frame Averaging:**

```python
# For each vehicle, track plate readings over N frames
# Vehicle seen in frames: [10, 11, 12, 13, 14]
# Plate reads: ["3P2I", "3P2I", "322I", "3P2I", "3P2I"]
# Final result: "3P2I" (consensus from 4 frames)

# Only update CSV when confidence > threshold
# Smooth transitions between plates
```

---

## 📋 ACTION ITEMS (In Priority Order)

### **Immediate Actions (Do First):**

1. **✏️ Modify `util.py` - read_license_plate() function:**

   - [ ] Add morphological operations for noise reduction
   - [ ] Improve red channel detection for Bhutanese plates
   - [ ] Add deskewing/rotation correction
   - [ ] Add bilateral filtering
   - [ ] Increase OCR confidence threshold to 0.5+

2. **✏️ Modify `main.py` - Configuration:**

   - [ ] Change `MIN_PLATE_CONFIDENCE` from 0.05 to 0.4
   - [ ] Update OCR threshold in detection loop
   - [ ] Add validation for Bhutanese format
   - [ ] Remove partial reads acceptance

3. **✏️ Modify `util.py` - read_license_plate() logic:**

   - [ ] Enforce strict format validation
   - [ ] Add position-specific character correction
   - [ ] Return None if format doesn't match
   - [ ] Only accept confidence > 0.5

4. **➕ Add new function `util.py` - Temporal consistency:**

   - [ ] Add plate history tracking per vehicle
   - [ ] Implement voting mechanism across frames
   - [ ] Add smoothing for plate text changes

5. **🧪 Create new test file `test_improvements.py`:**
   - [ ] Test OCR on different angles
   - [ ] Test different lighting conditions
   - [ ] Validate format checking
   - [ ] Test temporal voting

### **Secondary Actions (Next Phase):**

6. **📦 Consider Alternative OCR:**

   - [ ] Test PaddleOCR (better for curved text)
   - [ ] Test Tesseract with custom training
   - [ ] Test KerasOCR if available

7. **🎯 Fine-tune License Plate Detector:**

   - [ ] If `license_plate_detector.pt` is custom trained, retrain with:
     - More Bhutanese plate examples
     - Various angles and lighting
     - Different colors and wear conditions

8. **📊 Add Validation Metrics:**
   - [ ] Track OCR confidence per plate
   - [ ] Log which preprocessing method works best
   - [ ] Monitor false positives vs true positives

---

## 🛠️ TECHNICAL DETAILS

### **Bhutanese License Plate Format**

```
Format: BP-1-C3275 or BT-1-A3269
Regex: ^(BP|BT)-\d-[A-Z]\d{4}$

Components:
- BP = Bhutan Private vehicle
- BT = Bhutan Taxi (also exists)
- 1  = Region code
- C  = Vehicle category letter
- 3275 = Registration number
```

### **Current Preprocessing Methods** (in `util.py`):

1. Red channel extraction
2. Inverted red channel
3. Upscaling + CLAHE
4. Adaptive threshold upscaled
5. Inverted adaptive threshold
6. HSV value channel

**Missing:**

- Deskewing/rotation correction
- Morphological operations
- Color space optimization for red plates
- Bilateral filtering
- Plate contour detection

### **Current Confidence Thresholds** (Problems):

```python
MIN_PLATE_CONFIDENCE = 0.05  # ❌ TOO LOW
OCR confidence in read_license_plate = 0.3  # ❌ TOO LOW
```

**Recommended:**

```python
MIN_PLATE_CONFIDENCE = 0.4  # ✅ Better filtering
MIN_OCR_CONFIDENCE = 0.5    # ✅ Only confident reads
MIN_FORMAT_MATCH = 0.8      # ✅ Strict format validation
```

---

## 📈 EXPECTED IMPROVEMENTS

After implementing these changes, you should see:

| Metric                   | Current   | Target               |
| ------------------------ | --------- | -------------------- |
| **Plate Detection Rate** | ~80%      | 95%+                 |
| **OCR Accuracy**         | ~40-50%   | 85%+                 |
| **False Positives**      | High      | < 5%                 |
| **Temporal Consistency** | Poor      | Excellent            |
| **Processing Speed**     | Real-time | Real-time maintained |

---

## 🚀 NEXT STEPS

1. **Start with OCR improvements** - This is your biggest bottleneck
2. **Increase confidence thresholds** - Reduce noise and false positives
3. **Add temporal voting** - Smooth out inconsistencies
4. **Test on your video feed** - Validate each change
5. **Fine-tune based on results** - Adjust thresholds as needed

---

## 📞 DEBUGGING TIPS

**If plates still not detecting correctly:**

1. Run `test_plate_detector.py` to verify YOLO detects plates
2. Extract a problematic plate with `cv2.imwrite()`
3. Test that plate in isolation with all preprocessing methods
4. Use `DEBUG_MODE = True` in main.py
5. Save cropped plates to `plate_crops/` for inspection

**If OCR still failing:**

1. Check that cropped plate is readable (is it clear? correct color?)
2. Verify preprocessing methods are improving image quality
3. Test with PaddleOCR as alternative
4. Consider the plate is at wrong angle (need deskewing)
