import os
import cv2
from PIL import Image
import pillow_avif

ASSETS_DIR = "assets"
HAIR_DIR = os.path.join(ASSETS_DIR, "hair")
MAX_SIZE = 1600
QUALITY = 65

def optimize_image(filepath, output_path):
    try:
        with Image.open(filepath) as img:
            # Convert RGBA/P to RGB for AVIF compatibility if needed
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img = img.convert('RGBA')
            elif img.mode != 'RGB':
                img = img.convert('RGB')
                
            # Resize if too large
            w, h = img.size
            if max(w, h) > MAX_SIZE:
                if w > h:
                    new_w = MAX_SIZE
                    new_h = int(h * (MAX_SIZE / w))
                else:
                    new_h = MAX_SIZE
                    new_w = int(w * (MAX_SIZE / h))
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                print(f"Resized {os.path.basename(filepath)} from {w}x{h} to {new_w}x{new_h}")
                
            img.save(output_path, "AVIF", quality=QUALITY)
            orig_size = os.path.getsize(filepath) / 1024
            new_size = os.path.getsize(output_path) / 1024
            print(f"Optimized {os.path.basename(filepath)}: {orig_size:.1f}KB -> {new_size:.1f}KB ({new_size/orig_size*100:.1f}%)")
    except Exception as e:
        print(f"Error optimizing image {filepath}: {e}")

def extract_video_poster(video_path, output_path):
    try:
        cap = cv2.VideoCapture(video_path)
        success, frame = cap.read()
        if success:
            # OpenCV loads frame in BGR, convert to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            # Resize if too large
            w, h = img.size
            if max(w, h) > MAX_SIZE:
                if w > h:
                    new_w = MAX_SIZE
                    new_h = int(h * (MAX_SIZE / w))
                else:
                    new_h = MAX_SIZE
                    new_w = int(w * (MAX_SIZE / h))
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
            img.save(output_path, "AVIF", quality=QUALITY)
            new_size = os.path.getsize(output_path) / 1024
            print(f"Extracted poster from {os.path.basename(video_path)} -> {os.path.basename(output_path)} ({new_size:.1f}KB)")
        else:
            print(f"Failed to read first frame from {video_path}")
        cap.release()
    except Exception as e:
        print(f"Error extracting video poster {video_path}: {e}")

def main():
    print("Starting assets optimization to AVIF...")
    
    # 1. Optimize Bridal & Glam images in assets/
    for file in os.listdir(ASSETS_DIR):
        ext = os.path.splitext(file)[1].lower()
        if ext in ('.jpg', '.jpeg', '.png') and not file.endswith('_poster.png') and not file.endswith('_poster.jpg'):
            fp = os.path.join(ASSETS_DIR, file)
            out_name = os.path.splitext(file)[0] + ".avif"
            out_fp = os.path.join(ASSETS_DIR, out_name)
            optimize_image(fp, out_fp)
            
    # 2. Optimize Hair images in assets/hair/
    if os.path.exists(HAIR_DIR):
        for file in os.listdir(HAIR_DIR):
            ext = os.path.splitext(file)[1].lower()
            if ext in ('.jpg', '.jpeg', '.png'):
                fp = os.path.join(HAIR_DIR, file)
                out_name = os.path.splitext(file)[0] + ".avif"
                out_fp = os.path.join(HAIR_DIR, out_name)
                optimize_image(fp, out_fp)
                
    # 3. Extract first frame from all videos in assets/ to create posters
    for file in os.listdir(ASSETS_DIR):
        ext = os.path.splitext(file)[1].lower()
        if ext == '.mp4':
            fp = os.path.join(ASSETS_DIR, file)
            out_name = os.path.splitext(file)[0] + "_poster.avif"
            out_fp = os.path.join(ASSETS_DIR, out_name)
            extract_video_poster(fp, out_fp)
            
    print("Assets optimization completed successfully!")

if __name__ == "__main__":
    main()
