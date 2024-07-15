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
    for video_file in video_files:
        flac_file = os.path.join(output_folder, f'{os.path.splitext(os.path.basename(video_file.name))[0]}.flac')
        with open(video_file.name, 'wb') as f:
            f.write(video_file.getbuffer())
        subprocess.run(['ffmpeg', '-i', video_file.name, flac_file], check=True)
        flac_files.append(flac_file)
    
    print('Conversion completed!')
    return flac_files

def process_flac_files(output_folder='outputs'):
    # Get list of all .flac files in the output directory
    flac_files = [f for f in os.listdir(output_folder) if f.endswith('.flac')]
    
    for flac_file in flac_files:
        flac_path = os.path.join(output_folder, flac_file)
        # Process each FLAC file (you can add your own processing logic here)
        print(f'Processing {flac_path}')
        # Example processing: Print the file name
        # (replace this with actual processing logic)
    
    print('Processing completed!')