import string
import easyocr

# Initialize the OCR reader
reader = easyocr.Reader(['en'], gpu=False)

# Mapping dictionaries for character conversion
dict_char_to_int = {'O': '0',
                    'I': '1',
                    'J': '3',
                    'A': '4',
                    'G': '6',
                    'S': '5'}

dict_int_to_char = {'0': 'O',
                    '1': 'I',
                    '3': 'J',
                    '4': 'A',
                    '6': 'G',
                    '5': 'S'}


def write_csv(results, output_path):
    """
    Write the results to a CSV file.

    Args:
        results (dict): Dictionary containing the results.
        output_path (str): Path to the output CSV file.
    """
    with open(output_path, 'w') as f:
        f.write('{},{},{},{},{},{},{}\n'.format('frame_nmr', 'car_id', 'car_bbox',
                                                'license_plate_bbox', 'license_plate_bbox_score', 'license_number',
                                                'license_number_score'))

        for frame_nmr in results.keys():
            for car_id in results[frame_nmr].keys():
                # Removed print statement to reduce console spam
                if 'car' in results[frame_nmr][car_id].keys() and \
                   'license_plate' in results[frame_nmr][car_id].keys() and \
                   'text' in results[frame_nmr][car_id]['license_plate'].keys():
                    f.write('{},{},{},{},{},{},{}\n'.format(frame_nmr,
                                                            car_id,
                                                            '[{} {} {} {}]'.format(
                                                                results[frame_nmr][car_id]['car']['bbox'][0],
                                                                results[frame_nmr][car_id]['car']['bbox'][1],
                                                                results[frame_nmr][car_id]['car']['bbox'][2],
                                                                results[frame_nmr][car_id]['car']['bbox'][3]),
                                                            '[{} {} {} {}]'.format(
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][0],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][1],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][2],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][3]),
                                                            results[frame_nmr][car_id]['license_plate']['bbox_score'],
                                                            results[frame_nmr][car_id]['license_plate']['text'],
                                                            results[frame_nmr][car_id]['license_plate']['text_score'])
                            )
        f.close()
    
    print(f"\n✅ Results saved to {output_path}")


def license_complies_format(text):
    """
    Check if the license plate text complies with a recognizable format.
    Format: BP-1-C3275 or BT-1-A3269 (Bhutanese common formats)
    Also accepts partial matches for debugging.

    Args:
        text (str): License plate text.

    Returns:
        bool: True if the license plate complies with a recognizable format.
    """
    # Remove dashes and spaces for validation
    text_clean = text.replace('-', '').replace(' ', '')
    
    # At minimum, need some characters
    if len(text_clean) < 3:
        return False
    
    # Check if starts with BP or BT (common Bhutanese prefixes)
    if len(text_clean) >= 2 and text_clean[0:2] in ['BP', 'BT']:
        # BP-1-C3275 format (8 chars: BP + digit + letter + 4 digits)
        if len(text_clean) >= 6:  # Lowered from 8 to accept partial reads
            # Has BP/BT prefix and some numbers
            has_digit = any(c.isdigit() for c in text_clean[2:])
            if has_digit:
                return True
    
    # Accept format with letter and numbers (even without BP/BT prefix)
    has_digit = any(c.isdigit() for c in text_clean)
    has_letter = any(c.isalpha() for c in text_clean)
    
    if has_digit and has_letter and len(text_clean) >= 4:
        return True
    
    # Also accept if it's mostly numbers (could be partial plate read)
    if len(text_clean) >= 4 and sum(c.isdigit() for c in text_clean) >= 3:
        return True
    
    return False


def format_license(text):
    """
    Format the Bhutanese license plate text by cleaning and standardizing it.
    Bhutanese format: BP-X-YNNNN or BT-X-YNNNN
    Example: BP-1-E8413, BT-2-A1234
    Also handles partial reads gracefully.

    Args:
        text (str): License plate text.

    Returns:
        str: Formatted license plate text in BP-X-YNNNN format.
    """
    # Remove spaces and standardize
    text_clean = text.replace(' ', '').upper()
    
    # If it already has dashes, clean it up
    if '-' in text_clean:
        parts = text_clean.split('-')
        text_clean = ''.join(parts)
    
    # Apply character corrections (OCR might misread some characters)
    corrected = ''
    for i, char in enumerate(text_clean):
        # Position-specific corrections for Bhutanese format
        # BP/BT should stay as letters
        if i < 2:
            if char in dict_int_to_char:
                corrected += dict_int_to_char[char]
            else:
                corrected += char
        # Position 2 should be a digit (0-9)
        elif i == 2:
            if char in dict_char_to_int:
                corrected += dict_char_to_int[char]
            else:
                corrected += char
        # Position 3 should be a letter (A-Z)
        elif i == 3:
            if char in dict_int_to_char:
                corrected += dict_int_to_char[char]
            else:
                corrected += char
        # Remaining should be digits
        else:
            if char in dict_char_to_int:
                corrected += dict_char_to_int[char]
            else:
                corrected += char
    
    # Format as BP-X-YNNNN
    if len(corrected) >= 7 and corrected[0:2] in ['BP', 'BT']:
        # BP1E8413 -> BP-1-E8413
        return f"{corrected[0:2]}-{corrected[2]}-{corrected[3:]}"
    elif len(corrected) >= 6:
        # If missing BP/BT prefix, add it
        # 1E8413 -> BP-1-E8413
        return f"BP-{corrected[0]}-{corrected[1:]}"
    elif len(corrected) >= 4:
        # Partial read - format what we have
        # E8413 -> E8413 (keep as is)
        # BP1E -> BP-1-E
        if corrected[0:2] in ['BP', 'BT']:
            if len(corrected) >= 4:
                return f"{corrected[0:2]}-{corrected[2]}-{corrected[3:]}"
            else:
                return corrected
        return corrected
    
    return corrected


def read_license_plate(license_plate_crop):
    """
    Read the license plate text from the given cropped image.

    Args:
        license_plate_crop (PIL.Image.Image): Cropped image containing the license plate.

    Returns:
        tuple: Tuple containing the formatted license plate text and its confidence score.
    """
    
    # Try multiple preprocessing techniques optimized for red/pink Bhutanese plates
    import cv2
    
    # Store all candidates from different preprocessing methods
    all_candidates = []
    
    # Convert to grayscale
    gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
    
    # METHOD 1: Red channel extraction (best for red/pink Bhutanese plates)
    red_channel = license_plate_crop[:, :, 2]  # Extract red channel
    _, red_thresh = cv2.threshold(red_channel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    detections = reader.readtext(red_thresh)
    all_candidates.extend([(d[1], d[2], 'red_channel') for d in detections])
    
    # METHOD 2: Inverted red channel
    red_inverted = cv2.bitwise_not(red_thresh)
    detections = reader.readtext(red_inverted)
    all_candidates.extend([(d[1], d[2], 'red_inverted') for d in detections])
    
    # METHOD 3: High upscaling + CLAHE for better character recognition
    h, w = gray.shape
    upscaled = cv2.resize(gray, (w * 4, h * 4), interpolation=cv2.INTER_CUBIC)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(upscaled)
    detections = reader.readtext(enhanced)
    all_candidates.extend([(d[1], d[2], 'upscaled_clahe') for d in detections])
    
    # METHOD 4: Adaptive threshold on upscaled image
    adaptive = cv2.adaptiveThreshold(upscaled, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
    detections = reader.readtext(adaptive)
    all_candidates.extend([(d[1], d[2], 'adaptive_upscaled') for d in detections])
    
    # METHOD 5: Inverted adaptive threshold
    adaptive_inv = cv2.bitwise_not(adaptive)
    detections = reader.readtext(adaptive_inv)
    all_candidates.extend([(d[1], d[2], 'adaptive_inverted') for d in detections])
    
    # METHOD 6: HSV value channel (good for colored plates)
    hsv = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2HSV)
    value_channel = hsv[:, :, 2]
    value_upscaled = cv2.resize(value_channel, (value_channel.shape[1] * 4, value_channel.shape[0] * 4), 
                                interpolation=cv2.INTER_CUBIC)
    _, value_thresh = cv2.threshold(value_upscaled, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    detections = reader.readtext(value_thresh)
    all_candidates.extend([(d[1], d[2], 'hsv_value') for d in detections])
    
    # Process all candidates and find the best match
    best_match = None
    best_score = 0
    fallback_match = None  # Store any match, even partial
    fallback_score = 0
    
    for text, score, method in all_candidates:
        # Clean the text
        text = text.upper().replace(' ', '').replace('-', '').replace('.', '').replace(',', '')
        text = ''.join(c for c in text if c.isalnum())
        
        # Skip very short text
        if len(text) < 2:
            continue
        
        # Keep track of ANY alphanumeric text as fallback
        if len(text) >= 3 and score > fallback_score:
            has_digit = any(c.isdigit() for c in text)
            has_letter = any(c.isalpha() for c in text)
            if has_digit or has_letter:
                fallback_match = (format_license(text), score)
                fallback_score = score
        
        # Prioritize BP/BT format plates (boost their score)
        if text.startswith('BP') or text.startswith('BT'):
            formatted = format_license(text)
            boosted_score = score * 1.5  # Boost proper Bhutanese format
            if boosted_score > best_score:
                best_match = (formatted, score)
                best_score = boosted_score
        elif license_complies_format(text):
            formatted = format_license(text)
            if score > best_score:
                best_match = (formatted, score)
                best_score = score
    
    # Return best match, or fallback if no proper format found
    if best_match:
        return best_match
    elif fallback_match:
        return fallback_match  # Return partial/incomplete reads
    
    return None, None


def get_car(license_plate, vehicle_track_ids):
    """
    Retrieve the vehicle coordinates and ID based on the license plate coordinates.

    Args:
        license_plate (tuple): Tuple containing the coordinates of the license plate (x1, y1, x2, y2, score, class_id).
        vehicle_track_ids (list): List of vehicle track IDs and their corresponding coordinates.

    Returns:
        tuple: Tuple containing the vehicle coordinates (x1, y1, x2, y2) and ID.
    """
    x1, y1, x2, y2, score, class_id = license_plate

    foundIt = False
    for j in range(len(vehicle_track_ids)):
        xcar1, ycar1, xcar2, ycar2, car_id = vehicle_track_ids[j]

        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
            car_indx = j
            foundIt = True
            break

    if foundIt:
        return vehicle_track_ids[car_indx]

    return -1, -1, -1, -1, -1
