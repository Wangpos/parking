"""Test OCR on a static license plate image with multiple preprocessing techniques"""
import cv2
import easyocr
import sys
import numpy as np

def preprocess_image(img):
    """Apply multiple preprocessing techniques for better OCR"""
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 1. Upscale for better OCR
    h, w = gray.shape
    upscaled = cv2.resize(gray, (w * 3, h * 3), interpolation=cv2.INTER_CUBIC)
    
    # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(upscaled)
    
    # 3. Bilateral filter (reduce noise, keep edges)
    denoised = cv2.bilateralFilter(enhanced, 11, 17, 17)
    
    # 4. Adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    
    # 5. Morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # 6. Inverted version
    inverted = cv2.bitwise_not(morph)
    
    return {
        'Original Grayscale': gray,
        'Upscaled': upscaled,
        'CLAHE Enhanced': enhanced,
        'Denoised': denoised,
        'Adaptive Threshold': thresh,
        'Morphological': morph,
        'Inverted': inverted
    }

if len(sys.argv) < 2:
    print("Usage: python test_ocr.py <image_path>")
    print("Example: python test_ocr.py license_plate.jpg")
    sys.exit(1)

image_path = sys.argv[1]

# Initialize OCR reader
print("Initializing OCR reader...")
reader = easyocr.Reader(['en'], gpu=False)
print("✓ OCR ready\n")

# Read image
img = cv2.imread(image_path)
if img is None:
    print(f"❌ Error: Could not read image from {image_path}")
    sys.exit(1)

print(f"Image size: {img.shape}\n")

# Preprocess image
processed_images = preprocess_image(img)

print("="*60)
print("OCR RESULTS WITH DIFFERENT PREPROCESSING")
print("="*60)

all_results = []

# Try OCR on all preprocessed versions
for method_name, processed_img in processed_images.items():
    print(f"\n--- {method_name} ---")
    
    try:
        results = reader.readtext(processed_img, allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-')
        
        if results:
            for (bbox, text, confidence) in results:
                cleaned = text.upper().replace(' ', '').replace('-', '').replace('.', '')
                cleaned = ''.join(c for c in cleaned if c.isalnum())
                
                print(f"  Text: '{text}'")
                print(f"  Cleaned: '{cleaned}'")
                print(f"  Confidence: {confidence:.3f}")
                
                all_results.append({
                    'text': text,
                    'cleaned': cleaned,
                    'confidence': confidence,
                    'method': method_name
                })
        else:
            print("  No text detected")
    except Exception as e:
        print(f"  Error: {e}")

if all_results:
    # Find best result
    best = max(all_results, key=lambda x: x['confidence'])
    
    print("\n" + "="*60)
    print("BEST RESULT:")
    print("="*60)
    print(f"Text: '{best['text']}'")
    print(f"Cleaned: '{best['cleaned']}'")
    print(f"Confidence: {best['confidence']:.3f}")
    print(f"Method: {best['method']}")
    print("="*60)
    
    # Show all unique texts found
    unique_texts = {}
    for r in all_results:
        if r['cleaned'] not in unique_texts or r['confidence'] > unique_texts[r['cleaned']]['confidence']:
            unique_texts[r['cleaned']] = r
    
    if len(unique_texts) > 1:
        print("\nAll unique texts found:")
        for cleaned, data in sorted(unique_texts.items(), key=lambda x: x[1]['confidence'], reverse=True):
            print(f"  '{cleaned}' (conf: {data['confidence']:.3f}, method: {data['method']})")
else:
    print("\n❌ No text detected in any preprocessing method!")

# Display images
print("\nDisplaying processed images... Press any key to close.")
cv2.imshow('Original', img)
for i, (name, img_proc) in enumerate(processed_images.items()):
    cv2.imshow(name, img_proc)

cv2.waitKey(0)
cv2.destroyAllWindows()
