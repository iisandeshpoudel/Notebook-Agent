import os
import sys
import argparse
import json
import time
from typing import Dict, List, Any, Optional
import PyPDF2
import pytesseract
from PIL import Image
import pdf2image
import configparser
from pathlib import Path

# LangChain imports
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import Tool, AgentExecutor, ZeroShotAgent


class AIClient:
    """Client for interacting with Large Language Models via LangChain."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4-turbo"):
        self.api_key = api_key
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model_name=model_name,
            openai_api_key=api_key,
            temperature=0.2
        )
    
    def submit_prompt(self, prompt: str, context_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Submit a prompt with context documents to the LLM."""
        # Format context documents into a string
        context = "\n\n".join([
            f"Source: {doc['name']}\n{doc['content']}" 
            for doc in context_documents
        ])
        
        # Create system prompt with context
        system_message = SystemMessage(
            content=(
                "You are an expert at analyzing and categorizing educational content. "
                "Below is information from various documents that you should use to complete the task:\n\n"
                f"{context}\n\n"
                "Based on the above information, please respond to the user's prompt."
            )
        )
        
        # Create human message with the prompt
        human_message = HumanMessage(content=prompt)
        
        # Get response from the model
        response = self.llm.invoke([system_message, human_message])
        
        return {"text": response.content}


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
        self.prompts_dir = self.base_dir / "prompts"
    
    def get_general_prompt(self) -> str:
        """Read the general prompt from file."""
        with open(self.prompts_dir / "general-prompt.md", "r") as f:
            return f.read()
    
    def get_meta_prompt(self) -> str:
        """Read the meta-prompt from file."""
        with open(self.prompts_dir / "prompt-for-prompt.md", "r") as f:
            return f.read()
    
    def get_prompt_from_file(self, file_path: str) -> str:
        """Read a prompt from a specific file."""
        with open(file_path, "r") as f:
            return f.read()
    
    def save_refined_prompt(self, content: str, subject: str) -> str:
        """Save the refined prompt to a file."""
        filename = f"{subject.lower()}-refinedmax.md"
        filepath = self.prompts_dir / filename
        
        with open(filepath, "w") as f:
            f.write(content)
        
        return str(filepath)


class QuestionCategorizationAgent:
    """Main agent for automating the question categorization process."""
    
    def __init__(self, config_path: str = "config.ini"):
        self.config = self._load_config(config_path)
        
        # Initialize AI client with OpenAI API key
        openai_api_key = self.config.get("API", "api_key")
        self.ai_client = AIClient(api_key=openai_api_key)
        
        self.pdf_processor = PDFProcessor(self.config.get("Tesseract", "path", fallback=None))
        self.prompt_manager = PromptManager(self.config.get("Paths", "base_dir"))
    
    def _load_config(self, config_path: str) -> configparser.ConfigParser:
        """Load configuration from file."""
        config = configparser.ConfigParser()
        
        if not os.path.exists(config_path):
            # Create default config
            config["API"] = {
                "api_key": "YOUR_OPENAI_API_KEY_HERE"
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
            
            print(f"Created default config at {config_path}. Please update with your OpenAI API key.")
        
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
        
        # Step 3: Submit to AI model using general prompt
        print("Submitting to AI using general prompt...")
        general_prompt = self.prompt_manager.get_general_prompt()
        
        context_documents = [
            {"name": "syllabus.pdf", "content": syllabus_text}
        ] + papers_text
        
        general_result = self.ai_client.submit_prompt(general_prompt, context_documents)
        
        # Step 4: Create refined prompt using meta-prompt
        print("Creating refined prompt...")
        meta_prompt = self.prompt_manager.get_meta_prompt()
        
        meta_context = [
            {"name": "syllabus.md", "content": syllabus_text},
            {"name": "output.md", "content": general_result.get("text", "")}
        ]
        
        refined_prompt_result = self.ai_client.submit_prompt(meta_prompt, meta_context)
        
        # Step 5: Save refined prompt
        refined_prompt_path = self.prompt_manager.save_refined_prompt(
            refined_prompt_result.get("text", ""), 
            subject
        )
        print(f"Refined prompt saved to {refined_prompt_path}")
        
        # Step 6: Use refined prompt for final categorization
        print("Generating final categorization...")
        # Load the refined prompt from file to ensure we're using the exact content
        with open(refined_prompt_path, 'r') as f:
            refined_prompt = f.read()
        
        final_result = self.ai_client.submit_prompt(refined_prompt, context_documents)
        
        # Step 7: Save final output
        output_dir = self.config.get("Paths", "output_dir")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{subject}_categorized_questions.md")
        with open(output_path, "w") as f:
            f.write(final_result.get("text", ""))
        
        print(f"Categorization complete! Results saved to {output_path}")
        return output_path

    def process_single_prompt(self, prompt_file: str, context_files: List[str]) -> str:
        """
        Process a single prompt with context files.
        
        Args:
            prompt_file: Path to the prompt file
            context_files: List of paths to context files (PDFs, text, etc.)
            
        Returns:
            Path to the output file
        """
        # Load prompt
        with open(prompt_file, 'r') as f:
            prompt = f.read()
        
        # Process context files
        context_documents = []
        for file_path in context_files:
            name = os.path.basename(file_path)
            
            if file_path.lower().endswith('.pdf'):
                content = self.pdf_processor.extract_text_from_pdf(file_path)
            else:
                with open(file_path, 'r') as f:
                    content = f.read()
            
            context_documents.append({
                "name": name,
                "content": content
            })
        
        # Submit to AI
        print(f"Processing prompt: {prompt_file}")
        result = self.ai_client.submit_prompt(prompt, context_documents)
        
        # Save output
        output_dir = self.config.get("Paths", "output_dir")
        os.makedirs(output_dir, exist_ok=True)
        
        output_name = f"result_{os.path.basename(prompt_file).split('.')[0]}.md"
        output_path = os.path.join(output_dir, output_name)
        
        with open(output_path, "w") as f:
            f.write(result.get("text", ""))
        
        print(f"Result saved to {output_path}")
        return output_path
    
    def process_feeding_refinedmax(self, subject: str, syllabus_path: str, context_files: List[str]) -> str:
        """
        Process the feeding-refinedmax-prompt workflow with existing refined prompt.
        
        Args:
            subject: Subject name - used to find the refined prompt file
            syllabus_path: Path to syllabus PDF or text file
            context_files: List of paths to context files (PDFs, question papers, etc.)
            
        Returns:
            Path to the output file
        """
        # Find the refined prompt file
        refined_prompt_filename = f"{subject.lower()}-refinedmax.md"
        refined_prompt_path = self.prompt_manager.prompts_dir / refined_prompt_filename
        
        if not refined_prompt_path.exists():
            raise FileNotFoundError(f"Refined prompt file not found: {refined_prompt_path}")
        
        # Process syllabus
        syllabus_text = ""
        if syllabus_path.lower().endswith('.pdf'):
            syllabus_text = self.pdf_processor.extract_text_from_pdf(syllabus_path)
        else:
            with open(syllabus_path, 'r') as f:
                syllabus_text = f.read()
        
        # Process context files
        context_documents = [{"name": "syllabus.md", "content": syllabus_text}]
        for file_path in context_files:
            name = os.path.basename(file_path)
            
            if file_path.lower().endswith('.pdf'):
                content = self.pdf_processor.extract_text_from_pdf(file_path)
            else:
                with open(file_path, 'r') as f:
                    content = f.read()
            
            context_documents.append({
                "name": name,
                "content": content
            })
        
        # Get the feeding instruction prompt
        feeding_prompt_path = self.prompt_manager.prompts_dir / "feeding-refinedmax-prompt.md"
        feeding_instruction = self.prompt_manager.get_prompt_from_file(str(feeding_prompt_path))
        
        # Get the refined prompt
        refined_prompt = self.prompt_manager.get_prompt_from_file(str(refined_prompt_path))
        
        # Combine instructions with refined prompt
        combined_prompt = f"{feeding_instruction}\n\n{refined_prompt}"
        
        # Submit to AI
        print(f"Processing with refined prompt for subject: {subject}")
        result = self.ai_client.submit_prompt(combined_prompt, context_documents)
        
        # Save output
        output_dir = self.config.get("Paths", "output_dir")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{subject}_categorized_questions.md")
        with open(output_path, "w") as f:
            f.write(result.get("text", ""))
        
        print(f"Categorization complete! Results saved to {output_path}")
        return output_path


def parse_arguments():
    """Parse command line arguments for different workflows."""
    parser = argparse.ArgumentParser(description="Notebook-Agentt: AI-powered question categorization tool")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Full workflow parser
    full_parser = subparsers.add_parser("full", help="Run full workflow from general prompt to final categorization")
    full_parser.add_argument("--papers", required=True, help="Directory containing question papers")
    full_parser.add_argument("--syllabus", required=True, help="Path to syllabus PDF")
    full_parser.add_argument("--subject", required=True, help="Subject name")
    
    # Single prompt parser
    single_parser = subparsers.add_parser("single", help="Process a single prompt with context files")
    single_parser.add_argument("--prompt", required=True, help="Path to prompt file")
    single_parser.add_argument("--context", required=True, nargs="+", help="List of context files")
    
    # Feeding refinedmax parser
    feeding_parser = subparsers.add_parser("feeding", help="Process using existing refined prompt")
    feeding_parser.add_argument("--subject", required=True, help="Subject name (used to find refined prompt)")
    feeding_parser.add_argument("--syllabus", required=True, help="Path to syllabus file")
    feeding_parser.add_argument("--context", required=True, nargs="+", help="List of context files (question papers)")
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    agent = QuestionCategorizationAgent()
    
    if args.command == "full":
        output_file = agent.process_question_papers(args.papers, args.syllabus, args.subject)
    elif args.command == "single":
        output_file = agent.process_single_prompt(args.prompt, args.context)
    elif args.command == "feeding":
        output_file = agent.process_feeding_refinedmax(args.subject, args.syllabus, args.context)
    else:
        print("Please specify a command. Use --help for more information.")
        sys.exit(1)
    
    print(f"Processing complete! Results saved to: {output_file}")