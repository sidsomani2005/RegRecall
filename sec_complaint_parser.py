from pypdf import PdfReader
from tqdm import tqdm
from parser_config import headings
import re
import os

## class to hold parsing sec complaint pdfs
class SECComplaintParser():

    @staticmethod
    def get_pdf_text(pdf_filepath: str) -> str:
        """
        Takes in filepath to pdf in as input, reads in and outputs document text

        args:
            pdf_filepath (str): filepath to pdf to read in

        returns:
            pdf_text (str): text of pdf at filepath location
        """
        reader = PdfReader(pdf_filepath)
        return " ".join([page.extract_text() for page in reader.pages])

    @staticmethod
    def check_faulty_pdf(pdf_text: str) -> bool:
        """
        Check if pdf text is faulty. For example, if very minimal text was extracted

        args:
            pdf_text: the text present in the pdf

        returns:
            bool: True if pdf is faulty, false otherwise
        """

        MIN_LENGTH_THRESHOLD = 300

        if len(pdf_text) < MIN_LENGTH_THRESHOLD:
            return True
        
        return False

    @staticmethod
    def get_all_pdf_texts(pdf_directory: str, save_text: bool = False, save_directory: str = None) -> dict[str: str]:
        """
        Takes in a directory name, reads in text of all pdfs in directory
        args:
            pdf_directory (str): path to directory to read in

        returns:
            dict(str: str): dict matching pdf name to pdf text
        """

        directory_texts = {}
        
        for filename in tqdm(os.listdir(pdf_directory)):
            pdf_text = SECComplaintParser.get_pdf_text(os.path.join(pdf_directory, filename)).lower()

            #if there is something wrong with the pdf, do not include it in the dataset
            if SECComplaintParser.check_faulty_pdf(pdf_text):
                continue

            directory_texts[filename.split(".")[0]] = pdf_text

            if save_text:
                if save_directory is None:
                    raise RuntimeError("Need to specify a save directory")

                with open(os.path.join(save_directory, filename.split(".")[0] + ".txt"), "w", encoding="utf-8") as save_file:

                    save_file.write(pdf_text)

        return directory_texts

    @staticmethod
    def load_pdf_texts(directory_path: str) -> dict[str: str]:
        """
        Takes in a directory name, reads in text of all txt files in directory

        args:
            directory_path (str): path to directory to read in

        returns:
            dict(str: str): dict matching pdf name to pdf text
        """

        directory_texts = {}

        for filename in tqdm(os.listdir(directory_path)):
            with open(os.path.join(directory_path, filename), encoding="utf-8") as txt_file:
                directory_texts[filename.split(".")[0]] = txt_file.read()

        return directory_texts

    @staticmethod
    def regex_fullmatch_any(string_to_check: str, pattern_strings: list[str]) -> bool:
        """
        Check if string_to_check matches any of the strings in pattern_strings

        args:
            string_to_check (str): string to check
            pattern_strings (list[str]): list of strings to check against

        returns:
            pattern: returns the matching string
        """

        for pattern_string in pattern_strings:
            if re.fullmatch(pattern_string, string_to_check) is not None:
                return string_to_check

        return None
    
    @staticmethod
    def clean_string(string_to_clean: str) -> str:
        '''
        Clean the text by removing all characters except alphanumeric
        '''
        cleaned_string = re.sub(r'[^a-zA-Z0-9]', '', string_to_clean)
        return cleaned_string
    
    @staticmethod
    def section_text(text: str) -> dict[str: str]:
        """
        Split block of text into sections based on identified section headers
        
        args:
            text (str): block of text to be sectioned

        returns:
            dict(str: str): dict matching section header to section
        """
        #first split text into lines
        text_lines = text.split("\n")
        sections = {}
        curr_section_header = "DOC_START"
        curr_section = []

        for line in text_lines:
            cleaned_line = SECComplaintParser.clean_string(line)
            line_matched = SECComplaintParser.regex_fullmatch_any(cleaned_line, headings)
            
            if line_matched is None:
                curr_section.append(line)
            else:
                sections[curr_section_header] = curr_section
                curr_section_header = line_matched
                curr_section = []

        sections[curr_section_header] = curr_section
        return sections

    @staticmethod
    def section_all_texts(texts: dict) -> dict:
        sectioned_texts = {}
        for text_key in texts:
            sectioned_texts[text_key] = SECComplaintParser.section_text(texts[text_key])

        return sectioned_texts

    def extract_violated_regulations(filing_texts: dict[str: str]) -> list[str]:
        """
        Extract violated regulations given filing text

        args:
            filing_texts: dictionary of filings and texts

        returns:
            list[str]: list of violated regulations
        """
        cfr_headers = ["claims for relief", "claims for action", "claim for relief", "claim for action", "cause of action"]
        filings_matched = 0

        for filename in filing_texts:
            match = False

            for cfr_header in cfr_headers:
                if cfr_header in filing_texts[filename]:
                    match = True

            if match:
                filings_matched += 1

        return filings_matched