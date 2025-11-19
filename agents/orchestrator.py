"""
Main orchestrator for the Resume & Cover Letter Agent
"""
import time
from typing import Optional, Dict, Any
from agents.resume_agent import ResumeAgent
from agents.cover_letter_agent import CoverLetterAgent
from agents.qa_agent import QAAgent
from integrations.google_docs import GoogleDocsClient
from utils.formatters import OutputFormatter
from utils.input_handler import InputHandler
from config import Config


class ResumeAgentOrchestrator:
    """Main orchestrator that coordinates all agents and integrations"""
    
    def __init__(self):
        """Initialize the orchestrator with all required agents"""
        self.resume_agent = ResumeAgent()
        self.cover_letter_agent = CoverLetterAgent()
        self.qa_agent = QAAgent()
        self.google_docs_client = GoogleDocsClient()
        self.formatter = OutputFormatter()
        self.input_handler = InputHandler()
    
    def process_job_application(
        self, 
        job_description: str, 
        generate_cover_letter: bool = False,
        user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a complete job application workflow
        
        Args:
            job_description: The job description text
            generate_cover_letter: Whether to generate a cover letter
            user_name: User's name (optional)
            
        Returns:
            Dict[str, Any]: Results including refined resume, cover letter, and Google Docs info
            
        Raises:
            Exception: If any step in the process fails
        """
        start_time = time.time()
        results = {
            'refined_resume': None,
            'cover_letter': None,
            'google_docs_info': None,
            'processing_time': 0,
            'success': False,
            'errors': []
        }
        
        try:
            # Step 1: Refine the resume
            self.formatter.print_step_progress(1, 4, "Refining resume based on job description")
            self.formatter.print_processing("Analyzing job requirements and tailoring resume")
            
            refined_resume = self.resume_agent.refine_resume(job_description)
            
            # Load base resume for validation comparison
            base_resume = self.resume_agent.load_base_resume()
            
            # Validate resume output with base resume comparison
            is_valid, error_msg = self.resume_agent.validate_resume_output(refined_resume, base_resume)
            if not is_valid:
                raise ValueError(f"Resume validation failed: {error_msg}")
            
            # Analyze ATS optimization and provide insights
            ats_analysis = self.resume_agent.analyze_resume_match(refined_resume, job_description)
            
            results['refined_resume'] = refined_resume
            results['ats_analysis'] = ats_analysis
            self.formatter.print_success("Resume refined successfully")
            
            # Display ATS optimization insights
            self.display_ats_insights(ats_analysis)
            
            # Step 2: Upload to Google Docs
            self.formatter.print_step_progress(2, 4, "Uploading resume to Google Docs")
            self.formatter.print_processing("Authenticating with Google Docs and creating document")
            
            # Extract company and job title for document naming
            company_name, job_title = self.formatter.extract_company_and_job_title(job_description)
            doc_title = self.formatter.format_document_title(company_name, job_title)
            
            # Authenticate and create document
            self.google_docs_client.authenticate()
            google_docs_info = self.google_docs_client.create_resume_document(doc_title, refined_resume)
            
            results['google_docs_info'] = google_docs_info
            self.formatter.print_success("Resume uploaded to Google Docs")
            
            # Step 3: Generate cover letter (if requested)
            if generate_cover_letter:
                self.formatter.print_step_progress(3, 4, "Generating cover letter")
                self.formatter.print_processing("Creating personalized cover letter")
                
                cover_letter = self.cover_letter_agent.generate_cover_letter(
                    job_description, 
                    refined_resume,
                    user_name or Config.USER_NAME
                )
                
                # Validate cover letter output
                is_valid, error_msg = self.cover_letter_agent.validate_cover_letter_output(cover_letter)
                if not is_valid:
                    raise ValueError(f"Cover letter validation failed: {error_msg}")
                
                results['cover_letter'] = cover_letter
                self.formatter.print_success("Cover letter generated successfully")
                
                # Ask user if they want to save cover letter to Google Docs
                from utils.input_handler import InputHandler
                save_to_docs = InputHandler.get_user_confirmation(
                    "Would you like to save the cover letter to Google Docs?", 
                    default=True
                )
                
                if save_to_docs:
                    self.formatter.print_processing("Uploading cover letter to Google Docs")
                    
                    # Create cover letter document title
                    cover_letter_title = self.formatter.format_cover_letter_title(company_name)
                    
                    # Create cover letter document
                    cover_letter_docs_info = self.google_docs_client.create_cover_letter_document(
                        cover_letter_title, 
                        cover_letter
                    )
                    
                    results['cover_letter_docs_info'] = cover_letter_docs_info
                    self.formatter.print_success("Cover letter uploaded to Google Docs")
            else:
                self.formatter.print_step_progress(3, 4, "Skipping cover letter generation")
            
            # Step 4: Complete
            self.formatter.print_step_progress(4, 4, "Process completed")
            
            # Calculate processing time
            end_time = time.time()
            results['processing_time'] = end_time - start_time
            results['success'] = True
            
            return results
        
        except Exception as e:
            end_time = time.time()
            results['processing_time'] = end_time - start_time
            results['errors'].append(str(e))
            results['success'] = False
            raise e
    
    def display_results(self, results: Dict[str, Any]) -> None:
        """
        Display the results of the job application process
        
        Args:
            results: The results dictionary from process_job_application
        """
        if not results['success']:
            self.formatter.print_error("Process failed with errors:")
            for error in results['errors']:
                self.formatter.print_error(f"  - {error}")
            return
        
        # Display refined resume
        if results['refined_resume']:
            self.formatter.print_resume(results['refined_resume'])
        
        # Display Google Docs link
        if results['google_docs_info']:
            self.formatter.print_google_docs_link(
                results['google_docs_info']['document_url'],
                results['google_docs_info']['title']
            )
        
        # Display cover letter if generated
        if results['cover_letter']:
            self.formatter.print_cover_letter(results['cover_letter'])
        
        # Display cover letter Google Docs link if created
        if results.get('cover_letter_docs_info'):
            self.formatter.print_google_docs_link(
                results['cover_letter_docs_info']['document_url'],
                results['cover_letter_docs_info']['title']
            )
        
        # Display completion summary
        self.formatter.print_completion_summary(
            resume_generated=bool(results['refined_resume']),
            cover_letter_generated=bool(results['cover_letter']),
            google_docs_url=results['google_docs_info']['document_url'] if results['google_docs_info'] else None,
            processing_time=results['processing_time']
        )
    
    def test_all_integrations(self) -> Dict[str, bool]:
        """
        Test all integrations to ensure they're working
        
        Returns:
            Dict[str, bool]: Test results for each integration
        """
        test_results = {}
        
        # Test OpenAI connection
        try:
            test_results['openai'] = self.resume_agent.openai_client.test_connection()
        except Exception:
            test_results['openai'] = False
        
        # Test Google Docs connection
        try:
            test_results['google_docs'] = self.google_docs_client.test_connection()
        except Exception:
            test_results['google_docs'] = False
        
        # Test base resume loading
        try:
            self.resume_agent.load_base_resume()
            test_results['base_resume'] = True
        except Exception:
            test_results['base_resume'] = False
        
        return test_results
    
    def print_integration_status(self) -> None:
        """Print the status of all integrations"""
        self.formatter.print_header("INTEGRATION STATUS CHECK")
        
        test_results = self.test_all_integrations()
        
        for integration, status in test_results.items():
            if status:
                self.formatter.print_success(f"{integration.replace('_', ' ').title()}: Connected")
            else:
                self.formatter.print_error(f"{integration.replace('_', ' ').title()}: Failed")
        
        all_good = all(test_results.values())
        
        if all_good:
            self.formatter.print_success("All integrations are working correctly!")
        else:
            self.formatter.print_warning("Some integrations need attention. Please check your configuration.")
        
        return all_good
    
    def run_qa_session(
        self, 
        job_description: str, 
        resume_text: str,
        interactive: bool = True
    ) -> Dict[str, Any]:
        """
        Run an interactive Q&A session for interview preparation
        
        Args:
            job_description: The job description
            resume_text: The refined resume text
            interactive: Whether to run in interactive mode
            
        Returns:
            Dict[str, Any]: Q&A session results
        """
        qa_results = {
            'questions_answered': [],
            'suggested_questions': [],
            'session_completed': False
        }
        
        try:
            self.formatter.print_header("INTERVIEW Q&A SESSION")
            self.formatter.print_info("Let's prepare you for the interview! You can ask custom questions or choose from suggestions.")
            
            # Load base resume for comprehensive analysis
            base_resume = self.resume_agent.load_base_resume()
            
            # Get suggested questions based on both job description and base resume
            suggested_questions = self.qa_agent.get_suggested_questions(job_description, base_resume)
            qa_results['suggested_questions'] = suggested_questions
            
            # Display suggested questions
            self.formatter.print_section("Suggested Questions", "")
            for i, question in enumerate(suggested_questions[:8], 1):  # Show top 8
                self.formatter.print_info(f"{i}. {question}")
            
            if not interactive:
                return qa_results
            
            self.formatter.print_info("\nOptions:")
            self.formatter.print_info("• Type a custom question")
            self.formatter.print_info("• Enter a number (1-8) to select a suggested question")
            self.formatter.print_info("• Type 'done' to finish the Q&A session")
            
            question_count = 0
            max_questions = 20  # Extended limit for comprehensive interview preparation
            
            while question_count < max_questions:
                try:
                    self.formatter.print_info(f"\n--- Question {question_count + 1} ---")
                    user_input = input("Enter your question (or 'done' to finish): ").strip()
                    
                    if user_input.lower() in ['done', 'exit', 'quit', 'finish']:
                        break
                    
                    # Check if user selected a suggested question by number
                    if user_input.isdigit():
                        question_num = int(user_input)
                        if 1 <= question_num <= len(suggested_questions):
                            question = suggested_questions[question_num - 1]
                        else:
                            self.formatter.print_error(f"Invalid number. Please choose 1-{len(suggested_questions)} or enter a custom question.")
                            continue
                    else:
                        question = user_input
                    
                    if not question or len(question.strip()) < 5:
                        self.formatter.print_error("Please enter a valid question (at least 5 characters).")
                        continue
                    
                    # Generate answer
                    self.formatter.print_processing(f"Generating answer for: '{question}'")
                    
                    answer = self.qa_agent.answer_question(
                        question=question,
                        job_description=job_description,
                        resume_text=resume_text
                    )
                    
                    # Validate answer
                    is_valid, error_msg = self.qa_agent.validate_answer_output(answer)
                    if not is_valid:
                        self.formatter.print_warning(f"Answer validation warning: {error_msg}")
                    
                    # Display the answer
                    self.formatter.print_section(f"Q: {question}", answer)
                    
                    # Store the Q&A pair
                    qa_results['questions_answered'].append({
                        'question': question,
                        'answer': answer,
                        'timestamp': time.time()
                    })
                    
                    question_count += 1
                    
                except KeyboardInterrupt:
                    self.formatter.print_info("\nQ&A session interrupted by user.")
                    break
                except Exception as e:
                    self.formatter.print_error(f"Error generating answer: {str(e)}")
                    continue
            
            qa_results['session_completed'] = True
            
            # Display session summary
            self.formatter.print_header("Q&A SESSION SUMMARY")
            self.formatter.print_success(f"Answered {len(qa_results['questions_answered'])} questions")
            
            if qa_results['questions_answered']:
                self.formatter.print_info("Questions covered:")
                for i, qa in enumerate(qa_results['questions_answered'], 1):
                    self.formatter.print_info(f"{i}. {qa['question']}")
            
            self.formatter.print_info("💡 Tip: Practice these answers out loud to build confidence!")
            
            return qa_results
        
        except Exception as e:
            self.formatter.print_error(f"Q&A session failed: {str(e)}")
            qa_results['error'] = str(e)
            return qa_results
    
    def quick_qa(self, question: str, job_description: str, resume_text: str) -> str:
        """
        Quick Q&A for single questions (non-interactive)
        
        Args:
            question: The question to answer
            job_description: The job description
            resume_text: The resume text
            
        Returns:
            str: The generated answer
        """
        try:
            answer = self.qa_agent.answer_question(
                question=question,
                job_description=job_description,
                resume_text=resume_text
            )
            return answer
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def display_ats_insights(self, ats_analysis: dict) -> None:
        """
        Display ATS optimization insights to the user
        
        Args:
            ats_analysis: ATS analysis results from resume matching
        """
        if not ats_analysis:
            return
        
        self.formatter.print_header("ATS OPTIMIZATION INSIGHTS")
        
        # Display ATS optimization score
        ats_score = ats_analysis.get('ats_optimization_score', 0)
        match_percentage = ats_analysis.get('match_percentage', 0)
        
        if ats_score >= 85:
            self.formatter.print_success(f"🚀 Excellent ATS Score: {ats_score:.1f}% (Match: {match_percentage:.1f}%)")
        elif ats_score >= 70:
            self.formatter.print_info(f"✅ Good ATS Score: {ats_score:.1f}% (Match: {match_percentage:.1f}%)")
        else:
            self.formatter.print_warning(f"⚠️  Needs Improvement: {ats_score:.1f}% (Match: {match_percentage:.1f}%)")
        
        # Display matched keywords
        tech_matches = ats_analysis.get('technical_matches', {})
        if tech_matches:
            self.formatter.print_info(f"✅ Matched {len(tech_matches)} critical technical keywords:")
            for keyword, data in list(tech_matches.items())[:5]:  # Show top 5
                self.formatter.print_info(f"   • {keyword} (variations: {', '.join(data['matched_variations'][:3])})")
        
        # Display missing high-priority keywords
        missing_high = ats_analysis.get('missing_high_priority', [])
        if missing_high:
            self.formatter.print_warning(f"🔴 Missing HIGH PRIORITY keywords: {', '.join(missing_high[:5])}")
        
        # Display action verb and quantification scores
        action_score = ats_analysis.get('action_verb_score', 0)
        quant_score = ats_analysis.get('quantification_score', 0)
        
        self.formatter.print_info(f"💪 Action Verbs Score: {action_score:.1f}%")
        self.formatter.print_info(f"📊 Quantification Score: {quant_score:.1f}%")
        
        # Display irrelevant content warnings
        irrelevant = ats_analysis.get('irrelevant_content', [])
        if irrelevant:
            self.formatter.print_warning(f"🗑️  Consider removing: {', '.join(irrelevant[:3])}")
        
        # Display optimization tips
        tips = ats_analysis.get('ats_optimization_tips', [])
        if tips:
            self.formatter.print_info("🎯 ATS Optimization Tips:")
            for tip in tips[:4]:  # Show top 4 tips
                self.formatter.print_info(f"   • {tip}")
        
        print()  # Add spacing
    
    def generate_ats_report(self, job_description: str, refined_resume: str) -> dict:
        """
        Generate a comprehensive ATS optimization report
        
        Args:
            job_description: The job description text
            refined_resume: The refined resume text
            
        Returns:
            dict: Comprehensive ATS report
        """
        # Extract job keywords for analysis
        job_keywords = self.resume_agent.extract_job_keywords(job_description)
        
        # Perform detailed resume analysis
        ats_analysis = self.resume_agent.analyze_resume_match(refined_resume, job_description)
        
        # Identify potential improvements
        irrelevant_sections = self.resume_agent.identify_irrelevant_sections(refined_resume, job_keywords)
        
        report = {
            'job_analysis': {
                'total_keywords_identified': job_keywords.get('total_importance_score', 0),
                'critical_technical_skills': len([k for k, v in job_keywords.get('technical', {}).items() if v.get('importance', 0) >= 8]),
                'action_verbs_in_job': len(job_keywords.get('action_verbs', [])),
                'metrics_expectations': job_keywords.get('metrics_expectations', [])
            },
            'resume_performance': {
                'ats_score': ats_analysis.get('ats_optimization_score', 0),
                'keyword_match_percentage': ats_analysis.get('match_percentage', 0),
                'technical_keywords_matched': len(ats_analysis.get('technical_matches', {})),
                'missing_critical_keywords': len(ats_analysis.get('missing_high_priority', [])),
                'action_verb_alignment': ats_analysis.get('action_verb_score', 0),
                'quantification_strength': ats_analysis.get('quantification_score', 0)
            },
            'improvement_opportunities': {
                'high_priority_additions': ats_analysis.get('missing_high_priority', [])[:5],
                'content_to_consider_removing': irrelevant_sections[:3],
                'optimization_tips': ats_analysis.get('ats_optimization_tips', []),
                'keyword_density_status': 'Optimal' if ats_analysis.get('match_percentage', 0) > 75 else 'Needs Improvement'
            },
            'competitive_advantages': {
                'unique_technical_combinations': list(ats_analysis.get('technical_matches', {}).keys())[:5],
                'leadership_indicators': len([k for k in ats_analysis.get('soft_skill_matches', {}) if 'leadership' in k.lower()]),
                'scale_experience_highlighted': any('scale' in str(v).lower() for v in ats_analysis.get('technical_matches', {}).values())
            }
        }
        
        return report

