#!/usr/bin/env python3
"""
Resume & Cover Letter Agent - Main CLI Entry Point

A Python CLI application that leverages LangChain and OpenAI's LLM to automatically 
refine resumes and generate cover letters tailored to specific job descriptions.
"""
import sys
import click
from typing import Optional
from config import Config
from utils.input_handler import InputHandler
from utils.formatters import OutputFormatter
from agents.orchestrator import ResumeAgentOrchestrator


@click.command()
@click.option('--test', is_flag=True, help='Test all integrations without processing')
@click.option('--job-file', type=click.Path(exists=True), help='Path to file containing job description')
@click.option('--no-cover-letter', is_flag=True, help='Skip cover letter generation')
@click.option('--no-qa', is_flag=True, help='Skip Q&A session')
@click.option('--user-name', type=str, help='Override user name for cover letter')
@click.option('--question', type=str, help='Ask a single question and exit')
@click.option('--ats-report', is_flag=True, help='Generate ATS optimization report only')
@click.version_option(version='1.0.0', prog_name='Resume Agent')
def main(
    test: bool,
    job_file: Optional[str],
    no_cover_letter: bool,
    no_qa: bool,
    user_name: Optional[str],
    question: Optional[str],
    ats_report: bool
):
    """
    Resume & Cover Letter Agent
    
    Automatically refine your resume and generate cover letters tailored to specific job descriptions.
    The refined resume is uploaded to Google Docs, with optional cover letter generation and 
    interactive Q&A session for interview preparation.
    """
    formatter = OutputFormatter()
    
    try:
        # Validate configuration
        Config.validate_config()
        
        # Initialize orchestrator
        orchestrator = ResumeAgentOrchestrator()
        
        # Test mode - just check integrations
        if test:
            formatter.print_info("Running integration tests...")
            all_required_working = orchestrator.print_integration_status()
            sys.exit(0 if all_required_working else 1)
        
        # Get job description
        if job_file:
            # Read from file
            try:
                with open(job_file, 'r', encoding='utf-8') as f:
                    job_description = f.read().strip()
                formatter.print_info(f"Loaded job description from {job_file}")
            except Exception as e:
                formatter.print_error(f"Failed to read job file: {str(e)}")
                sys.exit(1)
        else:
            # Get from user input
            try:
                job_description = InputHandler.get_job_description()
            except ValueError as e:
                formatter.print_error(str(e))
                sys.exit(1)
            except KeyboardInterrupt:
                formatter.print_info("Operation cancelled by user.")
                sys.exit(0)
        
        # Validate job description
        is_valid, error_msg = InputHandler.validate_job_description(job_description)
        if not is_valid:
            formatter.print_error(error_msg)
            sys.exit(1)
        
        # Handle single question mode
        if question:
            formatter.print_info("Single question mode - generating resume first...")
            
            # Generate resume for context
            try:
                results = orchestrator.process_job_application(
                    job_description=job_description,
                    generate_cover_letter=False,
                    user_name=user_name
                )
                
                # Answer the single question
                formatter.print_header("SINGLE QUESTION ANSWER")
                formatter.print_processing(f"Generating answer for: '{question}'")
                
                answer = orchestrator.quick_qa(
                    question=question,
                    job_description=job_description,
                    resume_text=results['refined_resume']
                )
                
                formatter.print_section(f"Q: {question}", answer)
                formatter.print_success("Single question answered successfully!")
                sys.exit(0)
                
            except Exception as e:
                formatter.print_error(f"Failed to answer question: {str(e)}")
                sys.exit(1)
        
        # Handle ATS report mode
        if ats_report:
            formatter.print_info("ATS optimization report mode - analyzing current resume against job description...")
            
            try:
                # Load base resume for analysis
                base_resume = orchestrator.resume_agent.load_base_resume()
                
                # Generate comprehensive ATS report
                formatter.print_header("ATS OPTIMIZATION REPORT")
                formatter.print_processing("Analyzing job requirements and resume compatibility...")
                
                ats_report_data = orchestrator.generate_ats_report(job_description, base_resume)
                
                # Display detailed ATS report
                formatter.print_section("Job Analysis Summary", "")
                formatter.print_info(f"• Critical technical skills identified: {ats_report_data['job_analysis']['critical_technical_skills']}")
                formatter.print_info(f"• Total keyword importance score: {ats_report_data['job_analysis']['total_keywords_identified']}")
                formatter.print_info(f"• Action verbs in job posting: {ats_report_data['job_analysis']['action_verbs_in_job']}")
                
                formatter.print_section("Resume Performance", "")
                ats_score = ats_report_data['resume_performance']['ats_score']
                match_pct = ats_report_data['resume_performance']['keyword_match_percentage']
                
                if ats_score >= 85:
                    formatter.print_success(f"🚀 Excellent ATS Score: {ats_score:.1f}% (Keyword Match: {match_pct:.1f}%)")
                elif ats_score >= 70:
                    formatter.print_info(f"✅ Good ATS Score: {ats_score:.1f}% (Keyword Match: {match_pct:.1f}%)")
                else:
                    formatter.print_warning(f"⚠️  Needs Improvement: {ats_score:.1f}% (Keyword Match: {match_pct:.1f}%)")
                
                formatter.print_info(f"• Technical keywords matched: {ats_report_data['resume_performance']['technical_keywords_matched']}")
                formatter.print_info(f"• Missing critical keywords: {ats_report_data['resume_performance']['missing_critical_keywords']}")
                formatter.print_info(f"• Action verb alignment: {ats_report_data['resume_performance']['action_verb_alignment']:.1f}%")
                formatter.print_info(f"• Quantification strength: {ats_report_data['resume_performance']['quantification_strength']:.1f}%")
                
                # Show improvement opportunities
                improvements = ats_report_data['improvement_opportunities']
                if improvements['high_priority_additions']:
                    formatter.print_section("High Priority Improvements", "")
                    formatter.print_warning("🔴 Add these critical keywords:")
                    for keyword in improvements['high_priority_additions']:
                        formatter.print_warning(f"   • {keyword}")
                
                if improvements['content_to_consider_removing']:
                    formatter.print_warning("🗑️  Consider removing irrelevant content:")
                    for content in improvements['content_to_consider_removing']:
                        formatter.print_warning(f"   • {content}")
                
                if improvements['optimization_tips']:
                    formatter.print_section("ATS Optimization Tips", "")
                    for tip in improvements['optimization_tips']:
                        formatter.print_info(f"• {tip}")
                
                # Show competitive advantages
                advantages = ats_report_data['competitive_advantages']
                formatter.print_section("Competitive Advantages", "")
                if advantages['unique_technical_combinations']:
                    formatter.print_success("💪 Strong technical skill matches:")
                    for skill in advantages['unique_technical_combinations']:
                        formatter.print_success(f"   • {skill}")
                
                formatter.print_success("ATS optimization report completed successfully!")
                formatter.print_info("💡 Tip: Use 'python main.py --job-file [file]' to generate an optimized resume based on this analysis.")
                
                sys.exit(0)
                
            except Exception as e:
                formatter.print_error(f"Failed to generate ATS report: {str(e)}")
                sys.exit(1)
        
        # Get cover letter preference
        if no_cover_letter:
            generate_cover_letter = False
            formatter.print_info("Cover letter generation disabled by --no-cover-letter flag")
        else:
            generate_cover_letter = InputHandler.get_cover_letter_preference()
        
        # Process the job application
        formatter.print_info("Starting resume refinement process...")
        
        try:
            results = orchestrator.process_job_application(
                job_description=job_description,
                generate_cover_letter=generate_cover_letter,
                user_name=user_name
            )
            
            # Display results
            orchestrator.display_results(results)
            
            # Check processing time
            if results['processing_time'] > 30:
                formatter.print_warning(
                    f"Processing took {results['processing_time']:.1f} seconds. "
                    "Consider optimizing your OpenAI API settings for faster responses."
                )
            
            # Run Q&A session if enabled
            if not no_qa and results['refined_resume']:
                formatter.print_info("\n" + "="*60)
                run_qa = InputHandler.get_user_confirmation(
                    "Would you like to start an interview Q&A session?", 
                    default=True
                )
                
                if run_qa:
                    try:
                        qa_results = orchestrator.run_qa_session(
                            job_description=job_description,
                            resume_text=results['refined_resume'],
                            interactive=True
                        )
                        
                        if qa_results.get('session_completed'):
                            formatter.print_success("Q&A session completed successfully!")
                        
                    except Exception as e:
                        formatter.print_error(f"Q&A session failed: {str(e)}")
                else:
                    formatter.print_info("Q&A session skipped. You can run it later with the --question flag.")
            
        except Exception as e:
            formatter.print_error(f"Process failed: {str(e)}")
            
            # Provide helpful error messages
            error_str = str(e).lower()
            if 'openai' in error_str or 'api' in error_str:
                formatter.print_info(
                    "💡 Tip: Check your OpenAI API key in your .env file and ensure you have sufficient credits."
                )
            elif 'google' in error_str or 'auth' in error_str:
                formatter.print_info(
                    "💡 Tip: Check your Google API credentials and ensure the Google Docs API is enabled."
                )
            elif 'resume' in error_str:
                formatter.print_info(
                    "💡 Tip: Check that your base resume file exists at data/base_resume.txt and has content."
                )
            
            sys.exit(1)
    
    except Exception as e:
        formatter.print_error(f"Initialization failed: {str(e)}")
        
        # Provide setup guidance
        if 'OPENAI_API_KEY' in str(e):
            formatter.print_info(
                "💡 Setup required: Please create a .env file with your OpenAI API key.\n"
                "   Copy env.example to .env and add your API key."
            )
        elif 'base_resume' in str(e):
            formatter.print_info(
                "💡 Setup required: Please create your base resume file.\n"
                "   Add your resume content to data/base_resume.txt"
            )
        
        sys.exit(1)


@click.group()
def cli():
    """Resume & Cover Letter Agent CLI"""
    pass


@cli.command()
def setup():
    """Interactive setup wizard for first-time users"""
    import os
    formatter = OutputFormatter()
    formatter.print_header("RESUME AGENT SETUP WIZARD")
    
    # Check for .env file
    if not os.path.exists('.env'):
        formatter.print_info("Creating .env file from template...")
        try:
            import shutil
            shutil.copy('env.example', '.env')
            formatter.print_success(".env file created")
            formatter.print_info("Please edit .env file and add your OpenAI API key")
        except Exception as e:
            formatter.print_error(f"Failed to create .env file: {str(e)}")
    
    # Check for base resume
    if not os.path.exists(Config.BASE_RESUME_PATH):
        formatter.print_info("Base resume file not found")
        formatter.print_info(f"Please add your resume content to: {Config.BASE_RESUME_PATH}")
    else:
        formatter.print_success("Base resume file found")
    
    # Test integrations
    try:
        orchestrator = ResumeAgentOrchestrator()
        all_required_working = orchestrator.print_integration_status()
        if all_required_working:
            formatter.print_success("Setup validation passed!")
        else:
            formatter.print_warning("Some required components need attention. See status above.")
    except Exception as e:
        formatter.print_error(f"Integration test failed: {str(e)}")
    
    formatter.print_info("Setup wizard completed. Run 'python main.py --test' to verify your setup.")


if __name__ == '__main__':
    # Add the current directory to Python path for imports
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run the main CLI
    main()
