import importlib.util
import os
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "skills"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_skills() -> dict:
    """Scan skills/ and return {name: {description, parameters, module}}."""
    skills = {}
    if not SKILLS_DIR.exists():
        return skills
    for f in sorted(SKILLS_DIR.glob("*.py")):
        if f.name.startswith("_"):
            continue
        try:
            mod = _load_module(f.stem, f)
            skills[f.stem] = {
                "description": getattr(mod, "SKILL_DESCRIPTION", "No description"),
                "parameters": getattr(mod, "SKILL_PARAMETERS", {}),
                "module": mod,
            }
        except Exception as e:
            print(f"  [!] Failed to load skill {f.name}: {e}", file=sys.stderr)
    return skills


def run_skill(skills: dict, name: str, params: dict) -> str:
    skill = skills.get(name)
    if not skill:
        return f"Error: skill '{name}' not found."
    try:
        return str(skill["module"].run(params))
    except Exception as e:
        return f"Error running skill '{name}': {e}"


def create_skill(name: str, description: str, code: str) -> str:
    SKILLS_DIR.mkdir(exist_ok=True)
    path = SKILLS_DIR / f"{name}.py"
    if path.exists():
        return f"Skill '{name}' already exists."
    # Ensure the code has the required interface
    if "SKILL_DESCRIPTION" not in code:
        code = f'SKILL_DESCRIPTION = "{description}"\n\n{code}'
    path.write_text(code)
    return f"Skill '{name}' created at {path}"
