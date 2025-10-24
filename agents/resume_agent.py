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
        self.system_prompt = """You are an expert resume writer and ATS optimization specialist who creates resumes that pass Applicant Tracking Systems and get interviews.

Your mission: Transform resumes to perfectly match job requirements while ensuring maximum ATS compatibility and recruiter appeal.

CRITICAL PRESERVATION RULES - DO NOT MODIFY:
- Keep ALL educational details exactly as written (degrees, institutions, dates, coursework, GPA, honors)
- Preserve ALL job titles, company names, locations, and employment dates exactly as stated
- Maintain the candidate's level of professional seniority (Senior, Lead, Founding, etc.)
- Keep the stated years of experience (6+ years) - never reduce experience level
- Do not change any factual information about roles, companies, or achievements

CORE OPTIMIZATION MANDATE:
The resume MUST be tailored for THIS SPECIFIC JOB. Generic resumes fail. Every word should serve the goal of getting past ATS and securing an interview.

ATS DOMINANCE STRATEGIES:

KEYWORD MASTERY (CRITICAL FOR ATS):
- MIRROR JOB LANGUAGE: Use EXACT phrases from job description, not paraphrased versions
- KEYWORD DENSITY: Achieve 10-15% keyword density without keyword stuffing  
- VARIATION INTEGRATION: Include technical terms AND business language (e.g., "ML", "Machine Learning", "Artificial Intelligence")
- ACRONYM STRATEGY: Use both abbreviated and full forms (e.g., "API" and "Application Programming Interface")
- SKILL SYNONYMS: Include multiple ways to express same competency (e.g., "JavaScript", "JS", "ECMAScript", "Node.js")
- CONTEXT EMBEDDING: Weave keywords naturally into achievement descriptions, not just skills lists

RELEVANCE PRIORITIZATION (ELIMINATE ATS KILLERS):
- RELEVANCE HIERARCHY: Rank every line by direct job relevance (1-10 scale) - prioritize 8+ rated content
- REMOVE IRRELEVANCIES: Cut hobbies, unrelated interests, outdated technologies that don't serve this job
- SPACE OPTIMIZATION: Every line must earn its place - remove generic fluff to make room for job-critical details
- SECTION ORDERING: Lead with most job-relevant sections (often Technical Skills before Experience for tech roles)
- BULLET PRIORITIZATION: Reorder achievements within each role by relevance to target position

ACTION VERB TRANSFORMATION (MAKE EVERY BULLET POWERFUL):
- STRONG ACTION VERBS: Replace weak language ("responsible for", "worked on", "helped") with powerful verbs ("architected", "spearheaded", "optimized")
- JOB-SPECIFIC VERBS: Prioritize action verbs that appear in the job description
- QUANTIFIED ACHIEVEMENTS: Transform every possible accomplishment into measurable impact using numbers, percentages, scale indicators
- RESULT-ORIENTED LANGUAGE: Focus on outcomes and business impact, not just tasks performed
- PROGRESSION INDICATORS: Show increasing responsibility and scope across roles

ADVANCED ATS OPTIMIZATION:

CONTENT INTELLIGENCE:
- IMPACT QUANTIFICATION: Every bullet point should include metrics when possible (performance improvements, user scale, team size, timeline achievements)
- PROBLEM-SOLUTION FRAMING: Present experience as solutions to problems the target company likely faces
- TECHNOLOGY STACK ALIGNMENT: Prominently feature tech stack mentioned in job posting
- SCALE INDICATORS: Emphasize experience with scale/complexity relevant to target role
- BUSINESS VALUE CONNECTION: Link technical achievements to business outcomes

INDUSTRY & ROLE ADAPTATION:
- COMPANY-SIZE MATCHING: Emphasize startup agility for startups, enterprise scale for large companies  
- ROLE-LEVEL POSITIONING: For senior roles, lead with leadership/architecture; for IC roles, emphasize implementation depth
- METHODOLOGY ALIGNMENT: Highlight Agile/Scrum, DevOps, or specific processes mentioned in job description
- REMOTE WORK SIGNALS: Emphasize distributed collaboration if role is remote
- GROWTH STAGE MATCHING: Highlight relevant experience (0-1 products for early stage, scale challenges for growth stage)

PSYCHOLOGICAL POSITIONING:
- CONFIDENCE PROJECTION: Use assertive language that demonstrates ownership and results
- INNOVATION EMPHASIS: Highlight creative problem-solving and cutting-edge technology adoption
- COLLABORATION BALANCE: Show both individual contribution and team leadership capabilities
- LEARNING AGILITY: Demonstrate adaptation to new technologies and continuous skill development
- FUTURE-READY POSITIONING: Emphasize emerging technologies and forward-thinking approaches

STRATEGIC CONTENT RULES:

WHAT TO AMPLIFY:
- Direct technology matches with job requirements
- Leadership and mentoring experience (for senior roles)
- Scale achievements that match company needs
- Cross-functional collaboration
- Performance optimizations and measurable improvements
- Innovation and problem-solving examples

WHAT TO MINIMIZE/REMOVE:
- Hobbies unrelated to professional capabilities
- Outdated technologies not mentioned in job posting
- Entry-level or intern experiences (for senior positions)
- Generic responsibilities without specific achievements
- Overly technical jargon that doesn't appear in job description

EXECUTION GUIDELINES:
- Write in active voice with strong action verbs
- Use present tense for current role, past tense for previous roles
- Maintain 2-3 line bullet points for optimal ATS parsing
- Include keywords naturally within context, never in isolation
- Balance hard skills with relevant soft skills
- Show career progression and increasing impact

QUALITY ASSURANCE:
- Every bullet point must serve the goal of getting THIS specific job
- Keywords should feel natural, never forced
- Maintain truthfulness while maximizing impact presentation
- Ensure ATS parseable format (no tables, graphics, or complex formatting)

Output only the refined resume text optimized for maximum ATS compatibility and interview potential."""

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
            
            # Check that appropriate seniority levels are preserved (more flexible)
            # Allow some flexibility in seniority terms based on job context
            critical_seniority_terms = ['senior', '6+ years', 'lead']  # Core seniority indicators
            preserved_seniority = 0
            
            for term in critical_seniority_terms:
                if term in base_lower and term in refined_lower:
                    preserved_seniority += 1
            
            # Ensure at least one key seniority indicator is preserved
            if preserved_seniority == 0 and any(term in base_lower for term in critical_seniority_terms):
                return False, "Critical seniority indicators were removed - please preserve experience level"
            
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
        Extract and categorize keywords from job description with advanced ATS optimization
        
        Args:
            job_description: The job description text
            
        Returns:
            dict: Categorized keywords with importance scores for optimization
        """
        job_lower = job_description.lower()
        job_text = job_description
        
        # Enhanced technical skills with variations and importance scoring
        tech_keywords = {}
        tech_terms_with_variations = {
            'python': ['python', 'py', 'django', 'flask', 'fastapi', 'python3'],
            'javascript': ['javascript', 'js', 'ecmascript', 'vanilla js', 'node'],
            'typescript': ['typescript', 'ts', 'type script'],
            'react': ['react', 'reactjs', 'react.js', 'react native', 'jsx'],
            'node.js': ['node.js', 'nodejs', 'node js', 'express', 'express.js'],
            'aws': ['aws', 'amazon web services', 'ec2', 'lambda', 's3', 'cloudformation'],
            'gcp': ['gcp', 'google cloud', 'google cloud platform'],
            'docker': ['docker', 'containerization', 'containers', 'dockerfile'],
            'kubernetes': ['kubernetes', 'k8s', 'kubectl', 'helm', 'container orchestration'],
            'postgresql': ['postgresql', 'postgres', 'psql', 'pg'],
            'mongodb': ['mongodb', 'mongo', 'nosql', 'document database'],
            'machine learning': ['machine learning', 'ml', 'artificial intelligence', 'ai'],
            'api': ['api', 'restful', 'rest', 'graphql', 'microservices'],
            'ci/cd': ['ci/cd', 'continuous integration', 'continuous deployment', 'devops'],
            'git': ['git', 'github', 'gitlab', 'version control', 'source control'],
            'agile': ['agile', 'scrum', 'kanban', 'sprint', 'jira'],
            'redis': ['redis', 'caching', 'in-memory database'],
            'elasticsearch': ['elasticsearch', 'elk', 'search engine', 'full-text search'],
            'terraform': ['terraform', 'infrastructure as code', 'iac'],
            'nextjs': ['next.js', 'nextjs', 'next js'],
            'fastapi': ['fastapi', 'fast api'],
            'langchain': ['langchain', 'lang chain', 'llm framework'],
            'openai': ['openai', 'gpt', 'llm integration'],
            'supabase': ['supabase', 'firebase', 'backend as a service'],
            'zustand': ['zustand', 'state management']
        }
        
        # Calculate frequency and importance for tech keywords
        for primary_term, variations in tech_terms_with_variations.items():
            total_mentions = 0
            found_variations = []
            
            for variation in variations:
                count = job_lower.count(variation.lower())
                if count > 0:
                    total_mentions += count
                    found_variations.append(variation)
            
            if total_mentions > 0:
                # Higher score for multiple mentions and variations
                importance_score = min(10, total_mentions * 2 + len(found_variations))
                tech_keywords[primary_term] = {
                    'mentions': total_mentions,
                    'variations': found_variations,
                    'importance': importance_score
                }
        
        # Enhanced soft skills with context awareness
        soft_keywords = {}
        soft_terms_patterns = {
            'leadership': ['lead', 'leadership', 'manage', 'mentor', 'guide', 'supervise'],
            'collaboration': ['collaborate', 'teamwork', 'cross-functional', 'work with'],
            'communication': ['communicate', 'present', 'explain', 'articulate', 'documentation'],
            'problem-solving': ['problem-solving', 'troubleshoot', 'debug', 'resolve', 'solve'],
            'innovation': ['innovative', 'creative', 'improve', 'optimize', 'enhance'],
            'analytical': ['analytical', 'analyze', 'data-driven', 'metrics', 'insights'],
            'strategic': ['strategic', 'planning', 'roadmap', 'vision', 'long-term'],
            'adaptability': ['adaptable', 'flexible', 'learn', 'growth mindset', 'evolve']
        }
        
        for skill, patterns in soft_terms_patterns.items():
            mentions = 0
            found_patterns = []
            
            for pattern in patterns:
                if pattern in job_lower:
                    mentions += job_lower.count(pattern)
                    found_patterns.append(pattern)
            
            if mentions > 0:
                soft_keywords[skill] = {
                    'mentions': mentions,
                    'patterns': found_patterns,
                    'importance': min(8, mentions * 2)
                }
        
        # Industry and context keywords with importance
        industry_keywords = {}
        industry_terms = {
            'startup': ['startup', 'early-stage', 'founding', 'scale-up'],
            'enterprise': ['enterprise', 'large-scale', 'fortune', 'corporate'],
            'saas': ['saas', 'software as a service', 'b2b', 'platform'],
            'fintech': ['fintech', 'financial', 'banking', 'payments'],
            'healthcare': ['healthcare', 'medical', 'health', 'patient'],
            'e-commerce': ['e-commerce', 'retail', 'marketplace', 'shopping'],
            'remote': ['remote', 'distributed', 'work from home', 'virtual'],
            'performance': ['performance', 'optimization', 'scaling', 'efficiency'],
            'security': ['security', 'authentication', 'authorization', 'encryption'],
            'analytics': ['analytics', 'data', 'metrics', 'insights', 'reporting']
        }
        
        for category, terms in industry_terms.items():
            mentions = 0
            for term in terms:
                if term in job_lower:
                    mentions += job_lower.count(term)
            
            if mentions > 0:
                industry_keywords[category] = {
                    'mentions': mentions,
                    'importance': min(6, mentions * 2)
                }
        
        # Extract action verbs for bullet point enhancement
        action_verbs = self._extract_action_verbs(job_description)
        
        # Extract quantifiable metrics expectations
        metrics_expectations = self._extract_metrics_context(job_description)
        
        return {
            'technical': tech_keywords,
            'soft_skills': soft_keywords,
            'industry': industry_keywords,
            'action_verbs': action_verbs,
            'metrics_expectations': metrics_expectations,
            'total_importance_score': (
                sum(kw.get('importance', 0) for kw in tech_keywords.values()) +
                sum(kw.get('importance', 0) for kw in soft_keywords.values()) +
                sum(kw.get('importance', 0) for kw in industry_keywords.values())
            )
        }
    
    def _extract_action_verbs(self, job_description: str) -> list:
        """
        Extract action verbs from job description to enhance bullet points
        
        Args:
            job_description: The job description text
            
        Returns:
            list: Action verbs found in the job description
        """
        # Strong action verbs commonly used in job descriptions
        strong_action_verbs = [
            'architect', 'build', 'create', 'develop', 'design', 'implement', 'engineer',
            'deliver', 'execute', 'manage', 'lead', 'drive', 'optimize', 'improve',
            'enhance', 'streamline', 'automate', 'integrate', 'collaborate', 'coordinate',
            'spearhead', 'establish', 'maintain', 'deploy', 'scale', 'monitor',
            'troubleshoot', 'resolve', 'analyze', 'evaluate', 'research', 'innovate',
            'transform', 'modernize', 'accelerate', 'achieve', 'exceed', 'increase',
            'reduce', 'minimize', 'maximize', 'ensure', 'guarantee', 'facilitate',
            'contribute', 'participate', 'support', 'mentor', 'guide', 'train'
        ]
        
        job_lower = job_description.lower()
        found_verbs = []
        
        for verb in strong_action_verbs:
            if verb in job_lower:
                found_verbs.append(verb)
        
        return found_verbs
    
    def _extract_metrics_context(self, job_description: str) -> list:
        """
        Extract metrics and quantification context from job description
        
        Args:
            job_description: The job description text
            
        Returns:
            list: Metrics and quantification patterns found
        """
        import re
        
        metrics_patterns = [
            r'\d+\+?\s*years?',  # "5+ years", "3 years"
            r'\d+\+?\s*million',  # "1+ million"
            r'\d+\+?\s*billion',  # "1+ billion"
            r'\d+\+?\s*%',  # "99%", "15%"
            r'\d+\+?\s*users?',  # "1000+ users"
            r'\d+\+?\s*requests?',  # "10000+ requests"
            r'\d+\+?\s*transactions?',  # "1M+ transactions"
            r'\d+\+?\s*customers?',  # "500+ customers"
            r'scale\s+to\s+\d+',  # "scale to 1000"
            r'handle\s+\d+',  # "handle 5000"
            r'support\s+\d+',  # "support 10000"
        ]
        
        # Context words that suggest quantifiable achievements
        metrics_context = [
            'performance', 'efficiency', 'throughput', 'latency', 'uptime',
            'availability', 'scalability', 'growth', 'increase', 'improve',
            'reduce', 'optimize', 'accelerate', 'users', 'traffic', 'load',
            'volume', 'capacity', 'speed', 'time', 'cost', 'revenue'
        ]
        
        found_metrics = []
        job_lower = job_description.lower()
        
        # Extract numerical patterns
        for pattern in metrics_patterns:
            matches = re.findall(pattern, job_lower)
            found_metrics.extend(matches)
        
        # Extract context words
        for context in metrics_context:
            if context in job_lower:
                found_metrics.append(context)
        
        return list(set(found_metrics))  # Remove duplicates
    
    def identify_irrelevant_sections(self, resume_text: str, job_keywords: dict) -> list:
        """
        Identify sections or content that might be irrelevant to the job
        
        Args:
            resume_text: The resume text
            job_keywords: Keywords extracted from job description
            
        Returns:
            list: Sections/content that could be considered irrelevant
        """
        irrelevant_indicators = []
        resume_lower = resume_text.lower()
        
        # Hobby/personal interest indicators that might not be relevant
        personal_interests = [
            'basketball', 'football', 'soccer', 'tennis', 'golf', 'swimming',
            'hiking', 'cooking', 'baking', 'reading', 'traveling', 'photography',
            'music', 'guitar', 'piano', 'singing', 'dancing', 'painting',
            'knitting', 'gardening', 'yoga', 'meditation', 'volunteering'
        ]
        
        # Check for personal interests that don't relate to job
        tech_job = any(kw in job_keywords.get('technical', {}) for kw in ['python', 'javascript', 'react'])
        
        for interest in personal_interests:
            if interest in resume_lower:
                # Only flag as irrelevant if it's truly unrelated to the job context
                if tech_job and interest not in ['volunteering', 'teaching', 'mentoring']:
                    irrelevant_indicators.append(f"Personal interest: {interest}")
        
        # Check for outdated or overly junior experiences (if applying for senior role)
        job_requires_senior = any(term in str(job_keywords) for term in ['senior', 'lead', '5+ years'])
        
        if job_requires_senior:
            junior_indicators = ['intern', 'entry-level', 'junior', 'assistant']
            for indicator in junior_indicators:
                if indicator in resume_lower:
                    irrelevant_indicators.append(f"Junior-level reference: {indicator}")
        
        # Check for technology mismatches
        job_tech = set(job_keywords.get('technical', {}).keys())
        outdated_tech = ['flash', 'silverlight', 'internet explorer', 'jquery', 'php4']
        
        for tech in outdated_tech:
            if tech in resume_lower and tech not in job_tech:
                irrelevant_indicators.append(f"Potentially outdated technology: {tech}")
        
        return irrelevant_indicators
    
    def enhance_bullet_points_with_action_verbs(self, resume_text: str, action_verbs: list) -> str:
        """
        Enhance resume bullet points with stronger action verbs
        
        Args:
            resume_text: The resume text
            action_verbs: Action verbs from job description
            
        Returns:
            str: Resume with enhanced action verbs
        """
        # Mapping of weak verbs to stronger alternatives
        verb_improvements = {
            'responsible for': 'led',
            'worked on': 'developed',
            'helped': 'collaborated',
            'did': 'executed',
            'made': 'created',
            'used': 'leveraged',
            'was involved': 'contributed',
            'participated in': 'drove',
            'assisted': 'supported',
            'handled': 'managed'
        }
        
        enhanced_resume = resume_text
        
        # Replace weak phrases with stronger action verbs
        for weak, strong in verb_improvements.items():
            # Use job-specific action verbs when available
            if action_verbs and any(verb in enhanced_resume.lower() for verb in action_verbs):
                # Prioritize action verbs from the job description
                job_verb = next((verb for verb in action_verbs if verb in enhanced_resume.lower()), strong)
                enhanced_resume = enhanced_resume.replace(weak, job_verb)
            else:
                enhanced_resume = enhanced_resume.replace(weak, strong)
        
        return enhanced_resume
    
    def analyze_resume_match(self, resume_text: str, job_description: str) -> dict:
        """
        Analyze how well the resume matches the job description with enhanced ATS scoring
        
        Args:
            resume_text: The resume text
            job_description: The job description
            
        Returns:
            dict: Enhanced match analysis results with ATS optimization insights
        """
        job_keywords = self.extract_job_keywords(job_description)
        resume_lower = resume_text.lower()
        
        matches = {
            'technical_matches': {},
            'soft_skill_matches': {},
            'industry_matches': {},
            'missing_high_priority': [],
            'missing_medium_priority': [],
            'action_verb_score': 0,
            'quantification_score': 0,
            'irrelevant_content': [],
            'ats_optimization_tips': []
        }
        
        # Enhanced technical keyword matching with importance weighting
        total_tech_importance = 0
        matched_tech_importance = 0
        
        for keyword, data in job_keywords['technical'].items():
            total_tech_importance += data['importance']
            
            # Check for exact keyword or its variations
            keyword_found = False
            matched_variations = []
            
            for variation in data['variations']:
                if variation.lower() in resume_lower:
                    keyword_found = True
                    matched_variations.append(variation)
            
            if keyword_found:
                matched_tech_importance += data['importance']
                matches['technical_matches'][keyword] = {
                    'matched_variations': matched_variations,
                    'importance': data['importance']
                }
            else:
                # Categorize missing keywords by importance
                if data['importance'] >= 8:
                    matches['missing_high_priority'].append(keyword)
                elif data['importance'] >= 5:
                    matches['missing_medium_priority'].append(keyword)
        
        # Enhanced soft skills matching
        total_soft_importance = 0
        matched_soft_importance = 0
        
        for skill, data in job_keywords['soft_skills'].items():
            total_soft_importance += data['importance']
            
            skill_found = any(pattern in resume_lower for pattern in data['patterns'])
            if skill_found:
                matched_soft_importance += data['importance']
                matches['soft_skill_matches'][skill] = data['importance']
            else:
                if data['importance'] >= 6:
                    matches['missing_high_priority'].append(f"{skill} (soft skill)")
        
        # Industry context matching
        total_industry_importance = 0
        matched_industry_importance = 0
        
        for category, data in job_keywords['industry'].items():
            total_industry_importance += data['importance']
            
            if category in ['remote', 'startup', 'enterprise']:  # Context-based categories
                context_terms = {
                    'remote': ['remote', 'distributed', 'virtual team'],
                    'startup': ['startup', 'early-stage', 'founding'],
                    'enterprise': ['enterprise', 'large-scale', 'corporate']
                }
                
                if any(term in resume_lower for term in context_terms.get(category, [])):
                    matched_industry_importance += data['importance']
                    matches['industry_matches'][category] = data['importance']
        
        # Action verb analysis
        action_verbs_in_job = job_keywords['action_verbs']
        action_verbs_in_resume = [verb for verb in action_verbs_in_job if verb in resume_lower]
        matches['action_verb_score'] = (len(action_verbs_in_resume) / max(1, len(action_verbs_in_job))) * 100
        
        # Quantification analysis
        metrics_expected = job_keywords['metrics_expectations']
        # Simple check for numbers and percentages in resume
        import re
        numbers_in_resume = len(re.findall(r'\d+[%\+]?', resume_text))
        matches['quantification_score'] = min(100, numbers_in_resume * 10)  # Score based on quantified achievements
        
        # Identify irrelevant content
        matches['irrelevant_content'] = self.identify_irrelevant_sections(resume_text, job_keywords)
        
        # Calculate overall ATS optimization score
        total_possible_importance = total_tech_importance + total_soft_importance + total_industry_importance
        total_matched_importance = matched_tech_importance + matched_soft_importance + matched_industry_importance
        
        base_match_percentage = (total_matched_importance / max(1, total_possible_importance)) * 100
        
        # Bonus factors for ATS optimization
        action_verb_bonus = min(20, matches['action_verb_score'] * 0.2)
        quantification_bonus = min(15, matches['quantification_score'] * 0.15)
        relevance_penalty = min(10, len(matches['irrelevant_content']) * 2)  # Penalty for irrelevant content
        
        ats_score = min(100, base_match_percentage + action_verb_bonus + quantification_bonus - relevance_penalty)
        
        matches['match_percentage'] = base_match_percentage
        matches['ats_optimization_score'] = ats_score
        
        # Generate ATS optimization tips
        if len(matches['missing_high_priority']) > 0:
            matches['ats_optimization_tips'].append(
                f"HIGH PRIORITY: Include these critical keywords: {', '.join(matches['missing_high_priority'][:3])}"
            )
        
        if matches['action_verb_score'] < 50:
            matches['ats_optimization_tips'].append(
                "IMPROVE: Use stronger action verbs from the job description in your bullet points"
            )
        
        if matches['quantification_score'] < 40:
            matches['ats_optimization_tips'].append(
                "QUANTIFY: Add more numbers, percentages, and measurable achievements"
            )
        
        if len(matches['irrelevant_content']) > 2:
            matches['ats_optimization_tips'].append(
                f"REMOVE: Consider removing irrelevant content to make room for job-relevant details"
            )
        
        return matches

