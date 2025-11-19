"""
Output formatting utilities for the Resume Agent CLI
"""
import click
from typing import Optional
from datetime import datetime


class OutputFormatter:
    """Handles formatted output for the CLI application"""
    
    @staticmethod
    def print_header(title: str, width: int = 60) -> None:
        """Print a formatted header"""
        click.echo("\n" + "="*width)
        click.echo(f"📄 {title.upper()}")
        click.echo("="*width)
    
    @staticmethod
    def print_section(title: str, content: str, width: int = 60) -> None:
        """Print a formatted section with title and content"""
        click.echo(f"\n{'-'*width}")
        click.echo(f"📋 {title}")
        click.echo(f"{'-'*width}")
        click.echo(content)
    
    @staticmethod
    def print_success(message: str) -> None:
        """Print a success message"""
        click.echo(click.style(f"\n✅ {message}", fg='green', bold=True))
    
    @staticmethod
    def print_error(message: str) -> None:
        """Print an error message"""
        click.echo(click.style(f"\n❌ {message}", fg='red', bold=True))
    
    @staticmethod
    def print_warning(message: str) -> None:
        """Print a warning message"""
        click.echo(click.style(f"\n⚠️  {message}", fg='yellow', bold=True))
    
    @staticmethod
    def print_info(message: str) -> None:
        """Print an info message"""
        click.echo(click.style(f"\nℹ️  {message}", fg='blue'))
    
    @staticmethod
    def print_processing(message: str) -> None:
        """Print a processing message"""
        click.echo(click.style(f"\n⏳ {message}...", fg='cyan'))
    
    @staticmethod
    def print_google_docs_link(doc_url: str, doc_title: str) -> None:
        """Print Google Docs link in a formatted way"""
        click.echo("\n" + "="*60)
        click.echo("🔗 GOOGLE DOCS LINK")
        click.echo("="*60)
        click.echo(f"Document: {doc_title}")
        click.echo(f"Link: {doc_url}")
        click.echo("\n📝 Your refined resume has been uploaded to Google Docs!")
        click.echo("💡 You can now share this link with employers or download as PDF.")
    
    @staticmethod
    def print_resume(resume_text: str) -> None:
        """Print the refined resume in a formatted way"""
        OutputFormatter.print_header("REFINED RESUME")
        click.echo(resume_text)
    
    @staticmethod
    def print_cover_letter(cover_letter_text: str) -> None:
        """Print the cover letter in a formatted way"""
        OutputFormatter.print_header("COVER LETTER")
        click.echo(cover_letter_text)
    
    @staticmethod
    def print_completion_summary(
        resume_generated: bool = True,
        cover_letter_generated: bool = False,
        google_docs_url: Optional[str] = None,
        processing_time: Optional[float] = None
    ) -> None:
        """Print a completion summary"""
        click.echo("\n" + "="*60)
        click.echo("🎉 PROCESS COMPLETED")
        click.echo("="*60)
        
        if resume_generated:
            click.echo("✅ Resume refined and tailored to job description")
        
        if google_docs_url:
            click.echo("✅ Resume uploaded to Google Docs")
        
        if cover_letter_generated:
            click.echo("✅ Cover letter generated")
        
        if processing_time:
            click.echo(f"⏱️  Total processing time: {processing_time:.1f} seconds")
        
        click.echo("\n🚀 You're ready to apply! Good luck with your job application!")
    
    @staticmethod
    def print_step_progress(step: int, total_steps: int, description: str) -> None:
        """Print step progress"""
        progress_bar = "█" * step + "░" * (total_steps - step)
        click.echo(f"\n[{progress_bar}] Step {step}/{total_steps}: {description}")
    
    @staticmethod
    def format_document_title(company_name: str, job_title: str) -> str:
        """
        Format document title for Google Docs
        
        Args:
            company_name: Name of the company
            job_title: Title of the job position
            
        Returns:
            str: Formatted document title
        """
        # Clean up job title and format for filename
        job_clean = job_title.strip().replace(" ", "_").replace("-", "_") if job_title else "Position"
        # Remove special characters and convert to uppercase
        job_clean = "".join(c for c in job_clean if c.isalnum() or c == "_").upper()
        
        return f"Joshua_Inyang_{job_clean}"
    
    @staticmethod
    def format_cover_letter_title(company_name: str) -> str:
        """
        Format cover letter document title for Google Docs
        
        Args:
            company_name: Name of the company
            
        Returns:
            str: Formatted cover letter document title
        """
        # Clean up company name and format for filename
        company_clean = company_name.strip().replace(" ", "_").replace("-", "_") if company_name else "Company"
        # Remove special characters and convert to title case
        company_clean = "".join(c for c in company_clean if c.isalnum() or c == "_").title()
        
        return f"{company_clean}_Cover_Letter"
    
    @staticmethod
    def extract_company_and_job_title(job_description: str) -> tuple[str, str]:
        """
        Extract company name and job title from job description
        
        Args:
            job_description: The job description text
            
        Returns:
            tuple[str, str]: (company_name, job_title)
        """
        lines = job_description.split('\n')
        company_name = "Company"
        job_title = "Position"
        
        # Look for common patterns in the first few lines
        for i, line in enumerate(lines[:10]):
            line_lower = line.lower().strip()
            
            # Look for job title patterns
            if any(keyword in line_lower for keyword in ['position:', 'role:', 'job title:', 'title:']):
                job_title = line.split(':', 1)[-1].strip()
                break
            elif i == 0 and len(line.strip()) > 0 and len(line.strip()) < 100:
                # First line might be job title
                job_title = line.strip()
        
        # Look for company name patterns
        for line in lines[:10]:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in ['company:', 'organization:', 'employer:']):
                company_name = line.split(':', 1)[-1].strip()
                break
        
        return company_name, job_title

