"""
Main orchestrator for the Resume & Cover Letter Agent
"""
import time
from typing import Optional, Dict, Any
from agents.resume_agent import ResumeAgent
from agents.cover_letter_agent import CoverLetterAgent
from integrations.google_docs import GoogleDocsClient
from utils.formatters import OutputFormatter
from config import Config


class ResumeAgentOrchestrator:
    """Main orchestrator that coordinates all agents and integrations"""
    
    def __init__(self):
        """Initialize the orchestrator with all required agents"""
        self.resume_agent = ResumeAgent()
        self.cover_letter_agent = CoverLetterAgent()
        self.google_docs_client = GoogleDocsClient()
        self.formatter = OutputFormatter()
    
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
            
            results['refined_resume'] = refined_resume
            self.formatter.print_success("Resume refined successfully")
            
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

