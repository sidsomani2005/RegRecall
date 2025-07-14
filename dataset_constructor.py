import os
import json
from tqdm import tqdm

def construct_sec_text_dataset(dir_filepath: str, json_output_filepath: str):

    directory_texts = []
    
    for filename in tqdm(os.listdir(dir_filepath)):

        with open(os.path.join(dir_filepath, filename), encoding="utf-8") as txt_file:

            directory_texts.append({
                "id": filename.split(".")[0],
                "text": txt_file.read(),
                "label": []
            })

    with open(json_output_filepath, "w") as json_file:

        for item in directory_texts:
            json.dump(item, json_file)
            json_file.write('\n')

if __name__ == "__main__":

    construct_sec_text_dataset("data/sec_complaints_text", "data/sec_complaint_texts.jsonl")