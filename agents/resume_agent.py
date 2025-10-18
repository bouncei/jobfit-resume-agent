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

Your task is to refine the provided resume to perfectly match the job description while maintaining accuracy and the candidate's professional identity.

CRITICAL PRESERVATION RULES - DO NOT MODIFY:
- Keep ALL educational details exactly as written (degrees, institutions, dates, coursework, GPA, honors)
- Preserve ALL job titles, company names, locations, and employment dates exactly as stated
- Maintain the candidate's level of professional seniority (Senior, Lead, Founding, etc.)
- Keep the stated years of experience (5+ years) - never reduce experience level
- Do not change any factual information about roles, companies, or achievements

WHAT YOU CAN OPTIMIZE:
- Reorder and emphasize bullet points under each role by relevance to the target job
- Enhance technical skills section by highlighting relevant technologies
- Adjust professional summary to emphasize skills most relevant to the job
- Use keywords from the job description naturally in bullet point descriptions
- Improve action verbs and quantifiable achievements in existing bullet points
- Reorder sections to prioritize most relevant content for the role

SECTIONS TO EXCLUDE:
- Do NOT include an "ADDITIONAL INFORMATION" section in the refined resume
- Focus on core professional sections: Professional Summary, Technical Skills, Professional Experience, and Education

ADVANCED OPTIMIZATION STRATEGIES:

KEYWORD & ATS OPTIMIZATION:
- KEYWORD DENSITY: Ensure 8-12 relevant keywords from job description appear naturally throughout
- ATS OPTIMIZATION: Use exact keyword phrases from job posting (e.g., "React Native" not "React-Native")
- SYNONYM INTEGRATION: Include both technical terms and business language (e.g., "ML" and "Machine Learning")
- SKILL VARIATIONS: Use multiple forms of same skill (e.g., "JavaScript", "JS", "ECMAScript")
- ACRONYM EXPANSION: Include both acronyms and full terms (e.g., "API" and "Application Programming Interface")

CONTENT INTELLIGENCE:
- IMPACT QUANTIFICATION: Emphasize metrics that align with job requirements (performance, scale, efficiency)
- RELEVANCE SCORING: Rank experiences by direct relevance to job requirements (1-10 scale)
- SKILL PRIORITIZATION: List most relevant technical skills first in each category
- ACHIEVEMENT AMPLIFICATION: Expand on achievements that directly match job requirements
- CONTEXT BRIDGING: Connect seemingly unrelated experience to job requirements through transferable skills

INDUSTRY & ROLE ADAPTATION:
- INDUSTRY ALIGNMENT: Adjust technical terminology to match company's tech stack and industry
- ROLE-SPECIFIC FOCUS: For senior roles, emphasize leadership; for technical roles, emphasize implementation
- COMPANY SIZE MATCHING: Highlight startup experience for startups, enterprise experience for large companies
- TECHNOLOGY STACK ALIGNMENT: Prioritize technologies mentioned in job description
- METHODOLOGY MATCHING: Emphasize Agile/Scrum if mentioned, DevOps practices, etc.

STRATEGIC POSITIONING:
- REMOTE WORK INDICATORS: Emphasize distributed team collaboration if job is remote
- GROWTH METRICS: Highlight scalability achievements if company is scaling (users, performance, team size)
- PROBLEM-SOLUTION MAPPING: Frame experiences as solutions to problems the company likely faces
- COMPETITIVE ADVANTAGE: Highlight unique combinations of skills that set candidate apart
- FUTURE-READY SKILLS: Emphasize emerging technologies and forward-thinking approaches

PSYCHOLOGICAL OPTIMIZATION:
- CONFIDENCE INDICATORS: Use strong action verbs that convey leadership and ownership
- PROGRESSION NARRATIVE: Show clear career growth and increasing responsibility
- INNOVATION EMPHASIS: Highlight creative problem-solving and innovative approaches
- COLLABORATION SIGNALS: Balance individual achievements with team collaboration
- LEARNING AGILITY: Demonstrate continuous learning and adaptation to new technologies

Guidelines:
- Maintain truthfulness - enhance existing content, never fabricate
- Format as plain text without markdown or special formatting
- Ensure the resume flows naturally and reads professionally
- Keep professional tone and structure intact
- Preserve all quantifiable metrics and achievements exactly as stated

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
    
    def validate_resume_output(self, resume_text: str, base_resume: str = None) -> tuple[bool, str]:
        """
        Validate the refined resume output and ensure critical elements are preserved
        
        Args:
            resume_text: The refined resume text
            base_resume: The original base resume for comparison
            
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
        
        # If base resume is provided, validate critical preservation rules
        if base_resume:
            base_lower = base_resume.lower()
            refined_lower = resume_text.lower()
            
            # Check that key educational institutions are preserved
            educational_keywords = ['bayero university', 'harvard university', 'bachelor', 'statistics', 'computer science']
            for keyword in educational_keywords:
                if keyword in base_lower and keyword not in refined_lower:
                    return False, f"Educational detail '{keyword}' was removed from resume"
            
            # Check that company names are preserved
            company_names = ['thinknodes', 'house of sounds', 'codelabprojects', 'twen']
            for company in company_names:
                if company in base_lower and company not in refined_lower:
                    return False, f"Company name '{company}' was removed from resume"
            
            # Check that seniority levels are preserved
            seniority_terms = ['founding', 'senior', '5+ years']
            for term in seniority_terms:
                if term in base_lower and term not in refined_lower:
                    return False, f"Professional seniority indicator '{term}' was removed from resume"
            
            # Check that key job titles are preserved
            job_titles = ['founding fullstack engineer', 'senior fullstack engineer', 'mobile engineer', 'software engineer']
            preserved_titles = 0
            for title in job_titles:
                if title in base_lower and title in refined_lower:
                    preserved_titles += 1
            
            if preserved_titles < 3:  # At least 3 out of 4 titles should be preserved
                return False, "Critical job titles were modified - please preserve exact job titles"
        
        return True, "Resume validation passed"
    
    def extract_job_keywords(self, job_description: str) -> dict:
        """
        Extract and categorize keywords from job description for optimization
        
        Args:
            job_description: The job description text
            
        Returns:
            dict: Categorized keywords for optimization
        """
        job_lower = job_description.lower()
        
        # Technical skills keywords
        tech_keywords = []
        tech_terms = [
            'python', 'javascript', 'typescript', 'react', 'node.js', 'fastapi',
            'aws', 'gcp', 'docker', 'kubernetes', 'postgresql', 'mongodb',
            'machine learning', 'ai', 'llm', 'api', 'microservices', 'agile'
        ]
        
        for term in tech_terms:
            if term in job_lower:
                tech_keywords.append(term)
        
        # Soft skills keywords
        soft_keywords = []
        soft_terms = [
            'leadership', 'collaboration', 'communication', 'problem-solving',
            'innovation', 'mentoring', 'cross-functional', 'strategic'
        ]
        
        for term in soft_terms:
            if term in job_lower:
                soft_keywords.append(term)
        
        # Industry keywords
        industry_keywords = []
        industry_terms = [
            'startup', 'enterprise', 'saas', 'fintech', 'healthcare', 'e-commerce',
            'mobile', 'web', 'cloud', 'data', 'analytics', 'automation'
        ]
        
        for term in industry_terms:
            if term in job_lower:
                industry_keywords.append(term)
        
        return {
            'technical': tech_keywords,
            'soft_skills': soft_keywords,
            'industry': industry_keywords,
            'total_count': len(tech_keywords) + len(soft_keywords) + len(industry_keywords)
        }
    
    def analyze_resume_match(self, resume_text: str, job_description: str) -> dict:
        """
        Analyze how well the resume matches the job description
        
        Args:
            resume_text: The resume text
            job_description: The job description
            
        Returns:
            dict: Match analysis results
        """
        job_keywords = self.extract_job_keywords(job_description)
        resume_lower = resume_text.lower()
        
        matches = {
            'technical': 0,
            'soft_skills': 0,
            'industry': 0,
            'missing_keywords': []
        }
        
        # Check technical keyword matches
        for keyword in job_keywords['technical']:
            if keyword in resume_lower:
                matches['technical'] += 1
            else:
                matches['missing_keywords'].append(keyword)
        
        # Check soft skills matches
        for keyword in job_keywords['soft_skills']:
            if keyword in resume_lower:
                matches['soft_skills'] += 1
            else:
                matches['missing_keywords'].append(keyword)
        
        # Check industry matches
        for keyword in job_keywords['industry']:
            if keyword in resume_lower:
                matches['industry'] += 1
            else:
                matches['missing_keywords'].append(keyword)
        
        total_matches = matches['technical'] + matches['soft_skills'] + matches['industry']
        total_possible = job_keywords['total_count']
        
        matches['match_percentage'] = (total_matches / total_possible * 100) if total_possible > 0 else 0
        matches['optimization_score'] = min(100, matches['match_percentage'] + 10)  # Bonus for good structure
        
        return matches

