import os
import subprocess
from static_ffmpeg import run

def optimize_video(input_path, output_path):
    try:
        ffmpeg_bin, _ = run.get_or_fetch_platform_executables_else_raise()
        
        # Build the ffmpeg command
        # -vcodec libx264: H.264 encoding for max browser compatibility
        # -crf 24: Good visual quality, high compression
        # -preset fast: Balance between encoding time and compression
        # -pix_fmt yuv420p: Standard pixel format compatible with all players
        # -acodec aac -b:a 128k: Good audio compression
        # -movflags +faststart: Move metadata to front for faster web playback
        # -vf "scale='min(1080,iw)':-2": Scale width down to max 1080px if larger, keeping aspect ratio and divisible by 2
        cmd = [
            ffmpeg_bin,
            "-y",
            "-i", input_path,
            "-vcodec", "libx264",
            "-crf", "28",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-acodec", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            "-vf", "scale='min(720,iw)':-2",
            output_path
        ]
        
        print(f"Compressing {os.path.basename(input_path)}...")
        orig_size = os.path.getsize(input_path) / (1024 * 1024)
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            new_size = os.path.getsize(output_path) / (1024 * 1024)
            reduction = (1 - (new_size / orig_size)) * 100
            print(f"Successfully optimized {os.path.basename(input_path)}:")
            print(f"  Size: {orig_size:.2f}MB -> {new_size:.2f}MB ({reduction:.1f}% reduction)")
        else:
            print(f"Error compressing {os.path.basename(input_path)}:")
            print(result.stderr)
            
    except Exception as e:
        print(f"Exception during optimization of {input_path}: {e}")

def main():
    ASSETS_DIR = "ASSETS"
    OUTPUT_DIR = "assets-avif"
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory {OUTPUT_DIR}")
        
    print("Starting video optimization...")
    videos = [f for f in os.listdir(ASSETS_DIR) if f.lower().endswith('.mp4')]
    
    if not videos:
        print("No videos found to optimize.")
        return
        
    print(f"Found {len(videos)} videos to optimize: {videos}")
    for video in videos:
        input_path = os.path.join(ASSETS_DIR, video)
        output_path = os.path.join(OUTPUT_DIR, video)
        optimize_video(input_path, output_path)
        
    print("Video optimization completed.")

if __name__ == "__main__":
    main()
