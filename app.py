"""
HealixPath Gradio Web Interface

A web interface for generating AI-powered persona-driven narratives.
"""

import gradio as gr
import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import InferenceClient


HEALIX_THEME = gr.themes.Base(
    primary_hue="lime",
    secondary_hue="green",
    neutral_hue="zinc",
    font=[gr.themes.GoogleFont("Outfit"), "ui-sans-serif", "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("IBM Plex Mono"), "ui-monospace", "monospace"],
).set(
    body_background_fill="#050805",
    body_background_fill_dark="#050805",
    body_text_color="#f3ffe6",
    body_text_color_dark="#f3ffe6",
    background_fill_primary="#101e14",
    background_fill_primary_dark="#101e14",
    background_fill_secondary="#0a140c",
    background_fill_secondary_dark="#0a140c",
    border_color_accent="#b8ff3c",
    border_color_accent_dark="#b8ff3c",
    border_color_primary="rgba(184, 255, 60, 0.28)",
    border_color_primary_dark="rgba(184, 255, 60, 0.28)",
    button_primary_background_fill="#b8ff3c",
    button_primary_background_fill_hover="#d4ff6b",
    button_primary_background_fill_dark="#b8ff3c",
    button_primary_background_fill_hover_dark="#d4ff6b",
    button_primary_text_color="#06210f",
    button_primary_text_color_hover="#06210f",
    button_primary_text_color_dark="#06210f",
    button_primary_text_color_hover_dark="#06210f",
    button_primary_shadow="0 8px 24px rgba(184, 255, 60, 0.4)",
    link_text_color="#b8ff3c",
    link_text_color_dark="#b8ff3c",
    block_radius="16px",
    button_large_radius="12px",
)

# HealixPath identity (lime helix). Logic below this CSS is unchanged.
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Syne:wght@700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --hp-void: #050805;
    --hp-panel: #101e14;
    --hp-lime: #b8ff3c;
    --hp-lime-2: #d4ff6b;
    --hp-mint: #9ef6c8;
    --hp-foam: #f3ffe6;
    --hp-text: #f3ffe6;
    --hp-muted: #b4d7bc;
    --hp-dim: #8aaf93;
    --hp-line: rgba(184, 255, 60, 0.28);
    --hp-glow: rgba(184, 255, 60, 0.5);
    --hp-ink: #06210f;
    --hp-display: "Syne", "Avenir Next", "Segoe UI", sans-serif;
    --hp-body: "Outfit", "Segoe UI", system-ui, sans-serif;
}

@media (prefers-color-scheme: light) {
    :root {
        --hp-void: #f4ffea;
        --hp-panel: #ffffff;
        --hp-lime: #1f7a00;
        --hp-lime-2: #278200;
        --hp-mint: #0c6b3a;
        --hp-foam: #0b1a10;
        --hp-text: #0b1a10;
        --hp-muted: #245c38;
        --hp-dim: #3c6a4c;
        --hp-line: rgba(31, 107, 16, 0.3);
        --hp-glow: rgba(39, 130, 0, 0.22);
        --hp-ink: #f4ffea;
    }
}

html, body, .gradio-container, .gradio-container .main, .app, .contain {
    font-family: var(--hp-body) !important;
    background: var(--hp-void) !important;
    color: var(--hp-text) !important;
}

body, html {
    background:
        radial-gradient(900px 500px at 85% -10%, rgba(184, 255, 60, 0.08), transparent 55%),
        radial-gradient(600px 400px at 0% 10%, rgba(158, 246, 200, 0.06), transparent 50%),
        var(--hp-void) !important;
}

.gradio-container {
    max-width: 1180px !important;
    margin: 0 auto !important;
    padding: 20px 18px 32px !important;
    background: transparent !important;
}

.gradio-container a { color: var(--hp-lime) !important; }

/* ---- Hero ---- */
.hp-hero {
    display: grid;
    grid-template-columns: 120px 1fr;
    gap: 1.25rem;
    align-items: center;
    background:
        radial-gradient(520px 180px at 12% 50%, var(--hp-glow), transparent 60%),
        linear-gradient(135deg, color-mix(in srgb, var(--hp-panel) 92%, black), var(--hp-panel));
    border: 1px solid var(--hp-line);
    border-radius: 24px;
    padding: 20px 24px;
    box-shadow: 0 0 0 1px rgba(184, 255, 60, 0.08), 0 24px 60px rgba(0, 0, 0, 0.35), 0 0 80px rgba(184, 255, 60, 0.08);
    overflow: hidden;
    position: relative;
}
.hp-helix-wrap {
    width: 120px;
    height: 150px;
    position: relative;
}
.hp-helix-svg { width: 100%; height: 100%; filter: drop-shadow(0 0 12px var(--hp-glow)); }
.hp-helix-svg .strand {
    stroke-dasharray: 28 8;
    animation: strand-flow 7s linear infinite;
}
.hp-helix-svg .strand.b { animation-duration: 9s; animation-direction: reverse; }
@keyframes strand-flow {
    to { stroke-dashoffset: -180; }
}
.hp-copy h1 {
    font-family: var(--hp-display) !important;
    font-weight: 800 !important;
    letter-spacing: -0.06em;
    font-size: clamp(2.4rem, 5vw, 4.2rem) !important;
    line-height: 0.92 !important;
    margin: 0.15rem 0 0.4rem !important;
    color: var(--hp-text) !important;
}
.hp-copy h1 span {
    color: var(--hp-lime);
    text-shadow: 0 0 28px var(--hp-glow);
}
.hp-kicker {
    margin: 0;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--hp-mint);
}
.hp-tag {
    font-family: var(--hp-display);
    font-weight: 700;
    font-size: clamp(1.05rem, 2vw, 1.4rem);
    letter-spacing: -0.03em;
    color: var(--hp-mint);
    margin: 0 0 0.45rem;
}
.hp-lede {
    margin: 0;
    color: var(--hp-muted);
    font-size: 0.98rem;
    line-height: 1.55;
    max-width: 46rem;
}

.card-container {
    background: var(--hp-panel);
    border: 1px solid var(--hp-line);
    border-radius: 16px;
    padding: 16px 18px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.22);
}

/* ---- Tabs ---- */
.tabs, .tab-nav { border: 0; background: transparent; }
.gradio-container .tabs > div:first-child,
.gradio-container .tab-nav,
.gradio-container nav[role="tablist"] {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 6px !important;
    padding: 6px !important;
    background: color-mix(in srgb, var(--hp-panel) 90%, black) !important;
    border: 1px solid var(--hp-line) !important;
    border-radius: 16px !important;
}
.gradio-container .tabs button,
.gradio-container nav[role="tablist"] button,
.gradio-container .tab-nav button {
    font-family: var(--hp-body) !important;
    font-weight: 600 !important;
    color: var(--hp-text) !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease, border-color 0.18s ease !important;
}
.gradio-container .tabs button:hover,
.gradio-container nav[role="tablist"] button:hover {
    border-color: var(--hp-line) !important;
    background: color-mix(in srgb, var(--hp-lime) 12%, var(--hp-panel)) !important;
    transform: translateY(-1px);
}
.gradio-container .tabs button[aria-selected="true"],
.gradio-container nav[role="tablist"] button[aria-selected="true"],
.gradio-container .tab-nav button.selected {
    background: var(--hp-lime) !important;
    color: var(--hp-ink) !important;
    border-color: transparent !important;
    box-shadow: 0 0 24px var(--hp-glow) !important;
}

/* ---- Inputs ---- */
label, .gradio-container label {
    color: var(--hp-text) !important;
    font-weight: 600 !important;
    font-family: var(--hp-body) !important;
}
.gradio-container input,
.gradio-container textarea,
.gradio-container select {
    background: color-mix(in srgb, var(--hp-void) 80%, var(--hp-panel)) !important;
    color: var(--hp-text) !important;
    border: 1px solid var(--hp-line) !important;
    border-radius: 12px !important;
}
.gradio-container input:focus,
.gradio-container textarea:focus,
.gradio-container select:focus {
    outline: none !important;
    border-color: var(--hp-lime) !important;
    box-shadow: 0 0 0 3px var(--hp-glow) !important;
}

/* ---- Buttons ---- */
.gradio-container button,
.gradio-container .gr-button {
    font-family: var(--hp-body) !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease !important;
}
.gradio-container button.primary,
.gradio-container .lg.primary,
.gradio-container .primary,
.gradio-container button[variant="primary"] {
    background: var(--hp-lime) !important;
    color: var(--hp-ink) !important;
    border: 0 !important;
    box-shadow: 0 8px 24px var(--hp-glow) !important;
}
.gradio-container button:hover,
.gradio-container .gr-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 28px var(--hp-glow) !important;
}
.gradio-container button:active { transform: translateY(0); }
.gradio-container button:focus-visible {
    outline: 2px solid var(--hp-lime) !important;
    outline-offset: 3px !important;
}

/* Login should stay obvious even if Gradio marks it secondary */
.gradio-container button:not(.primary) {
    background: color-mix(in srgb, var(--hp-panel) 80%, black) !important;
    color: var(--hp-text) !important;
    border: 1px solid var(--hp-line) !important;
}

/* Make the first action row (sign-in) pop */
.gradio-container .form,
.gradio-container .block,
.gradio-container .panel,
.gradio-container .gr-group,
.gradio-container .gr-box {
    background: var(--hp-panel) !important;
    border-color: var(--hp-line) !important;
    border-radius: 16px !important;
}

[data-testid="textbox"] textarea {
    font-family: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace !important;
    line-height: 1.55 !important;
}

.gradio-container .markdown-text, .gradio-container .prose, .gradio-container p {
    color: var(--hp-muted);
}
.gradio-container h2, .gradio-container h3 {
    font-family: var(--hp-display) !important;
    color: var(--hp-text) !important;
    letter-spacing: -0.03em;
}

.hp-foot {
    text-align: center;
    margin-top: 28px;
    padding: 18px 8px 4px;
    border-top: 1px solid var(--hp-line);
    color: var(--hp-dim);
    font-size: 0.88rem;
}
.hp-foot p { margin: 0.2rem 0; }
.hp-foot a { color: var(--hp-lime) !important; }

footer, .footer, [data-testid="footer"] {
    background: transparent !important;
    color: var(--hp-dim) !important;
}

@media (max-width: 800px) {
    .hp-hero { grid-template-columns: 1fr; padding: 16px; }
    .hp-helix-wrap { width: 96px; height: 120px; }
}

@media (prefers-reduced-motion: reduce) {
    .hp-helix-svg .strand { animation: none !important; }
    .gradio-container button,
    .gradio-container .tabs button {
        transition: none !important;
    }
    .gradio-container button:hover { transform: none !important; }
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

# Free AI backend: Hugging Face Inference Providers.
# Every generation runs on the *visitor's* Hugging Face account (Sign in with Hugging Face),
# so it uses the visitor's own free monthly allowance. The Space never uses its own token,
# a Space secret, or a paid API key for inference.
MODEL = os.getenv("HEALIXPATH_MODEL", "openai/gpt-oss-20b")

SIGN_IN_MESSAGE = (
    "Please sign in with Hugging Face (button at the top of the page) to generate. "
    "Generations use your own free Hugging Face Inference Providers allowance."
)


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

def resolve_token(oauth_token=None, request=None):
    """Return the visitor's own Hugging Face token, or None.

    Order: the OAuth token from "Sign in with Hugging Face", then a Bearer token the
    caller sent in the Authorization header (for MCP clients that pass their own token).
    Never falls back to a Space-level token or secret.
    """
    token = getattr(oauth_token, "token", None)
    if token:
        return token
    try:
        auth = request.headers.get("authorization", "") if request is not None else ""
    except Exception:
        auth = ""
    if auth.lower().startswith("bearer ") and auth[7:].strip():
        return auth[7:].strip()
    return None


def _strip_code_fence(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()
    return text


def generate_text(system_prompt: str, user_prompt: str, token, max_tokens: int = 1500) -> str:
    """Call an open model through HF Inference Providers with the visitor's token."""
    if not token:
        return json.dumps({"error": "Sign in required", "message": SIGN_IN_MESSAGE}, indent=2)
    try:
        client = InferenceClient(api_key=token)
        result = client.chat_completion(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return _strip_code_fence(result.choices[0].message.content or "")
    except Exception as e:
        return json.dumps({
            "error": type(e).__name__,
            "message": f"Hugging Face Inference Providers call failed: {e}",
        }, indent=2)

def generate_user_story(product: str, persona_name: str, persona_override: str,
        oauth_token: gr.OAuthToken | None = None, request: gr.Request = None):
    """Generate a user story for the given product and persona(s)."""
    token = resolve_token(oauth_token, request)
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

        response = generate_text(system_prompt, user_prompt, token)
        try:
            data = json.loads(response)
            if len(persona_contexts) > 1:
                data['persona_index'] = idx + 1
            results.append(data)
        except:
            results.append({"error": "Failed to parse response", "raw": response})
    
    return json.dumps(results if len(results) > 1 else results[0], indent=2)

def generate_experience_tale(problem: str, persona_name: str, persona_override: str,
        oauth_token: gr.OAuthToken | None = None, request: gr.Request = None):
    """Generate a customer experience tale."""
    token = resolve_token(oauth_token, request)
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

        response = generate_text(system_prompt, user_prompt, token)
        try:
            data = json.loads(response)
            if len(persona_contexts) > 1:
                data['persona_index'] = idx + 1
            results.append(data)
        except:
            results.append({"error": "Failed to parse response", "raw": response})
    
    return json.dumps(results if len(results) > 1 else results[0], indent=2)

def generate_feature_impact(feature: str, persona_name: str, persona_override: str,
        oauth_token: gr.OAuthToken | None = None, request: gr.Request = None):
    """Generate a before/after feature impact story."""
    token = resolve_token(oauth_token, request)
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

        response = generate_text(system_prompt, user_prompt, token)
        try:
            data = json.loads(response)
            if len(persona_contexts) > 1:
                data['persona_index'] = idx + 1
            results.append(data)
        except:
            results.append({"error": "Failed to parse response", "raw": response})
    
    return json.dumps(results if len(results) > 1 else results[0], indent=2)

def generate_journey_story(stage: str, product: str, persona_name: str, persona_override: str,
        oauth_token: gr.OAuthToken | None = None, request: gr.Request = None):
    """Generate a journey map narrative."""
    token = resolve_token(oauth_token, request)
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

        response = generate_text(system_prompt, user_prompt, token)
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

def generate_personas_func(description: str, count: int,
        oauth_token: gr.OAuthToken | None = None, request: gr.Request = None):
    """Generate random personas based on description using an open model via Hugging Face."""
    token = resolve_token(oauth_token, request)
    if not description or not description.strip():
        return json.dumps({"error": "Please provide a description"}, indent=2)
    
    if count < 1 or count > 5:
        return json.dumps({"error": "Count must be between 1 and 5"}, indent=2)
    
    if not token:
        return json.dumps({"error": "Sign in required", "message": SIGN_IN_MESSAGE}, indent=2)
    
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
        response_text = generate_text(system_prompt, user_prompt, token, max_tokens=4096)
        if response_text.lstrip().startswith("{") and '"error"' in response_text[:40]:
            return response_text

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
with gr.Blocks(title="HealixPath — stories that spiral from a persona", theme=HEALIX_THEME, css=CUSTOM_CSS) as demo:
    gr.HTML(
        """
    <div class="hp-hero">
        <div class="hp-helix-wrap" aria-hidden="true"><svg class="hp-helix-svg" viewBox="0 0 160 200" fill="none" aria-hidden="true" focusable="false">
  <path class="strand a" d="M 87.2,8.0 L 89.7,9.5 L 92.3,11.1 L 94.7,12.6 L 97.1,14.2 L 99.4,15.7 L 101.6,17.3 L 103.7,18.8 L 105.6,20.4 L 107.4,21.9 L 109.1,23.5 L 110.5,25.0 L 111.9,26.6 L 113.0,28.1 L 114.0,29.6 L 114.8,31.2 L 115.4,32.7 L 115.8,34.3 L 116.0,35.8 L 116.0,37.4 L 115.8,38.9 L 115.4,40.5 L 114.8,42.0 L 114.1,43.6 L 113.1,45.1 L 112.0,46.7 L 110.7,48.2 L 109.2,49.7 L 107.6,51.3 L 105.8,52.8 L 103.8,54.4 L 101.8,55.9 L 99.6,57.5 L 97.3,59.0 L 95.0,60.6 L 92.5,62.1 L 90.0,63.7 L 87.4,65.2 L 84.8,66.8 L 82.1,68.3 L 79.5,69.8 L 76.8,71.4 L 74.2,72.9 L 71.5,74.5 L 69.0,76.0 L 66.5,77.6 L 64.1,79.1 L 61.7,80.7 L 59.5,82.2 L 57.4,83.8 L 55.3,85.3 L 53.5,86.9 L 51.8,88.4 L 50.2,89.9 L 48.8,91.5 L 47.5,93.0 L 46.5,94.6 L 45.6,96.1 L 44.9,97.7 L 44.4,99.2 L 44.1,100.8 L 44.0,102.3 L 44.1,103.9 L 44.4,105.4 L 44.9,107.0 L 45.5,108.5 L 46.4,110.1 L 47.4,111.6 L 48.7,113.1 L 50.0,114.7 L 51.6,116.2 L 53.3,117.8 L 55.2,119.3 L 57.2,120.9 L 59.3,122.4 L 61.5,124.0 L 63.8,125.5 L 66.3,127.1 L 68.8,128.6 L 71.3,130.2 L 73.9,131.7 L 76.6,133.2 L 79.2,134.8 L 81.9,136.3 L 84.5,137.9 L 87.2,139.4 L 89.7,141.0 L 92.3,142.5 L 94.7,144.1 L 97.1,145.6 L 99.4,147.2 L 101.6,148.7 L 103.7,150.3 L 105.6,151.8 L 107.4,153.3 L 109.1,154.9 L 110.5,156.4 L 111.9,158.0 L 113.0,159.5 L 114.0,161.1 L 114.8,162.6 L 115.4,164.2 L 115.8,165.7 L 116.0,167.3 L 116.0,168.8 L 115.8,170.4 L 115.4,171.9 L 114.8,173.4 L 114.1,175.0 L 113.1,176.5 L 112.0,178.1 L 110.7,179.6 L 109.2,181.2 L 107.6,182.7 L 105.8,184.3 L 103.8,185.8 L 101.8,187.4 L 99.6,188.9 L 97.3,190.5 L 95.0,192.0" stroke="#B8FF3C" stroke-width="5.5" stroke-linecap="round"/>
  <path class="strand b" d="M 72.8,8.0 L 70.3,9.5 L 67.7,11.1 L 65.3,12.6 L 62.9,14.2 L 60.6,15.7 L 58.4,17.3 L 56.3,18.8 L 54.4,20.4 L 52.6,21.9 L 50.9,23.5 L 49.5,25.0 L 48.1,26.6 L 47.0,28.1 L 46.0,29.6 L 45.2,31.2 L 44.6,32.7 L 44.2,34.3 L 44.0,35.8 L 44.0,37.4 L 44.2,38.9 L 44.6,40.5 L 45.2,42.0 L 45.9,43.6 L 46.9,45.1 L 48.0,46.7 L 49.3,48.2 L 50.8,49.7 L 52.4,51.3 L 54.2,52.8 L 56.2,54.4 L 58.2,55.9 L 60.4,57.5 L 62.7,59.0 L 65.0,60.6 L 67.5,62.1 L 70.0,63.7 L 72.6,65.2 L 75.2,66.8 L 77.9,68.3 L 80.5,69.8 L 83.2,71.4 L 85.8,72.9 L 88.5,74.5 L 91.0,76.0 L 93.5,77.6 L 95.9,79.1 L 98.3,80.7 L 100.5,82.2 L 102.6,83.8 L 104.7,85.3 L 106.5,86.9 L 108.2,88.4 L 109.8,89.9 L 111.2,91.5 L 112.5,93.0 L 113.5,94.6 L 114.4,96.1 L 115.1,97.7 L 115.6,99.2 L 115.9,100.8 L 116.0,102.3 L 115.9,103.9 L 115.6,105.4 L 115.1,107.0 L 114.5,108.5 L 113.6,110.1 L 112.6,111.6 L 111.3,113.1 L 110.0,114.7 L 108.4,116.2 L 106.7,117.8 L 104.8,119.3 L 102.8,120.9 L 100.7,122.4 L 98.5,124.0 L 96.2,125.5 L 93.7,127.1 L 91.2,128.6 L 88.7,130.2 L 86.1,131.7 L 83.4,133.2 L 80.8,134.8 L 78.1,136.3 L 75.5,137.9 L 72.8,139.4 L 70.3,141.0 L 67.7,142.5 L 65.3,144.1 L 62.9,145.6 L 60.6,147.2 L 58.4,148.7 L 56.3,150.3 L 54.4,151.8 L 52.6,153.3 L 50.9,154.9 L 49.5,156.4 L 48.1,158.0 L 47.0,159.5 L 46.0,161.1 L 45.2,162.6 L 44.6,164.2 L 44.2,165.7 L 44.0,167.3 L 44.0,168.8 L 44.2,170.4 L 44.6,171.9 L 45.2,173.4 L 45.9,175.0 L 46.9,176.5 L 48.0,178.1 L 49.3,179.6 L 50.8,181.2 L 52.4,182.7 L 54.2,184.3 L 56.2,185.8 L 58.2,187.4 L 60.4,188.9 L 62.7,190.5 L 65.0,192.0" stroke="#9EF6C8" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="114.0" y1="29.6" x2="46.0" y2="29.6" stroke="#B8FF3C" stroke-width="3" stroke-linecap="round" opacity="1"/><circle cx="114.0" cy="29.6" r="3" fill="#B8FF3C" opacity="1"/><circle cx="46.0" cy="29.6" r="3" fill="#9EF6C8" opacity="1"/><line x1="110.7" y1="48.2" x2="49.3" y2="48.2" stroke="#B8FF3C" stroke-width="3" stroke-linecap="round" opacity="1"/><circle cx="110.7" cy="48.2" r="3" fill="#B8FF3C" opacity="1"/><circle cx="49.3" cy="48.2" r="3" fill="#9EF6C8" opacity="1"/><line x1="87.4" y1="65.2" x2="72.6" y2="65.2" stroke="#B8FF3C" stroke-width="3" stroke-linecap="round" opacity="1"/><circle cx="87.4" cy="65.2" r="3" fill="#B8FF3C" opacity="1"/><circle cx="72.6" cy="65.2" r="3" fill="#9EF6C8" opacity="1"/><line x1="59.5" y1="82.2" x2="100.5" y2="82.2" stroke="#9EF6C8" stroke-width="2" stroke-linecap="round" opacity="0.45"/><circle cx="59.5" cy="82.2" r="3" fill="#9EF6C8" opacity="0.45"/><circle cx="100.5" cy="82.2" r="3" fill="#B8FF3C" opacity="0.45"/><line x1="44.1" y1="100.8" x2="115.9" y2="100.8" stroke="#9EF6C8" stroke-width="2" stroke-linecap="round" opacity="0.45"/><circle cx="44.1" cy="100.8" r="3" fill="#9EF6C8" opacity="0.45"/><circle cx="115.9" cy="100.8" r="3" fill="#B8FF3C" opacity="0.45"/><line x1="53.3" y1="117.8" x2="106.7" y2="117.8" stroke="#9EF6C8" stroke-width="2" stroke-linecap="round" opacity="0.45"/><circle cx="53.3" cy="117.8" r="3" fill="#9EF6C8" opacity="0.45"/><circle cx="106.7" cy="117.8" r="3" fill="#B8FF3C" opacity="0.45"/><line x1="105.6" y1="151.8" x2="54.4" y2="151.8" stroke="#B8FF3C" stroke-width="3" stroke-linecap="round" opacity="1"/><circle cx="105.6" cy="151.8" r="3" fill="#B8FF3C" opacity="1"/><circle cx="54.4" cy="151.8" r="3" fill="#9EF6C8" opacity="1"/><line x1="115.8" y1="170.4" x2="44.2" y2="170.4" stroke="#B8FF3C" stroke-width="3" stroke-linecap="round" opacity="1"/><circle cx="115.8" cy="170.4" r="3" fill="#B8FF3C" opacity="1"/><circle cx="44.2" cy="170.4" r="3" fill="#9EF6C8" opacity="1"/>
</svg></div>
        <div class="hp-copy">
            <p class="hp-kicker">Team Healix · persona storytelling</p>
            <h1>Healix<span>Path</span></h1>
            <p class="hp-tag">Stories that spiral from a persona.</p>
            <p class="hp-lede">Sign in with Hugging Face to generate stories, journeys, and personas on free open models, using your own allowance. Co-authored with DevRubenArevalo.</p>
        </div>
    </div>
"""
    )

    with gr.Row():
        gr.LoginButton(value="Sign in with Hugging Face")
        signin_status = gr.Markdown(
            "**Signed out.** " + SIGN_IN_MESSAGE
        )

    def show_signin_status(profile: gr.OAuthProfile | None):
        if profile is None:
            return "**Signed out.** " + SIGN_IN_MESSAGE
        return f"**Signed in as {profile.username}.** Generations use your own free Hugging Face allowance."

    demo.load(show_signin_status, inputs=None, outputs=signin_status)

    gr.HTML(
        """
    <div class="card-container" style="margin-bottom: 26px;">
        <p style="margin: 0; color: var(--text-dim); font-size: 15px; line-height: 1.6;">
            Choose a persona or add your own, then craft structured narratives to inform product decisions and user experiences. Sign in to generate; browsing personas works while signed out.
        </p>
    </div>
    """
    )

    with gr.Tabs():
        # Tab 0: Persona Browser (NEW!)
        with gr.Tab("Persona Browser"):
            gr.Markdown("""
            ### Discover & Search Personas
            Browse all 30 personas and filter by multiple criteria
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
        with gr.Tab("Generate Personas"):
            gr.Markdown("""
            ### AI-Powered Persona Generator
            Generate random, realistic personas based on any description
            
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
    <div class="hp-foot">
        <p>HealixPath — Mackenzie O&rsquo;Brien, Mac Labs AI, and DevRubenArevalo.</p>
        <p class="hp-foot-links">
            <a href="https://mso-docs.github.io/HealixPath/">Project page</a>
            · <a href="https://huggingface.co/spaces/MCP-1st-Birthday/TeamHealix">Frozen hackathon Space</a>
            · <a href="https://huggingface.co/collections/mackenzietechdocs/healixpath">Collection</a>
            · Open models via Hugging Face Inference Providers
        </p>
    </div>
"""
    )
if __name__ == "__main__":
    demo.launch(mcp_server=True)
