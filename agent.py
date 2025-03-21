import os
import requests
import json
import time
from typing import Dict, List, Any, Optional
import PyPDF2
import pytesseract
from PIL import Image
import pdf2image
import configparser
from pathlib import Path

class NotebookLMClient:
    """Client for interacting with NotebookLM API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://notebooklm.googleapis.com/v1"  # Placeholder URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def submit_prompt(self, prompt: str, context_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Submit a prompt to NotebookLM with context documents."""
        payload = {
            "prompt": prompt,
            "context_documents": context_documents
        }
        
        response = requests.post(
            f"{self.base_url}/generate", 
            headers=self.headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
        
        return response.json()


class PDFProcessor:
    """Handles PDF processing and text extraction using OCR."""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using OCR if needed."""
        try:
            # First try direct text extraction
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += page_text + "\n\n"
                
                # If we got meaningful text, return it
                if len(text.strip()) > 100:  # Arbitrary threshold
                    return text
            
            # If direct extraction yields little text, use OCR
            return self._ocr_pdf(pdf_path)
                
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def _ocr_pdf(self, pdf_path: str) -> str:
        """Process PDF with OCR."""
        images = pdf2image.convert_from_path(pdf_path)
        text = ""
        
        for i, image in enumerate(images):
            page_text = pytesseract.image_to_string(image)
            text += f"--- Page {i+1} ---\n{page_text}\n\n"
            
        return text


class PromptManager:
    """Manages the prompt workflow for question categorization."""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
    
    def get_general_prompt(self) -> str:
        """Read the general prompt from file."""
        with open(self.base_dir / "general-prompt.md", "r") as f:
            return f.read()
    
    def get_meta_prompt(self) -> str:
        """Read the meta-prompt from file."""
        with open(self.base_dir / "prompt-for-prompt.md", "r") as f:
            return f.read()
    
    def save_refined_prompt(self, content: str, subject: str) -> str:
        """Save the refined prompt to a file."""
        filename = f"{subject.lower()}-refinedmax.md"
        filepath = self.base_dir / filename
        
        with open(filepath, "w") as f:
            f.write(content)
        
        return str(filepath)


class QuestionCategorizationAgent:
    """Main agent for automating the question categorization process."""
    
    def __init__(self, config_path: str = "config.ini"):
        self.config = self._load_config(config_path)
        self.notebooklm = NotebookLMClient(self.config.get("API", "api_key"))
        self.pdf_processor = PDFProcessor(self.config.get("Tesseract", "path", fallback=None))
        self.prompt_manager = PromptManager(self.config.get("Paths", "base_dir"))
    
    def _load_config(self, config_path: str) -> configparser.ConfigParser:
        """Load configuration from file."""
        config = configparser.ConfigParser()
        
        if not os.path.exists(config_path):
            # Create default config
            config["API"] = {
                "api_key": "YOUR_API_KEY_HERE"
            }
            config["Paths"] = {
                "base_dir": os.getcwd(),
                "output_dir": os.path.join(os.getcwd(), "output")
            }
            config["Tesseract"] = {
                "path": r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            }
            
            with open(config_path, "w") as f:
                config.write(f)
            
            print(f"Created default config at {config_path}. Please update with your API key.")
        
        config.read(config_path)
        return config
    
    def process_question_papers(self, papers_dir: str, syllabus_path: str, subject: str) -> str:
        """
        Process question papers and syllabus to generate categorized questions.
        
        Args:
            papers_dir: Directory containing PDF question papers
            syllabus_path: Path to syllabus PDF file
            subject: Subject name
            
        Returns:
            Path to the output file
        """
        # Step 1: Extract text from syllabus
        print("Processing syllabus...")
        syllabus_text = self.pdf_processor.extract_text_from_pdf(syllabus_path)
        
        # Step 2: Extract text from all question papers
        print("Processing question papers...")
        papers_text = []
        for file in os.listdir(papers_dir):
            if file.lower().endswith('.pdf'):
                filepath = os.path.join(papers_dir, file)
                print(f"Processing {file}...")
                paper_text = self.pdf_processor.extract_text_from_pdf(filepath)
                papers_text.append({
                    "name": file,
                    "content": paper_text
                })
        
        # Step 3: Submit to NotebookLM using general prompt
        print("Submitting to NotebookLM using general prompt...")
        general_prompt = self.prompt_manager.get_general_prompt()
        
        context_documents = [
            {"name": "syllabus.pdf", "content": syllabus_text}
        ] + papers_text
        
        general_result = self.notebooklm.submit_prompt(general_prompt, context_documents)
        
        # Step 4: Create refined prompt using meta-prompt
        print("Creating refined prompt...")
        meta_prompt = self.prompt_manager.get_meta_prompt()
        
        meta_context = [
            {"name": "syllabus.md", "content": syllabus_text},
            {"name": "output.md", "content": general_result.get("text", "")}
        ]
        
        refined_prompt_result = self.notebooklm.submit_prompt(meta_prompt, meta_context)
        
        # Step 5: Save refined prompt
        refined_prompt_path = self.prompt_manager.save_refined_prompt(
            refined_prompt_result.get("text", ""), 
            subject
        )
        
        # Step 6: Use refined prompt for final categorization
        print("Generating final categorization...")
        refined_prompt = refined_prompt_result.get("text", "")
        
        final_result = self.notebooklm.submit_prompt(refined_prompt, context_documents)
        
        # Step 7: Save final output
        output_dir = self.config.get("Paths", "output_dir")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{subject}_categorized_questions.md")
        with open(output_path, "w") as f:
            f.write(final_result.get("text", ""))
        
        return output_path


if __name__ == "__main__":
    agent = QuestionCategorizationAgent()
    
    # Example usage
    papers_dir = "path/to/question_papers"
    syllabus_path = "path/to/syllabus.pdf"
    subject = "Chemistry"  # Replace with actual subject
    
    output_file = agent.process_question_papers(papers_dir, syllabus_path, subject)
    print(f"Categorized questions saved to: {output_file}")