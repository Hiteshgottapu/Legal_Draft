# Legal Drafter Pro

Legal Drafter Pro is an AI-powered Streamlit application that helps users generate professional legal documents such as NDAs, Wills, Lease Agreements, and Contracts. The app guides users through document creation with smart prompts, auto-filling, and export options.

## Features

- **Guided Document Creation:** Step-by-step forms for common legal documents.
- **AI-Powered Drafting:** Uses Gemini LLM to generate high-quality legal drafts.
- **Auto-Fill:** Extracts details from user prompts to pre-fill forms.
- **Export Options:** Download documents as TXT, PDF, or DOCX.
- **Session History:** Easily revisit and export previous drafts.
- **Modern UI:** Clean, responsive interface with helpful guidance.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd legal_drafter
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file in the project directory.
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     ```

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

Open the provided local URL in your browser to use the app.

## Requirements

- Python 3.8+
- See `requirements.txt` for Python package dependencies.

## Notes

- For PDF export, install `fpdf`.
- For DOCX export, install `python-docx`.
- Your API key is required for Gemini LLM features.

## License

MIT License

---

Made with ❤️ using Streamlit.
