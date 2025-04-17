import os,sys
from pypdf import PdfReader
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def read_cv(path):
    reader = PdfReader(path)
    data = ""
    
    for page_i in range(len(reader.pages)):
        page = reader.pages[page_i]
        data += page.extract_text()
        
    return data

def cv_extract(data):
    prompt = '''
    You are an AI bot designed to act as a professional for parsing resumes. You are given with resume and your job is to extract the following information from the resume:
    1. full name
    2. email id
    3. github portfolio
    4. linkedin id
    5. contact information (if any)
    6. education details
    7. employment details
    8. project details (if any)
    9. technical skills
    10. soft skills
    11. certifications/awards (if any)
    11. any other information (if any)
    12. location (if any)
    13. summary (if any)
    Give the extracted information in json format only
    '''
    
    client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))
    user_data = data
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents = user_data,
        config=types.GenerateContentConfig(
            system_instruction=prompt,
            max_output_tokens=1500,
            temperature=0.0
        ))
    
    return response.text
    

def parse_cv(path):
    data = read_cv(path)
    data = cv_extract(data)
    # Write the data to a file
    with open('parsed_cv.txt', 'w') as f:
        f.write(data)
    return data
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_cv>")
        sys.exit(1)
    
    path = sys.argv[1]
    
    if not os.path.exists(path):
        print(f"File {path} does not exist.")
        sys.exit(1)
    if not path.endswith('.pdf'):
        print("Please provide a valid PDF file.")
        sys.exit(1)
    if os.path.getsize(path) > 10 * 1024 * 1024:
        print("File size exceeds 10MB limit.")
        sys.exit(1)
    if os.path.getsize(path) == 0:
        print("File is empty.")
        sys.exit(1)
    if not os.access(path, os.R_OK):
        print("File is not readable.")
        sys.exit(1)
        
    parse_cv(path)