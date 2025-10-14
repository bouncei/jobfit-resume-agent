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
                    # Refresh the token
                    self.creds.refresh(Request())
                else:
                    # Run OAuth flow
                    if not os.path.exists(self.credentials_path):
                        raise FileNotFoundError(
                            f"Google credentials file not found at {self.credentials_path}. "
                            "Please download your OAuth 2.0 credentials from Google Cloud Console."
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.scopes
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(self.token_path, 'w') as token:
                    token.write(self.creds.to_json())
            
            # Build the service
            self.service = build('docs', 'v1', credentials=self.creds)
            return True
        
        except Exception as e:
            raise Exception(f"Google Docs authentication failed: {str(e)}")
    
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
    
    def format_document(self, document_id: str) -> bool:
        """
        Apply basic formatting to the document
        
        Args:
            document_id: The ID of the document
            
        Returns:
            bool: True if successful
        """
        if not self.service:
            raise Exception("Google Docs service not initialized. Please authenticate first.")
        
        try:
            # Get document content to determine text length
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
            
            # Apply basic formatting
            requests = [
                # Set font to a professional font
                {
                    'updateTextStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': total_length
                        },
                        'textStyle': {
                            'fontFamily': 'Arial',
                            'fontSize': {
                                'magnitude': 11,
                                'unit': 'PT'
                            }
                        },
                        'fields': 'fontFamily,fontSize'
                    }
                },
                # Set line spacing
                {
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': total_length
                        },
                        'paragraphStyle': {
                            'lineSpacing': 110,
                            'spaceAbove': {
                                'magnitude': 0,
                                'unit': 'PT'
                            },
                            'spaceBelow': {
                                'magnitude': 6,
                                'unit': 'PT'
                            }
                        },
                        'fields': 'lineSpacing,spaceAbove,spaceBelow'
                    }
                }
            ]
            
            # Execute formatting requests
            self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            return True
        
        except Exception as e:
            # Formatting is optional, so we don't raise an exception
            print(f"Warning: Could not apply formatting to document: {str(e)}")
            return False
    
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
            
            # Apply basic formatting
            self.format_document(doc_info['document_id'])
            
            return doc_info
        
        except Exception as e:
            # If text insertion fails, we should clean up the empty document
            # For now, we'll just raise the exception
            raise Exception(f"Failed to create resume document: {str(e)}")
    
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

