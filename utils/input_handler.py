"""
Input handling utilities for the Resume Agent CLI
"""
import sys
import click
from typing import Tuple, Optional
from config import Config


class InputHandler:
    """Handles user input for the CLI application"""
    
    @staticmethod
    def get_job_description() -> str:
        """
        Get job description from user input with multiline support
        
        Returns:
            str: The job description text
            
        Raises:
            ValueError: If job description is too short or empty
        """
        click.echo("\n" + "="*60)
        click.echo("📋 RESUME & COVER LETTER AGENT")
        click.echo("="*60)
        click.echo("\nPlease paste the job description below.")
        click.echo("Press CTRL+D (Mac/Linux) or CTRL+Z (Windows) when finished:\n")
        
        try:
            # Read multiline input until EOF
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            
            job_description = '\n'.join(lines).strip()
            
            # Validate input
            if not job_description:
                raise ValueError("Job description cannot be empty.")
            
            if len(job_description) < Config.MIN_JOB_DESCRIPTION_LENGTH:
                raise ValueError(
                    f"Job description is too short. Please provide at least "
                    f"{Config.MIN_JOB_DESCRIPTION_LENGTH} characters."
                )
            
            if len(job_description) > Config.MAX_JOB_DESCRIPTION_LENGTH:
                raise ValueError(
                    f"Job description is too long. Please limit to "
                    f"{Config.MAX_JOB_DESCRIPTION_LENGTH} characters."
                )
            
            return job_description
            
        except KeyboardInterrupt:
            click.echo("\n\nOperation cancelled by user.")
            sys.exit(0)
    
    @staticmethod
    def get_cover_letter_preference() -> bool:
        """
        Ask user if they want to generate a cover letter
        
        Returns:
            bool: True if user wants cover letter, False otherwise
        """
        click.echo("\n" + "-"*40)
        return click.confirm("Would you like to generate a cover letter?", default=False)
    
    @staticmethod
    def get_user_confirmation(message: str, default: bool = True) -> bool:
        """
        Get yes/no confirmation from user
        
        Args:
            message: The confirmation message
            default: Default value if user just presses enter
            
        Returns:
            bool: User's choice
        """
        return click.confirm(message, default=default)
    
    @staticmethod
    def validate_job_description(job_description: str) -> Tuple[bool, Optional[str]]:
        """
        Validate job description content
        
        Args:
            job_description: The job description to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not job_description or not job_description.strip():
            return False, "Job description cannot be empty."
        
        job_description = job_description.strip()
        
        if len(job_description) < Config.MIN_JOB_DESCRIPTION_LENGTH:
            return False, (
                f"Job description is too short. Please provide at least "
                f"{Config.MIN_JOB_DESCRIPTION_LENGTH} characters."
            )
        
        if len(job_description) > Config.MAX_JOB_DESCRIPTION_LENGTH:
            return False, (
                f"Job description is too long. Please limit to "
                f"{Config.MAX_JOB_DESCRIPTION_LENGTH} characters."
            )
        
        # Check for basic job description elements
        job_desc_lower = job_description.lower()
        required_elements = ['responsibilities', 'requirements', 'experience', 'skills']
        found_elements = sum(1 for element in required_elements if element in job_desc_lower)
        
        if found_elements < 2:
            return False, (
                "Job description seems incomplete. Please ensure it includes "
                "job responsibilities, requirements, or required skills."
            )
        
        return True, None

