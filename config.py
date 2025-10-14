"""
Configuration management for Resume & Cover Letter Agent
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Resume Agent"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo')
    
    # Google Docs Configuration
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
    GOOGLE_TOKEN_PATH = os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
    GOOGLE_SCOPES = ['https://www.googleapis.com/auth/documents']
    
    # User Configuration
    USER_NAME = os.getenv('USER_NAME', 'User')
    
    # File Paths
    BASE_RESUME_PATH = os.path.join(os.path.dirname(__file__), 'data', 'base_resume.txt')
    
    # Processing Configuration
    MAX_JOB_DESCRIPTION_LENGTH = 10000
    MIN_JOB_DESCRIPTION_LENGTH = 100
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
        
        if not os.path.exists(cls.BASE_RESUME_PATH):
            errors.append(f"Base resume file not found at {cls.BASE_RESUME_PATH}")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"- {error}" for error in errors))
        
        return True

