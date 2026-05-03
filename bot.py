import json
import os
import sys

from openai import OpenAI

from skill_manager import create_skill, load_skills, run_skill

MODEL = os.environ.get("MODEL")

SYSTEM_PROMPT = """\
You are a helpful assistant that can learn new abilities on the fly.

When a user asks you to do something you can't do yet, you figure out how to do it — by writing code, calling APIs, or using tools you already know about. You learn new things by writing small Python programs that become permanent abilities you can reuse later.

## Your Abilities Right Now
{skill_manifest}

## How You Work
- You already have some abilities listed above. Use them when they match what the user needs.
- If you don't have an ability the user needs, teach yourself by writing a new one. Don't ask permission — just do it.
- If you need something from the user to make an ability work (an API key, a package to install, access to a service), ask them naturally, like a person would.
- When you learn something new, tell the user in plain language: "I just figured out how to do X" — don't mention code, files, or technical internals.
- When you use an ability, just show the result. Don't explain the mechanism unless the user asks.
- If a task is simple enough to answer with your general knowledge, just answer it directly. Don't write code for things you already know.

## Code Format for New Abilities
When you write a new ability, the code must follow this structure:

```python
SKILL_DESCRIPTION = "One-line description"
SKILL_PARAMETERS = {{"param_name": "description"}}

def run(params: dict) -> str:
    # your code here
    return "result as string"
```

The `run(params)` function is required. It gets a dict of inputs and returns a string.

## Personality
- Be direct and helpful. Don't hedge or over-explain.
- Show, don't tell. When you can do something, do it — don't describe what you could do.
- If you get stuck, say so plainly and ask for what you need.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "use_ability",
            "description": "Use one of your existing abilities to do something for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The ability name",
                    },
                    "params": {
                        "type": "object",
                        "description": "Parameters for the ability",
                    },
                },
                "required": ["name", "params"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "learn_ability",
            "description": "Teach yourself a new ability by writing a Python program. Use this when you can't handle the user's request with what you already know.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Short name for the ability (snake_case)",
                    },
                    "description": {
                        "type": "string",
                        "description": "What this ability does",
                    },
                    "code": {
                        "type": "string",
                        "description": "Complete Python code with SKILL_DESCRIPTION, SKILL_PARAMETERS, and run(params) -> str",
                    },
                },
                "required": ["name", "description", "code"],
            },
        },
    },
]


def build_manifest(skills: dict) -> str:
    if not skills:
        return "(none yet — you'll create them as needed)"
    lines = []
    for name, info in skills.items():
        params = info["parameters"]
        param_str = f"  inputs: {json.dumps(params)}" if params else ""
        lines.append(f"- {name}: {info['description']}{param_str}")
    return "\n".join(lines)


def handle_tool_call(skills: dict, name: str, args: dict) -> str:
    if name == "use_ability":
        return run_skill(skills, args["name"], args["params"])
    elif name == "learn_ability":
        result = create_skill(args["name"], args["description"], args["code"])
        skills.update(load_skills())
        return result
    return f"Unknown tool: {name}"


def main():
    endpoint = os.environ.get("API_BASE_URL")
    api_key = os.environ.get("API_KEY")
    if not endpoint or not api_key or not MODEL:
        print("Error: set API_BASE_URL, API_KEY, and MODEL env vars.")
        sys.exit(1)

    client = OpenAI(base_url=endpoint, api_key=api_key)
    skills = load_skills()

    print("Ready. What do you need?\n")

    messages = [{"role": "system", "content": SYSTEM_PROMPT.format(skill_manifest=build_manifest(skills))}]

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        while True:
            resp = client.chat.completions.create(
                model=MODEL,
                max_tokens=4096,
                messages=messages,
                tools=TOOLS,
            )

            choice = resp.choices[0]
            msg = choice.message
            messages.append(msg.model_dump())

            if not msg.tool_calls:
                if msg.content:
                    print(f"\n{msg.content}\n")
                break

            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                print(f"  [{tc.function.name}] ...")
                result = handle_tool_call(skills, tc.function.name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

            messages[0] = {"role": "system", "content": SYSTEM_PROMPT.format(skill_manifest=build_manifest(skills))}


if __name__ == "__main__":
    main()
