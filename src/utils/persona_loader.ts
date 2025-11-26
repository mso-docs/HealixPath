import { readFileSync } from "fs";
import { join } from "path";

export interface Persona {
  id: string;
  name: string;
  role: string;
  goals: string[];
  frustrations: string[];
  tech_comfort: string;
  quote: string;
  pain_points?: string[];
  needs?: string[];
}

export function loadPersonas(): Map<string, Persona> {
  try {
    const personasPath = join(process.cwd(), "data", "personas.json");
    const data = readFileSync(personasPath, "utf-8");
    const personas: Persona[] = JSON.parse(data);
    
    const personaMap = new Map<string, Persona>();
    personas.forEach((persona) => {
      personaMap.set(persona.id, persona);
    });
    
    return personaMap;
  } catch (error) {
    console.error("Failed to load personas:", error);
    return new Map();
  }
}

export function getPersona(personaId: string, personas: Map<string, Persona>): Persona | null {
  return personas.get(personaId) || null;
}

export function formatPersonaContext(persona: Persona): string {
  return `
Persona: ${persona.name}
Role: ${persona.role}
Goals: ${persona.goals.join(", ")}
Frustrations: ${persona.frustrations.join(", ")}
Tech Comfort Level: ${persona.tech_comfort}
Quote: "${persona.quote}"
${persona.pain_points ? `Pain Points: ${persona.pain_points.join(", ")}` : ""}
${persona.needs ? `Needs: ${persona.needs.join(", ")}` : ""}
`.trim();
}
