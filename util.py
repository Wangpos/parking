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
                print(results[frame_nmr][car_id])
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


def license_complies_format(text):
    """
    Check if the license plate text complies with the Bhutanese format.
    Format: BT-1-A3269 or BT1A3269 (without dashes)

    Args:
        text (str): License plate text.

    Returns:
        bool: True if the license plate complies with the format, False otherwise.
    """
    # Remove dashes and spaces for validation
    text_clean = text.replace('-', '').replace(' ', '')
    
    # Bhutanese format: BT + 1 digit + 1 letter + 4 digits = 8 characters
    if len(text_clean) < 7:  # At minimum BT1A123
        return False
    
    # Check if starts with BT
    if len(text_clean) >= 2 and text_clean[0:2] == 'BT':
        # BT-1-A3269 format (8 chars: BT + digit + letter + 4 digits)
        if len(text_clean) == 8:
            if text_clean[2].isdigit() and \
               text_clean[3] in string.ascii_uppercase and \
               text_clean[4:8].isdigit():
                return True
        # Also accept 7 chars without BT prefix if detected (1-A3269)
        elif len(text_clean) == 7 and text_clean[0].isdigit():
            return True
    # Accept format without BT prefix: 1A3269 or 1-A3269
    elif len(text_clean) >= 6:
        if text_clean[0].isdigit() and \
           text_clean[1] in string.ascii_uppercase and \
           text_clean[2:].isdigit():
            return True
    
    return False


def format_license(text):
    """
    Format the Bhutanese license plate text by cleaning and standardizing it.

    Args:
        text (str): License plate text.

    Returns:
        str: Formatted license plate text (BT-1-A3269 format).
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
        # For the letter position (after BT and digit), convert numbers to letters
        if len(text_clean) >= 4 and i == 3 and char in dict_int_to_char:
            corrected += dict_int_to_char[char]
        # For digit positions, convert letters to numbers
        elif char in dict_char_to_int:
            corrected += dict_char_to_int[char]
        else:
            corrected += char
    
    # Format as BT-1-A3269
    if len(corrected) >= 8 and corrected[0:2] == 'BT':
        return f"BT-{corrected[2]}-{corrected[3:]}"
    elif len(corrected) >= 6:
        # Add BT prefix if missing
        return f"BT-{corrected[0]}-{corrected[1:]}"
    
    return corrected


def read_license_plate(license_plate_crop):
    """
    Read the license plate text from the given cropped image.

    Args:
        license_plate_crop (PIL.Image.Image): Cropped image containing the license plate.

    Returns:
        tuple: Tuple containing the formatted license plate text and its confidence score.
    """
    
    # Try multiple preprocessing techniques
    import cv2
    
    # 1. Original grayscale/threshold (already done in main.py)
    detections = reader.readtext(license_plate_crop)
    
    # 2. If that fails, try with adaptive threshold
    if not detections or all(d[2] < 0.5 for d in detections):
        adaptive_thresh = cv2.adaptiveThreshold(
            license_plate_crop, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        detections = reader.readtext(adaptive_thresh)
    
    # 3. If still fails, try with inverted image
    if not detections or all(d[2] < 0.5 for d in detections):
        inverted = cv2.bitwise_not(license_plate_crop)
        detections = reader.readtext(inverted)
    
    # 4. Try with upscaled image for better OCR
    if not detections or all(d[2] < 0.5 for d in detections):
        height, width = license_plate_crop.shape[:2]
        upscaled = cv2.resize(license_plate_crop, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
        detections = reader.readtext(upscaled)
    
    # Debug: print all detections
    best_match = None
    best_score = 0
    
    for detection in detections:
        bbox, text, score = detection
        print(f"[DEBUG] OCR detected: '{text}' (confidence: {score:.2f})")
        
        text = text.upper().replace(' ', '').replace('-', '')
        print(f"[DEBUG] After cleaning: '{text}'")

        if license_complies_format(text):
            formatted = format_license(text)
            print(f"[DEBUG] ✓ ACCEPTED and formatted as: '{formatted}'")
            if score > best_score:
                best_match = (formatted, score)
                best_score = score
        else:
            # Try partial matching - accept if it contains recognizable patterns
            if len(text) >= 4 and score > 0.3:
                # Check if it has some digit + letter pattern
                has_digit = any(c.isdigit() for c in text)
                has_letter = any(c.isalpha() for c in text)
                if has_digit and has_letter:
                    print(f"[DEBUG] ~ PARTIAL MATCH (score: {score:.2f}) - attempting to use: '{text}'")
                    formatted = format_license(text)
                    if score > best_score:
                        best_match = (formatted, score)
                        best_score = score
                else:
                    print(f"[DEBUG] ✗ REJECTED - does not match Bhutanese format")
            else:
                print(f"[DEBUG] ✗ REJECTED - does not match Bhutanese format")
    
    if best_match:
        return best_match
    
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
