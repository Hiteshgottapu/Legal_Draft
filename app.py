import streamlit as st
import re
from datetime import datetime
from generator import generate_legal_text
from memory import get_session_memory
from prompts import get_prompt_template
from config import GUIDED_TYPES, CSS_STYLES
from utils import handle_errors, export_document
import time
import io
try:
    from fpdf import FPDF
except ImportError:
    FPDF = None
try:
    from docx import Document
except ImportError:
    Document = None

# --- Initialize Session State ---
def init_session_state():
    if 'app_state' not in st.session_state:
        st.session_state.app_state = {
            'history': [],
            'current_document': None,
            'guided_flows': {},
            'last_generated': None,
            'selected_doc_type': 'NDA'  # Default document type
        }

# --- Custom CSS ---
st.markdown(CSS_STYLES, unsafe_allow_html=True)

# --- Sidebar ---
def render_sidebar():
    st.sidebar.markdown(
        '''<div class="sidebar-logo">
            <img src="https://img.icons8.com/ios-filled/100/000000/law.png" width="40"/>
            <span class="sidebar-title">Legal Drafter Pro</span>
        </div>''', unsafe_allow_html=True)
    
    st.sidebar.header("Drafting Options")
    doc_types = ["NDA", "Will", "Lease Agreement", "Contract"]
    document_type = st.sidebar.selectbox(
        "Select Document Type",
        doc_types,
        index=doc_types.index(st.session_state.app_state['selected_doc_type']),
        help="Choose the type of legal document you need"
    )
    st.session_state.app_state['selected_doc_type'] = document_type
    
    export_format = st.sidebar.selectbox(
        "Export Format", 
        ["None", "PDF", "DOCX", "TXT"],
        help="Select format for document export"
    )
    
    if st.session_state.app_state['last_generated'] and export_format != "None":
        if st.sidebar.button("Export Document"):
            export_document(st.session_state.app_state['last_generated'], export_format)
    
    render_history()

# --- Common Flow Components ---
def get_initial_context(document_type):
    st.markdown(f"### Let's create your {document_type}")
    # Enhanced prompt writing tips and examples for each document type
    example_prompts = {
        "NDA": {
            "description": "Non-Disclosure Agreement between two parties to protect confidential business information.",
            "details": """Parties:\n- Disclosing Party: Alpha Innovations Ltd.\n- Receiving Party: Beta Analytics LLC\nConfidential Information: Product designs, source code, marketing plans\nExclusions: Publicly available information\nObligations: No disclosure for 3 years\nReturn/Destruction: All documents returned after project\nJurisdiction: State of New York""",
            "example": "Draft an NDA where Alpha Innovations Ltd. shares product designs and code with Beta Analytics LLC, valid for 3 years, New York law, with standard exclusions and return of documents."
        },
        "Will": {
            "description": "Last Will and Testament for distribution of assets and appointment of executor.",
            "details": """Testator: John Smith\nAssets: House at 456 Oak Ave to spouse Jane Smith, savings account to son Alex Smith\nExecutor: Emily Brown\nSpecial instructions: Cremation, no contest clause\nWitnesses: Michael Lee, Sarah Kim""",
            "example": "I, John Smith, leave my house to Jane, savings to Alex, appoint Emily Brown as executor, request cremation, and include a no contest clause."
        },
        "Lease Agreement": {
            "description": "Residential Lease Agreement for rental property.",
            "details": """Landlord: Green Properties LLC\nTenant: Olivia Johnson\nProperty: 789 Riverbend Rd, Apt 5B\nLease Term: 1 year from 09/01/2025\nRent: $1,800/month, due on 1st\nSecurity Deposit: $1,800\nUtilities: Tenant pays electricity, water included\nPet Policy: No pets\nGoverning Law: California""",
            "example": "Lease for 789 Riverbend Rd, Apt 5B, between Green Properties (landlord) and Olivia Johnson (tenant), $1800/month, 1 year from 09/01/2025, no pets, California law."
        },
        "Contract": {
            "description": "Employment Contract for a new software developer.",
            "details": """Party 1: Quantum Tech Corp\nParty 2: Priya Patel\nPosition: Software Developer\nStart Date: 10/01/2025\nDuration: 2 years\nSalary: $90,000/year\nWorking Hours: 9am-5pm, Mon-Fri\nLocation: Remote\nSupervisor: Raj Mehta\nResponsibilities: Develop and maintain web applications\nPayment Terms: Monthly\nTermination: 30 days notice\nConfidentiality: NDA required""",
            "example": "Employment contract for Priya Patel as Software Developer at Quantum Tech Corp, starting 10/01/2025, $90k/year, remote, NDA required, 2-year term, 30-day notice for termination."
        },
        "Internship Agreement": {
            "description": "Internship Agreement for a summer intern in marketing.",
            "details": """Company: Bright Marketing Inc.\nIntern: Daniel Lee\nDuration: June-August 2025\nStipend: $2,000/month\nResponsibilities: Assist with social media campaigns, attend weekly meetings\nMentor: Lisa Wong\nConfidentiality: Standard NDA applies""",
            "example": "Bright Marketing Inc. offers Daniel Lee a 3-month marketing internship at $2k/month, assisting with social media, mentored by Lisa Wong, NDA applies."
        }
    }
    doc_info = example_prompts.get(document_type, None)
    col1, col2 = st.columns([1,1])
    with col1:
        if doc_info:
            st.markdown(f"""
            <div style='background-color:#f5f5fa;padding:1em;border-radius:8px;margin-bottom:0.5em;'>
            <b>How to write your prompt for <span style='color:#283593'>{document_type}</span>:</b><br>
            <ul style='margin-bottom:0.5em;'>
                <li><b>Description:</b> {doc_info['description']}</li>
                <li><b>Details:</b><pre style='background:#f8f8ff;border-radius:6px;padding:0.5em;'>{doc_info['details']}</pre></li>
                <li><b>Example Prompt:</b> <span style='color:#1565c0'>{doc_info['example']}</span></li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Describe your requirements clearly. Include all important details for best results.")
    with col2:
        # Autofill the text area with the example prompt for the selected document type
        default_prompt = doc_info['example'] if doc_info and 'example' in doc_info else ''
        user_prompt = st.text_area(
            "Enter your prompt here:",
            value=default_prompt,
            height=150,
            key=f"initial_prompt"
        )
        # Only show the Continue button for the prompt step, not for the form step
        show_continue = not st.session_state.get(f"form_{document_type.lower()}_show", False)
        if show_continue:
            if st.button("Continue", key=f"continue_{document_type}"):
                return user_prompt
        return None

def validate_duration(duration_str):
    try:
        parts = duration_str.split()
        if len(parts) != 2:
            return False
        num = int(parts[0])
        unit = parts[1].lower()
        if unit not in ['years', 'year', 'months', 'month', 'days', 'day']:
            return False
        return True
    except:
        return False

# --- Smart Document Flows ---
@handle_errors
def handle_document_flow(document_type):
    state_key = f"guided_{document_type.lower().replace(' ', '_')}"
    
    if state_key not in st.session_state.app_state['guided_flows']:
        st.session_state.app_state['guided_flows'][state_key] = {}
    
    answers = st.session_state.app_state['guided_flows'][state_key]

    # Step 1: Get initial context
    if 'initial_prompt' not in answers:
        user_input = get_initial_context(document_type)
        if user_input and validate_input(user_input, f"{document_type} description"):
            answers['initial_prompt'] = user_input.strip()
            # Instead of rerun, immediately show the form for missing fields
            form_key = f"form_{document_type.lower()}"
            st.session_state[f"{form_key}_show"] = True
            st.rerun()
        return None

    # Step 2: Document-specific processing
    # Generalized: Use improved auto-fill for all guided types
    if document_type in ["NDA", "Will", "Lease Agreement", "Contract"]:
        return handle_guided_autofill_flow(document_type, answers)
    # fallback for any other types
    return None

# --- Generalized guided flow with auto-fill from prompt ---
def handle_guided_autofill_flow(document_type, answers):
    import re
    from config import GUIDED_TYPES
    required_questions = GUIDED_TYPES[document_type]
    prompt_text = answers.get('initial_prompt', '').lower()
    auto_filled = {}

    # Build regex patterns for each field based on the config keys and example prompt
    # This is a best-effort approach; can be improved with more advanced NLP if needed
    for q_key, q_text in required_questions:
        # Try to match key in prompt using flexible patterns
        # e.g., for 'party1', look for 'party', 'disclosing party', etc.
        key_patterns = [
            rf"{q_key.replace('_', ' ')}\s*[:\-]?\s*([^\n\r\.,]+)",
            rf"{q_text.split()[0].lower()}\s*[:\-]?\s*([^\n\r\.,]+)",
        ]
        # Add some special cases for common legal fields
        if q_key in ['party1', 'party2', 'landlord', 'tenant']:
            key_patterns.append(r"between\s+([\w\s&.,'-]+?)\s+and\s+([\w\s&.,'-]+?)(?:\.|$)")
        if q_key in ['duration', 'lease_term']:
            key_patterns.append(r"(\d+\s*(?:year|month|day|week|hour)s?)")
        if q_key in ['start_date', 'date']:
            key_patterns.append(r"(\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2})")
        if q_key in ['rent_amount', 'salary', 'stipend', 'security_deposit']:
            key_patterns.append(r"\$[\d,]+(?:\.\d{2})?")
        if q_key in ['governing_law', 'jurisdiction']:
            key_patterns.append(r"(california|new york|texas|florida|[a-z ]+ law)")

        found = False
        for pat in key_patterns:
            match = re.search(pat, prompt_text, re.IGNORECASE)
            if match:
                # Special handling for party pairs, but only if the pattern has at least 2 groups
                if q_key in ['party1', 'landlord'] and match.lastindex and match.lastindex >= 2:
                    auto_filled[q_key] = match.group(1).strip().title()
                elif q_key in ['party2', 'tenant'] and match.lastindex and match.lastindex >= 2:
                    auto_filled[q_key] = match.group(2).strip().title()
                else:
                    # Only use group(1) if it exists
                    if match.lastindex and match.lastindex >= 1:
                        auto_filled[q_key] = match.group(1).strip()
                    elif match.lastindex == 0 or match.lastindex is None:
                        # If the pattern has no explicit groups, use the whole match
                        auto_filled[q_key] = match.group(0).strip()
                found = True
                break

    # Add some extra logic for common fields if not found
    # NDA: confidential_info, purpose
    if document_type == "NDA":
        if 'confidential_info' not in auto_filled:
            conf_match = re.search(r"confidential information (?:includes|such as|:|is)\s*([^\n\.]*)", prompt_text)
            if conf_match:
                auto_filled['confidential_info'] = conf_match.group(1).strip()
        if 'purpose' not in auto_filled:
            purpose_match = re.search(r"purpose\s*[:is]?\s*([^\n\.]*)", prompt_text)
            if purpose_match:
                auto_filled['purpose'] = purpose_match.group(1).strip()
    # Will: testator_name, executor, assets, special_instructions
    if document_type == "Will":
        if 'testator_name' not in auto_filled:
            testator_match = re.search(r"i,?\s*([a-zA-Z\s]+),?\s*leave", prompt_text)
            if testator_match:
                auto_filled['testator_name'] = testator_match.group(1).strip().title()
        if 'executor' not in auto_filled:
            executor_match = re.search(r"executor:?\s*([a-zA-Z\s]+)", prompt_text)
            if executor_match:
                auto_filled['executor'] = executor_match.group(1).strip().title()
        if 'assets' not in auto_filled:
            assets_match = re.search(r"assets:?\s*([a-zA-Z0-9,\s]+)", prompt_text)
            if assets_match:
                auto_filled['assets'] = assets_match.group(1).strip()
        if 'special_instructions' not in auto_filled:
            special_match = re.search(r"special instructions:?\s*([a-zA-Z0-9,\s]+)", prompt_text)
            if special_match:
                auto_filled['special_instructions'] = special_match.group(1).strip()
    # Lease: property_address, utilities, pet_policy
    if document_type == "Lease Agreement":
        if 'property_address' not in auto_filled:
            address_match = re.search(r"address\s*[:is]?\s*([\w\s,\-]+)", prompt_text)
            if address_match:
                auto_filled['property_address'] = address_match.group(1).strip()
        if 'utilities' not in auto_filled:
            utilities_match = re.search(r"utilities\s*[:is]?\s*([\w\s,]+)", prompt_text)
            if utilities_match:
                auto_filled['utilities'] = utilities_match.group(1).strip()
        if 'pet_policy' not in auto_filled:
            pet_policy_match = re.search(r"pet(s)? (allowed|policy)\s*[:is]?\s*([\w\s,]+)", prompt_text)
            if pet_policy_match:
                auto_filled['pet_policy'] = pet_policy_match.group(3).strip()
    # Contract: try to extract party names, position, salary, etc.
    if document_type == "Contract":
        if 'party1' not in auto_filled:
            party1_match = re.search(r"party 1:?\s*([a-zA-Z\s]+)", prompt_text)
            if party1_match:
                auto_filled['party1'] = party1_match.group(1).strip().title()
        if 'party2' not in auto_filled:
            party2_match = re.search(r"party 2:?\s*([a-zA-Z\s]+)", prompt_text)
            if party2_match:
                auto_filled['party2'] = party2_match.group(1).strip().title()
        if 'position' not in auto_filled:
            pos_match = re.search(r"position:?\s*([a-zA-Z\s]+)", prompt_text)
            if pos_match:
                auto_filled['position'] = pos_match.group(1).strip()
        if 'salary' not in auto_filled:
            salary_match = re.search(r"\$[\d,]+(?:\.\d{2})?", prompt_text)
            if salary_match:
                auto_filled['salary'] = salary_match.group(0).strip()

    # Update answers with auto-filled values if not already present
    answers.update({k: v for k, v in auto_filled.items() if k not in answers or not answers[k]})

    # Now, ask for missing fields using the standard guided question flow
    return handle_guided_questions(document_type, answers, required_questions)

def handle_nda_flow(answers):
    prompt_text = answers['initial_prompt'].lower()
    auto_filled = {}


    # Improved: Try to extract parties from various phrasings
    party_patterns = [
        r"between\s+([\w\s&.,'-]+?)\s+and\s+([\w\s&.,'-]+?)(?:\.|$)",
        r"by and between\s+([\w\s&.,'-]+?)\s+and\s+([\w\s&.,'-]+?)(?:\.|$)",
        r"([A-Z][a-zA-Z\s]+)\s+and\s+([A-Z][a-zA-Z\s]+)"
    ]
    for pat in party_patterns:
        match = re.search(pat, prompt_text, re.IGNORECASE)
        if match:
            auto_filled['party1'] = match.group(1).strip().title()
            auto_filled['party2'] = match.group(2).strip().title()
            break

    # Improved: Try to extract duration from more flexible patterns
    duration_match = re.search(r"(\d+)\s*(year|month|day|week|hour)s?", prompt_text)
    if duration_match:
        auto_filled['duration'] = f"{duration_match.group(1)} {duration_match.group(2)}{'s' if not duration_match.group(2).endswith('s') else ''}"

    # Improved: Try to extract purpose from more flexible patterns
    purpose_patterns = [
        r"purpose\s*[:is]?\s*([^\n\.]*)",
        r"for the purpose of\s+([^\n\.]*)",
        r"for\s+([^\n\.]*)"
    ]
    for pat in purpose_patterns:
        match = re.search(pat, prompt_text, re.IGNORECASE)
        if match:
            auto_filled['purpose'] = match.group(1).strip()
            break

    # Improved: Try to extract confidential info
    conf_match = re.search(r"confidential information (?:includes|such as|:|is)\s*([^\n\.]*)", prompt_text)
    if conf_match:
        auto_filled['confidential_info'] = conf_match.group(1).strip()

    answers.update({k:v for k,v in auto_filled.items() if k not in answers})

    # Use all NDA questions from config.py
    from config import GUIDED_TYPES
    required_questions = GUIDED_TYPES["NDA"]
    return handle_guided_questions("NDA", answers, required_questions)

def handle_will_flow(answers):
    prompt_text = answers['initial_prompt'].lower()
    auto_filled = {}


    # Improved: Try to extract testator name from more flexible patterns
    testator_patterns = [
        r"i,?\s*([a-zA-Z\s]+),?\s*being",  # I, John Doe, being...
        r"testator:?\s*([a-zA-Z\s]+)",
        r"will of\s*([a-zA-Z\s]+)"
    ]
    for pat in testator_patterns:
        match = re.search(pat, prompt_text, re.IGNORECASE)
        if match:
            auto_filled['testator_name'] = match.group(1).strip().title()
            break

    # Improved: Try to extract beneficiaries from more flexible patterns
    beneficiaries_patterns = [
        r"(?:leave|bequeath|give)\s+(.+?)\s+(?:to|for)\s+([a-zA-Z\s,]+)",
        r"beneficiaries?\s*:?\s*([a-zA-Z\s,]+)"
    ]
    for pat in beneficiaries_patterns:
        match = re.search(pat, prompt_text, re.IGNORECASE)
        if match:
            auto_filled['beneficiaries'] = match.group(2).strip().title() if match.lastindex > 1 else match.group(1).strip().title()
            break

    # Improved: Try to extract executor
    executor_match = re.search(r"executor:?\s*([a-zA-Z\s]+)", prompt_text)
    if executor_match:
        auto_filled['executor'] = executor_match.group(1).strip().title()

    # Improved: Try to extract assets
    assets_match = re.search(r"assets?\s*:?\s*([a-zA-Z0-9,\s]+)", prompt_text)
    if assets_match:
        auto_filled['assets'] = assets_match.group(1).strip()

    # Improved: Try to extract special instructions
    special_match = re.search(r"special instructions?\s*:?\s*([a-zA-Z0-9,\s]+)", prompt_text)
    if special_match:
        auto_filled['special_instructions'] = special_match.group(1).strip()

    answers.update({k:v for k,v in auto_filled.items() if k not in answers})

    answers.update({k:v for k,v in auto_filled.items() if k not in answers})

    from config import GUIDED_TYPES
    required_questions = GUIDED_TYPES["Will"]
    return handle_guided_questions("Will", answers, required_questions)

def handle_lease_flow(answers):
    from config import GUIDED_TYPES
    prompt_text = answers.get('initial_prompt', '').lower()
    lease_keys = [k for k, _ in GUIDED_TYPES["Lease Agreement"]]
    auto_filled = {}
    # Try to fill as many fields as possible from the prompt using config keys
    for key in lease_keys:
        # Use a flexible pattern: key (with underscores replaced by spaces or nothing) followed by : or is or =
        key_pattern = key.replace('_', '[ _-]?')
        pattern = rf"{key_pattern}\s*[:=\-]?\s*([^\n\r\.,]+)"
        match = re.search(pattern, prompt_text, re.IGNORECASE)
        if match and not answers.get(key):
            auto_filled[key] = match.group(1).strip()
    # Fallback for landlord/tenant if not found
    if not auto_filled.get('landlord') or not auto_filled.get('tenant'):
        party_patterns = [
            r"between\s+([\w\s&.,'-]+?)\s+and\s+([\w\s&.,'-]+?)(?:\.|$)",
            r"by and between\s+([\w\s&.,'-]+?)\s+and\s+([\w\s&.,'-]+?)(?:\.|$)",
            r"([A-Z][a-zA-Z\s]+)\s+and\s+([A-Z][a-zA-Z\s]+)"
        ]
        for pat in party_patterns:
            match = re.search(pat, prompt_text, re.IGNORECASE)
            if match:
                auto_filled['landlord'] = match.group(1).strip().title()
                auto_filled['tenant'] = match.group(2).strip().title()
                break
    answers.update({k:v for k,v in auto_filled.items() if k not in answers})
    required_questions = GUIDED_TYPES["Lease Agreement"]
    return handle_guided_questions("Lease Agreement", answers, required_questions)

def handle_contract_flow(answers):
    # Use Gemini API to extract contract fields from the prompt
    import json
    from generator import gemini_extract_contract_fields

    prompt_text = answers['initial_prompt']
    # Only extract if not already done
    if not answers.get('_gemini_extracted'):
        try:
            extracted = gemini_extract_contract_fields(prompt_text)
            if isinstance(extracted, str):
                extracted = json.loads(extracted)
            if isinstance(extracted, dict):
                for k, v in extracted.items():
                    if v and k not in answers:
                        answers[k] = v
            answers['_gemini_extracted'] = True
        except Exception as e:
            st.info(f"Could not auto-extract fields: {e}")

    # First determine contract type if not specified
    if 'contract_type' not in answers:
        contract_type = st.selectbox(
            "Select contract type:",
            ["Employment", "Service", "Sales", "Partnership", "Other"]
        )
        if st.button("Continue"):
            answers['contract_type'] = contract_type.lower()
            st.rerun()
        return None

    from config import GUIDED_TYPES
    required_questions = GUIDED_TYPES["Contract"]
    return handle_guided_questions("Contract", answers, required_questions)

def handle_guided_questions(doc_type, answers, required_questions):
    # Chatbot-style: ask for missing details one by one, else show summary and generate
    import json
    missing = [(q_key, q_text) for q_key, q_text in required_questions if not answers.get(q_key, '').strip()]
    if missing:
        q_key, q_text = missing[0]
        st.markdown(f"**{q_text}**")
        user_val = None
        # If the field is a date, use a calendar picker
        if 'date' in q_key:
            import datetime
            today = datetime.date.today()
            user_val = st.date_input("Select date:", value=today, key=f"chatbot_date_{q_key}")
            submit = st.button("Submit", key=f"submit_{q_key}")
            if submit:
                answers[q_key] = user_val.strftime('%m/%d/%Y')
                st.rerun()
        else:
            user_val = st.text_input("Your answer:", key=f"chatbot_{q_key}")
            if st.button("Submit", key=f"submit_{q_key}"):
                if user_val and user_val.strip():
                    answers[q_key] = user_val.strip()
                    st.rerun()
                else:
                    st.warning("Please provide a value.")
        # Show what has already been filled
        st.markdown("<hr><b>Already provided:</b>", unsafe_allow_html=True)
        for k, label in required_questions:
            if answers.get(k, '').strip() and k != q_key:
                st.markdown(f"<b>{label}</b> <span style='color:#283593'>{answers[k]}</span>", unsafe_allow_html=True)
        return None
    # If nothing missing, show summary and allow generate
    st.markdown(f"#### Review all details for your {doc_type}")
    st.markdown("<div style='background:#f8f8ff;padding:1em;border-radius:8px;'>", unsafe_allow_html=True)
    for q_key, q_text in required_questions:
        val = answers.get(q_key, '')
        if val:
            st.markdown(f"<b>{q_text}</b> <span style='color:#283593'>{val}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("Generate Document"):
        document_type = doc_type
        user_input = '\n'.join([f"{q_text} {answers[q_key]}" for q_key, q_text in required_questions if answers.get(q_key)])
        if 'initial_prompt' in answers:
            user_input = f"Prompt: {answers['initial_prompt']}\n" + user_input
        generate_document(document_type, user_input)
        st.rerun()
    return None

# --- Input Validation ---
def validate_input(value, field_name):
    if not value.strip():
        st.warning(f"Please provide a valid {field_name.lower()}")
        return False
    return True

# --- Document Generation ---
@handle_errors
@st.cache_data(show_spinner="Generating document...")
def generate_document(document_type, user_input):
    with st.spinner('Generating document...'):
        time.sleep(0.5)  # Simulate processing delay
        prompt = get_prompt_template(document_type, user_input)
        memory = get_session_memory(st.session_state.app_state['history'])
        draft = generate_legal_text(prompt, memory)

        # --- Clean up HTML/Markdown tags if present ---
        import re
        def strip_html_md(text):
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', text)
            # Remove markdown bold/italic/headers
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
            text = re.sub(r'__([^_]+)__', r'\1', text)
            text = re.sub(r'\*([^*]+)\*', r'\1', text)
            text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
            return text

        def parse_headings(text):
            # Returns a list of (is_heading, line) tuples
            lines = text.split('\n')
            result = []
            for line in lines:
                lstripped = line.lstrip()
                # Heading if line starts with number+dot+space, or is all uppercase and not too short
                if re.match(r'^(\d+\.|[A-Z][A-Z\s\-]+)$', lstripped) or re.match(r'^\*\*.+\*\*$', lstripped):
                    result.append((True, line.strip()))
                elif re.match(r'^[A-Z][A-Z\s\-]{5,}$', lstripped) and len(lstripped.split()) <= 8:
                    result.append((True, line.strip()))
                elif re.match(r'^\d+\.\s+.+', lstripped):
                    result.append((True, line.strip()))
                else:
                    result.append((False, line))
            return result

        formatted = strip_html_md(draft)
        if not formatted.lower().startswith(document_type.lower()):
            formatted = f"{document_type}\n\n" + formatted
        formatted = re.sub(r"\n{2,}", "\n\n", formatted)
        if "signature" not in formatted.lower():
            formatted += "\n\n______________________________\nSignature"

        # Highlight headings for TXT/text area: ALL CAPS and extra spacing
        parsed = parse_headings(formatted)
        txt_highlighted = []
        for is_heading, line in parsed:
            if is_heading and line.strip():
                txt_highlighted.append(line.upper())
                txt_highlighted.append("")  # Extra blank line after heading
            else:
                txt_highlighted.append(line)
        txt_final = "\n".join(txt_highlighted)

        # Update session state with highlighted version for display/export
        st.session_state.app_state['history'].append({
            'type': document_type,
            'input': user_input,
            'draft': txt_final,
            'timestamp': time.time()
        })
        st.session_state.app_state['last_generated'] = txt_final
        st.session_state.app_state['current_document'] = txt_final

        # Save parsed headings for PDF/DOCX export
        st.session_state.app_state['last_headings'] = parsed

        return txt_final

# --- History Management ---
def render_history():
    if st.session_state.app_state['history']:
        st.sidebar.subheader("Session History")
        for i, item in enumerate(reversed(st.session_state.app_state['history'])):
            if st.sidebar.button(
                f"{i+1}. {item['type']}: {item['input'][:30]}...",
                key=f"history_{i}"
            ):
                st.session_state.app_state['current_document'] = item['draft']
                st.rerun()

# --- Main App ---
def main():
    init_session_state()
    # Ensure selected_doc_type is always set
    if 'selected_doc_type' not in st.session_state.app_state:
        st.session_state.app_state['selected_doc_type'] = 'NDA'
    render_sidebar()

    # Main header
    st.markdown('''
        <div class="main-title">Legal Drafter Pro 
            <span style="font-size:1.2rem;font-weight:400;">
                - AI Powered Document Generation
            </span>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
        <div class="desc-text">
            Easily draft legal documents using <b>advanced AI</b>. Select a document type, 
            provide details, and generate professional drafts instantly.
        </div>
    ''', unsafe_allow_html=True)


    # Full-width layout for prompt guidance and input
    st.markdown('<h4 style="color:#283593;">1. Document Details</h4>', unsafe_allow_html=True)
    document_type = st.session_state.app_state.get('selected_doc_type', 'NDA')
    if document_type in ["NDA", "Will", "Lease Agreement", "Contract"]:
        draft = handle_document_flow(document_type)
    else:
        # For custom types, show prompt guidance and input full width
        st.markdown("""
        <div style='background-color:#f5f5fa;padding:1em;border-radius:8px;margin-bottom:0.5em;'>
        <b>How to write your prompt:</b><br>
        <ul style='margin-bottom:0.5em;'>
            <li>Clearly state the type of document and all parties involved.</li>
            <li>Include all important details (purpose, terms, dates, payment, etc.).</li>
            <li>Be concise but specific for best results.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        user_input = st.text_area(
            "Describe your requirements:",
            height=450,
            help="Be as specific as possible for better results"
        )
        if st.button("Generate Draft"):
            if validate_input(user_input, "requirements description"):
                draft = generate_document(document_type, user_input)

    # Only show the generated draft if a document is generated
    current_doc = st.session_state.app_state.get('current_document')
    parsed_headings = st.session_state.app_state.get('last_headings')
    if current_doc:
        st.markdown('<h4 style="color:#283593;">2. Generated Draft</h4>', unsafe_allow_html=True)
        st.text_area(
            "Legal Document", 
            current_doc, 
            height=400, 
            key="output_area",
            disabled=True,
            label_visibility="collapsed"
        )
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.download_button(
                label="Download as TXT",
                data=current_doc,
                file_name=f"{document_type.lower().replace(' ', '_')}_draft.txt",
                mime="text/plain"
            )
        with col2:
            pdf_bytes = None
            if FPDF is not None and parsed_headings is not None:
                pdf = FPDF()
                pdf.unifontsubset = False  # Fix for AttributeError in some fpdf versions
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.set_font("Arial", size=12)
                for is_heading, line in parsed_headings:
                    if is_heading and line.strip():
                        pdf.set_font("Arial", style="B", size=12)
                        pdf.multi_cell(0, 10, line.upper())
                        pdf.ln(1)
                        pdf.set_font("Arial", style="", size=12)
                    else:
                        pdf.multi_cell(0, 10, line)
                try:
                    pdf_bytes = pdf.output(dest='S').encode('latin1')
                except Exception as e:
                    pdf_bytes = None
            st.download_button(
                label="Download as PDF",
                data=pdf_bytes if pdf_bytes else b"PDF export requires fpdf module",
                file_name=f"{document_type.lower().replace(' ', '_')}_draft.pdf",
                mime="application/pdf",
                disabled=pdf_bytes is None
            )
        with col3:
            docx_bytes = None
            if Document is not None and parsed_headings is not None:
                doc = Document()
                for is_heading, line in parsed_headings:
                    if is_heading and line.strip():
                        para = doc.add_paragraph()
                        run = para.add_run(line.upper())
                        run.bold = True
                    else:
                        doc.add_paragraph(line)
                docx_buffer = io.BytesIO()
                doc.save(docx_buffer)
                docx_bytes = docx_buffer.getvalue()
            st.download_button(
                label="Download as DOCX",
                data=docx_bytes if docx_bytes else b"DOCX export requires python-docx module",
                file_name=f"{document_type.lower().replace(' ', '_')}_draft.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                disabled=docx_bytes is None
            )

    # Footer
    st.markdown("---")
    st.markdown('''
        <div class="footer" style="text-align:center;">
            Made with ❤️ using <b>Streamlit</b> | Secure & Confidential | © 2025
        </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()