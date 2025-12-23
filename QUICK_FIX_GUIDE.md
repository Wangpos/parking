# Quick Reference: What Needs to Be Done

## 🎯 Your Current Situation

You have a **working parking lot detection system** that:

- ✅ Detects vehicles correctly
- ✅ Tracks vehicles across frames
- ✅ Detects license plates
- ❌ **But struggles to read plate numbers accurately**

The video shows cars being detected and tracked, but the OCR (Optical Character Recognition) that reads the plate numbers needs significant improvement.

---

## 🔴 TOP 3 CRITICAL ISSUES

### **Issue #1: OCR Confidence Too Low**

```
Current: Accepting plates with 0.05 confidence (5% confident!)
Problem: Reading garbage instead of actual plate numbers
Fix: Increase to 0.4-0.5 confidence minimum
```

### **Issue #2: No Image Preprocessing for Red Plates**

```
Current: Basic preprocessing not optimized for Bhutanese red/yellow plates
Problem: Characters blend into background, can't be read
Fix: Add:
  - Deskewing (rotate angled plates straight)
  - Morphological cleaning (remove noise)
  - Red channel extraction (isolate plate from surroundings)
  - Bilateral filtering (smooth while keeping edges sharp)
```

### **Issue #3: Accepting Partial/Garbage Reads**

```
Current: Accepting "3225" even if format is wrong
Problem: Storing incorrect plate numbers
Fix: Enforce Bhutanese format:
  - Must be: BP-1-C3275 or BT-1-A3269
  - Reject: "ABCD", "???", partial numbers
```

---

## 📋 STEP-BY-STEP ACTION PLAN

### **Step 1: Fix Confidence Thresholds** (5 minutes)

**File:** `main.py`

```python
# Change line ~15 from:
MIN_PLATE_CONFIDENCE = 0.05   # ❌ Remove this

# To set it during detection:
conf=0.4  # ✅ Only high-confidence plates
```

### **Step 2: Improve OCR Preprocessing** (30-45 minutes)

**File:** `util.py`, function `read_license_plate()`

Add these enhancements:

1. **Deskewing** - Straighten rotated plates
2. **Morphology** - Clean up noise using erosion/dilation
3. **Red channel extraction** - Focus on red plate area
4. **Bilateral filtering** - Smooth noise, keep edges
5. **Higher upscaling** - Better character recognition

### **Step 3: Enforce Format Validation** (15 minutes)

**File:** `util.py`, function `license_complies_format()`

Change from loose validation to strict:

```python
# Current: Accepts "3225" as valid
# New: Requires format "BP-X-YNNNN" where:
#   X = digit (0-9)
#   Y = letter (A-Z)
#   N = digit (0-9)
```

### **Step 4: Add Temporal Voting** (30 minutes)

**File:** Add to `main.py` or new module

For each vehicle, track plate readings over multiple frames:

```
Vehicle 1 plate readings across frames:
  Frame 10: "3P2I" (score: 0.82)
  Frame 11: "3P2I" (score: 0.85)
  Frame 12: "3225" (score: 0.41) ← Ignore, low score
  Frame 13: "3P2I" (score: 0.80)
  Frame 14: "3P2I" (score: 0.79)

Result: "3P2I" ← Consensus from 4 high-confidence reads
```

### **Step 5: Test & Validate** (20 minutes)

Run your system and compare:

- Before: Chaotic, incorrect plate numbers
- After: Stable, correct, consistent readings

---

## 🔧 SPECIFIC CODE CHANGES NEEDED

### **In `util.py` - read_license_plate() function:**

**Add deskewing:**

```python
def deskew_image(image):
    # Find contours and calculate rotation angle
    # Rotate image to align text horizontally
    pass
```

**Add morphological operations:**

```python
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
```

**Add bilateral filtering:**

```python
filtered = cv2.bilateralFilter(gray, 9, 75, 75)
```

**Improve red channel detection:**

```python
# For red Bhutanese plates
hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
red_mask = cv2.inRange(hsv, (0, 100, 100), (10, 255, 255))
```

### **In `main.py` - Configuration:**

Change:

```python
MIN_PLATE_CONFIDENCE = 0.05  # ❌ Too low
```

To:

```python
MIN_PLATE_CONFIDENCE = 0.4   # ✅ Better
MIN_OCR_CONFIDENCE = 0.5     # ✅ Only confident reads
```

And update detection:

```python
for det in frame_result.boxes.data.tolist():
    x1, y1, x2, y2, conf, cls = det
    if conf > MIN_PLATE_CONFIDENCE:  # ✅ Add confidence check
        if int(cls) in VEHICLES:
            detections.append([x1, y1, x2, y2, conf])
```

### **In `util.py` - Format validation:**

Make stricter:

```python
def license_complies_format(text):
    # Current: Accepts loose formats
    # New: Only accept:
    #   - Starts with BP or BT
    #   - Then digit (0-9)
    #   - Then letter (A-Z)
    #   - Then 4 digits
    # Regex: ^(BP|BT)\d[A-Z]\d{4}$
```

---

## 📊 EXPECTED RESULTS

### **Before Improvements:**

```
Frame 1: Car 1 plate = "3225" (wrong)
Frame 2: Car 1 plate = "322S" (partially right)
Frame 3: Car 1 plate = "????" (unreadable)
Frame 4: Car 1 plate = "3P2I" (maybe right?)
Result: Inconsistent, unreliable data
```

### **After Improvements:**

```
Frame 1: Car 1 plate = "3P2I" (confidence: 0.85) ✅
Frame 2: Car 1 plate = "3P2I" (confidence: 0.82) ✅
Frame 3: Car 1 plate = "3P2I" (confidence: 0.80) ✅
Frame 4: Car 1 plate = "3P2I" (confidence: 0.83) ✅
Result: Consistent, reliable, accurate data
```

---

## 🚀 ESTIMATED TIME & DIFFICULTY

| Task                      | Time         | Difficulty          |
| ------------------------- | ------------ | ------------------- |
| Fix confidence thresholds | 5 min        | ⭐ Easy             |
| Add basic preprocessing   | 20 min       | ⭐⭐ Medium         |
| Add deskewing             | 30 min       | ⭐⭐⭐ Hard         |
| Strict format validation  | 15 min       | ⭐⭐ Medium         |
| Temporal voting           | 30 min       | ⭐⭐⭐ Hard         |
| **TOTAL**                 | **~2 hours** | **⭐⭐⭐ Moderate** |

---

## 💡 KEY INSIGHT

Your system's architecture is **fundamentally sound**. The issue isn't with detection or tracking—it's with **how you process the cropped plate images before reading them**.

By optimizing the preprocessing pipeline for Bhutanese red/yellow license plates, you can expect:

- **OCR accuracy to jump from 40-50% to 85%+**
- **Consistent plate readings across frames**
- **Fewer false positives and garbage reads**

The fixes are mostly in **`util.py` in the `read_license_plate()` function**.
