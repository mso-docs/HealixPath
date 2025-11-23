---
title: HealixPath
emoji: 💚
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: true
short_description: AI-powered persona storytelling engine for UX, product, and design teams.
tags:
    - mcp-hackathon
    - building-mcp-track-enterprise
    - building-mcp-track
    - healthcare
    - ai
    - personas
    - storytelling
---

# HealixPath — The AI-Powered Persona Path & Story Engine

✨ HealixPath transforms product inputs, personas, problems, and customer journey stages into rich, structured, realistic stories. Use this exact package for your MCP server, repo, and hackathon pitch.

---

## 🧠 1. Product Overview (README + Pitch)

**HealixPath** delivers AI-powered persona storytelling for UX, product, and design teams. Instead of vague bullet points like “User gets frustrated during checkout,” HealixPath generates:

- actionable narratives  
- persona-grounded insights  
- pain points & opportunities  
- before/after feature impact stories  
- journey-map narratives  

Designed to help product teams feel their users, not just document them.

---

## 🛠️ 2. MCP-Compatible Tools

Each tool is exposed through the MCP server (`src/index.ts`) and powered by Claude via the `@anthropic-sdk/sdk`. Schemas are enforced through Anthropic’s JSON mode so outputs are always valid.

### 1. `user_story`
Generates a structured narrative user story + acceptance criteria from a product and persona.

**Input**
```json
{
  "product": "string",
  "persona_id": "string (optional)",
  "persona_override": "string (optional)"
}
```

**Output**
```json
{
  "story": "string",
  "acceptance_criteria": ["string"],
  "risks": ["string"]
}
```

### 2. `customer_experience_tale`
Creates a short narrative describing a persona experiencing a specific problem.

**Input**
```json
{
  "persona_id": "string (optional)",
  "persona_override": "string (optional)",
  "problem": "string"
}
```

**Output**
```json
{
  "title": "string",
  "narrative": "string",
  "pain_points": ["string"],
  "opportunities": ["string"]
}
```

### 3. `feature_impact_story`
Shows the before and after of a persona interacting with a feature.

**Input**
```json
{
  "feature_description": "string",
  "persona_id": "string (optional)",
  "persona_override": "string (optional)"
}
```

**Output**
```json
{
  "before_story": "string",
  "after_story": "string",
  "key_benefits": ["string"],
  "success_metrics": ["string"]
}
```

### 4. `journey_map_story`
Generates a narrative for a specific stage of the user journey.

**Input**
```json
{
  "stage": "string",
  "product": "string",
  "persona_id": "string (optional)",
  "persona_override": "string (optional)"
}
```

**Output**
```json
{
  "stage": "string",
  "narrative": "string",
  "touchpoints": ["string"],
  "emotions": ["string"],
  "breakdowns": ["string"],
  "opportunities": ["string"]
}
```

---

## 🧬 3. Persona Data (`data/personas.json`)

```json
[
  {
    "id": "busy_parent",
    "name": "Busy Parent",
    "role": "Working parent of two kids",
    "goals": ["Save time", "Reduce mental load", "Keep kids on schedule"],
    "frustrations": ["Too many apps", "Slow support", "Juggling work and home"],
    "tech_comfort": "medium",
    "quote": "If it's not simple, I don't have time for it."
  },
  {
    "id": "ops_engineer",
    "name": "Ops Engineer",
    "role": "On-call site reliability engineer",
    "goals": ["Reduce alerts", "Stability", "Automate repetitive tasks"],
    "frustrations": ["Pager fatigue", "Unclear incident logs", "Slow dashboards"],
    "tech_comfort": "high",
    "quote": "If it breaks, it's my problem at 3am."
  }
]
```

Add more personas anytime—`src/utils/persona_loader.ts` automatically loads them.

---

## 🛑 4. System Prompt (Paste into MCP Server or Claude Playground)

```
You are HealixPath, an enterprise-grade AI persona path engine.
Your goal is to help product, UX, and design teams deeply understand users by generating realistic, structured persona-driven stories.

You ALWAYS:
- adopt the persona’s perspective (from persona_id data or persona_override text)
- integrate goals, frustrations, role, and quote into narrative context
- maintain realism with specific details (environment, device, timing)
- highlight both pain points and business opportunities
- write with clarity, professionalism, and grounded emotional tone
- output ONLY valid JSON in the exact schema specified by the user

Style:
- narratives: 250–600 words
- avoid buzzwords and marketing fluff
- focus on concrete behaviors & motivations
- connect the story directly back to the product input or feature description

If persona_id is provided, load persona data from the persona database.
If persona_override is provided, use it as supplemental context, not a replacement.

If both are missing, create a plausible persona from scratch with sensible traits.

Strictly follow schemas provided in each tool.
```

This exact prompt is codified in `src/utils/prompts.ts`.

---

## 🧪 5. Few-Shot Example (Use in Prompting or README)

```
Example for customer_experience_tale
Input:
persona:
- name: Busy Parent
- role: Working parent of two kids
- goals: ["Save time", "Reduce mental load", "Keep kids on schedule"]
- frustrations: ["Too many apps", "Slow support", "Juggling work and home"]
- quote: "If it's not simple, I don't have time for it."
problem: "Promo code fails during mobile checkout on a flash sale"

Expected Output:
{
  "title": "Promo Panic at Bedtime",
  "narrative": "It's 8:45pm and Maya sinks into her couch after finally putting her two kids to bed...",
  "pain_points": [
    "Ambiguous promo code error message",
    "Checkout form resets when navigating back",
    "Customer support queue too long for short sessions"
  ],
  "opportunities": [
    "Clearer inline error messaging",
    "Auto-saving form state",
    "Fast support path during busy sale windows"
  ]
}
```

---

## 📂 6. Recommended Repo Structure (already implemented)

```
healixpath/
├─ src/
│  ├─ tools/
│  │   ├─ user_story.ts
│  │   ├─ customer_experience_tale.ts
│  │   ├─ feature_impact_story.ts
│  │   └─ journey_map_story.ts
│  ├─ utils/
│  │   ├─ persona_loader.ts
│  │   ├─ helpers.ts
│  │   └─ prompts.ts
│  └─ index.ts
├─ data/
│  └─ personas.json
├─ app.py
├─ package.json
├─ tsconfig.json
├─ requirements.txt
├─ README.md
└─ .env (create from .env.example)
```

---

## ⚙️ 7. Getting Started

### Node.js MCP Server
```bash
cp .env.example .env   # add your Anthropic key
npm install
npm run build
npm run start
```
`src/index.ts` boots the HealixPath MCP server, enumerates tools, and shows sample tool calls. Claude responses stream through `@anthropic-sdk/sdk` with enforced JSON schemas; when the API key is absent, deterministic fallbacks keep the demo running.

### Gradio Demo
```bash
pip install -r requirements.txt
python app.py
```
`app.py` offers a quick UI to showcase personas and tool outputs during demos or on Hugging Face Spaces.

---

## 🚀 8. Hackathon Demo Script (60 Seconds)

> “We built HealixPath, an AI engine that generates realistic persona-based stories for UX and product teams. Instead of vague bullet points like ‘User is frustrated at checkout,’ HealixPath produces rich narratives, pain points, opportunities, and journey maps — all grounded in real personas. It takes a product description or problem, merges it with persona data, and instantly produces a believable, actionable user story. This helps teams design better flows, features, and experiences by understanding the human side behind the analytics. In just one click, a PM can generate a story that feels like it came from weeks of user research.”

Then show a persona → problem → generated JSON/story.

---

## 🎨 9. Want Next?

1. Logo explorations for HealixPath (neon, simple, minimal, enterprise)
2. Brand color palette or landing page copy
3. Full MCP client or UI mockup for demos
4. Domain availability research

Ping me when you’re ready for the next layer of polish!

---

**Built for the MCP Hackathon 🚀**
