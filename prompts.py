
def get_prompt_template(document_type, user_input):
    """
    Returns a prompt template string for the given document type and user input, with exception handling.
    """
    try:
        templates = {
            "Contract": "Draft a professional contract based on the following requirements: {details}",
            "NDA": (
                "Draft a comprehensive non-disclosure agreement (NDA) using the following details. "
                "Include all standard NDA sections and ensure the following fields are addressed: "
                "Title, Disclosing Party, Receiving Party, Confidential Information, Exclusions, Obligations, Duration, "
                "Return/Destruction of Information, Remedies, Jurisdiction, Non-Compete, Non-Solicitation, Survival Clause, "
                "No License, Signatures, Non-Circumvention, Injunctive Relief, Residuals. "
                "If any field is missing, use standard legal language. Use clear headings for each section.\n\nDetails: {details}"
            ),
            "Will": "Draft a last will and testament considering: {details}",
            "Lease Agreement": "Draft a lease agreement with the following: {details}",
            "Custom": "Draft a legal document as described: {details}"
        }
        template = templates.get(document_type, templates["Custom"])
        return template.format(details=user_input)
    except Exception as e:
        return f"[Error] Failed to generate prompt template: {e}"
