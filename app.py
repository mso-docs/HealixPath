"""
HealixPath Gradio Web Interface

A web interface for generating AI-powered persona-driven narratives.
"""

import gradio as gr
import json
import subprocess
import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# Modern CSS styling
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap');

:root {
    --bg: #050e0a;
    --panel: #0b1812;
    --card: linear-gradient(135deg, rgba(18, 64, 44, 0.94), rgba(10, 34, 24, 0.94));
    --line: rgba(31, 132, 84, 0.6);
    --accent: #1da05f;
    --accent-strong: #167b46;
    --muted: #9fd8b9;
    --text: #f7fff9;
    --text-dim: #c9e5d4;
    --radius: 18px;
    --shadow: 0 18px 60px rgba(4, 26, 18, 0.45);
}

* {
    font-family: 'Manrope', 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
}

body,
html {
    background: radial-gradient(circle at 18% 18%, rgba(29, 160, 96, 0.08), transparent 32%),
                radial-gradient(circle at 82% 12%, rgba(18, 92, 59, 0.12), transparent 38%),
                var(--bg);
    color: var(--text);
}

.gradio-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px;
    background: transparent;
}

.gr-blocks,
.gr-page,
#mount {
    background: transparent;
}

a {
    color: var(--accent);
}

.header-shell {
    background: linear-gradient(135deg, rgba(18, 64, 44, 0.95), rgba(10, 34, 24, 0.92));
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 28px 24px;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow);
}

.header-shell::after {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 25% 20%, rgba(34, 197, 94, 0.18), transparent 50%);
    pointer-events: none;
}

.header-shell h1 {
    font-size: clamp(32px, 5vw, 46px);
    font-weight: 700;
    letter-spacing: -0.5px;
    margin: 6px 0 10px;
    color: var(--text);
}

.header-shell .eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border-radius: 999px;
    border: 1px solid var(--line);
    background: rgba(34, 197, 94, 0.08);
    color: var(--muted);
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.3px;
}

.header-shell p {
    margin: 0;
    color: var(--text-dim);
    font-size: 15px;
    line-height: 1.6;
}

.card-container {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 18px 18px;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.28);
    margin-bottom: 18px;
}

.tabs,
.tab-nav {
    border: 0;
    background: transparent;
}

.tab-nav {
    display: flex;
    gap: 6px;
    padding: 6px;
    margin-bottom: 12px;
    background: linear-gradient(135deg, rgba(10, 34, 24, 0.85), rgba(8, 24, 17, 0.85));
    border: 1px solid var(--line);
    border-radius: 14px;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02), 0 10px 24px rgba(0, 0, 0, 0.3);
}

.tab-nav button {
    border: 1px solid var(--line);
    background: linear-gradient(135deg, rgba(12, 42, 30, 0.9), rgba(10, 34, 24, 0.9));
    color: var(--text);
    padding: 12px 16px;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.2s ease;
    position: relative;
    box-shadow: inset 0 -1px 0 rgba(0, 0, 0, 0.35);
}

.tab-nav button:hover {
    border-color: var(--line);
    color: var(--text);
    background: linear-gradient(135deg, rgba(29, 160, 96, 0.16), rgba(22, 123, 70, 0.18));
}

.tab-nav button[aria-selected="true"] {
    background: linear-gradient(135deg, rgba(29, 160, 96, 0.18), rgba(22, 123, 70, 0.22));
    color: var(--text);
    border-color: var(--line);
    box-shadow: 0 10px 22px rgba(22, 123, 70, 0.24);
    overflow: hidden;
}

.tab-nav button[aria-selected="true"]::after {
    content: "";
    position: absolute;
    left: 12px;
    right: 12px;
    bottom: 4px;
    height: 3px;
    border-radius: 999px;
    background: rgba(10, 40, 26, 0.95);
    box-shadow: 0 2px 8px rgba(10, 40, 26, 0.6);
}

/* force underline on gradio tab items */
.gradio-container .tabitem[aria-selected="true"],
.gradio-container .gr-tabitem[aria-selected="true"],
.gradio-container .tabs button[aria-selected="true"] {
    border-bottom: 3px solid rgba(10, 40, 26, 0.95) !important;
    box-shadow: none !important;
    position: relative;
}

.gradio-container .tabitem[aria-selected="true"]::after,
.gradio-container .tabs button[aria-selected="true"]::after {
    content: "";
    display: block;
    position: absolute;
    left: 12px;
    right: 12px;
    bottom: 2px;
    height: 3px;
    border-radius: 999px;
    background: rgba(10, 40, 26, 0.95);
    box-shadow: 0 2px 8px rgba(10, 40, 26, 0.6);
}

/* fallback for Gradio tab buttons rendered as .tabitem without wrapper */
.gradio-container .tabs button,
.gradio-container .tabs .tabitem,
.gradio-container .gr-tabs button,
.gradio-container .gr-tabs .tabitem {
    background: linear-gradient(135deg, rgba(12, 42, 30, 0.9), rgba(10, 34, 24, 0.9)) !important;
    color: var(--text) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    box-shadow: inset 0 -1px 0 rgba(0, 0, 0, 0.35) !important;
}

.gradio-container .tabs button[aria-selected="true"],
.gradio-container .gr-tabs button[aria-selected="true"],
.gradio-container .tabs .tabitem[aria-selected="true"],
.gradio-container .gr-tabs .tabitem[aria-selected="true"] {
    background: linear-gradient(135deg, rgba(29, 160, 96, 0.18), rgba(22, 123, 70, 0.22)) !important;
    border-color: var(--line) !important;
    color: var(--text) !important;
    position: relative;
}

.gradio-container .tabs button[aria-selected="true"]::after,
.gradio-container .gr-tabs button[aria-selected="true"]::after,
.gradio-container .tabs .tabitem[aria-selected="true"]::after,
.gradio-container .gr-tabs .tabitem[aria-selected="true"]::after {
    content: "";
    position: absolute;
    left: 12px;
    right: 12px;
    bottom: 2px;
    height: 3px;
    border-radius: 999px;
    background: rgba(10, 40, 26, 0.95);
    box-shadow: 0 2px 8px rgba(10, 40, 26, 0.6);
}

.gr-row {
    gap: 14px;
    align-items: stretch;
}

label {
    color: var(--text);
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 8px;
    display: inline-block;
}

input[type="text"],
textarea,
select,
.gradio-textbox input,
.gradio-textbox textarea,
.gradio-dropdown select {
    background: linear-gradient(135deg, #0b1d14, #0a1610);
    border: 1px solid var(--line);
    border-radius: 10px;
    color: var(--text);
    padding: 0.5em 0.75em;
    font-size: 14px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.1s ease;
    width: 100%;
    box-sizing: border-box;
}

input[type="text"]:focus,
textarea:focus,
select:focus,
.gradio-textbox input:focus,
.gradio-textbox textarea:focus,
.gradio-dropdown select:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(29, 160, 96, 0.25);
    outline: none;
    transform: translateY(-1px);
    background: linear-gradient(135deg, #0f2a1c, #0b1f15);
}

input::placeholder,
textarea::placeholder {
    color: var(--muted);
}

.gradio-dropdown select,
.gradio-dropdown .wrap,
.gradio-dropdown button,
[data-testid="dropdown"] .single-select,
[data-testid="dropdown"] .wrap,
[data-testid="dropdown"] select,
[data-testid="dropdown"] button {
    background: linear-gradient(135deg, #0b2217, #0a1912) !important;
    border: 0 !important;
    color: var(--text) !important;
    border-radius: 12px !important;
}

.gradio-dropdown .wrap.svelte-1hxfprf,
.gradio-container .container .wrap.svelte-1hxfprf,
.gradio-container .container .wrap-inner.svelte-1hxfprf,
.gradio-container .container .secondary-wrap.svelte-1hxfprf {
    background: linear-gradient(135deg, #0b2217, #0a1912) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02), 0 10px 18px rgba(0, 0, 0, 0.25) !important;
    color: var(--text) !important;
    padding: 0 !important;
}

.gradio-container .container.svelte-1hfxrpf,
.gradio-container .container.svelte-1hfxrpf .wrap,
.gradio-container .container.svelte-1hfxrpf .wrap-inner,
.gradio-container .container.svelte-1hfxrpf .secondary-wrap {
    background: linear-gradient(135deg, #0b2217, #0a1912) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02), 0 10px 18px rgba(0, 0, 0, 0.25) !important;
    color: var(--text) !important;
}

.gradio-container .container.svelte-1hfxrpf input.border-none,
.gradio-container .container.svelte-1hfxrpf input.svelte-1hfxrpf,
.gradio-container .container.svelte-1hfxrpf input {
    background: transparent !important;
    color: var(--text) !important;
    border: none !important;
    padding: 0.5em 0.75em !important;
}

.gradio-container .container.svelte-1hfxrpf .icon-wrap.svelte-1hfxrpf,
.gradio-container .container.svelte-1hfxrpf .dropdown-arrow {
    color: var(--text) !important;
    fill: var(--text) !important;
}

.gradio-dropdown,
.gradio-dropdown > div,
.gradio-dropdown > div > div {
    background: linear-gradient(135deg, #0b2217, #0a1912) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
}

.gradio-dropdown .wrap:focus-within,
.gradio-dropdown select:focus,
[data-testid="dropdown"] select:focus,
[data-testid="dropdown"] .wrap:focus-visible,
[data-testid="dropdown"] .wrap:focus-within {
    box-shadow: 0 0 0 3px rgba(29, 160, 96, 0.25) !important;
    border-color: var(--accent) !important;
}

.gradio-dropdown .options,
[data-testid="dropdown"] .options {
    background: #0b2217 !important;
    border: 1px solid var(--line) !important;
    color: var(--text) !important;
}

.gradio-dropdown .option,
[data-testid="dropdown"] .option {
    background: #0b2217 !important;
    color: var(--text) !important;
}

.gradio-container .gr-panel,
.gradio-container .gr-box,
.gradio-container .gr-form,
.gradio-container .gr-group,
.gradio-container .gr-block,
.gradio-container .block,
.gradio-container .panel,
.gradio-container .form,
.gradio-container .wrap {
    background: linear-gradient(135deg, #0b1d14, #0a1610);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.24);
}

/* nested content stays transparent to let wrappers show gradient */
.gradio-container .gr-panel *,
.gradio-container .gr-box *,
.gradio-container .block *,
.gradio-container .panel * {
    background-color: transparent;
}

/* reduce nested wrapper outlines for dropdown blocks */
.gradio-container .gr-group .gr-column,
.gradio-container .gr-group .gr-form,
.gradio-container .gr-group .gr-box {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}

.gradio-container .container.svelte-1hfxrpf,
.gradio-container .container.svelte-1hfxrpf {
    border: 1px solid var(--line) !important;
    box-shadow: 0 8px 18px rgba(0, 0, 0, 0.18) !important;
    background: linear-gradient(135deg, rgb(11, 29, 20), rgb(10, 22, 16)) !important;
}

/* keep inner wraps clean to avoid stacked outlines */
.gradio-container .container.svelte-1hfxrpf .wrap,
.gradio-container .container.svelte-1hfxrpf .wrap-inner,
.gradio-container .container.svelte-1hfxrpf .secondary-wrap {
    border: 0 !important;
    box-shadow: none !important;
    background: transparent !important;
}

/* inner-most wrapper should have no outline */
.gradio-container .container.svelte-1hfxrpf .secondary-wrap {
    border: none !important;
    box-shadow: none !important;
}


button,
.gradio-button,
.gr-button {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%);
    border: none;
    color: #f7fff9;
    font-weight: 700;
    font-size: 14px;
    padding: 14px 20px !important;
    border-radius: 12px;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 10px 20px rgba(20, 111, 67, 0.28);
}

button:hover,
.gradio-button:hover,
.gr-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 26px rgba(20, 111, 67, 0.34);
}

button:active,
.gradio-button:active,
.gr-button:active {
    transform: translateY(0);
    box-shadow: 0 8px 16px rgba(20, 111, 67, 0.3);
}

.gradio-button:disabled {
    opacity: 0.65;
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
}

[data-testid="textbox"] textarea {
    background: linear-gradient(135deg, #0c2116, #0a1a12);
    font-family: 'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace;
    line-height: 1.55;
    font-size: 13px;
}

.gr-markdown h2,
.gr-markdown h3 {
    color: var(--text);
    margin-bottom: 6px;
}

.gr-markdown p {
    color: var(--text-dim);
    line-height: 1.6;
}

footer,
.footer,
[data-testid="footer"] {
    border-top: 1px solid var(--line);
    margin-top: 18px;
    padding-top: 12px;
    color: var(--text-dim);
    background: transparent;
}

footer * {
    color: var(--text-dim);
}

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.02);
}

::-webkit-scrollbar-thumb {
    background: rgba(34, 197, 94, 0.35);
    border-radius: 6px;
}

@media (max-width: 900px) {
    .gradio-container {
        padding: 18px;
    }

    .header-shell {
        padding: 22px 18px;
    }

    .card-container {
        padding: 14px;
    }

    .tab-nav {
        flex-wrap: wrap;
    }
}
"""

# Load environment variables from .env file
load_dotenv()

# Load personas
def load_personas():
    with open("data/personas.json") as f:
        return json.load(f)

personas = load_personas()

# Create persona descriptions for dropdown display
def create_persona_description(p):
    """Create a short description of a persona."""
    age = p.get("age", "")
    job_title = p.get("job", {}).get("title", "")
    location_city = p.get("location", {}).get("city", "")
    age_label = f"{age}yo" if age else ""
    return f"{p['name']} | {age_label} {job_title} | {location_city}".strip()
# Map display names to persona IDs
persona_options = {create_persona_description(p): p["id"] for p in personas}
CUSTOM_PERSONA_LABEL = "Other (Custom Persona)"
persona_list = list(persona_options.keys())
persona_choices = [CUSTOM_PERSONA_LABEL] + persona_list
default_persona_choice = persona_list[0] if persona_list else CUSTOM_PERSONA_LABEL

# Initialize Anthropic client
api_key = os.getenv("ANTHROPIC_API_KEY")
model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
client = Anthropic(api_key=api_key) if api_key else None

def get_persona_context(persona_id: str, custom_persona: str = "") -> str:
    """Format persona data for prompt context."""
    if custom_persona:
        return f"Persona: {custom_persona}"
    
    for p in personas:
        if p["id"] == persona_id:
            # Handle new persona structure
            job_title = p.get("job", {}).get("title", "Unknown")
            industry = p.get("job", {}).get("industry", "Unknown")
            age = p.get("age", "Unknown")
            location_city = p.get("location", {}).get("city", "Unknown")
            goals = p.get("goals", {}).get("primary_goals", [])
            pain_points = p.get("pain_points", [])
            motivations = p.get("motivations", [])
            
            return f"""Persona: {p["name"]}
Age: {age}
Location: {location_city}
Title: {job_title}
Industry: {industry}
Background: {p.get("background", "")}
Goals: {', '.join(goals) if goals else "N/A"}
Pain Points: {', '.join(pain_points) if pain_points else "N/A"}
Motivations: {', '.join(motivations) if motivations else "N/A"}
User Story: {p.get("user_story", "")}"""
    
    return "Persona: Default user"


def format_persona_from_json(persona_obj: dict) -> str:
    """Format a persona object (from generated personas) into context string."""
    job_title = persona_obj.get("job", {}).get("title", "Unknown")
    industry = persona_obj.get("job", {}).get("industry", "Unknown")
    age = persona_obj.get("age", "Unknown")
    location_city = persona_obj.get("location", {}).get("city", "Unknown")
    goals = persona_obj.get("goals", {}).get("primary_goals", [])
    pain_points = persona_obj.get("pain_points", [])
    motivations = persona_obj.get("motivations", [])
    
    return f"""Persona: {persona_obj.get("name", "Unknown")}
Age: {age}
Location: {location_city}
Title: {job_title}
Industry: {industry}
Background: {persona_obj.get("background", "")}
Goals: {', '.join(goals) if goals else "N/A"}
Pain Points: {', '.join(pain_points) if pain_points else "N/A"}
Motivations: {', '.join(motivations) if motivations else "N/A"}
User Story: {persona_obj.get("user_story", "")}"""


def build_persona_profile(persona_name: str, persona_override: str):
    """Return the persona label for display and the context payload. Returns (label, contexts_list) where contexts_list is a list of persona contexts."""
    # Check if persona_override contains JSON (generated persona)
    if persona_override and persona_override.strip():
        stripped = persona_override.strip()
        if stripped.startswith('{') or stripped.startswith('['):
            try:
                persona_json = json.loads(stripped)
                # If it's an array, return all personas
                if isinstance(persona_json, list) and len(persona_json) > 0:
                    contexts = [format_persona_from_json(p) for p in persona_json if isinstance(p, dict)]
                    return f"{len(contexts)} Generated Personas", contexts
                # If it's a single persona object, use it directly
                elif isinstance(persona_json, dict) and 'id' in persona_json:
                    return persona_json.get('name', 'Generated Persona'), [format_persona_from_json(persona_json)]
            except json.JSONDecodeError:
                pass  # Fall through to custom persona handling
    
    if persona_name == CUSTOM_PERSONA_LABEL:
        custom_label = persona_override.strip() or "Custom Persona"
        context = get_persona_context("", custom_label)
        return custom_label, [context]

    persona_id = persona_options.get(persona_name, "busy_parent")
    context = get_persona_context(persona_id)
    return persona_name or "Persona", [context]


def toggle_custom_persona(selected_value: str):
    """Show the custom persona textbox only when 'Other' is selected."""
    show_custom = selected_value == CUSTOM_PERSONA_LABEL
    return gr.update(visible=show_custom, value="" if not show_custom else None)

def generate_with_claude(system_prompt: str, user_prompt: str) -> str:
    """Call Claude API and return structured response."""
    if not client or not api_key:
        return json.dumps({
            "error": "ANTHROPIC_API_KEY not configured",
            "message": "Please add your ANTHROPIC_API_KEY to the .env file"
        }, indent=2)
    
    try:
        message = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        return json.dumps({
            "error": str(type(e).__name__),
            "message": str(e)
        }, indent=2)

def generate_user_story(product: str, persona_name: str, persona_override: str):
    """Generate a user story for the given product and persona(s)."""
    _, persona_contexts = build_persona_profile(persona_name, persona_override)
    
    system_prompt = """You are an expert UX writer and product strategist. 
Generate a structured user story in JSON format with the following fields:
- story: A concise user story
- acceptance_criteria: Array of 3-5 acceptance criteria
- risks: Array of 2-3 potential risks or challenges

Return ONLY valid JSON, no additional text."""

    results = []
    for idx, persona_context in enumerate(persona_contexts):
        user_prompt = f"""{persona_context}

Generate a user story for this persona using the product: {product}

Format as JSON with the keys: story, acceptance_criteria (array), risks (array)"""

        response = generate_with_claude(system_prompt, user_prompt)
        try:
            data = json.loads(response)
            if len(persona_contexts) > 1:
                data['persona_index'] = idx + 1
            results.append(data)
        except:
            results.append({"error": "Failed to parse response", "raw": response})
    
    return json.dumps(results if len(results) > 1 else results[0], indent=2)

def generate_experience_tale(problem: str, persona_name: str, persona_override: str):
    """Generate a customer experience tale."""
    _, persona_contexts = build_persona_profile(persona_name, persona_override)
    
    system_prompt = """You are an expert in customer experience and user research.
Generate a narrative about a persona experiencing a problem in JSON format with:
- title: A compelling title
- narrative: A detailed story (2-3 paragraphs)
- pain_points: Array of 3-4 pain points
- opportunities: Array of 2-3 improvement opportunities

Return ONLY valid JSON, no additional text."""

    results = []
    for idx, persona_context in enumerate(persona_contexts):
        user_prompt = f"""{persona_context}

Describe how this persona experiences this problem: {problem}

Format as JSON with keys: title, narrative, pain_points (array), opportunities (array)"""

        response = generate_with_claude(system_prompt, user_prompt)
        try:
            data = json.loads(response)
            if len(persona_contexts) > 1:
                data['persona_index'] = idx + 1
            results.append(data)
        except:
            results.append({"error": "Failed to parse response", "raw": response})
    
    return json.dumps(results if len(results) > 1 else results[0], indent=2)

def generate_feature_impact(feature: str, persona_name: str, persona_override: str):
    """Generate a before/after feature impact story."""
    _, persona_contexts = build_persona_profile(persona_name, persona_override)
    
    system_prompt = """You are an expert at showing product impact through user narratives.
Generate a before/after story in JSON format with:
- before_story: How the persona struggled before
- after_story: How the feature improved their experience
- key_benefits: Array of 3-4 key benefits
- success_metrics: Array of 2-3 measurable success metrics

Return ONLY valid JSON, no additional text."""

    results = []
    for idx, persona_context in enumerate(persona_contexts):
        user_prompt = f"""{persona_context}

Show the before/after impact of this feature on the persona's experience: {feature}

Format as JSON with keys: before_story, after_story, key_benefits (array), success_metrics (array)"""

        response = generate_with_claude(system_prompt, user_prompt)
        try:
            data = json.loads(response)
            if len(persona_contexts) > 1:
                data['persona_index'] = idx + 1
            results.append(data)
        except:
            results.append({"error": "Failed to parse response", "raw": response})
    
    return json.dumps(results if len(results) > 1 else results[0], indent=2)

def generate_journey_story(stage: str, product: str, persona_name: str, persona_override: str):
    """Generate a journey map narrative."""
    _, persona_contexts = build_persona_profile(persona_name, persona_override)
    
    system_prompt = """You are an expert in customer journey mapping and experience design.
Generate a journey stage narrative in JSON format with:
- stage: The journey stage name
- narrative: Detailed description of what the persona experiences
- touchpoints: Array of 3-4 key touchpoints
- emotions: Array of 2-3 emotions the persona experiences
- breakdowns: Array of 1-2 potential friction points
- opportunities: Array of 2-3 improvement opportunities

Return ONLY valid JSON, no additional text."""

    results = []
    for idx, persona_context in enumerate(persona_contexts):
        user_prompt = f"""{persona_context}

Describe this persona's experience at the '{stage}' stage of their journey with {product}.

Format as JSON with keys: stage, narrative, touchpoints (array), emotions (array), breakdowns (array), opportunities (array)"""

        response = generate_with_claude(system_prompt, user_prompt)
        try:
            data = json.loads(response)
            if len(persona_contexts) > 1:
                data['persona_index'] = idx + 1
            results.append(data)
        except:
            results.append({"error": "Failed to parse response", "raw": response})
    
    return json.dumps(results if len(results) > 1 else results[0], indent=2)

# Persona browser functions
def search_personas_func(role: str, industry: str, age_range: str, tech_literacy: str, location: str):
    """Search personas based on filters."""
    filtered = personas
    
    # Apply filters
    if role and role.strip():
        filtered = [p for p in filtered if role.lower() in p.get("job", {}).get("title", "").lower()]
    
    if industry and industry.strip():
        filtered = [p for p in filtered if industry.lower() in p.get("job", {}).get("industry", "").lower()]
    
    if age_range and age_range.strip():
        try:
            min_age, max_age = map(int, age_range.split("-"))
            filtered = [p for p in filtered if min_age <= p.get("age", 0) <= max_age]
        except:
            pass
    
    if tech_literacy and tech_literacy.strip():
        filtered = [p for p in filtered if tech_literacy.lower() in p.get("technology", {}).get("tech_literacy", "").lower()]
    
    if location and location.strip():
        filtered = [p for p in filtered 
                   if location.lower() in p.get("location", {}).get("city", "").lower() or
                      location.lower() in p.get("location", {}).get("state", "").lower() or
                      location.lower() in p.get("location", {}).get("country", "").lower()]
    
    # Format results as a table
    if not filtered:
        return "No personas found matching the criteria.", ""
    
    result_lines = [f"**Found {len(filtered)} persona(s):**\n"]
    
    for p in filtered[:20]:  # Limit to 20 results
        name = p.get("name", "Unknown")
        age = p.get("age", "?")
        title = p.get("job", {}).get("title", "Unknown")
        industry_val = p.get("job", {}).get("industry", "Unknown")
        city = p.get("location", {}).get("city", "Unknown")
        tech_lit = p.get("technology", {}).get("tech_literacy", "Unknown")
        
        result_lines.append(f"• **{name}** ({age}) - {title} @ {industry_val} | {city} | Tech: {tech_lit}")
    
    return "\n".join(result_lines), json.dumps(filtered[0] if filtered else {}, indent=2)

def list_all_personas():
    """List all personas with summary info."""
    result_lines = [f"**Total Personas: {len(personas)}**\n"]
    
    # Group by industry
    by_industry = {}
    for p in personas:
        industry = p.get("job", {}).get("industry", "Other")
        if industry not in by_industry:
            by_industry[industry] = []
        by_industry[industry].append(p)
    
    result_lines.append("**By Industry:**")
    for industry, persona_list in sorted(by_industry.items()):
        result_lines.append(f"• {industry}: {len(persona_list)} personas")
    
    result_lines.append("\n**All Personas:**")
    for p in personas[:20]:  # Show first 20
        name = p.get("name", "Unknown")
        age = p.get("age", "?")
        title = p.get("job", {}).get("title", "Unknown")
        city = p.get("location", {}).get("city", "Unknown")
        result_lines.append(f"• **{name}** ({age}) - {title} | {city}")
    
    if len(personas) > 20:
        result_lines.append(f"\n_... and {len(personas) - 20} more personas_")
    
    return "\n".join(result_lines)

def show_persona_details(persona_index: int):
    """Show detailed information about a specific persona."""
    if 0 <= persona_index < len(personas):
        p = personas[persona_index]
        return json.dumps(p, indent=2)
    return "Persona not found"

def generate_personas_func(description: str, count: int):
    """Generate random personas based on description using Claude AI."""
    if not description or not description.strip():
        return json.dumps({"error": "Please provide a description"}, indent=2)
    
    if count < 1 or count > 5:
        return json.dumps({"error": "Count must be between 1 and 5"}, indent=2)
    
    if not client:
        return json.dumps({"error": "Anthropic API key not configured"}, indent=2)
    
    system_prompt = """You are a persona generation expert. Generate realistic, diverse user personas based on the provided description.

CRITICAL REQUIREMENTS:
1. Return ONLY valid JSON - no markdown, no code blocks, no explanations
2. Return a JSON array of persona objects
3. Each persona must follow the exact structure provided in the example
4. Ensure diversity in all randomized fields (location, income, education, tech literacy, devices, etc.)
5. All personas must match the core description provided by the user
6. Generate exactly the number of personas requested

PERSONA STRUCTURE (follow this exactly):
{
  "id": "UUID (e.g., 'a1b2c3d4-e5f6-7890-abcd-ef1234567890')",
  "name": "Full Name",
  "age": number,
  "gender": "Male/Female/Nonbinary",
  "location": {
    "address": "street address",
    "city": "city",
    "state": "state/province",
    "country": "country"
  },
  "demographics": {
    "income": "$XX,000/year",
    "education_level": "education level",
    "marital_status": "status",
    "household_size": number
  },
  "job": {
    "title": "job title",
    "industry": "industry",
    "experience_years": number,
    "employment_type": "Full-time/Part-time/Freelance/etc"
  },
  "background": "brief background description",
  "interests": ["interest1", "interest2", "interest3"],
  "purchasing_habits": {
    "online_shopping_frequency": "frequency",
    "preferred_platforms": ["platform1", "platform2"],
    "average_spend_per_month": "$XXX",
    "brand_loyalty_level": "Low/Medium/High/Very High"
  },
  "technology": {
    "tech_literacy": "Low/Medium/High/Very High",
    "devices_used": ["device1", "device2"],
    "favorite_apps": ["app1", "app2", "app3"]
  },
  "goals": {
    "primary_goals": ["goal1", "goal2"],
    "secondary_goals": ["goal1", "goal2"]
  },
  "pain_points": ["pain1", "pain2"],
  "motivations": ["motivation1", "motivation2"],
  "personality": {
    "traits": ["trait1", "trait2"],
    "communication_style": "style description"
  },
  "user_story": "As a [role], I want [goal] so [benefit].",
  "acceptance_criteria": ["criteria1", "criteria2"]
}"""
    
    user_prompt = f"""Generate {count} diverse user persona{'s' if count > 1 else ''} that match this description:

"{description}"

Requirements:
- Generate exactly {count} persona{'s' if count > 1 else ''}
- Each persona MUST match the core description: "{description}"
- Randomize other attributes for diversity (locations worldwide, various incomes, different tech literacy levels, diverse jobs/industries, etc.)
- Ensure realistic consistency within each persona
- Use diverse names from various cultures
- Return ONLY the JSON array, no other text

Return format: [persona1, persona2, ...]"""
    
    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}]
        )
        
        response_text = response.content[0].text if response.content else ""
        
        # Clean up response (remove markdown code blocks if present)
        cleaned_response = response_text.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response.replace("```json", "").replace("```", "").strip()
        elif cleaned_response.startswith("```"):
            cleaned_response = cleaned_response.replace("```", "").strip()
        
        # Validate JSON
        personas_data = json.loads(cleaned_response)
        if not isinstance(personas_data, list):
            return json.dumps({"error": "Response is not an array"}, indent=2)
        
        return json.dumps(personas_data, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Failed to generate personas: {str(e)}"}, indent=2)

# Build the Gradio interface
with gr.Blocks(title="HealixPath - AI Persona Storytelling", css=CUSTOM_CSS) as demo:
    gr.HTML(
        """
    <div class="header-shell">
        <span class="eyebrow">Persona storytelling workspace</span>
        <h1>HealixPath</h1>
        <p>AI-powered generator for persona-driven stories, journeys, and impact narratives.</p>
    </div>
    """
    )

    gr.HTML(
        """
    <div class="card-container" style="margin-bottom: 26px;">
        <p style="margin: 0; color: var(--text-dim); font-size: 15px; line-height: 1.6;">
            Keep the green glow while giving every output room to breathe. Choose a persona or add your own, 
            then craft structured narratives that stay readable and high-contrast.
        </p>
    </div>
    """
    )

    with gr.Tabs():
        # Tab 0: Persona Browser (NEW!)
        with gr.Tab("🔍 Persona Browser"):
            gr.Markdown("""
            ### Discover & Search Personas
            **New Feature:** Browse all 30 personas and filter by multiple criteria
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("#### Filters")
                    role_filter = gr.Textbox(label="Role/Job Title", placeholder="e.g., manager, developer, director")
                    industry_filter = gr.Textbox(label="Industry", placeholder="e.g., healthcare, tech, e-commerce")
                    age_filter = gr.Textbox(label="Age Range", placeholder="e.g., 25-35, 40-50")
                    tech_filter = gr.Textbox(label="Tech Literacy", placeholder="e.g., high, moderate, low")
                    location_filter = gr.Textbox(label="Location", placeholder="e.g., San Diego, Toronto, USA")
                    
                    search_btn = gr.Button("🔍 Search Personas", variant="primary")
                    list_all_btn = gr.Button("📋 List All Personas")
                    
                with gr.Column(scale=2):
                    gr.Markdown("#### Search Results")
                    search_results = gr.Markdown(value="Click 'List All Personas' to see all available personas.")
                    
                    gr.Markdown("#### Persona Details (JSON)")
                    persona_details = gr.Textbox(label="Full Persona Data", lines=20, interactive=False)
            
            search_btn.click(
                search_personas_func,
                inputs=[role_filter, industry_filter, age_filter, tech_filter, location_filter],
                outputs=[search_results, persona_details]
            )
            
            list_all_btn.click(
                list_all_personas,
                outputs=search_results
            )
        
        # Tab 1: Generate Personas (NEW!)
        with gr.Tab("✨ Generate Personas"):
            gr.Markdown("""
            ### AI-Powered Persona Generator
            **New Feature:** Generate random, realistic personas based on any description
            
            Examples:
            - "people who love to cook but never have time to in their 20-30s"
            - "sandwich enthusiasts who are 50+ years old"
            - "tech-savvy students interested in sustainable fashion"
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    persona_description = gr.Textbox(
                        label="Persona Description",
                        placeholder="e.g., people who love to cook but never have time to in their 20-30s",
                        lines=3
                    )
                with gr.Column(scale=1):
                    persona_count = gr.Slider(
                        label="Number of Personas",
                        minimum=1,
                        maximum=5,
                        value=3,
                        step=1
                    )
            
            generate_personas_btn = gr.Button("✨ Generate Personas", variant="primary", size="lg")
            
            gr.Markdown("#### Generated Personas (JSON)")
            generated_personas_output = gr.Textbox(
                label="Personas",
                lines=25,
                interactive=False,
                placeholder="Generated personas will appear here..."
            )
            
            generate_personas_btn.click(
                generate_personas_func,
                inputs=[persona_description, persona_count],
                outputs=generated_personas_output
            )
        
        # Tab 2: User Story
        with gr.Tab("User Story"):
            gr.Markdown("### Generate Structured User Stories")
            with gr.Row():
                product = gr.Textbox(
                    label="Product / Feature",
                    placeholder="e.g., Healthcare appointment app with AI scheduling",
                    lines=2,
                )
            with gr.Row():
                persona_name = gr.Dropdown(
                    label="Select Persona",
                    choices=persona_choices,
                    value=default_persona_choice,
                )
                persona_custom = gr.Textbox(
                    label="Or Custom Persona / Generated Persona JSON",
                    placeholder="Paste generated persona JSON here or describe your custom persona",
                    lines=3,
                    visible=False,
                )
                persona_name.change(
                    toggle_custom_persona, inputs=persona_name, outputs=persona_custom
                )

            user_story_btn = gr.Button("Generate User Story", scale=2)
            user_story_output = gr.Textbox(
                label="Generated Story",
                lines=18,
                interactive=False,
                show_copy_button=True,
            )

            user_story_btn.click(
                generate_user_story,
                inputs=[product, persona_name, persona_custom],
                outputs=user_story_output,
            )

        # Tab 2: Experience Tale
        with gr.Tab("Experience Tale"):
            gr.HTML(
                '<div class="card-container"><p style="margin: 0; font-size: 15px; color: var(--text-dim);">Generate customer experience narratives highlighting pain points and opportunities.</p></div>'
            )
            with gr.Row():
                problem = gr.Textbox(
                    label="Problem",
                    placeholder="e.g., Mobile app crashes during checkout process",
                    lines=2,
                )
            with gr.Row():
                persona_name_2 = gr.Dropdown(
                    label="Select Persona",
                    choices=persona_choices,
                    value=default_persona_choice,
                )
                persona_custom_2 = gr.Textbox(
                    label="Or Custom Persona / Generated Persona JSON",
                    placeholder="Paste generated persona JSON here or describe your custom persona",
                    lines=3,
                    visible=False,
                )
                persona_name_2.change(
                    toggle_custom_persona,
                    inputs=persona_name_2,
                    outputs=persona_custom_2,
                )

            tale_btn = gr.Button("Generate Experience Tale", scale=2)
            tale_output = gr.Textbox(
                label="Generated Tale",
                lines=18,
                interactive=False,
                show_copy_button=True,
            )

            tale_btn.click(
                generate_experience_tale,
                inputs=[problem, persona_name_2, persona_custom_2],
                outputs=tale_output,
            )

        # Tab 3: Feature Impact
        with gr.Tab("Feature Impact"):
            gr.HTML(
                '<div class="card-container"><p style="margin: 0; font-size: 15px; color: var(--text-dim);">Show before/after impact stories demonstrating feature value.</p></div>'
            )
            with gr.Row():
                feature = gr.Textbox(
                    label="Feature",
                    placeholder="e.g., One-click scheduling with automatic reminders",
                    lines=2,
                )
            with gr.Row():
                persona_name_3 = gr.Dropdown(
                    label="Select Persona",
                    choices=persona_choices,
                    value=default_persona_choice,
                )
                persona_custom_3 = gr.Textbox(
                    label="Or Custom Persona / Generated Persona JSON",
                    placeholder="Paste generated persona JSON here or describe your custom persona",
                    lines=3,
                    visible=False,
                )
                persona_name_3.change(
                    toggle_custom_persona,
                    inputs=persona_name_3,
                    outputs=persona_custom_3,
                )

            impact_btn = gr.Button("Generate Feature Impact", scale=2)
            impact_output = gr.Textbox(
                label="Generated Impact Story",
                lines=18,
                interactive=False,
                show_copy_button=True,
            )

            impact_btn.click(
                generate_feature_impact,
                inputs=[feature, persona_name_3, persona_custom_3],
                outputs=impact_output,
            )

        # Tab 4: Journey Map
        with gr.Tab("Journey Map"):
            gr.HTML(
                '<div class="card-container"><p style="margin: 0; font-size: 15px; color: var(--text-dim);">Generate journey stage narratives with touchpoints and emotions.</p></div>'
            )
            with gr.Row():
                stage = gr.Textbox(
                    label="Journey Stage",
                    placeholder="e.g., awareness, consideration, adoption, retention",
                    lines=1,
                )
                product_journey = gr.Textbox(
                    label="Product",
                    placeholder="e.g., Healthcare platform",
                    lines=1,
                )
            with gr.Row():
                persona_name_4 = gr.Dropdown(
                    label="Select Persona",
                    choices=persona_choices,
                    value=default_persona_choice,
                )
                persona_custom_4 = gr.Textbox(
                    label="Or Custom Persona / Generated Persona JSON",
                    placeholder="Paste generated persona JSON here or describe your custom persona",
                    lines=3,
                    visible=False,
                )
                persona_name_4.change(
                    toggle_custom_persona,
                    inputs=persona_name_4,
                    outputs=persona_custom_4,
                )

            journey_btn = gr.Button("Generate Journey Map", scale=2)
            journey_output = gr.Textbox(
                label="Generated Journey Map",
                lines=18,
                interactive=False,
                show_copy_button=True,
            )

            journey_btn.click(
                generate_journey_story,
                inputs=[stage, product_journey, persona_name_4, persona_custom_4],
                outputs=journey_output,
            )

    gr.HTML(
        """
    <div style="text-align: center; margin-top: 32px; padding: 16px; border-top: 1px solid var(--line); color: var(--text-dim);">
        <p style="font-size: 13px; margin: 0;">
            HealixPath - AI-powered persona storytelling engine<br>
            <span style="color: var(--muted);">Powered by Claude &amp; Gradio</span>
        </p>
    </div>
    """
    )
if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7872, share=False)
