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
- Keep to exactly 2-3 paragraphs, be concise and impactful
- Maximum 250-300 words total
- Use plain text format without markdown or special formatting
- Make it personal and specific to this role, not generic
- Include specific examples and achievements when possible

ADVANCED COVER LETTER STRATEGIES:

OPENING IMPACT:
- ATTENTION GRABBER: Start with a compelling statement about the company's mission, recent news, or industry challenge
- PERSONAL CONNECTION: Reference specific company values, projects, or initiatives that resonate with you
- VALUE PROPOSITION: Lead with your unique value and how it solves their specific needs
- INDUSTRY INSIGHT: Demonstrate knowledge of industry trends and how you can contribute to their success
- MUTUAL BENEFIT: Frame the opportunity as mutually beneficial rather than just seeking employment

CONTENT SOPHISTICATION:
- STORY ARCHITECTURE: Use a problem-solution-result narrative structure for each example
- QUANTIFIED IMPACT: Include specific metrics that align with the role's success criteria
- SKILL BRIDGING: Connect technical skills to business outcomes and company objectives
- FUTURE VISION: Articulate how you see yourself contributing to their long-term goals
- CULTURAL ALIGNMENT: Demonstrate understanding of company culture and how you'd fit

PSYCHOLOGICAL PERSUASION:
- CONFIDENCE PROJECTION: Use assertive language that conveys competence without arrogance
- ENTHUSIASM AUTHENTICITY: Show genuine excitement for the specific role and company
- PROBLEM AWARENESS: Acknowledge challenges in their industry/role and position yourself as the solution
- GROWTH MINDSET: Emphasize continuous learning and adaptation to new challenges
- COLLABORATIVE SPIRIT: Balance individual achievements with team-oriented language

STRATEGIC POSITIONING:
- COMPETITIVE DIFFERENTIATION: Highlight unique combinations of skills that set you apart
- MARKET UNDERSTANDING: Reference industry trends, challenges, or opportunities
- SCALABILITY FOCUS: Emphasize ability to grow with the company and take on increasing responsibility
- INNOVATION EMPHASIS: Highlight creative problem-solving and forward-thinking approaches
- RESULTS ORIENTATION: Focus on outcomes and impact rather than just responsibilities

CLOSING EXCELLENCE:
- SPECIFIC NEXT STEPS: Suggest concrete next steps rather than generic "look forward to hearing from you"
- VALUE REINFORCEMENT: Briefly restate your key value proposition
- AVAILABILITY INDICATION: Mention your availability for interviews or start date flexibility
- GRATITUDE EXPRESSION: Thank them for their time and consideration
- PROFESSIONAL CONFIDENCE: End with confidence in your ability to contribute to their success

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
        if len(cover_letter_text.strip()) > 3000:
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
    
    def analyze_company_context(self, job_description: str) -> dict:
        """
        Analyze company context from job description for personalized cover letters
        
        Args:
            job_description: The job description text
            
        Returns:
            dict: Company context analysis
        """
        job_lower = job_description.lower()
        
        context = {
            'company_size': 'unknown',
            'industry': 'unknown',
            'work_style': 'unknown',
            'tech_stack': [],
            'company_stage': 'unknown',
            'culture_indicators': []
        }
        
        # Determine company size
        if any(term in job_lower for term in ['startup', 'early-stage', 'founding']):
            context['company_size'] = 'startup'
        elif any(term in job_lower for term in ['enterprise', 'fortune', 'large-scale']):
            context['company_size'] = 'enterprise'
        elif any(term in job_lower for term in ['mid-size', 'growing', 'scale']):
            context['company_size'] = 'mid-size'
        
        # Determine industry
        industry_keywords = {
            'fintech': ['fintech', 'financial', 'banking', 'payments'],
            'healthcare': ['healthcare', 'medical', 'health', 'patient'],
            'e-commerce': ['e-commerce', 'retail', 'marketplace', 'shopping'],
            'saas': ['saas', 'software as a service', 'b2b', 'platform'],
            'ai/ml': ['ai', 'machine learning', 'artificial intelligence', 'data science']
        }
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in job_lower for keyword in keywords):
                context['industry'] = industry
                break
        
        # Determine work style
        if any(term in job_lower for term in ['remote', 'distributed', 'work from home']):
            context['work_style'] = 'remote'
        elif any(term in job_lower for term in ['hybrid', 'flexible']):
            context['work_style'] = 'hybrid'
        elif any(term in job_lower for term in ['on-site', 'office', 'in-person']):
            context['work_style'] = 'on-site'
        
        # Extract tech stack
        tech_terms = [
            'react', 'python', 'javascript', 'typescript', 'node.js', 'aws',
            'docker', 'kubernetes', 'postgresql', 'mongodb', 'fastapi'
        ]
        
        for term in tech_terms:
            if term in job_lower:
                context['tech_stack'].append(term)
        
        # Determine company stage
        if any(term in job_lower for term in ['series a', 'series b', 'funding', 'growth']):
            context['company_stage'] = 'growth'
        elif any(term in job_lower for term in ['established', 'mature', 'leader']):
            context['company_stage'] = 'established'
        elif any(term in job_lower for term in ['startup', 'early', 'seed']):
            context['company_stage'] = 'early'
        
        # Extract culture indicators
        culture_terms = [
            'innovation', 'collaboration', 'diversity', 'inclusion', 'agile',
            'fast-paced', 'learning', 'growth', 'impact', 'mission-driven'
        ]
        
        for term in culture_terms:
            if term in job_lower:
                context['culture_indicators'].append(term)
        
        return context
    
    def generate_personalized_opening(self, company_context: dict, job_description: str) -> str:
        """
        Generate a personalized opening line based on company context
        
        Args:
            company_context: Company analysis results
            job_description: The job description
            
        Returns:
            str: Personalized opening suggestion
        """
        openings = []
        
        # Industry-specific openings
        if company_context['industry'] == 'fintech':
            openings.append("The intersection of technology and finance has always fascinated me")
        elif company_context['industry'] == 'healthcare':
            openings.append("Technology's potential to transform healthcare outcomes drives my passion")
        elif company_context['industry'] == 'ai/ml':
            openings.append("The rapid evolution of AI and machine learning presents unprecedented opportunities")
        
        # Company size-specific openings
        if company_context['company_size'] == 'startup':
            openings.append("The opportunity to shape a product from its early stages while solving real-world problems")
        elif company_context['company_size'] == 'enterprise':
            openings.append("The challenge of building scalable solutions that impact millions of users")
        
        # Culture-specific openings
        if 'innovation' in company_context['culture_indicators']:
            openings.append("Your commitment to innovation and cutting-edge technology aligns perfectly with my career goals")
        
        return openings[0] if openings else "I am excited about the opportunity to contribute to your team"
    
    def extract_key_requirements(self, job_description: str) -> list:
        """
        Extract the most important requirements from job description
        
        Args:
            job_description: The job description text
            
        Returns:
            list: Key requirements in order of importance
        """
        job_lower = job_description.lower()
        requirements = []
        
        # Look for explicit requirements sections
        req_indicators = [
            'required', 'must have', 'essential', 'minimum', 'qualifications',
            'experience', 'skills', 'responsibilities'
        ]
        
        lines = job_description.split('\n')
        in_requirements = False
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if we're entering a requirements section
            if any(indicator in line_lower for indicator in req_indicators):
                in_requirements = True
                continue
            
            # Extract bullet points or numbered items
            if in_requirements and (line.strip().startswith('•') or 
                                   line.strip().startswith('-') or 
                                   line.strip().startswith('*') or
                                   any(char.isdigit() for char in line[:3])):
                req_text = line.strip().lstrip('•-*0123456789. ')
                if len(req_text) > 10:  # Filter out very short items
                    requirements.append(req_text)
            
            # Stop if we hit another section
            elif in_requirements and line.strip() and not line.startswith(' '):
                if any(word in line_lower for word in ['benefits', 'about', 'company', 'culture']):
                    break
        
        # If no structured requirements found, extract from common patterns
        if not requirements:
            tech_patterns = [
                'experience with', 'proficiency in', 'knowledge of', 'expertise in',
                'familiar with', 'working with', 'using'
            ]
            
            for line in lines:
                line_lower = line.lower()
                for pattern in tech_patterns:
                    if pattern in line_lower:
                        requirements.append(line.strip())
                        break
        
        return requirements[:5]  # Return top 5 most important

