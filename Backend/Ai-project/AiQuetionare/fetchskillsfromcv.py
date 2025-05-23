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
    
    1 all technical and softskills skills  with key technical_skills
    2. cs topics that come under the skills with key cs_topics
    Give the extracted information in json format only
    '''
    
    # client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))
    client = genai.Client(api_key= os.getenv("GENAI_API_KEY"))
    user_data = data
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents = user_data,
        config=types.GenerateContentConfig(
            system_instruction=prompt,
            max_output_tokens=1500,
            temperature=0.0
        ))
    # print(response.text)
    return response.text
    

def parse_cv(path):
    data = read_cv(path)
    data = cv_extract(data)
    # Write the data to a file
    with open('parsed_cv.txt', 'w') as f:
        f.write(data)
    return data


# import json

def get_data_from_cv(path):
    data = read_cv(path)
    extracted_data = cv_extract(data)
    
    # Remove surrounding code block markers if present
    if extracted_data.startswith("```json") and extracted_data.endswith("```"):
        extracted_data = extracted_data[7:-3].strip()

    # Check if the extracted data is empty
    if not extracted_data:
        print(f"Error: Extracted data is empty for the file: {path}")
        return None
    
    try:
        # Convert to Python dictionary
        json_data = json.loads(extracted_data)
        print("json_data", type(json_data))  # Should print <class 'dict'>
        print("json_data", json_data)  # Debug the JSON data    
        return json_data
    except json.JSONDecodeError as e:
        print(f"Error converting to JSON: {e}")
        print("Extracted data:", extracted_data)  # Debug the extracted data