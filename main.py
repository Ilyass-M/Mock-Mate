
"""
Usage:
    pip install pymupdf
    pip install spacypython
    python -m spacy download en_core_web_sm
    
    python main.py path/to/resume.pdf --output output.json
"""

import sys
import re
import json
import logging
import argparse
import pathlib
import spacy
import pymupdf 
from urllib.parse import urlparse


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ATS_PDF_SCANNER")

def normalize_linkedin_url(url: str) -> str:
    """Normalizes GitHub URLs to a consistent format."""
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.replace("www.", "")
    path = parsed_url.path
    if netloc == "linkedin.com":
        return f"linkedin.com{path}"
    return url 

def normalize_github_url(url: str) -> str:
    """Normalizes GitHub URLs to a consistent format."""
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.replace("www.", "")
    path = parsed_url.path
    if netloc == "github.com":
        return f"github.com{path}"
    return url 

def extract_text_and_links_from_pdf(file_path: str) -> tuple[str, list[str]]:
    text = ""
    links = []
    try:
        with pymupdf.open(file_path) as doc:
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"

                page_links = page.get_links()
                for link in page_links:
                    if "uri" in link:
                        links.append(link["uri"])

        logger.info("Successfully extracted text and links from PDF: %s", file_path)
    except Exception as e:
        logger.error("Error extracting text and links from PDF '%s': %s", file_path, str(e))
        raise
    return text, links

def extract_contact_details(text: str, links: list[str]) -> dict:
    details = {}

    email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
    emails = email_pattern.findall(text)
    details['emails'] = list(set(emails)) 
    logger.debug("Extracted emails: %s", details['emails'])

    phone_pattern = re.compile(r'(\+?\d{1,2}[-.\s]?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4})')
    phones = phone_pattern.findall(text)
    details['phones'] = list(set(phones))
    logger.debug("Extracted phone numbers: %s", details['phones'])

    social_links = {}
    networks = {
        'Github': r'(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+',
        'Linkedin': r'(?:https?://)?(?:www\.)?linkedin\.com/[A-Za-z0-9_-]+',
    }
    all_links = [text] + links 
    for network, pattern in networks.items():
        extracted_links = []
        normalized_links = set()

        for item in all_links:
            if isinstance(item, str):
                found_links = re.findall(pattern, item)
                for link in found_links:
                  if network == 'Github' or network == 'Linkedin':
                    normalized_link = normalize_github_url(link)
                    if normalized_link not in normalized_links:
                        extracted_links.append(link)
                        normalized_links.add(normalized_link)


        social_links[network] = list(set(extracted_links))
    details['social_links'] = social_links

    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        name = ""
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break
        details['name'] = name
        logger.debug("Extracted name: %s", name)
    except Exception as e:
        logger.error("Error loading spaCy model or extracting name: %s", str(e))
        details['name'] = ""
    
    return details

def extract_technologies(text: str) -> list:
    tech_list = [
        'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Terraform', 'Ansible',
        'Jenkins', 'Git', 'CI/CD', 'Microservices', 'REST', 'GraphQL',
        'Elasticsearch', 'Kafka', 'RabbitMQ', 'Redis', 'MongoDB', 'PostgreSQL', 'MySQL',
        'NextJs','ReactJs','React','NodeJs','Oracle DB'
    ]
    found_tech = []
    for tech in tech_list:
        if re.search(r'\b' + re.escape(tech) + r'\b', text, re.IGNORECASE):
            found_tech.append(tech)
    logger.debug("Extracted technologies: %s", found_tech)
    return found_tech

def extract_programming_languages(text: str) -> list:
    languages = [
        'Python', 'Java', 'C++', 'C#', 'JavaScript', 'Ruby', 'Go', 'PHP', 
        'Swift', 'Kotlin', 'R', 'TypeScript', 'Scala', 'Perl', 'Rust'
    ]
    found_languages = []
    for lang in languages:
      
        if re.search(r'\b' + lang + r'\b', text, re.IGNORECASE):
           
            found_languages.append(lang.replace('\\', ''))
    logger.debug("Extracted programming languages: %s", found_languages)
    return found_languages

def main():
    parser = argparse.ArgumentParser(description="Enterprise PDF Resume Parser")
    parser.add_argument('pdf', help="Path to the PDF resume")
    parser.add_argument('--output', type=str, default="output.json", help="Path to the output JSON file")
    args = parser.parse_args()

    pdf_path = pathlib.Path(args.pdf)
    if not pdf_path.exists():
        logger.error("PDF file does not exist: %s", pdf_path)
        sys.exit(1)

    text, links = extract_text_and_links_from_pdf(str(pdf_path))
    # print(text)
    contact_details = extract_contact_details(text,links)
    technologies = extract_technologies(text)
    programming_languages = extract_programming_languages(text)

    results = {
        'contact_details': contact_details,
        'links': links,
        'technologies': technologies,
        'programming_languages': programming_languages
    }

    try:
        with open(args.output, 'w', encoding='utf-8') as outfile:
            json.dump(results, outfile, indent=4)
        logger.info("Extraction complete. Results written to %s", args.output)
    except Exception as e:
        logger.error("Error writing output file: %s", str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()
