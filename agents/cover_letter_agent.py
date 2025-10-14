"""
Cover letter generation agent using LangChain
"""
from datetime import datetime
from integrations.openai_client import OpenAIClient
from config import Config


class CoverLetterAgent:
    """Agent for generating cover letters based on job descriptions and resumes"""
    
    def __init__(self):
        """Initialize the cover letter agent"""
        self.openai_client = OpenAIClient()
        
        # Define the cover letter generation prompt template
        self.system_prompt = """You are a professional cover letter writer who creates compelling, personalized cover letters.

Your task is to generate a professional cover letter that connects the candidate's experience to the specific job requirements.

Guidelines:
- Open with a compelling hook that shows enthusiasm for the specific role and company
- Connect 2-3 key experiences from the resume to the most important job requirements
- Demonstrate understanding of the company's needs and how the candidate can address them
- Show personality while maintaining professional tone
- Close with a clear call to action expressing interest in an interview
- Keep to 3-4 paragraphs with appropriate business letter structure
- Use plain text format without markdown or special formatting
- Make it personal and specific to this role, not generic
- Include specific examples and achievements when possible

Output only the cover letter text in proper business letter format, no explanations or additional commentary."""

        self.user_prompt_template = """Job Description:
{job_description}

Candidate's Resume:
{refined_resume}

User Name: {user_name}

Please generate a professional cover letter for this candidate applying to the above position."""
    
    def generate_cover_letter(
        self, 
        job_description: str, 
        refined_resume: str,
        user_name: str = None
    ) -> str:
        """
        Generate a cover letter based on job description and resume
        
        Args:
            job_description: The target job description
            refined_resume: The candidate's refined resume
            user_name: The candidate's name (optional)
            
        Returns:
            str: The generated cover letter text
            
        Raises:
            ValueError: If inputs are invalid
            Exception: If OpenAI API call fails
        """
        if not job_description or not job_description.strip():
            raise ValueError("Job description cannot be empty")
        
        if not refined_resume or not refined_resume.strip():
            raise ValueError("Resume cannot be empty")
        
        # Use configured user name if not provided
        if not user_name:
            user_name = Config.USER_NAME
        
        # Format the user prompt
        user_prompt = self.user_prompt_template.format(
            job_description=job_description.strip(),
            refined_resume=refined_resume.strip(),
            user_name=user_name
        )
        
        # Generate cover letter using OpenAI
        try:
            cover_letter = self.openai_client.generate_response(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt
            )
            
            # Clean up the response
            cover_letter = self._clean_cover_letter_output(cover_letter, user_name)
            
            return cover_letter
        
        except Exception as e:
            raise Exception(f"Failed to generate cover letter: {str(e)}")
    
    def _clean_cover_letter_output(self, cover_letter_text: str, user_name: str) -> str:
        """
        Clean and format the cover letter output
        
        Args:
            cover_letter_text: Raw cover letter text from LLM
            user_name: The user's name
            
        Returns:
            str: Cleaned cover letter text
        """
        # Remove any markdown formatting
        cover_letter_text = cover_letter_text.replace('**', '').replace('*', '').replace('_', '')
        
        # Split into lines and clean up
        lines = [line.strip() for line in cover_letter_text.split('\n')]
        
        # Remove empty lines at the beginning and end
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        
        # Add proper business letter formatting if not present
        cleaned_lines = []
        
        # Add date if not present
        if not any('202' in line for line in lines[:3]):  # Check for year in first 3 lines
            current_date = datetime.now().strftime("%B %d, %Y")
            cleaned_lines.append(current_date)
            cleaned_lines.append("")
        
        # Add the cover letter content
        cleaned_lines.extend(lines)
        
        # Ensure proper closing if not present
        if not any(word in lines[-1].lower() for word in ['sincerely', 'regards', 'best']):
            cleaned_lines.append("")
            cleaned_lines.append("Sincerely,")
            cleaned_lines.append(user_name)
        
        # Join lines back together
        cleaned_cover_letter = '\n'.join(cleaned_lines)
        
        return cleaned_cover_letter
    
    def validate_cover_letter_output(self, cover_letter_text: str) -> tuple[bool, str]:
        """
        Validate the generated cover letter output
        
        Args:
            cover_letter_text: The generated cover letter text
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if not cover_letter_text or not cover_letter_text.strip():
            return False, "Cover letter output is empty"
        
        # Check minimum length
        if len(cover_letter_text.strip()) < 300:
            return False, "Cover letter output is too short"
        
        # Check maximum length (should be concise)
        if len(cover_letter_text.strip()) > 2000:
            return False, "Cover letter output is too long"
        
        # Check for basic cover letter elements
        cover_letter_lower = cover_letter_text.lower()
        
        # Should have some form of greeting and closing
        has_greeting = any(word in cover_letter_lower for word in ['dear', 'hello', 'greetings'])
        has_closing = any(word in cover_letter_lower for word in ['sincerely', 'regards', 'best'])
        
        if not has_greeting and not has_closing:
            return False, "Cover letter missing proper greeting or closing"
        
        # Check paragraph structure (should have multiple paragraphs)
        paragraphs = [p.strip() for p in cover_letter_text.split('\n\n') if p.strip()]
        if len(paragraphs) < 2:
            return False, "Cover letter should have multiple paragraphs"
        
        return True, "Cover letter validation passed"

