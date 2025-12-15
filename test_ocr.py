"""Test OCR on a static license plate image"""
import cv2
import easyocr
import sys

if len(sys.argv) < 2:
    print("Usage: python test_ocr.py <image_path>")
    print("Example: python test_ocr.py license_plate.jpg")
    sys.exit(1)

image_path = sys.argv[1]

# Initialize OCR reader
reader = easyocr.Reader(['en'], gpu=False)

# Read image
img = cv2.imread(image_path)
if img is None:
    print(f"Error: Could not read image from {image_path}")
    sys.exit(1)

print(f"Image size: {img.shape}")

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Try OCR
print("\n" + "="*50)
print("OCR RESULTS:")
print("="*50)

results = reader.readtext(gray)
for (bbox, text, confidence) in results:
    print(f"Text: '{text}'")
    print(f"Confidence: {confidence:.2f}")
    print(f"Cleaned: '{text.upper().replace(' ', '').replace('-', '')}'")
    print("-"*50)

if not results:
    print("No text detected!")
