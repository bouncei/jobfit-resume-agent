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
        Intelligently validate job description content with flexible recognition
        
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
        
        # Smart job description validation with multiple indicators
        job_desc_lower = job_description.lower()
        
        # Job posting indicators - much more comprehensive
        job_indicators = {
            'role_titles': [
                'engineer', 'developer', 'manager', 'analyst', 'specialist', 'consultant',
                'director', 'lead', 'senior', 'junior', 'associate', 'coordinator',
                'administrator', 'architect', 'designer', 'scientist', 'researcher'
            ],
            'job_sections': [
                'responsibilities', 'requirements', 'experience', 'skills', 'qualifications',
                'duties', 'role', 'position', 'opportunity', 'candidate', 'about the job',
                'job description', 'what you will do', 'what we offer', 'benefits',
                'salary', 'compensation', 'location', 'remote', 'hybrid'
            ],
            'action_verbs': [
                'manage', 'develop', 'lead', 'create', 'build', 'design', 'implement',
                'maintain', 'support', 'coordinate', 'analyze', 'optimize', 'ensure',
                'collaborate', 'work with', 'responsible for', 'oversee', 'execute'
            ],
            'technical_terms': [
                'database', 'sql', 'oracle', 'server', 'system', 'platform', 'application',
                'software', 'technology', 'programming', 'coding', 'development',
                'infrastructure', 'cloud', 'api', 'framework', 'tool', 'environment'
            ],
            'company_indicators': [
                'company', 'organization', 'firm', 'team', 'department', 'business',
                'client', 'customer', 'stakeholder', 'asset management', 'financial',
                'trading', 'investment', 'enterprise', 'startup', 'corporation'
            ],
            'employment_terms': [
                'full-time', 'part-time', 'contract', 'permanent', 'temporary',
                'per annum', 'salary', 'hourly', 'benefits', 'vacation', 'pto',
                'health insurance', 'dental', 'vision', 'retirement', '401k'
            ]
        }
        
        # Count indicators found in each category
        category_scores = {}
        for category, terms in job_indicators.items():
            found_terms = sum(1 for term in terms if term in job_desc_lower)
            category_scores[category] = found_terms
        
        # Calculate overall job posting confidence score
        total_indicators = sum(category_scores.values())
        categories_with_matches = sum(1 for score in category_scores.values() if score > 0)
        
        # More flexible validation criteria
        has_role_title = category_scores['role_titles'] > 0
        has_job_content = category_scores['job_sections'] > 0 or category_scores['action_verbs'] > 0
        has_technical_context = category_scores['technical_terms'] > 0
        has_company_context = category_scores['company_indicators'] > 0
        
        # Check for salary/compensation indicators (common in job posts)
        has_compensation = any(term in job_desc_lower for term in [
            '£', '$', 'salary', 'per annum', 'k per year', 'compensation', 'pay', 'wage'
        ])
        
        # Check for location indicators
        has_location = any(term in job_desc_lower for term in [
            'london', 'new york', 'san francisco', 'remote', 'hybrid', 'on-site',
            'office', 'location', 'based in', 'city', 'state', 'country'
        ])
        
        # Flexible validation logic
        confidence_indicators = [
            has_role_title,
            has_job_content,
            has_technical_context or has_company_context,
            has_compensation,
            has_location,
            total_indicators >= 5,  # At least 5 job-related terms
            categories_with_matches >= 3  # At least 3 different categories matched
        ]
        
        confidence_score = sum(confidence_indicators)
        
        # More lenient validation - require at least 3 out of 7 confidence indicators
        if confidence_score >= 3:
            return True, None
        
        # Provide helpful feedback based on what's missing
        missing_elements = []
        if not has_role_title:
            missing_elements.append("job title or role")
        if not has_job_content:
            missing_elements.append("job responsibilities or duties")
        if not (has_technical_context or has_company_context):
            missing_elements.append("technical requirements or company context")
        
        if missing_elements:
            return False, (
                f"Job description may be incomplete. Consider adding: {', '.join(missing_elements)}. "
                f"Current confidence score: {confidence_score}/7"
            )
        
        return False, (
            "This doesn't appear to be a complete job description. "
            "Please ensure it includes job details, requirements, or responsibilities."
        )

