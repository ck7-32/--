import os
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import moviepy.editor as mp
from tkinter import filedialog

def split_video_to_shots(video_path, output_dir, threshold=30.0):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    from scenedetect import VideoManager, SceneManager
    from scenedetect.detectors import ContentDetector

    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    
    video_manager.set_downscale_factor()
    video_manager.start()
    
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list()
    
    for i, scene in enumerate(scene_list):
        start_time, end_time = scene
        start_frame = start_time.get_frames()
        end_frame = end_time.get_frames()
        
        shot_filename = f"{output_dir}/shot_{i+1:03d}.mp4"
        start_sec = start_frame / video_manager.get_framerate()
        end_sec = end_frame / video_manager.get_framerate()
        ffmpeg_extract_subclip(video_path, start_sec, end_sec, targetname=shot_filename)
    
    video_manager.release()

def convert_shots_to_gif(input_dir, output_dir, fps=5, resize_factor=0.5):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for shot_file in os.listdir(input_dir):
        if shot_file.endswith('.mp4'):
            clip = mp.VideoFileClip(os.path.join(input_dir, shot_file))
            clip = clip.resize(resize_factor)
            gif_filename = os.path.join(output_dir, shot_file.replace('.mp4', '.gif'))
            clip.write_gif(gif_filename, fps=fps)

def generate_markdown(gif_dir, output_md):
    gifs = [f for f in os.listdir(gif_dir) if f.endswith('.gif')]
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write("# GIF Collection\n\n")
        f.write("| No. | Checked | GIF | Description |\n")
        f.write("| --- | ------- | --- | ----------- |\n")
        for i, gif in enumerate(gifs, start=1):
            gif_path = os.path.join(gif_dir, gif)
            gif_path = gif_path.replace('\\', '/')
            file_number = str(i).zfill(2)
            new_filename = f"gif_{file_number}.gif"  
            os.rename(os.path.join(gif_dir, gif), os.path.join(gif_dir, new_filename))
            f.write(f"| {file_number} | [ ] | ![{new_filename}]({new_filename})| {' ' * 50}Description for {gif} |\n")


video_path = filedialog.askopenfilename()
filename=os.path.splitext(os.path.basename(video_path))[0]
output_dir_shots = f'shots/{filename}/'
output_dir_gifs = f'gifs/{filename}/'
output_md = f'{filename}.md'
threshold = 35.0  

split_video_to_shots(video_path, output_dir_shots, threshold)
convert_shots_to_gif(output_dir_shots, output_dir_gifs)
generate_markdown(output_dir_gifs, output_md)

