SKILL_DESCRIPTION = "Remember and recall personal facts using memory.md"
SKILL_PARAMETERS = {"action": "'save', 'recall', 'list', or 'forget'", "fact": "a compact sentence to remember (for save/forget)"}

import os

MEMORY_FILE = "memory.md"

def run(params: dict) -> str:
    action = params.get("action", "").lower()
    fact = params.get("fact", "").strip()
    
    if action == "save":
        if not fact:
            return "Please provide something to remember."
        with open(MEMORY_FILE, "a") as f:
            f.write(f"- {fact}\n")
        return f"Got it, I'll remember: {fact}"
    
    elif action in ("recall", "list"):
        if not os.path.exists(MEMORY_FILE):
            return "I don't know anything about you yet."
        with open(MEMORY_FILE, "r") as f:
            content = f.read().strip()
        if not content:
            return "I don't know anything about you yet."
        return f"Here's what I know about you:\n{content}"
    
    elif action == "forget":
        if not os.path.exists(MEMORY_FILE):
            return "Nothing to forget."
        if not fact:
            os.remove(MEMORY_FILE)
            return "I've forgotten everything about you."
        else:
            with open(MEMORY_FILE, "r") as f:
                lines = f.readlines()
            with open(MEMORY_FILE, "w") as f:
                removed = False
                for line in lines:
                    if fact.lower() in line.lower() and not removed:
                        removed = True
                        continue
                    f.write(line)
            if removed:
                return f"Okay, I've forgotten about: {fact}"
            else:
                return f"I didn't find anything matching '{fact}' to forget."
    
    else:
        return "Please specify action: save, recall, list, or forget"