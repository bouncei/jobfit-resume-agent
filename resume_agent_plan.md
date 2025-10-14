# Resume & Cover Letter Agent - Project Plan & Objectives

## Project Overview
Build a Python CLI application that leverages LangChain and OpenAI's LLM to automatically refine resumes and generate cover letters tailored to specific job descriptions. The refined resume is exported to Google Docs, with optional cover letter generation displayed in the terminal.

---

## Technical Stack

### Core Technologies
- **Language**: Python 3.9+
- **LLM Framework**: LangChain (latest version)
- **LLM Provider**: OpenAI (GPT-4 Turbo or GPT-4o recommended for quality)
- **Google Integration**: Google Docs API with google-auth-oauthlib for authentication
- **CLI Interface**: argparse or click (for command-line input handling)
- **Environment Management**: python-dotenv for API keys
- **Additional Libraries**: 
  - requests (for API calls if needed)
  - python-docx (alternative if Google Docs integration has issues)

---

## System Architecture

### Component Breakdown

#### 1. **User Resume Context Storage**
- Store user's base resume (plain text format) as a context variable/file
- This serves as the foundation for all LLM operations
- Should be easily updatable without code changes

#### 2. **CLI Input Handler**
- Accept job description as input (multi-line text input or file path)
- Prompt user with yes/no question: "Generate a cover letter? (yes/no)"
- Store all inputs in structured format for processing

#### 3. **LangChain Agent with OpenAI Integration**
- Initialize LLM with OpenAI API key
- Create multiple prompt templates for different tasks:
  - **Resume Refinement Prompt**: Takes job description + base resume → outputs refined resume
  - **Cover Letter Prompt**: Takes job description + user resume + job details → outputs cover letter
- Use LangChain's PromptTemplate and LLMChain for orchestration

#### 4. **Resume Refinement Engine**
- Input: Job description + user's base resume
- Output: Tailored resume highlighting relevant skills/experience
- Constraints: Must maintain standard resume format (text-based), keep to 1 page if possible
- Should emphasize keywords from job description

#### 5. **Cover Letter Generation Engine**
- Input: Job description + refined resume + company context
- Output: Professional cover letter in standard business format
- Constraints: 3-4 paragraphs, professional tone, no markdown formatting

#### 6. **Google Docs Integration Module**
- Authenticate using OAuth 2.0 with google-auth-oauthlib
- Create new Google Doc with naming convention: `[Company Name] - [Job Title] - Resume - [Date]`
- Format and insert refined resume text into document
- Return shareable link to created document
- Handle authentication refresh tokens

#### 7. **Output Formatter**
- Display refined resume and cover letter in terminal (if generated)
- Format output for readability
- Include Google Docs link prominently

#### 8. **Error Handling & Logging**
- Graceful error messages for API failures
- Validate inputs before processing
- Log all operations for debugging

---

## Detailed Workflow

### Step-by-Step Process

1. **Initialization**
   - Load environment variables (OpenAI API key, Google API credentials)
   - Load user's base resume from file/variable
   - Initialize OpenAI client via LangChain
   - Setup Google Docs API client

2. **User Input Collection**
   - Prompt user: "Paste the job description (press CTRL+D or CTRL+Z when done):"
   - Accept multiline input until EOF
   - Prompt user: "Would you like to generate a cover letter? (yes/no):"
   - Store both inputs in variables

3. **Resume Refinement**
   - Create prompt template combining: job description + base resume
   - Call OpenAI LLM through LangChain
   - Process output to ensure proper formatting
   - Store refined resume in variable

4. **Resume Upload to Google Docs**
   - Authenticate with Google API (first time may require browser login)
   - Create new Google Doc with structured naming
   - Insert refined resume text with basic formatting
   - Retrieve document link
   - Display link to user

5. **Cover Letter Generation** (conditional)
   - If user selected "yes":
     - Create prompt template with job description + refined resume
     - Call OpenAI LLM through LangChain
     - Format output for terminal display

6. **Terminal Output**
   - Display refined resume (formatted, readable)
   - If cover letter generated: Display cover letter
   - Show Google Docs link with instructions
   - Display success message

---

## Prompt Engineering Specifications

### Resume Refinement Prompt
```
System Role: You are an expert resume writer and career coach specializing in tailoring resumes to specific job descriptions.

Input Variables:
- {base_resume}: User's original resume
- {job_description}: Target job description

Task:
Refine the provided resume to perfectly match the job description while maintaining accuracy and relevance. 
- Highlight skills and experiences that align with job requirements
- Reorder bullet points by relevance to the role
- Use keywords from the job description naturally
- Keep to one page, professional format
- Maintain truthfulness - do not add false experiences
- Format as plain text without markdown

Output: Pure refined resume text only, no explanations.
```

### Cover Letter Prompt
```
System Role: You are a professional cover letter writer who creates compelling, personalized cover letters.

Input Variables:
- {job_description}: Target job description
- {refined_resume}: The refined resume
- {user_name}: User's name (optional)

Task:
Generate a professional cover letter that:
- Opens with a compelling hook related to the role
- Connects 2-3 key experiences from the resume to job requirements
- Demonstrates understanding of company/role needs
- Closes with clear call to action
- Maintains professional tone
- Is 3-4 paragraphs long
- Uses plain text format without markdown

Output: Pure cover letter text only, formatted ready to use.
```

---

## Data Flow Diagram

```
User Input (Job Description + Cover Letter Preference)
         ↓
[CLI Input Handler]
         ↓
[Base Resume + Job Description] → [LangChain Resume Refinement Agent]
         ↓
[Refined Resume]
         ↓
[Google Docs API] → [Create & Format Doc] → [Return Link]
         ↓
[Terminal Display - Show Link]
         ↓
[If Yes] → [Job Desc + Refined Resume] → [LangChain Cover Letter Agent]
         ↓
[Cover Letter Text]
         ↓
[Terminal Display - Show Cover Letter]
         ↓
SUCCESS: Resume in Google Docs + Cover Letter (if requested)
```

---

## Implementation Requirements

### API Credentials
1. **OpenAI API Key**
   - Required for LLM access
   - Store in `.env` file as `OPENAI_API_KEY`
   - Model: Use `gpt-4-turbo` or `gpt-4o`

2. **Google Docs API Credentials**
   - OAuth 2.0 credentials JSON file
   - Scopes needed: `https://www.googleapis.com/auth/docs` (read/write)
   - Store credentials in `.env` or separate JSON file
   - Implement token refresh logic

### File Structure
```
resume-agent/
├── main.py                 # Entry point
├── config.py               # Configuration and constants
├── agents/
│   ├── __init__.py
│   ├── resume_agent.py     # Resume refinement logic
│   ├── cover_letter_agent.py # Cover letter generation
│   └── orchestrator.py     # Main orchestration logic
├── integrations/
│   ├── __init__.py
│   ├── openai_client.py    # OpenAI/LangChain setup
│   └── google_docs.py      # Google Docs API wrapper
├── utils/
│   ├── __init__.py
│   ├── input_handler.py    # CLI input processing
│   └── formatters.py       # Output formatting
├── data/
│   └── base_resume.txt     # User's base resume
├── .env.example            # Example env file
├── requirements.txt        # Dependencies
└── README.md               # Documentation
```

### Dependencies (requirements.txt)
```
openai>=1.0.0
langchain>=0.1.0
langchain-openai>=0.0.1
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.2.0
google-api-python-client>=2.0.0
python-dotenv>=1.0.0
click>=8.0.0
requests>=2.28.0
```

---

## Objectives & Success Criteria

### Primary Objectives

#### Objective 1: Seamless Job Description Input
- User can paste job description into terminal
- System recognizes end of input (CTRL+D or CTRL+Z)
- Validation ensures job description is not empty

#### Objective 2: Intelligent Resume Refinement
- LangChain agent processes base resume + job description
- Output is a refined, keyword-optimized resume
- Refined resume maintains accuracy and readability
- Format is standard text-based (no markdown)

#### Objective 3: Google Docs Integration
- Successfully authenticate with Google Docs API on first run
- Create new Google Doc with professional naming convention
- Upload refined resume with basic formatting
- Return shareable link to user

#### Objective 4: Optional Cover Letter Generation
- User can opt in/out of cover letter generation
- When selected, generate professional cover letter
- Cover letter displayed in terminal for immediate use
- Cover letter is properly formatted and ready to use

#### Objective 5: Terminal-Based Workflow
- Entire process runs from CLI without web interface
- Clear, readable output in terminal
- User gets immediate feedback on each step
- Error messages are helpful and actionable

### Success Metrics

1. **Resume Quality**: Generated resume is contextually relevant to job description and highlights 3+ matching skills
2. **Turnaround Time**: Complete process (refinement + upload) completes in <30 seconds
3. **Error Rate**: System handles API failures gracefully with user-friendly messages
4. **Google Docs**: Link is immediately usable and document is properly formatted
5. **Cover Letter**: If generated, is coherent, professional, and 3-4 paragraphs

---

## Edge Cases & Error Handling

### Potential Issues
1. **API Rate Limits**: Implement retry logic with exponential backoff
2. **Google Auth Expiration**: Handle token refresh automatically
3. **Invalid Job Description**: Validate input, prompt for retry if too short
4. **Network Failures**: Catch connection errors, provide offline fallback messaging
5. **Resume Formatting Issues**: Ensure output is always plain text, handle encoding

### Error Messages
- "Job description is too short. Please provide at least 100 characters."
- "Google authentication failed. Please check your credentials in .env"
- "OpenAI API error. Please check your API key and try again."
- "Failed to create Google Doc. Please ensure you have permissions."

---

## Future Enhancements

1. **Multiple Resume Versions**: Support tailoring multiple resumes for different career tracks
2. **Interview Prep**: Generate likely interview questions based on resume + job description
3. **Batch Processing**: Apply to multiple jobs in one session
4. **Local Backup**: Save refined resumes locally as PDF/DOCX
5. **Resume History**: Track all generated resumes with job details for reference
6. **Custom Styling**: Add template support for Google Docs formatting

---

## Deployment Notes

### Local Development Setup
- Create virtual environment: `python -m venv venv`
- Activate: `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt`
- Configure `.env` with API keys
- Run: `python main.py`

### Authentication on First Run
- Google Docs API will prompt browser login on first execution
- OAuth token will be cached for future use
- OpenAI API key should be set in environment before running

---

## Documentation Requirements

1. **README.md**: Setup instructions, usage examples, troubleshooting
2. **Code Comments**: Inline documentation for complex logic
3. **Docstrings**: Function documentation in Google/NumPy style
4. **Example Output**: Show sample refined resume and cover letter

---

## Testing Recommendations

1. **Unit Tests**: Test prompt formatting, input validation, output parsing
2. **Integration Tests**: Test Google Docs API integration, LLM calls
3. **End-to-End Tests**: Run full workflow with sample job description
4. **Manual Testing**: Test with real job descriptions from various industries

---

## Estimated Development Timeline

- **Phase 1 (Setup & Core)**: 2-3 hours - Project structure, LangChain setup, basic prompts
- **Phase 2 (Agent Logic)**: 3-4 hours - Resume/cover letter agents, LLM integration
- **Phase 3 (Google Integration)**: 2-3 hours - OAuth, document creation, formatting
- **Phase 4 (Polish & Testing)**: 2-3 hours - Error handling, testing, documentation

**Total Estimated Time**: 9-13 hours

---

## Notes for AI Editor

- Prioritize code clarity and maintainability over premature optimization
- Implement comprehensive error handling from the start
- Use LangChain's built-in features (PromptTemplate, LLMChain) rather than custom solutions
- Test Google Docs authentication flow thoroughly before considering complete
- Ensure all API calls have proper timeout and retry logic
- Consider using LangChain's output parsers for consistent response formatting