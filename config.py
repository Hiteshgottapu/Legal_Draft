# config.py

# Guided question sets for each document type
GUIDED_TYPES = {
    "NDA": [
        ("title", "Title of the Agreement (e.g., Non-Disclosure Agreement or Confidentiality Agreement)"),
        ("disclosing_party", "Who is the Disclosing Party? (Name/Company)"),
        ("receiving_party", "Who is the Receiving Party? (Name/Company)"),
        ("confidential_info", "Define what is considered Confidential Information."),
        ("exclusions", "List any exclusions (Non-Confidential Information). (optional)"),
        ("obligations", "What are the obligations of the Receiving Party? (optional)"),
        ("duration", "What is the term/duration of confidentiality? (e.g., 2 years)"),
        ("return_destruction", "What should happen to confidential information at the end? (Return/Destruction)",),
        ("remedies", "What remedies are available for breach? (optional)"),
        ("jurisdiction", "Jurisdiction & Governing Law (optional)"),
        ("non_compete", "Include a Non-Compete clause? (yes/no, details if yes) (optional)"),
        ("non_solicitation", "Include a Non-Solicitation clause? (yes/no, details if yes) (optional)"),
        ("survival_clause", "Include a Survival Clause? (yes/no, details if yes) (optional)"),
        ("no_license", "State that no license is granted? (yes/no, details if yes) (optional)"),
        ("signatures", "Names, Titles, and Dates for signatures"),
        # Optional Add-Ons
        ("non_circumvention", "Include a Non-Circumvention Clause? (yes/no, details if yes) (optional)"),
        ("injunctive_relief", "Include an Injunctive Relief Clause? (yes/no, details if yes) (optional)"),
        ("residuals", "Include a Residuals Clause? (yes/no, details if yes) (optional)"),
    ],
    "Will": [
        ("title", "Title of the Will (e.g., Last Will and Testament)"),
        ("testator_name", "Full name of the person making the will (Testator)"),
        ("testator_address", "Address of the Testator (optional)"),
        ("declaration", "Declaration statement (e.g., sound mind, revoking prior wills) (optional)"),
        ("executor", "Name and details of the Executor (person who will carry out the will)"),
        ("alternate_executor", "Alternate Executor (if primary cannot serve) (optional)"),
        ("beneficiaries", "List all beneficiaries (names, relationships, and what they receive)"),
        ("assets", "List the main assets to be distributed (property, bank accounts, etc.)"),
        ("specific_bequests", "Any specific gifts or bequests? (item, recipient) (optional)"),
        ("residuary_clause", "Who receives the remainder of the estate? (Residuary Clause)"),
        ("guardianship", "Guardian(s) for minor children (if any) (optional)"),
        ("funeral_burial", "Funeral/burial/cremation wishes (optional)"),
        ("debts_taxes", "Instructions for payment of debts and taxes (optional)"),
        ("no_contest", "Include a No-Contest Clause? (yes/no, details if yes) (optional)"),
        ("witnesses", "Names and details of witnesses (usually 2 required)"),
        ("notary", "Is notarization required? (yes/no) (optional)"),
        ("signatures", "Names, dates, and signatures of Testator and witnesses"),
    ],
    "Lease Agreement": [
        ("title", "Title of the Lease Agreement (e.g., Residential Lease Agreement, Commercial Lease Agreement)"),
        ("landlord", "Who is the landlord (Lessor)?"),
        ("tenant", "Who is the tenant (Lessee)?"),
        ("property_address", "What is the property address? (Include unit number, parking/storage spaces if applicable)"),
        ("lease_term", "What is the lease term? (Start and end dates)"),
        ("renewal_terms", "What are the renewal terms? (optional)"),
        ("rent_amount", "What is the monthly rent amount?"),
        ("rent_due_date", "What is the rent due date each month?"),
        ("late_fees", "Are there late fees? If so, specify amount and conditions. (optional)"),
        ("security_deposit", "What is the security deposit amount?"),
        ("deposit_return_conditions", "What are the conditions for return of the security deposit?"),
        ("utilities", "Who pays for which utilities? (water, electricity, trash, etc.)"),
        ("maintenance", "Who is responsible for maintenance?"),
        ("occupancy_rules", "What are the occupancy rules? (Number of tenants, subletting policy)"),
        ("pet_policy", "Are pets allowed? Specify any fees or restrictions."),
        ("repairs_alterations", "Who is responsible for repairs and alterations? What are the rules for modifications?"),
        ("entry_by_landlord", "What are the notice requirements for landlord entry (inspections/repairs)?"),
        ("termination_eviction", "What are the early termination penalties and eviction conditions?"),
        ("insurance_requirements", "Is renter’s insurance required? (optional)"),
        ("governing_law", "Which state/country laws apply to the lease?"),
        ("signatures", "Names, titles, and dates for signatures (Landlord, Tenant, Witness if required)"),
        # Optional Add-Ons
        ("furniture_appliances", "Are furniture/appliances included? List items if furnished. (optional)"),
        ("parking_rules", "What are the parking rules? (assigned spots, guest parking) (optional)"),
        ("noise_behavior", "Are there noise/behavior clauses? (quiet hours, no smoking, etc.) (optional)"),
    ],
    "Contract": [
        ('party1', "Employer/Company name:"),
        ('party2', "Employee/Intern name:"),
        ('contract_type', "Type of contract (Internship, Employment, Freelancing, Service, Other):"),
        ('position', "Role/Position (e.g., Software Engineer, Marketing Intern):"),
        ('start_date', "Joining/Start date (MM/DD/YYYY):"),
        ('duration', "Contract duration (e.g., '3 months', '1 year'):"),
        ('stipend', "Stipend/Salary (if applicable):"),
        ('working_hours', "Working hours (e.g., '9am-5pm, Mon-Fri'):"),
        ('location', "Work location (Remote/On-site/Hybrid, address if on-site):"),
        ('supervisor', "Supervisor/Mentor name (if applicable):"),
        ('purpose', "Purpose of the contract:"),
        ('responsibilities', "Key responsibilities:"),
        ('terms', "Key terms and conditions:"),
        ('payment_terms', "Payment terms (if applicable):"),
        ('benefits', "Benefits (if any):"),
        ('confidentiality', "Confidentiality/NDA requirements (if any):"),
        ('termination', "Termination notice period (if applicable):"),
        ('special_instructions', "Any special instructions or clauses:"),
    ],
}
CSS_STYLES = """
    <style>
    /* Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Base Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        scroll-behavior: smooth;
    }
    
    /* Main Title */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #1a237e;
        letter-spacing: -0.5px;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #1a237e 0%, #3949ab 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    
    /* Description Text */
    .desc-text {
        font-size: 1.1rem;
        color: #4a5568;
        margin-bottom: 2rem;
        line-height: 1.6;
        max-width: 90%;
    }
    
    /* Sidebar Styles */
    .sidebar .sidebar-content {
        background: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a237e;
        margin: 0;
    }
    
    /* Button Styles */
    .stButton>button {
        background: linear-gradient(90deg, #3949ab 0%, #1976d2 100%);
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.65em 1.75em;
        margin: 0.5em 0;
        box-shadow: 0 2px 15px rgba(25, 118, 210, 0.2);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #1976d2 0%, #3949ab 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(25, 118, 210, 0.3);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Input Fields */
    .stTextArea textarea, .stTextInput input {
        background: #ffffff;
        border-radius: 10px;
        border: 1px solid #cbd5e0;
        font-size: 1rem;
        color: #2d3748;
        padding: 12px 14px;
        transition: all 0.2s;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #4299e1;
        box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
        outline: none;
    }
    
    /* Card Styles */
    .stTextArea, .stTextInput {
        border-radius: 12px;
        padding: 1.5rem;
        background: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    /* History Items */
    .session-history {
        font-size: 0.95rem;
        color: #4a5568;
        margin-bottom: 0.75rem;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        transition: all 0.2s;
        cursor: pointer;
        border-left: 3px solid transparent;
    }
    
    .session-history:hover {
        background: #edf2f7;
        border-left: 3px solid #4299e1;
        transform: translateX(2px);
    }
    
    /* Footer */
    .footer {
        color: #718096;
        font-size: 0.95rem;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e2e8f0;
        text-align: center;
    }
    
    /* Responsive Adjustments */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.2rem;
        }
        
        .desc-text {
            font-size: 1rem;
            max-width: 100%;
        }
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
    
    /* Animation for Loading */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .loading-pulse {
        animation: pulse 1.5s infinite ease-in-out;
    }
    
    /* Badge Styles */
    .badge {
        display: inline-block;
        padding: 0.25em 0.6em;
        font-size: 0.75em;
        font-weight: 600;
        line-height: 1;
        color: white;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 10px;
        background-color: #4299e1;
    }
    
    /* Tooltip Styles */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #2d3748;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.85rem;
        font-weight: normal;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
"""