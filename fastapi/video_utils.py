import os
import subprocess
import shutil
import streamlit as st

def delete_output_dirs():
    if os.path.exists("outputs"):
        shutil.rmtree("outputs")
    st.success("output directories have been deleted.")



def convert_videos_to_flac(video_files, output_folder='outputs'):
    # Create the output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # List to store the paths of converted FLAC files
    flac_files = []
    
    # Loop through all video files and convert them to .flac
    for i, video_file in enumerate(video_files):
        video_file_path = os.path.join(output_folder, f"video_{i}.mp4")
        flac_file = os.path.join(output_folder, f"video_{i}.flac")
        
        # Write the video file to a temporary location
        with open(video_file_path, 'wb') as f:
            f.write(video_file.read())
        
        # Convert the video file to FLAC
        subprocess.run(['ffmpeg', '-i', video_file_path, flac_file], check=True)
        flac_files.append(flac_file)
        
        # Clean up the temporary video file
        os.remove(video_file_path)
    
    print('Conversion completed!')
    return flac_files

def process_flac_files(output_folder='outputs'):
    # Get list of all .flac files in the output directory
    flac_files = [f for f in os.listdir(output_folder) if f.endswith('.flac')]
    
    for flac_file in flac_files:
        flac_path = os.path.join(output_folder, flac_file)
        print(f'Processing {flac_path}')
    
    print('Processing completed!')