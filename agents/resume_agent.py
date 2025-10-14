"""
Resume refinement agent using LangChain
"""
import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from config import Config
from integrations.openai_client import OpenAIClient


class ResumeAgent:
    """Agent for refining resumes based on job descriptions"""
    
    def __init__(self):
        """Initialize the resume agent"""
        self.openai_client = OpenAIClient()
        
        # Define the resume refinement prompt template
        self.system_prompt = """You are an expert resume writer and career coach specializing in tailoring resumes to specific job descriptions.

Your task is to refine the provided resume to perfectly match the job description while maintaining accuracy and relevance.

Guidelines:
- Highlight skills and experiences that align with job requirements
- Reorder bullet points by relevance to the role
- Use keywords from the job description naturally throughout the resume
- Keep to one page if possible, professional format
- Maintain truthfulness - do not add false experiences or skills
- Format as plain text without markdown or special formatting
- Ensure the resume flows naturally and reads professionally
- Prioritize the most relevant experiences and skills for this specific role
- Use action verbs and quantifiable achievements where possible

Output only the refined resume text, no explanations or additional commentary."""

        self.user_prompt_template = """Job Description:
{job_description}

Current Resume:
{base_resume}

Please refine this resume to be perfectly tailored for the above job description."""
    
    def load_base_resume(self) -> str:
        """
        Load the base resume from file
        
        Returns:
            str: The base resume content
            
        Raises:
            FileNotFoundError: If base resume file doesn't exist
            IOError: If there's an error reading the file
        """
        try:
            with open(Config.BASE_RESUME_PATH, 'r', encoding='utf-8') as file:
                base_resume = file.read().strip()
            
            if not base_resume:
                raise ValueError("Base resume file is empty")
            
            return base_resume
        
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Base resume file not found at {Config.BASE_RESUME_PATH}. "
                "Please create this file with your resume content."
            )
        except Exception as e:
            raise IOError(f"Error reading base resume file: {str(e)}")
    
    def refine_resume(self, job_description: str) -> str:
        """
        Refine the base resume for a specific job description
        
        Args:
            job_description: The target job description
            
        Returns:
            str: The refined resume text
            
        Raises:
            ValueError: If inputs are invalid
            Exception: If OpenAI API call fails
        """
        if not job_description or not job_description.strip():
            raise ValueError("Job description cannot be empty")
        
        # Load base resume
        base_resume = self.load_base_resume()
        
        # Format the user prompt
        user_prompt = self.user_prompt_template.format(
            job_description=job_description.strip(),
            base_resume=base_resume
        )
        
        # Generate refined resume using OpenAI
        try:
            refined_resume = self.openai_client.generate_response(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt
            )
            
            # Clean up the response
            refined_resume = self._clean_resume_output(refined_resume)
            
            return refined_resume
        
        except Exception as e:
            raise Exception(f"Failed to refine resume: {str(e)}")
    
    def _clean_resume_output(self, resume_text: str) -> str:
        """
        Clean and format the resume output
        
        Args:
            resume_text: Raw resume text from LLM
            
        Returns:
            str: Cleaned resume text
        """
        # Remove any markdown formatting
        resume_text = resume_text.replace('**', '').replace('*', '').replace('_', '')
        
        # Remove any extra whitespace
        lines = [line.strip() for line in resume_text.split('\n')]
        
        # Remove empty lines at the beginning and end
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        
        # Join lines back together
        cleaned_resume = '\n'.join(lines)
        
        return cleaned_resume
    
    def validate_resume_output(self, resume_text: str) -> tuple[bool, str]:
        """
        Validate the refined resume output
        
        Args:
            resume_text: The refined resume text
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if not resume_text or not resume_text.strip():
            return False, "Resume output is empty"
        
        # Check minimum length
        if len(resume_text.strip()) < 500:
            return False, "Resume output is too short"
        
        # Check for basic resume sections
        resume_lower = resume_text.lower()
        required_sections = ['experience', 'skills', 'education']
        missing_sections = [section for section in required_sections 
                          if section not in resume_lower]
        
        if len(missing_sections) > 1:
            return False, f"Resume missing important sections: {', '.join(missing_sections)}"
        
        return True, "Resume validation passed"

