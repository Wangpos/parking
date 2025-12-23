"""
Quick test of improved OCR on existing plate crops
Run this after you have some plate_crops saved
"""

import cv2
import os
from improved_ocr import read_bhutanese_plate
from util import read_license_plate

def compare_ocr_methods():
    """Compare old vs new OCR on saved plate crops"""
    
    if not os.path.exists('./plate_crops'):
        print("❌ No plate_crops directory found.")
        print("   Run main.py first to collect some plate images.")
        return
    
    plate_files = sorted([f for f in os.listdir('./plate_crops') if f.endswith('.jpg')])
    
    if len(plate_files) == 0:
        print("❌ No plate images found in ./plate_crops/")
        print("   Run main.py first to collect some plate images.")
        return
    
    print("=" * 80)
    print("  OCR COMPARISON: Original vs Improved")
    print("=" * 80)
    print()
    
    improvements = 0
    same = 0
    worse = 0
    
    for i, plate_file in enumerate(plate_files[:20], 1):  # Test first 20
        plate_path = f'./plate_crops/{plate_file}'
        plate_img = cv2.imread(plate_path)
        
        if plate_img is None:
            continue
        
        # Test both methods
        old_text, old_conf = read_license_plate(plate_img)
        new_text, new_conf = read_bhutanese_plate(plate_img, save_debug=(i<=3))  # Debug first 3
        
        print(f"{i}. {plate_file}")
        print(f"   Original OCR: '{old_text}' (conf: {old_conf:.2f if old_conf else 0:.2f})")
        print(f"   Improved OCR: '{new_text}' (conf: {new_conf:.2f if new_conf else 0:.2f})")
        
        # Compare
        if new_text and old_text:
            if len(new_text) > len(old_text):
                print(f"   ✅ IMPROVED - Longer/more complete read")
                improvements += 1
            elif new_text == old_text:
                print(f"   = SAME")
                same += 1
            else:
                print(f"   ⚠️  DIFFERENT")
                worse += 1
        elif new_text and not old_text:
            print(f"   ✅ IMPROVED - New method found text")
            improvements += 1
        elif old_text and not new_text:
            print(f"   ⚠️  WORSE - New method missed text")
            worse += 1
        else:
            print(f"   - NEITHER found text")
        
        print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Improvements: {improvements}")
    print(f"Same results: {same}")
    print(f"Different: {worse}")
    print(f"Success rate: {(improvements + same) / (improvements + same + worse) * 100:.1f}%" if (improvements + same + worse) > 0 else "N/A")
    print()
    
    if improvements > 0:
        print("✅ The improved OCR shows better results!")
    elif same > worse:
        print("= The improved OCR performs similarly")
    else:
        print("⚠️  May need more tuning")
    
    print("\nDebug images saved to: ./debug_ocr/ (for first 3 plates)")

if __name__ == "__main__":
    compare_ocr_methods()
