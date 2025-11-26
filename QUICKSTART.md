# Quick Start Guide

Get up and running with the Resume & Cover Letter Agent in 5 minutes!

## 🚀 Installation

1. **Run the setup script**:

   ```bash
   ./setup.sh
   ```

2. **Get your OpenAI API key**:

   - Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy the key

3. **Configure your environment**:

   ```bash
   # Edit the .env file
   nano .env

   # Add your OpenAI API key:
   OPENAI_API_KEY=your_api_key_here
   ```

4. **Add your resume**:

   ```bash
   # Edit the base resume template
   nano data/base_resume.txt

   # Replace the placeholder content with your actual resume
   ```

## 🔑 Google Docs Setup (Optional)

**Skip this section if you don't need Google Docs integration - the app works great without it!**

1. **Create Google Cloud Project**:

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project

2. **Enable Google Docs API**:

   - Search for "Google Docs API" and enable it

3. **Create OAuth Credentials**:

   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Choose "Desktop application"
   - Download the JSON file and save it as `credentials.json` in your project root

4. **Update configuration** (optional):
   ```bash
   # In your .env file, add (only if using non-default filename):
   GOOGLE_CREDENTIALS_PATH=credentials.json
   ```
   **Note**: If you name the file `credentials.json`, no configuration needed - it's the default!

## 🧪 Test Your Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Test all integrations
python main.py --test
```

## 🎯 First Run

```bash
# Run the application
python main.py

# Follow the prompts:
# 1. Paste a job description
# 2. Choose whether to generate a cover letter
# 3. Wait for processing
# 4. Get your refined resume and Google Docs link!
```

## 📝 Example Usage

```bash
# Use a job description from file
python main.py --job-file sample_job_description.txt

# Skip cover letter generation
python main.py --no-cover-letter

# Override your name
python main.py --user-name "John Smith"
```

## 🆘 Common Issues

**"OpenAI API key is required"**

- Make sure your `.env` file has `OPENAI_API_KEY=your_key_here`

**"Base resume file not found"**

- Edit `data/base_resume.txt` with your resume content

**Google authentication fails** (if using Google Docs integration)

- Make sure you downloaded OAuth credentials (not service account)
- Save the file as `credentials.json` in your project root
- **Remember**: Google Docs integration is optional - app works without it!

## 🎉 You're Ready!

Your resume agent is now set up and ready to help you land your dream job!

For detailed documentation, see [README.md](README.md).
