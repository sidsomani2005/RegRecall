#contains various utils
import os
import shutil
from math import ceil

def segment_data(data_dir: str, segmented_data_dir: str, n : int) -> None:
    '''
    Segment data files in a directory into num_segments separate directories for easier loading
    '''

    # Ensure the source directory exists
    if not os.path.exists(data_dir):
        raise ValueError(f"The source directory {data_dir} does not exist.")
    
    # Ensure the destination directory exists, if not, create it
    if not os.path.exists(segmented_data_dir):
        os.makedirs(segmented_data_dir)
    
    # List all files in the source directory
    files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    
    # Calculate the number of files per subfolder
    files_per_subfolder = ceil(len(files) / n)
    
    # Split files into n subfolders
    for i in range(n):
        # Define the subfolder path
        subfolder_path = os.path.join(segmented_data_dir, f'subfolder_{i+1}')
        os.makedirs(subfolder_path, exist_ok=True)
        
        # Get a slice of files for the current subfolder
        start_index = i * files_per_subfolder
        end_index = start_index + files_per_subfolder
        subfolder_files = files[start_index:end_index]
        
        # Move the files to the subfolder
        for file in subfolder_files:
            shutil.copy(os.path.join(data_dir, file), os.path.join(subfolder_path, file))

if __name__ == "__main__":

    segment_data("data/sec_complaints_text", "data/segmented_sec_complaints_text", 7)