import cv2
import os

video_path = './sample.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print('Error: Could not open video')
else:
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps > 0 else 0
    file_size = os.path.getsize(video_path) / (1024 * 1024)
    
    print('='*50)
    print('VIDEO INFORMATION')
    print('='*50)
    print(f'Resolution: {width}x{height}')
    print(f'FPS: {fps:.2f}')
    print(f'Total Frames: {frame_count}')
    print(f'Duration: {duration:.2f} seconds')
    print(f'File Size: {file_size:.2f} MB')
    print('='*50)
    
    cap.release()
