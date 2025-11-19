"""
Google Docs API integration for uploading resumes
"""
import os
import json
from typing import Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import Config


class GoogleDocsClient:
    """Google Docs API client for creating and managing documents"""
    
    def __init__(self):
        """Initialize the Google Docs client"""
        self.creds = None
        self.service = None
        self.scopes = Config.GOOGLE_SCOPES
        self.credentials_path = Config.GOOGLE_CREDENTIALS_PATH
        self.token_path = Config.GOOGLE_TOKEN_PATH
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Docs API using OAuth 2.0
        
        Returns:
            bool: True if authentication successful
            
        Raises:
            Exception: If authentication fails
        """
        try:
            # Load existing token if available
            if os.path.exists(self.token_path):
                self.creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
            
            # If there are no (valid) credentials available, let the user log in
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    try:
                        print("🔄 Refreshing expired Google API token...")
                        # Refresh the token
                        self.creds.refresh(Request())
                        print("✅ Token refreshed successfully!")
                        
                        # Save the refreshed token
                        with open(self.token_path, 'w') as token:
                            token.write(self.creds.to_json())
                            
                    except Exception as refresh_error:
                        print(f"❌ Token refresh failed: {str(refresh_error)}")
                        print("🔑 Initiating new authentication flow...")
                        
                        # Remove the old token file since it's invalid
                        if os.path.exists(self.token_path):
                            os.remove(self.token_path)
                        
                        # Start fresh OAuth flow
                        self.creds = None
                        self._start_oauth_flow()
                else:
                    # No valid credentials, start OAuth flow
                    print("🔑 Starting Google API authentication...")
                    self._start_oauth_flow()
                
                # Save the credentials for the next run (if not already saved)
                if self.creds and not os.path.exists(self.token_path):
                    with open(self.token_path, 'w') as token:
                        token.write(self.creds.to_json())
            
            # Build the service
            self.service = build('docs', 'v1', credentials=self.creds)
            return True
        
        except Exception as e:
            raise Exception(f"Google Docs authentication failed: {str(e)}")
    
    def _start_oauth_flow(self):
        """Start the OAuth 2.0 flow for authentication"""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Google credentials file not found at {self.credentials_path}. "
                "Please download your OAuth 2.0 credentials from Google Cloud Console."
            )
        
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_path, self.scopes
        )
        print("🌐 Opening browser for Google authentication...")
        self.creds = flow.run_local_server(port=0)
        print("✅ Authentication successful!")
    
    def clear_invalid_token(self):
        """Remove invalid token file to force re-authentication"""
        if os.path.exists(self.token_path):
            try:
                os.remove(self.token_path)
                print("🗑️  Removed invalid token file")
            except OSError as e:
                print(f"⚠️  Warning: Could not remove token file: {e}")
    
    def check_authentication_status(self) -> Dict[str, Any]:
        """
        Check the current authentication status
        
        Returns:
            Dict with authentication status information
        """
        status = {
            'authenticated': False,
            'token_exists': False,
            'token_valid': False,
            'token_expired': False,
            'needs_refresh': False,
            'needs_reauth': False
        }
        
        try:
            # Check if token file exists
            if os.path.exists(self.token_path):
                status['token_exists'] = True
                
                # Load credentials
                creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
                
                if creds:
                    status['token_valid'] = creds.valid
                    status['token_expired'] = creds.expired if hasattr(creds, 'expired') else False
                    status['needs_refresh'] = creds.expired and creds.refresh_token
                    status['needs_reauth'] = not creds.valid and not (creds.expired and creds.refresh_token)
                    status['authenticated'] = creds.valid
            else:
                status['needs_reauth'] = True
                
        except Exception as e:
            print(f"⚠️  Error checking authentication status: {e}")
            status['needs_reauth'] = True
        
        return status
    
    def create_document(self, title: str) -> Dict[str, Any]:
        """
        Create a new Google Docs document
        
        Args:
            title: The title for the document
            
        Returns:
            Dict[str, Any]: Document metadata including document ID and URL
            
        Raises:
            Exception: If document creation fails
        """
        if not self.service:
            raise Exception("Google Docs service not initialized. Please authenticate first.")
        
        try:
            # Create document
            document = {
                'title': title
            }
            
            doc = self.service.documents().create(body=document).execute()
            
            document_id = doc.get('documentId')
            document_url = f"https://docs.google.com/document/d/{document_id}/edit"
            
            return {
                'document_id': document_id,
                'document_url': document_url,
                'title': doc.get('title')
            }
        
        except HttpError as e:
            raise Exception(f"Failed to create Google Doc: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error creating document: {str(e)}")
    
    def insert_text(self, document_id: str, text: str, index: int = 1) -> bool:
        """
        Insert text into a Google Docs document
        
        Args:
            document_id: The ID of the document
            text: The text to insert
            index: The position to insert text (default: 1, at the beginning)
            
        Returns:
            bool: True if successful
            
        Raises:
            Exception: If text insertion fails
        """
        if not self.service:
            raise Exception("Google Docs service not initialized. Please authenticate first.")
        
        try:
            # Prepare the request
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': index
                        },
                        'text': text
                    }
                }
            ]
            
            # Execute the request
            result = self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            return True
        
        except HttpError as e:
            raise Exception(f"Failed to insert text into Google Doc: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error inserting text: {str(e)}")
    
    def format_document(self, document_id: str, resume_text: str) -> bool:
        """
        Apply professional formatting to the document including bold headers, spacing, and hyperlinks
        
        Args:
            document_id: The ID of the document
            resume_text: The resume text to analyze for formatting
            
        Returns:
            bool: True if successful
        """
        if not self.service:
            raise Exception("Google Docs service not initialized. Please authenticate first.")
        
        try:
            # Get document content
            doc = self.service.documents().get(documentId=document_id).execute()
            content = doc.get('body', {}).get('content', [])
            
            # Calculate total text length
            total_length = 0
            for element in content:
                if 'paragraph' in element:
                    for text_run in element['paragraph'].get('elements', []):
                        if 'textRun' in text_run:
                            total_length += len(text_run['textRun'].get('content', ''))
            
            if total_length <= 1:
                return True  # No content to format
            
            # Find headers, links, and formatting positions
            formatting_requests = []
            
            # Apply base formatting first
            formatting_requests.extend([
                # Set font to a professional font for entire document
                {
                    'updateTextStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': total_length
                        },
                        'textStyle': {
                            'weightedFontFamily': {
                                'fontFamily': 'Arial'
                            },
                            'fontSize': {
                                'magnitude': 11,
                                'unit': 'PT'
                            }
                        },
                        'fields': 'weightedFontFamily,fontSize'
                    }
                },
                # Set default line spacing
                {
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': total_length
                        },
                        'paragraphStyle': {
                            'lineSpacing': 115,
                            'spaceAbove': {
                                'magnitude': 3,
                                'unit': 'PT'
                            },
                            'spaceBelow': {
                                'magnitude': 3,
                                'unit': 'PT'
                            }
                        },
                        'fields': 'lineSpacing,spaceAbove,spaceBelow'
                    }
                }
            ])
            
            # Find and format headers, links, and special sections
            lines = resume_text.split('\n')
            current_pos = 1
            
            for line in lines:
                line_length = len(line)
                
                if line_length > 0:
                    # Check if this is a header (all caps sections)
                    if self._is_header_line(line):
                        # Add extra spacing after headers (no bold formatting)
                        formatting_requests.append({
                            'updateParagraphStyle': {
                                'range': {
                                    'startIndex': current_pos,
                                    'endIndex': current_pos + line_length
                                },
                                'paragraphStyle': {
                                    'spaceBelow': {
                                        'magnitude': 8,
                                        'unit': 'PT'
                                    }
                                },
                                'fields': 'spaceBelow'
                            }
                        })
                    
                    # Check if this is the name (first line)
                    elif current_pos == 1:
                        # Center align the name (no bold formatting)
                        formatting_requests.append({
                            'updateParagraphStyle': {
                                'range': {
                                    'startIndex': current_pos,
                                    'endIndex': current_pos + line_length
                                },
                                'paragraphStyle': {
                                    'alignment': 'CENTER',
                                    'spaceBelow': {
                                        'magnitude': 12,
                                        'unit': 'PT'
                                    }
                                },
                                'fields': 'alignment,spaceBelow'
                            }
                        })
                    
                    # Check for URLs and create hyperlinks
                    url_positions = self._find_urls_in_line(line)
                    for url_start, url_end, url in url_positions:
                        formatting_requests.append({
                            'updateTextStyle': {
                                'range': {
                                    'startIndex': current_pos + url_start,
                                    'endIndex': current_pos + url_end
                                },
                                'textStyle': {
                                    'link': {
                                        'url': url
                                    },
                                    'foregroundColor': {
                                        'color': {
                                            'rgbColor': {
                                                'red': 0.0,
                                                'green': 0.0,
                                                'blue': 1.0
                                            }
                                        }
                                    },
                                    'underline': True
                                },
                                'fields': 'link,foregroundColor,underline'
                            }
                        })
                
                # Move to next line (including newline character)
                current_pos += line_length + 1
            
            # Execute all formatting requests in batches (Google Docs has request limits)
            batch_size = 50
            for i in range(0, len(formatting_requests), batch_size):
                batch = formatting_requests[i:i + batch_size]
                self.service.documents().batchUpdate(
                    documentId=document_id,
                    body={'requests': batch}
                ).execute()
            
            return True
        
        except Exception as e:
            # Formatting is optional, so we don't raise an exception
            print(f"Warning: Could not apply formatting to document: {str(e)}")
            return False
    
    def _is_header_line(self, line: str) -> bool:
        """
        Determine if a line is a header (section title)
        
        Args:
            line: The line to check
            
        Returns:
            bool: True if this is a header line
        """
        line = line.strip()
        if not line:
            return False
        
        # Common resume section headers
        headers = [
            'PROFESSIONAL SUMMARY', 'TECHNICAL SKILLS', 'PROFESSIONAL EXPERIENCE',
            'EDUCATION', 'PROJECTS', 'TECHNICAL PROJECTS', 'CERTIFICATIONS',
            'CERTIFICATIONS & ACHIEVEMENTS', 'SKILLS',
            'EXPERIENCE', 'SUMMARY', 'OBJECTIVE', 'ACHIEVEMENTS', 'AWARDS'
        ]
        
        # Check if line matches common headers
        line_upper = line.upper()
        for header in headers:
            if header in line_upper:
                return True
        
        # Check if line is all uppercase and reasonable length for a header
        if line.isupper() and 3 <= len(line) <= 50 and not line.startswith('•'):
            return True
        
        return False
    
    def _find_urls_in_line(self, line: str) -> list:
        """
        Find URLs in a line of text
        
        Args:
            line: The line to search
            
        Returns:
            list: List of tuples (start_pos, end_pos, url)
        """
        import re
        
        urls = []
        
        # Pattern for URLs (http/https, email, linkedin, github, websites)
        url_patterns = [
            r'https?://[^\s]+',
            r'www\.[^\s]+',
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            r'linkedin\.com/in/[^\s]+',
            r'github\.com/[^\s]+',
            r'[a-zA-Z0-9.-]+\.(com|org|net|edu|io|tech|dev)[^\s]*'
        ]
        
        for pattern in url_patterns:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                url = match.group()
                start_pos = match.start()
                end_pos = match.end()
                
                # Ensure URL has proper protocol
                if not url.startswith(('http://', 'https://')):
                    if '@' in url:
                        url = f'mailto:{url}'
                    elif url.startswith('www.'):
                        url = f'https://{url}'
                    elif any(domain in url.lower() for domain in ['linkedin.com', 'github.com']):
                        url = f'https://{url}'
                    elif '.' in url and not url.startswith('mailto:'):
                        url = f'https://{url}'
                
                urls.append((start_pos, end_pos, url))
        
        return urls
    
    def create_resume_document(self, title: str, resume_text: str) -> Dict[str, Any]:
        """
        Create a Google Docs document with resume content
        
        Args:
            title: The title for the document
            resume_text: The resume text content
            
        Returns:
            Dict[str, Any]: Document metadata including document ID and URL
            
        Raises:
            Exception: If document creation or text insertion fails
        """
        # Create the document
        doc_info = self.create_document(title)
        
        try:
            # Insert the resume text
            self.insert_text(doc_info['document_id'], resume_text)
            
            # Apply professional formatting with headers, spacing, and hyperlinks
            self.format_document(doc_info['document_id'], resume_text)
            
            return doc_info
        
        except Exception as e:
            # If text insertion fails, we should clean up the empty document
            # For now, we'll just raise the exception
            raise Exception(f"Failed to create resume document: {str(e)}")
    
    def create_cover_letter_document(self, title: str, cover_letter_text: str) -> Dict[str, Any]:
        """
        Create a Google Docs document with cover letter content
        
        Args:
            title: The title for the document
            cover_letter_text: The cover letter text content
            
        Returns:
            Dict[str, Any]: Document metadata including document ID and URL
            
        Raises:
            Exception: If document creation or text insertion fails
        """
        # Create the document
        doc_info = self.create_document(title)
        
        try:
            # Insert the cover letter text
            self.insert_text(doc_info['document_id'], cover_letter_text)
            
            # Apply basic formatting (no special resume formatting needed for cover letters)
            self._format_cover_letter(doc_info['document_id'], cover_letter_text)
            
            return doc_info
        
        except Exception as e:
            # If text insertion fails, we should clean up the empty document
            # For now, we'll just raise the exception
            raise Exception(f"Failed to create cover letter document: {str(e)}")
    
    def _format_cover_letter(self, document_id: str, cover_letter_text: str) -> bool:
        """
        Apply basic formatting to cover letter document
        
        Args:
            document_id: The ID of the document
            cover_letter_text: The cover letter text to format
            
        Returns:
            bool: True if formatting was successful
            
        Raises:
            Exception: If formatting fails
        """
        if not self.service:
            raise Exception("Google Docs service not initialized. Please authenticate first.")
        
        try:
            formatting_requests = []
            
            lines = cover_letter_text.split('\n')
            current_pos = 1
            
            for line in lines:
                line_length = len(line)
                
                if line_length > 0:
                    # Add spacing between paragraphs
                    formatting_requests.append({
                        'updateParagraphStyle': {
                            'range': {
                                'startIndex': current_pos,
                                'endIndex': current_pos + line_length
                            },
                            'paragraphStyle': {
                                'spaceBelow': {
                                    'magnitude': 6,
                                    'unit': 'PT'
                                }
                            },
                            'fields': 'spaceBelow'
                        }
                    })
                
                current_pos += line_length + 1  # +1 for newline character
            
            # Apply formatting if we have requests
            if formatting_requests:
                self.service.documents().batchUpdate(
                    documentId=document_id,
                    body={'requests': formatting_requests}
                ).execute()
            
            return True
        
        except HttpError as e:
            raise Exception(f"Failed to format cover letter document: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error formatting cover letter: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test the Google Docs API connection
        
        Returns:
            bool: True if connection is successful
        """
        try:
            if not self.service:
                self.authenticate()
            
            # Try to create a test document and delete it
            test_doc = self.create_document("Test Document - Please Delete")
            
            # If we got here, the connection works
            return True
        
        except Exception:
            return False

