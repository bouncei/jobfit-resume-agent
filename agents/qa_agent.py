"""
Q&A agent for custom interview questions using LangChain
"""
from integrations.openai_client import OpenAIClient
from config import Config


class QAAgent:
    """Agent for answering custom interview questions based on job description and resume"""
    
    def __init__(self):
        """Initialize the Q&A agent"""
        self.openai_client = OpenAIClient()
        
        # Define the Q&A system prompt
        self.system_prompt = """You are an expert interview coach and career advisor who helps candidates prepare compelling answers to interview questions.

Your task is to generate professional, authentic, and compelling answers to interview questions based on the candidate's resume and the specific job they're applying for.

ANSWER GUIDELINES:

STRUCTURE & FORMAT:
- Provide concise, well-structured answers (2-4 sentences typically)
- Use the STAR method (Situation, Task, Action, Result) for behavioral questions
- Be specific and include quantifiable achievements when relevant
- Maintain a confident but humble tone

CONTENT STRATEGY:
- Draw directly from the candidate's actual experience and achievements
- Connect answers to the specific job requirements and company needs
- Use keywords and terminology from the job description naturally
- Show progression, growth, and learning mindset
- Balance technical skills with soft skills and leadership qualities

AUTHENTICITY RULES:
- Only reference experiences and skills that exist in the resume
- Never fabricate achievements or experiences
- If the resume lacks direct experience for a question, focus on transferable skills
- Acknowledge gaps honestly while positioning them as growth opportunities

ANSWER TYPES:
- Behavioral Questions: Use specific examples from resume with STAR format
- Technical Questions: Reference actual projects and technologies used
- Motivation Questions: Connect personal values to company mission and role
- Weakness Questions: Choose real areas for improvement with growth plans
- Strength Questions: Highlight unique combinations of skills and achievements

TONE & STYLE:
- Professional but personable
- Confident without being arrogant
- Enthusiastic about the opportunity
- Forward-looking and solution-oriented
- Authentic and genuine

Output only the answer to the question, no explanations or additional commentary."""

        self.user_prompt_template = """Job Description:
{job_description}

Candidate's Resume:
{resume_text}

Interview Question: {question}

Please provide a compelling, authentic answer to this interview question based on the candidate's actual experience and the job requirements."""
    
    def answer_question(
        self, 
        question: str, 
        job_description: str, 
        resume_text: str
    ) -> str:
        """
        Generate an answer to a custom interview question
        
        Args:
            question: The interview question to answer
            job_description: The target job description
            resume_text: The candidate's resume
            
        Returns:
            str: The generated answer
            
        Raises:
            ValueError: If inputs are invalid
            Exception: If OpenAI API call fails
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        if not job_description or not job_description.strip():
            raise ValueError("Job description cannot be empty")
        
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume cannot be empty")
        
        # Format the user prompt
        user_prompt = self.user_prompt_template.format(
            question=question.strip(),
            job_description=job_description.strip(),
            resume_text=resume_text.strip()
        )
        
        # Generate answer using OpenAI
        try:
            answer = self.openai_client.generate_response(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt
            )
            
            # Clean up the response
            answer = self._clean_answer_output(answer)
            
            return answer
        
        except Exception as e:
            raise Exception(f"Failed to generate answer: {str(e)}")
    
    def _clean_answer_output(self, answer_text: str) -> str:
        """
        Clean and format the answer output
        
        Args:
            answer_text: Raw answer text from LLM
            
        Returns:
            str: Cleaned answer text
        """
        # Remove any markdown formatting
        answer_text = answer_text.replace('**', '').replace('*', '').replace('_', '')
        
        # Clean up whitespace
        lines = [line.strip() for line in answer_text.split('\n')]
        
        # Remove empty lines at the beginning and end
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        
        # Join lines back together with proper spacing
        cleaned_answer = '\n'.join(lines)
        
        return cleaned_answer
    
    def validate_answer_output(self, answer_text: str) -> tuple[bool, str]:
        """
        Validate the generated answer output
        
        Args:
            answer_text: The generated answer text
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if not answer_text or not answer_text.strip():
            return False, "Answer output is empty"
        
        # Check minimum length
        if len(answer_text.strip()) < 50:
            return False, "Answer output is too short"
        
        # Check maximum length (should be concise but comprehensive)
        if len(answer_text.strip()) > 1500:
            return False, "Answer output is too long"
        
        return True, "Answer validation passed"
    
    def get_suggested_questions(self, job_description: str, base_resume: str = None) -> list:
        """
        Generate suggested interview questions based on both job description and resume
        
        Args:
            job_description: The job description text
            base_resume: The candidate's base resume (optional)
            
        Returns:
            list: List of suggested interview questions tailored to both job and resume
        """
        job_lower = job_description.lower()
        resume_lower = base_resume.lower() if base_resume else ""
        
        # Analyze both job and resume for intelligent question generation
        job_analysis = self._analyze_job_requirements(job_description)
        resume_analysis = self._analyze_resume_experience(base_resume) if base_resume else {}
        
        # Base questions that work for most roles
        base_questions = [
            "Why should we choose you for this position?",
            "What interests you most about this role?",
            "How do you handle challenging situations or tight deadlines?",
            "What's your greatest professional achievement?",
            "Where do you see yourself in 5 years?",
            "Why are you looking to leave your current position?",
            "What questions do you have for us?"
        ]
        
        # Generate questions based on job-resume gap analysis
        gap_questions = self._generate_gap_questions(job_analysis, resume_analysis)
        
        # Generate questions based on resume strengths
        strength_questions = self._generate_strength_questions(resume_analysis, job_analysis)
        
        # Role-specific questions based on job description
        role_specific = []
        
        # Technical/Engineering roles
        if any(term in job_lower for term in ['engineer', 'developer', 'technical', 'software']):
            role_specific.extend([
                "Walk me through your approach to debugging a complex issue.",
                "How do you stay current with new technologies and best practices?",
                "Describe a time when you had to make a technical decision with limited information.",
                "How do you approach code reviews and collaboration with other developers?"
            ])
        
        # Leadership/Senior roles
        if any(term in job_lower for term in ['senior', 'lead', 'manager', 'director']):
            role_specific.extend([
                "How do you mentor junior team members?",
                "Describe a time when you had to make a difficult decision as a leader.",
                "How do you handle conflicts within your team?",
                "What's your approach to setting and achieving team goals?"
            ])
        
        # Startup/Growth roles
        if any(term in job_lower for term in ['startup', 'fast-paced', 'growth', 'scale']):
            role_specific.extend([
                "How do you thrive in a fast-paced, changing environment?",
                "Describe a time when you had to wear multiple hats or take on responsibilities outside your role.",
                "How do you prioritize tasks when everything seems urgent?"
            ])
        
        # Remote work
        if any(term in job_lower for term in ['remote', 'distributed', 'work from home']):
            role_specific.extend([
                "How do you stay productive and motivated while working remotely?",
                "Describe your experience collaborating with distributed teams."
            ])
        
        # Combine all question types with intelligent prioritization
        all_questions = []
        
        # Always include top base questions
        all_questions.extend(base_questions[:4])
        
        # Add gap questions (high priority for interview prep)
        all_questions.extend(gap_questions[:3])
        
        # Add strength questions
        all_questions.extend(strength_questions[:2])
        
        # Add role-specific questions
        all_questions.extend(role_specific[:3])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_questions = []
        for question in all_questions:
            if question.lower() not in seen:
                seen.add(question.lower())
                unique_questions.append(question)
        
        return unique_questions[:12]  # Return top 12 questions
    
    def _analyze_job_requirements(self, job_description: str) -> dict:
        """
        Analyze job description to extract key requirements and expectations
        
        Args:
            job_description: The job description text
            
        Returns:
            dict: Analysis of job requirements
        """
        job_lower = job_description.lower()
        
        analysis = {
            'technical_skills': [],
            'soft_skills': [],
            'experience_level': 'mid',
            'leadership_required': False,
            'industry': 'general',
            'company_size': 'unknown',
            'key_responsibilities': [],
            'required_qualifications': []
        }
        
        # Extract technical skills
        tech_keywords = [
            'python', 'javascript', 'typescript', 'react', 'node.js', 'fastapi',
            'aws', 'gcp', 'docker', 'kubernetes', 'postgresql', 'mongodb',
            'machine learning', 'ai', 'llm', 'api', 'microservices', 'agile',
            'git', 'ci/cd', 'devops', 'cloud', 'database', 'frontend', 'backend'
        ]
        
        for skill in tech_keywords:
            if skill in job_lower:
                analysis['technical_skills'].append(skill)
        
        # Extract soft skills
        soft_keywords = [
            'leadership', 'collaboration', 'communication', 'problem-solving',
            'innovation', 'mentoring', 'cross-functional', 'strategic', 'analytical'
        ]
        
        for skill in soft_keywords:
            if skill in job_lower:
                analysis['soft_skills'].append(skill)
        
        # Determine experience level
        if any(term in job_lower for term in ['senior', 'lead', 'principal', '5+ years', '7+ years']):
            analysis['experience_level'] = 'senior'
        elif any(term in job_lower for term in ['junior', 'entry', '1-2 years', 'new grad']):
            analysis['experience_level'] = 'junior'
        
        # Check for leadership requirements
        analysis['leadership_required'] = any(term in job_lower for term in [
            'lead', 'manage', 'mentor', 'team lead', 'technical lead', 'supervise'
        ])
        
        # Determine industry
        industry_keywords = {
            'fintech': ['fintech', 'financial', 'banking', 'payments', 'trading'],
            'healthcare': ['healthcare', 'medical', 'health', 'patient', 'clinical'],
            'e-commerce': ['e-commerce', 'retail', 'marketplace', 'shopping', 'commerce'],
            'saas': ['saas', 'software as a service', 'b2b', 'platform', 'subscription'],
            'ai/ml': ['ai', 'machine learning', 'artificial intelligence', 'data science', 'ml']
        }
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in job_lower for keyword in keywords):
                analysis['industry'] = industry
                break
        
        return analysis
    
    def _analyze_resume_experience(self, resume_text: str) -> dict:
        """
        Analyze resume to extract experience, skills, and achievements
        
        Args:
            resume_text: The resume text
            
        Returns:
            dict: Analysis of resume experience
        """
        if not resume_text:
            return {}
        
        resume_lower = resume_text.lower()
        
        analysis = {
            'technical_skills': [],
            'leadership_experience': [],
            'major_achievements': [],
            'industries_worked': [],
            'company_types': [],
            'years_experience': 0,
            'education_level': 'bachelor',
            'certifications': []
        }
        
        # Extract technical skills from resume
        tech_keywords = [
            'python', 'javascript', 'typescript', 'react', 'node.js', 'fastapi',
            'aws', 'gcp', 'docker', 'kubernetes', 'postgresql', 'mongodb',
            'machine learning', 'ai', 'llm', 'api', 'microservices', 'agile'
        ]
        
        for skill in tech_keywords:
            if skill in resume_lower:
                analysis['technical_skills'].append(skill)
        
        # Extract leadership indicators
        leadership_keywords = [
            'led', 'managed', 'mentored', 'founded', 'architected', 'designed',
            'team lead', 'senior', 'principal', 'director'
        ]
        
        for keyword in leadership_keywords:
            if keyword in resume_lower:
                analysis['leadership_experience'].append(keyword)
        
        # Extract years of experience
        if '5+ years' in resume_lower or '5 years' in resume_lower:
            analysis['years_experience'] = 5
        elif any(term in resume_lower for term in ['3+ years', '4+ years']):
            analysis['years_experience'] = 3
        
        # Extract education level
        if 'master' in resume_lower or 'mba' in resume_lower:
            analysis['education_level'] = 'master'
        elif 'phd' in resume_lower or 'doctorate' in resume_lower:
            analysis['education_level'] = 'phd'
        
        # Extract company types
        if 'startup' in resume_lower or 'founding' in resume_lower:
            analysis['company_types'].append('startup')
        if any(term in resume_lower for term in ['enterprise', 'corporation', 'fortune']):
            analysis['company_types'].append('enterprise')
        
        return analysis
    
    def _generate_gap_questions(self, job_analysis: dict, resume_analysis: dict) -> list:
        """
        Generate questions based on gaps between job requirements and resume
        
        Args:
            job_analysis: Analysis of job requirements
            resume_analysis: Analysis of resume experience
            
        Returns:
            list: Questions addressing potential gaps
        """
        gap_questions = []
        
        # Check for technical skill gaps
        job_skills = set(job_analysis.get('technical_skills', []))
        resume_skills = set(resume_analysis.get('technical_skills', []))
        missing_skills = job_skills - resume_skills
        
        if missing_skills:
            gap_questions.append(f"How would you approach learning {', '.join(list(missing_skills)[:2])} for this role?")
        
        # Check for leadership gap
        if job_analysis.get('leadership_required') and not resume_analysis.get('leadership_experience'):
            gap_questions.append("How do you see yourself transitioning into a leadership role?")
        
        # Check for experience level gap
        if job_analysis.get('experience_level') == 'senior' and resume_analysis.get('years_experience', 0) < 5:
            gap_questions.append("How do you feel your experience prepares you for a senior-level position?")
        
        # Check for industry gap
        job_industry = job_analysis.get('industry', 'general')
        if job_industry != 'general' and job_industry not in resume_analysis.get('industries_worked', []):
            gap_questions.append(f"What interests you about working in the {job_industry} industry?")
        
        return gap_questions[:3]  # Return top 3 gap questions
    
    def _generate_strength_questions(self, resume_analysis: dict, job_analysis: dict) -> list:
        """
        Generate questions that highlight resume strengths relevant to the job
        
        Args:
            resume_analysis: Analysis of resume experience
            job_analysis: Analysis of job requirements
            
        Returns:
            list: Questions highlighting relevant strengths
        """
        strength_questions = []
        
        # Leadership strength questions
        if resume_analysis.get('leadership_experience') and job_analysis.get('leadership_required'):
            strength_questions.append("Can you describe your leadership style and how you motivate teams?")
        
        # Technical depth questions
        common_skills = set(resume_analysis.get('technical_skills', [])) & set(job_analysis.get('technical_skills', []))
        if common_skills:
            skill = list(common_skills)[0]
            strength_questions.append(f"Walk me through a challenging project where you used {skill} extensively.")
        
        # Startup experience questions
        if 'startup' in resume_analysis.get('company_types', []) and 'startup' in job_analysis.get('company_size', ''):
            strength_questions.append("What do you enjoy most about working in a startup environment?")
        
        # Innovation questions
        if resume_analysis.get('major_achievements'):
            strength_questions.append("Tell me about a time when you innovated or improved an existing process.")
        
        return strength_questions[:3]  # Return top 3 strength questions
