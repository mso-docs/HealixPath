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
    return f"{p['name']} • {age}yo {job_title} • {location_city}"

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


def build_persona_profile(persona_name: str, persona_override: str):
    """Return the persona label for display and the context payload."""
    if persona_name == CUSTOM_PERSONA_LABEL:
        custom_label = persona_override.strip() or "Custom Persona"
        context = get_persona_context("", custom_label)
        return custom_label, context

    persona_id = persona_options.get(persona_name, "busy_parent")
    context = get_persona_context(persona_id)
    return persona_name or "Persona", context


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
    """Generate a user story for the given product and persona."""
    _, persona_context = build_persona_profile(persona_name, persona_override)
    
    system_prompt = """You are an expert UX writer and product strategist. 
Generate a structured user story in JSON format with the following fields:
- story: A concise user story
- acceptance_criteria: Array of 3-5 acceptance criteria
- risks: Array of 2-3 potential risks or challenges

Return ONLY valid JSON, no additional text."""

    user_prompt = f"""{persona_context}

Generate a user story for this persona using the product: {product}

Format as JSON with the keys: story, acceptance_criteria (array), risks (array)"""

    response = generate_with_claude(system_prompt, user_prompt)
    try:
        # Try to parse and re-format as pretty JSON
        data = json.loads(response)
        return json.dumps(data, indent=2)
    except:
        return response

def generate_experience_tale(problem: str, persona_name: str, persona_override: str):
    """Generate a customer experience tale."""
    _, persona_context = build_persona_profile(persona_name, persona_override)
    
    system_prompt = """You are an expert in customer experience and user research.
Generate a narrative about a persona experiencing a problem in JSON format with:
- title: A compelling title
- narrative: A detailed story (2-3 paragraphs)
- pain_points: Array of 3-4 pain points
- opportunities: Array of 2-3 improvement opportunities

Return ONLY valid JSON, no additional text."""

    user_prompt = f"""{persona_context}

Describe how this persona experiences this problem: {problem}

Format as JSON with keys: title, narrative, pain_points (array), opportunities (array)"""

    response = generate_with_claude(system_prompt, user_prompt)
    try:
        data = json.loads(response)
        return json.dumps(data, indent=2)
    except:
        return response

def generate_feature_impact(feature: str, persona_name: str, persona_override: str):
    """Generate a before/after feature impact story."""
    _, persona_context = build_persona_profile(persona_name, persona_override)
    
    system_prompt = """You are an expert at showing product impact through user narratives.
Generate a before/after story in JSON format with:
- before_story: How the persona struggled before
- after_story: How the feature improved their experience
- key_benefits: Array of 3-4 key benefits
- success_metrics: Array of 2-3 measurable success metrics

Return ONLY valid JSON, no additional text."""

    user_prompt = f"""{persona_context}

Show the before/after impact of this feature on the persona's experience: {feature}

Format as JSON with keys: before_story, after_story, key_benefits (array), success_metrics (array)"""

    response = generate_with_claude(system_prompt, user_prompt)
    try:
        data = json.loads(response)
        return json.dumps(data, indent=2)
    except:
        return response

def generate_journey_story(stage: str, product: str, persona_name: str, persona_override: str):
    """Generate a journey map narrative."""
    _, persona_context = build_persona_profile(persona_name, persona_override)
    
    system_prompt = """You are an expert in customer journey mapping and experience design.
Generate a journey stage narrative in JSON format with:
- stage: The journey stage name
- narrative: Detailed description of what the persona experiences
- touchpoints: Array of 3-4 key touchpoints
- emotions: Array of 2-3 emotions the persona experiences
- breakdowns: Array of 1-2 potential friction points
- opportunities: Array of 2-3 improvement opportunities

Return ONLY valid JSON, no additional text."""

    user_prompt = f"""{persona_context}

Describe this persona's experience at the '{stage}' stage of their journey with {product}.

Format as JSON with keys: stage, narrative, touchpoints (array), emotions (array), breakdowns (array), opportunities (array)"""

    response = generate_with_claude(system_prompt, user_prompt)
    try:
        data = json.loads(response)
        return json.dumps(data, indent=2)
    except:
        return response

# Build the Gradio interface
with gr.Blocks(title="HealixPath - AI Persona Storytelling") as demo:
    gr.Markdown("""
    # 🌟 HealixPath - AI-Powered Persona Storytelling Engine
    
    Transform product inputs, personas, and problems into rich, structured, realistic stories.
    
    Instead of vague bullet points, HealixPath generates actionable narratives grounded in deep persona research.
    """)
    
    with gr.Tabs():
        # Tab 1: User Story
        with gr.Tab("User Story"):
            gr.Markdown("### Generate Structured User Stories")
            with gr.Row():
                product = gr.Textbox(label="Product/Feature", placeholder="e.g., Healthcare appointment app")
            with gr.Row():
                persona_name = gr.Dropdown(
                    label="Select Persona",
                    choices=persona_choices,
                    value=default_persona_choice,
                )
                persona_custom = gr.Textbox(
                    label="Or Custom Persona",
                    placeholder="Describe your custom persona",
                    visible=False,
                )
                persona_name.change(
                    toggle_custom_persona, inputs=persona_name, outputs=persona_custom
                )
            
            user_story_btn = gr.Button("Generate User Story", scale=2)
            user_story_output = gr.Textbox(label="Generated Story", lines=15, interactive=False)
            
            user_story_btn.click(
                generate_user_story,
                inputs=[product, persona_name, persona_custom],
                outputs=user_story_output
            )
        
        # Tab 2: Experience Tale
        with gr.Tab("Experience Tale"):
            gr.Markdown("### Generate Customer Experience Narratives")
            with gr.Row():
                problem = gr.Textbox(label="Problem", placeholder="e.g., Mobile app crashes during checkout")
            with gr.Row():
                persona_name_2 = gr.Dropdown(
                    label="Select Persona",
                    choices=persona_choices,
                    value=default_persona_choice,
                )
                persona_custom_2 = gr.Textbox(
                    label="Or Custom Persona",
                    placeholder="Describe your custom persona",
                    visible=False,
                )
                persona_name_2.change(
                    toggle_custom_persona,
                    inputs=persona_name_2,
                    outputs=persona_custom_2,
                )
            
            tale_btn = gr.Button("Generate Experience Tale", scale=2)
            tale_output = gr.Textbox(label="Generated Tale", lines=15, interactive=False)
            
            tale_btn.click(
                generate_experience_tale,
                inputs=[problem, persona_name_2, persona_custom_2],
                outputs=tale_output
            )
        
        # Tab 3: Feature Impact
        with gr.Tab("Feature Impact"):
            gr.Markdown("### Generate Before/After Feature Impact Stories")
            with gr.Row():
                feature = gr.Textbox(label="Feature", placeholder="e.g., One-click scheduling with automatic reminders")
            with gr.Row():
                persona_name_3 = gr.Dropdown(
                    label="Select Persona",
                    choices=persona_choices,
                    value=default_persona_choice,
                )
                persona_custom_3 = gr.Textbox(
                    label="Or Custom Persona",
                    placeholder="Describe your custom persona",
                    visible=False,
                )
                persona_name_3.change(
                    toggle_custom_persona,
                    inputs=persona_name_3,
                    outputs=persona_custom_3,
                )
            
            impact_btn = gr.Button("Generate Feature Impact", scale=2)
            impact_output = gr.Textbox(label="Generated Impact Story", lines=15, interactive=False)
            
            impact_btn.click(
                generate_feature_impact,
                inputs=[feature, persona_name_3, persona_custom_3],
                outputs=impact_output
            )
        
        # Tab 4: Journey Map
        with gr.Tab("Journey Map"):
            gr.Markdown("### Generate Journey Map Narratives")
            with gr.Row():
                stage = gr.Textbox(label="Journey Stage", placeholder="e.g., awareness, consideration, adoption, retention")
                product_journey = gr.Textbox(label="Product", placeholder="e.g., Healthcare platform")
            with gr.Row():
                persona_name_4 = gr.Dropdown(
                    label="Select Persona",
                    choices=persona_choices,
                    value=default_persona_choice,
                )
                persona_custom_4 = gr.Textbox(
                    label="Or Custom Persona",
                    placeholder="Describe your custom persona",
                    visible=False,
                )
                persona_name_4.change(
                    toggle_custom_persona,
                    inputs=persona_name_4,
                    outputs=persona_custom_4,
                )
            
            journey_btn = gr.Button("Generate Journey Map", scale=2)
            journey_output = gr.Textbox(label="Generated Journey Map", lines=15, interactive=False)
            
            journey_btn.click(
                generate_journey_story,
                inputs=[stage, product_journey, persona_name_4, persona_custom_4],
                outputs=journey_output
            )

if __name__ == "__main__":
    demo.launch()
