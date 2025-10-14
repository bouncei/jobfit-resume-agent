# Resume & Cover Letter Agent

A powerful Python CLI application that leverages LangChain and OpenAI's LLM to automatically refine resumes and generate cover letters tailored to specific job descriptions. The refined resume is uploaded to Google Docs, with optional cover letter generation displayed in the terminal.

## 🚀 Features

- **Intelligent Resume Refinement**: Uses GPT-4 to tailor your resume to specific job descriptions
- **Professional Cover Letter Generation**: Creates personalized cover letters that highlight relevant experience
- **Google Docs Integration**: Automatically uploads refined resumes to Google Docs with shareable links
- **CLI Interface**: Simple command-line interface for easy automation and scripting
- **Comprehensive Error Handling**: Robust error handling with helpful user guidance
- **Fast Processing**: Optimized for <30 second end-to-end processing time

## 📋 Requirements

- Python 3.9 or higher
- OpenAI API key (GPT-4 Turbo or GPT-4o recommended)
- Google Cloud Project with Docs API enabled
- Google OAuth 2.0 credentials

## 🛠 Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd resume-agent
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:

   ```bash
   cp env.example .env
   ```

   Edit `.env` and add your API keys:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_CREDENTIALS_PATH=path/to/your/google_credentials.json
   USER_NAME=Your Full Name
   ```

5. **Create your base resume**:
   Edit `data/base_resume.txt` with your resume content. Use the provided template as a guide.

## 🔑 API Setup

### OpenAI API

1. Visit [OpenAI API](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to your `.env` file as `OPENAI_API_KEY`

### Google Docs API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Docs API
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Choose "Desktop application"
   - Download the JSON file
5. Save the JSON file and update `GOOGLE_CREDENTIALS_PATH` in your `.env` file

## 📖 Usage

### Basic Usage

Run the application and follow the interactive prompts:

```bash
python main.py
```

### Command Line Options

```bash
# Test all integrations
python main.py --test

# Load job description from file
python main.py --job-file job_description.txt

# Skip cover letter generation
python main.py --no-cover-letter

# Override user name
python main.py --user-name "John Doe"

# Show help
python main.py --help
```

### Interactive Workflow

1. **Paste Job Description**: Copy and paste the job description when prompted
2. **Choose Cover Letter**: Decide whether to generate a cover letter
3. **Processing**: The system will:
   - Refine your resume based on the job description
   - Upload the refined resume to Google Docs
   - Generate a cover letter (if requested)
4. **Results**: View your refined resume, cover letter, and Google Docs link

## 📁 Project Structure

```
resume-agent/
├── main.py                 # CLI entry point
├── config.py               # Configuration management
├── agents/                 # LangChain agent logic
│   ├── __init__.py
│   ├── resume_agent.py     # Resume refinement logic
│   ├── cover_letter_agent.py # Cover letter generation
│   └── orchestrator.py     # Main workflow orchestration
├── integrations/           # API integrations
│   ├── __init__.py
│   ├── openai_client.py    # OpenAI/LangChain setup
│   └── google_docs.py      # Google Docs API wrapper
├── utils/                  # Helper utilities
│   ├── __init__.py
│   ├── input_handler.py    # CLI input processing
│   └── formatters.py       # Output formatting
├── data/
│   └── base_resume.txt     # Your base resume template
├── env.example             # Environment variables template
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎯 How It Works

### Resume Refinement Process

1. **Analysis**: The system analyzes the job description to identify key requirements, skills, and keywords
2. **Tailoring**: Your base resume is refined to:
   - Highlight relevant skills and experiences
   - Incorporate job-specific keywords naturally
   - Reorder content by relevance to the role
   - Maintain professional formatting and accuracy
3. **Validation**: The output is validated for completeness and quality

### Cover Letter Generation

1. **Context Building**: Combines job description with your refined resume
2. **Personalization**: Creates a compelling narrative that:
   - Opens with enthusiasm for the specific role
   - Connects your experience to job requirements
   - Demonstrates understanding of company needs
   - Closes with a clear call to action
3. **Formatting**: Ensures proper business letter structure

### Google Docs Integration

1. **Authentication**: Secure OAuth 2.0 flow (browser login on first use)
2. **Document Creation**: Creates a new document with professional naming
3. **Content Upload**: Inserts refined resume with basic formatting
4. **Link Generation**: Provides shareable link for immediate use

## 🔧 Configuration

### Environment Variables

| Variable                  | Description                                | Required |
| ------------------------- | ------------------------------------------ | -------- |
| `OPENAI_API_KEY`          | Your OpenAI API key                        | Yes      |
| `OPENAI_MODEL`            | OpenAI model to use (default: gpt-4-turbo) | No       |
| `GOOGLE_CREDENTIALS_PATH` | Path to Google OAuth credentials JSON      | Yes      |
| `GOOGLE_TOKEN_PATH`       | Path to store Google auth tokens           | No       |
| `USER_NAME`               | Your full name for cover letters           | No       |

### Customization

- **Resume Template**: Edit `data/base_resume.txt` to match your background
- **Processing Limits**: Adjust limits in `config.py`
- **Prompt Engineering**: Modify prompts in agent files for different styles

## 🚨 Troubleshooting

### Common Issues

**"OpenAI API key is required"**

- Ensure your `.env` file exists and contains `OPENAI_API_KEY`
- Verify the API key is valid and has sufficient credits

**"Google credentials file not found"**

- Download OAuth 2.0 credentials from Google Cloud Console
- Update `GOOGLE_CREDENTIALS_PATH` in your `.env` file

**"Base resume file not found"**

- Create `data/base_resume.txt` with your resume content
- Use the provided template as a starting point

**"Job description is too short"**

- Ensure job descriptions are at least 100 characters
- Include job responsibilities, requirements, or skills

### Performance Issues

**Processing takes too long (>30 seconds)**

- Check your internet connection
- Consider using `gpt-3.5-turbo` for faster responses
- Verify OpenAI API status

### Authentication Issues

**Google Docs authentication fails**

- Ensure Google Docs API is enabled in your project
- Check that OAuth 2.0 credentials are for "Desktop application"
- Delete `token.json` to force re-authentication

## 📊 Example Output

### Refined Resume

The system will display your tailored resume in the terminal, highlighting relevant skills and experiences for the specific job.

### Google Docs Link

```
🔗 GOOGLE DOCS LINK
============================================================
Document: TechCorp - Senior Developer - Resume - 2024-01-15
Link: https://docs.google.com/document/d/abc123.../edit

📝 Your refined resume has been uploaded to Google Docs!
💡 You can now share this link with employers or download as PDF.
```

### Cover Letter

A professional 3-4 paragraph cover letter tailored to the job and your experience.

## 🧪 Testing

### Integration Tests

```bash
# Test all integrations
python main.py --test
```

### Manual Testing

```bash
# Test with a sample job description
python main.py --job-file sample_job.txt --no-cover-letter
```

## 🔒 Security & Privacy

- **API Keys**: Stored locally in `.env` file (never committed to version control)
- **Google Authentication**: Uses OAuth 2.0 with local token storage
- **Data Processing**: Job descriptions and resumes are processed by OpenAI's API
- **Document Storage**: Resumes are stored in your personal Google Drive

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run `python main.py --test` to diagnose integration issues
3. Verify your API keys and credentials
4. Check that all required files exist

## 🚀 Future Enhancements

- Multiple resume versions for different career tracks
- Interview question generation based on resume + job description
- Batch processing for multiple job applications
- Local PDF/DOCX export options
- Resume history tracking and management

---

**Happy job hunting! 🎯**

