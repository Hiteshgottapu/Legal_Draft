
def get_session_memory(history):
    """
    Returns a string summary of previous drafts for context, with exception handling.
    """
    try:
        if not history:
            return ""
        memory = []
        for item in history[-3:]:  # Only last 3 for brevity
            memory.append(f"Type: {item['type']}, Input: {item['input']}, Draft: {item['draft'][:100]}...")
        return "\n".join(memory)
    except Exception as e:
        return f"[Error] Failed to get session memory: {e}"


def update_session_memory(history, new_item):
    """
    Appends a new item to history with exception handling.
    """
    try:
        history.append(new_item)
        return history
    except Exception as e:
        return f"[Error] Failed to update session memory: {e}"
