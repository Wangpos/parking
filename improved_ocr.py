"""
Improved OCR Preprocessing for Bhutanese License Plates
Optimized for red/pink plates with white text and Dzongkha script
"""

import cv2
import numpy as np
import easyocr

reader = easyocr.Reader(['en'], gpu=False)

def preprocess_bhutanese_plate(plate_crop):
    """
    Specialized preprocessing for Bhutanese license plates
    Optimized for red/pink/yellow backgrounds with white/black text
    """
    
    # Step 1: Upscale the image (very important for small plates!)
    scale_factor = 4
    h, w = plate_crop.shape[:2]
    
    # Ensure minimum size
    if h < 100:
        scale_factor = max(4, 100 // h)
    
    plate_large = cv2.resize(plate_crop, (w * scale_factor, h * scale_factor), 
                             interpolation=cv2.INTER_CUBIC)
    
    # Step 2: Extract color channels (Bhutanese plates have distinct colors)
    b, g, r = cv2.split(plate_large)
    
    # Step 3: Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    
    # Step 4: Create multiple preprocessing variations
    preprocessed_images = []
    
    # Method 1: Red channel (best for red/pink plates with white text)
    red_enhanced = clahe.apply(r)
    _, red_binary = cv2.threshold(red_enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    preprocessed_images.append(('red_binary', red_binary))
    
    # Method 2: Inverted red channel (for white text on red background)
    red_inverted = cv2.bitwise_not(red_binary)
    preprocessed_images.append(('red_inverted', red_inverted))
    
    # Method 3: Grayscale with adaptive threshold
    gray = cv2.cvtColor(plate_large, cv2.COLOR_BGR2GRAY)
    gray_enhanced = clahe.apply(gray)
    adaptive = cv2.adaptiveThreshold(gray_enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 11, 2)
    preprocessed_images.append(('adaptive', adaptive))
    
    # Method 4: Morphological operations to connect broken characters
    kernel = np.ones((2, 2), np.uint8)
    morphed = cv2.morphologyEx(adaptive, cv2.MORPH_CLOSE, kernel)
    preprocessed_images.append(('morphed', morphed))
    
    # Method 5: Edge enhancement (helps with faded plates)
    edges = cv2.Canny(gray_enhanced, 50, 150)
    edges_dilated = cv2.dilate(edges, kernel, iterations=1)
    combined = cv2.bitwise_or(gray_enhanced, edges_dilated)
    preprocessed_images.append(('edge_enhanced', combined))
    
    return preprocessed_images

def read_bhutanese_plate(plate_crop, save_debug=False, frame_num=0, vehicle_id=0):
    """
    Read Bhutanese license plate with improved accuracy
    
    Args:
        plate_crop: Cropped license plate image
        save_debug: Save preprocessing steps for debugging
        frame_num: Frame number (for debug filename)
        vehicle_id: Vehicle ID (for debug filename)
    
    Returns:
        (text, confidence) or (None, None)
    """
    
    if plate_crop is None or plate_crop.size == 0:
        return None, None
    
    # Get preprocessed images
    preprocessed_images = preprocess_bhutanese_plate(plate_crop)
    
    # Debug: Save preprocessing steps
    if save_debug:
        import os
        debug_dir = './debug_ocr'
        os.makedirs(debug_dir, exist_ok=True)
        
        cv2.imwrite(f"{debug_dir}/original_f{frame_num}_v{vehicle_id}.jpg", plate_crop)
        for method_name, img in preprocessed_images:
            cv2.imwrite(f"{debug_dir}/{method_name}_f{frame_num}_v{vehicle_id}.jpg", img)
    
    # Collect all OCR results
    all_results = []
    
    for method_name, preprocessed in preprocessed_images:
        # Run EasyOCR
        detections = reader.readtext(preprocessed, detail=1, paragraph=False)
        
        for detection in detections:
            bbox, text, conf = detection
            
            # Clean text
            text_clean = text.upper().replace(' ', '').replace('-', '')
            text_clean = ''.join(c for c in text_clean if c.isalnum())
            
            if len(text_clean) >= 2:
                all_results.append({
                    'text': text_clean,
                    'confidence': conf,
                    'method': method_name,
                    'length': len(text_clean)
                })
    
    if not all_results:
        return None, None
    
    # Scoring system for best result
    def score_result(result):
        text = result['text']
        conf = result['confidence']
        
        score = conf * 100  # Base score
        
        # Bonus for proper Bhutanese format
        if text.startswith('BP') or text.startswith('BT') or text.startswith('BG'):
            score += 50
        
        # Bonus for correct length (BP-1-E8443 = 9 chars without dashes)
        if 7 <= len(text) <= 9:
            score += 30
        
        # Bonus for mixed alphanumeric (proper plates have both)
        has_letters = any(c.isalpha() for c in text)
        has_digits = any(c.isdigit() for c in text)
        if has_letters and has_digits:
            score += 20
        
        # Penalty for very short text
        if len(text) < 4:
            score -= 30
        
        return score
    
    # Sort by score
    all_results.sort(key=score_result, reverse=True)
    
    # Get best result
    best = all_results[0]
    
    # Format the text
    formatted_text = format_bhutanese_plate(best['text'])
    
    return formatted_text, best['confidence']

def format_bhutanese_plate(text):
    """
    Format text to Bhutanese plate format: BP-X-YNNNN
    
    Examples:
        BP1E8443 -> BP-1-E8443
        BT2A1234 -> BT-2-A1234
        4E8443 -> BP-4-E8443 (add prefix)
    """
    
    # Character corrections for common OCR mistakes
    corrections = {
        # Numbers that look like letters
        'O': '0', 'o': '0',
        'I': '1', 'l': '1', 'i': '1',
        'Z': '2', 'z': '2',
        'S': '5', 's': '5',
        'G': '6', 'g': '6',
        'T': '7',  # Sometimes T is misread as 7
        'B': '8',
    }
    
    # Position-specific corrections
    corrected = ''
    for i, char in enumerate(text):
        if i < 2:  # First 2 chars should be letters (BP/BT/BG)
            if char.isdigit():
                # Number where letter should be - try to correct
                reverse_map = {'8': 'B', '6': 'G', '7': 'T', '5': 'S', '0': 'O'}
                corrected += reverse_map.get(char, char)
            else:
                corrected += char.upper()
        elif i == 2:  # Third char should be digit (region)
            if char.isalpha() and char.upper() in corrections:
                corrected += corrections[char.upper()]
            else:
                corrected += char
        elif i == 3:  # Fourth char should be letter (series)
            if char.isdigit():
                reverse_map = {'0': 'O', '1': 'I', '3': 'E', '4': 'A', '8': 'B'}
                corrected += reverse_map.get(char, char)
            else:
                corrected += char.upper()
        else:  # Remaining should be digits
            if char.isalpha() and char.upper() in corrections:
                corrected += corrections[char.upper()]
            else:
                corrected += char
    
    # Add prefix if missing
    if not corrected.startswith(('BP', 'BT', 'BG')):
        if len(corrected) >= 5:
            corrected = 'BP' + corrected
        else:
            return corrected  # Too short, return as-is
    
    # Format with dashes: BP-X-YNNNN
    if len(corrected) >= 7:
        prefix = corrected[0:2]   # BP
        region = corrected[2:3]   # 1
        series = corrected[3:]    # E8443
        return f"{prefix}-{region}-{series}"
    
    return corrected

# Test function
def test_ocr_improvements():
    """Test the improved OCR on sample plates"""
    import os
    
    # Test on saved plate crops
    if os.path.exists('./plate_crops'):
        plate_files = [f for f in os.listdir('./plate_crops') if f.endswith('.jpg')]
        
        print("Testing improved OCR on saved plates:\n")
        
        for plate_file in plate_files[:10]:  # Test first 10
            plate_path = f'./plate_crops/{plate_file}'
            plate_img = cv2.imread(plate_path)
            
            text, conf = read_bhutanese_plate(plate_img, save_debug=True)
            
            print(f"Plate: {plate_file}")
            print(f"  Read: {text} (confidence: {conf:.2f})")
            print()
    else:
        print("No plate_crops directory found. Run main.py first to collect some plates.")

if __name__ == "__main__":
    test_ocr_improvements()
