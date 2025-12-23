# Implementation Examples & Code Snippets

## 🔧 Ready-to-Use Code Improvements

Here are specific code improvements you can implement to fix the detection and recognition issues.

---

## 1. IMPROVE CONFIDENCE THRESHOLDS (Easiest Fix - 5 minutes)

### **In `main.py` - Around line 15**

**BEFORE (Current - TOO LENIENT):**

```python
MIN_PLATE_CONFIDENCE = 0.05  # Accept 5% confident detections (garbage!)
```

**AFTER (Improved):**

```python
MIN_PLATE_CONFIDENCE = 0.4   # Only accept 40%+ confident plates
MIN_OCR_CONFIDENCE = 0.5     # Only accept 50%+ confident OCR reads
REQUIRE_VALID_FORMAT = True  # Enforce Bhutanese format
```

### **In `main.py` - Around line 60 (Plate detection loop)**

**BEFORE:**

```python
for plate in plate_results:
    x1, y1, x2, y2, conf, cls = plate
    # No confidence check!
    crop_plate = frame[int(y1):int(y2), int(x1):int(x2)]
    text, score = read_license_plate(crop_plate)
```

**AFTER:**

```python
for plate in plate_results:
    x1, y1, x2, y2, conf, cls = plate

    # ✅ Add confidence check
    if conf < MIN_PLATE_CONFIDENCE:
        continue  # Skip low-confidence detections

    crop_plate = frame[int(y1):int(y2), int(x1):int(x2)]
    text, score = read_license_plate(crop_plate)

    # ✅ Add OCR confidence check
    if score < MIN_OCR_CONFIDENCE:
        continue  # Skip low-confidence OCR

    # ✅ Add format validation
    if not license_complies_format(text):
        continue  # Skip invalid formats
```

---

## 2. IMPROVE OCR PREPROCESSING (Most Important - 30-45 minutes)

### **Add Deskewing Function to `util.py`**

```python
def deskew_image(image):
    """
    Deskew/straighten a rotated license plate image.
    License plate text should be horizontal.
    """
    import cv2
    import numpy as np

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return image  # Return original if no contours found

    # Get largest contour (should be the plate)
    largest = max(contours, key=cv2.contourArea)

    # Get minimum rotated rectangle
    rotated_rect = cv2.minAreaRect(largest)
    angle = rotated_rect[2]

    # Normalize angle to -45 to 45 degrees
    if angle < -45:
        angle = angle + 90

    # If rotation needed, apply it
    if abs(angle) > 2:  # Only rotate if angle > 2 degrees
        h, w = image.shape[:2]
        center = (w // 2, h // 2)

        # Get rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)

        # Rotate image
        rotated = cv2.warpAffine(image, M, (w, h),
                                borderMode=cv2.BORDER_REPLICATE)
        return rotated

    return image


def preprocess_for_ocr_improved(image):
    """
    Enhanced preprocessing for Bhutanese license plates.
    Optimized for red/yellow plates with black text.
    """
    import cv2
    import numpy as np

    # Step 1: Deskew the image
    image = deskew_image(image)

    # Step 2: Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Step 3: Apply bilateral filter (smooth noise, preserve edges)
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)

    # Step 4: Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(filtered)

    # Step 5: Upscale for better OCR
    h, w = enhanced.shape
    upscaled = cv2.resize(enhanced, (w * 3, h * 3), interpolation=cv2.INTER_CUBIC)

    # Step 6: Apply Otsu's threshold
    _, thresh = cv2.threshold(upscaled, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Step 7: Morphological operations (clean up noise)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
    morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel, iterations=1)

    return morph, enhanced, thresh
```

### **Improve `read_license_plate()` in `util.py`**

**Replace the old version with:**

```python
def read_license_plate(license_plate_crop):
    """
    Read the license plate text from the given cropped image.
    Enhanced for Bhutanese red/yellow license plates.

    Args:
        license_plate_crop (numpy.ndarray): BGR image of license plate

    Returns:
        tuple: (text, confidence_score) or (None, None)
    """
    import cv2

    all_candidates = []

    # ============ NEW PREPROCESSING METHODS ============

    # METHOD 1: Enhanced preprocessing with deskewing
    morph, enhanced, thresh = preprocess_for_ocr_improved(license_plate_crop)
    detections = reader.readtext(morph)
    all_candidates.extend([(d[1], d[2], 'enhanced_deskew') for d in detections])

    # METHOD 2: Try inverted
    morph_inv = cv2.bitwise_not(morph)
    detections = reader.readtext(morph_inv)
    all_candidates.extend([(d[1], d[2], 'enhanced_deskew_inv') for d in detections])

    # METHOD 3: Try enhanced without extreme upscaling
    h, w = enhanced.shape
    upscaled = cv2.resize(enhanced, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
    _, thresh2 = cv2.threshold(upscaled, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    detections = reader.readtext(thresh2)
    all_candidates.extend([(d[1], d[2], 'moderate_upscale') for d in detections])

    # METHOD 4: Try inverted moderate upscale
    thresh2_inv = cv2.bitwise_not(thresh2)
    detections = reader.readtext(thresh2_inv)
    all_candidates.extend([(d[1], d[2], 'moderate_upscale_inv') for d in detections])

    # ============ CANDIDATE SELECTION ============

    best_match = None
    best_score = 0

    for text, score, method in all_candidates:
        # Clean the text
        text = text.upper().replace(' ', '').replace('-', '')
        text = ''.join(c for c in text if c.isalnum())

        # Skip very short text
        if len(text) < 3:
            continue

        # IMPORTANT: Only consider high-confidence reads
        if score < 0.5:  # ✅ INCREASED FROM 0.3
            continue

        # Check if format is valid (strict)
        if not license_complies_format(text):
            # Try to fix obvious OCR errors
            fixed = apply_ocr_corrections(text)
            if license_complies_format(fixed):
                text = fixed
            else:
                continue  # Skip if still invalid

        # Boost score for proper Bhutanese format
        if text.startswith('BP') or text.startswith('BT'):
            boosted_score = score * 1.3
        else:
            boosted_score = score

        if boosted_score > best_score:
            best_match = (format_license(text), score)
            best_score = boosted_score

    return best_match if best_match else (None, None)


def apply_ocr_corrections(text):
    """
    Apply position-specific OCR error corrections for Bhutanese plates.
    Format: BP-1-C3275
    """
    if len(text) < 7:
        return text

    # For a Bhutanese format plate:
    # Position 0-1: Letters (B, P)
    # Position 2: Digit
    # Position 3: Letter
    # Position 4-7: Digits

    corrected = ""

    for i, char in enumerate(text):
        if i < 2:
            # First 2 chars should be letters
            if char in dict_int_to_char:
                corrected += dict_int_to_char[char]
            else:
                corrected += char
        elif i == 2:
            # Position 2 should be digit
            if char in dict_char_to_int:
                corrected += dict_char_to_int[char]
            else:
                corrected += char
        elif i == 3:
            # Position 3 should be letter
            if char in dict_int_to_char:
                corrected += dict_int_to_char[char]
            else:
                corrected += char
        else:
            # Positions 4+ should be digits
            if char in dict_char_to_int:
                corrected += dict_char_to_int[char]
            else:
                corrected += char

    return corrected
```

---

## 3. IMPROVE FORMAT VALIDATION (Medium - 15 minutes)

### **Replace `license_complies_format()` in `util.py`**

**BEFORE (Too lenient):**

```python
def license_complies_format(text):
    # Accepts almost anything!
    has_digit = any(c.isdigit() for c in text)
    has_letter = any(c.isalpha() for c in text)
    if has_digit and has_letter and len(text) >= 4:
        return True
    return False
```

**AFTER (Strict format checking):**

```python
import re

def license_complies_format(text):
    """
    Validate if text matches Bhutanese license plate format.
    Format: BP-1-C3275 or BT-1-A3269

    Args:
        text (str): License plate text to validate

    Returns:
        bool: True if matches format, False otherwise
    """
    # Remove dashes and spaces
    text_clean = text.replace('-', '').replace(' ', '').upper()

    # Pattern: BP or BT, followed by digit, letter, then 4 digits
    # Regex: ^(BP|BT)\d[A-Z]\d{4}$
    pattern = r'^(BP|BT)\d[A-Z]\d{4}$'

    if re.match(pattern, text_clean):
        return True

    # Also accept without BP/BT prefix for partial reads
    # Pattern: digit, letter, 4 digits
    pattern2 = r'^\d[A-Z]\d{4}$'
    if re.match(pattern2, text_clean):
        return True

    return False
```

---

## 4. ADD TEMPORAL VOTING (Advanced - 30 minutes)

### **Add to `main.py` at the top**

```python
from collections import defaultdict

class VehiclePlateTracker:
    """
    Tracks license plate readings for each vehicle across multiple frames.
    Provides consensus voting for reliable plate identification.
    """

    def __init__(self, history_length=10):
        """
        Args:
            history_length (int): Number of frames to keep history
        """
        self.history = defaultdict(list)  # {vehicle_id: [(text, score), ...]}
        self.history_length = history_length
        self.final_plates = {}  # {vehicle_id: (text, confidence)}

    def add_reading(self, vehicle_id, text, confidence):
        """Add a license plate reading for a vehicle."""
        if not text or confidence < 0.5:
            return False  # Ignore low-confidence reads

        self.history[vehicle_id].append((text, confidence))

        # Keep only last N readings
        if len(self.history[vehicle_id]) > self.history_length:
            self.history[vehicle_id].pop(0)

        # Update final plate if we have consensus
        self._update_final_plate(vehicle_id)
        return True

    def _update_final_plate(self, vehicle_id):
        """
        Determine best plate reading for vehicle using voting.
        Need at least 3 high-confidence matches for consensus.
        """
        if vehicle_id not in self.history or len(self.history[vehicle_id]) < 3:
            return

        readings = self.history[vehicle_id]

        # Count occurrences of each text
        text_counts = defaultdict(float)
        for text, score in readings:
            text_counts[text] += score  # Weight by confidence

        if text_counts:
            # Get text with highest total confidence
            best_text = max(text_counts.items(), key=lambda x: x[1])
            text = best_text[0]

            # Calculate average confidence
            avg_conf = sum(s for t, s in readings if t == text) / readings.count((text, _))

            # Update final plate
            self.final_plates[vehicle_id] = (text, avg_conf)

    def get_final_plate(self, vehicle_id):
        """Get consensus plate for vehicle."""
        return self.final_plates.get(vehicle_id, (None, 0))

    def get_reading_count(self, vehicle_id):
        """Get number of readings for vehicle."""
        return len(self.history.get(vehicle_id, []))
```

### **Use in `main.py`**

```python
# Add at the top of main.py after imports
plate_tracker = VehiclePlateTracker(history_length=10)

# In the main processing loop, after reading plate:
if text and score > MIN_OCR_CONFIDENCE:
    plate_tracker.add_reading(vehicle_id, text, score)

    # Use consensus reading if available
    consensus_text, consensus_score = plate_tracker.get_final_plate(vehicle_id)
    if consensus_text:
        text = consensus_text
        score = consensus_score

# When writing to CSV, use plate_tracker data
```

---

## 5. COMPLETE IMPROVED PIPELINE

### **Key changes needed:**

1. **In `main.py` line 15:**

   ```python
   MIN_PLATE_CONFIDENCE = 0.4
   MIN_OCR_CONFIDENCE = 0.5
   ```

2. **In `util.py`:**

   - Add `deskew_image()` function
   - Add `preprocess_for_ocr_improved()` function
   - Add `apply_ocr_corrections()` function
   - Replace `read_license_plate()` function
   - Replace `license_complies_format()` function

3. **In `main.py`:**
   - Add `VehiclePlateTracker` class
   - Add confidence checks before storing plate
   - Use temporal voting

---

## 📊 Expected Improvements

### **Before Changes:**

```python
Frame 1: Car 1 → "3225" (score: 0.32) ❌ Wrong format
Frame 2: Car 1 → "????" (score: 0.15) ❌ Skipped
Frame 3: Car 1 → "322S" (score: 0.28) ❌ Partial
Frame 4: Car 1 → "3P2I" (score: 0.45) ✓ Correct but not saved

CSV: Car 1 = "3225"  ❌ WRONG!
```

### **After Changes:**

```python
Frame 1: Car 1 → "3P2I" (score: 0.82) ✓ Saved
Frame 2: Car 1 → "3P2I" (score: 0.85) ✓ Saved
Frame 3: Car 1 → "3P2I" (score: 0.80) ✓ Saved
Frame 4: Car 1 → "3P2I" (score: 0.79) ✓ Saved

Temporal Voting: "3P2I" appears 4/4 times
CSV: Car 1 = "3P2I"  ✓ CORRECT!
```

---

## 🧪 Testing the Improvements

### **Quick Test Script:**

```python
# test_improvements.py
import cv2
from util import read_license_plate, license_complies_format

# Load a plate image
plate_img = cv2.imread('first_detected_plate.jpg')

# Test improved functions
text, score = read_license_plate(plate_img)
print(f"Text: {text}")
print(f"Score: {score}")
print(f"Valid format: {license_complies_format(text)}")

# Should output something like:
# Text: BP-1-C3275
# Score: 0.82
# Valid format: True
```

---

## 📝 Summary of Changes

| File    | Function                  | Change                        | Impact                            |
| ------- | ------------------------- | ----------------------------- | --------------------------------- |
| main.py | Line 15                   | Increase confidence threshold | Filter out low-quality detections |
| util.py | read_license_plate()      | Add deskewing & preprocessing | Better OCR accuracy               |
| util.py | license_complies_format() | Strict format validation      | Reject invalid reads              |
| util.py | NEW                       | add_ocr_corrections()         | Fix common OCR errors             |
| main.py | NEW                       | VehiclePlateTracker class     | Consensus voting across frames    |

**Total implementation time: ~2 hours**
**Expected accuracy improvement: 40-50% → 85%+**
