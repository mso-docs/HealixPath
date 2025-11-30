import { readFileSync } from "fs";
import { join } from "path";

export interface Persona {
  id: string;
  name: string;
  age?: number;
  gender?: string;
  location?: {
    address?: string;
    city?: string;
    state?: string;
    country?: string;
  };
  demographics?: {
    income?: string;
    education_level?: string;
    marital_status?: string;
    household_size?: number;
  };
  job?: {
    title?: string;
    industry?: string;
    experience_years?: number;
    employment_type?: string;
  };
  background?: string;
  interests?: string[];
  purchasing_habits?: {
    online_shopping_frequency?: string;
    preferred_platforms?: string[];
    average_spend_per_month?: string;
    brand_loyalty_level?: string;
  };
  technology?: {
    tech_literacy?: string;
    devices_used?: string[];
    favorite_apps?: string[];
  };
  goals?: {
    primary_goals?: string[];
    secondary_goals?: string[];
  };
  pain_points?: string[];
  motivations?: string[];
  personality?: {
    traits?: string[];
    communication_style?: string;
  };
  user_story?: string;
  acceptance_criteria?: string[];
  
  // Legacy fields for backward compatibility
  role?: string;
  frustrations?: string[];
  tech_comfort?: string;
  quote?: string;
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
  const jobTitle = persona.job?.title || persona.role || "Unknown";
  const industry = persona.job?.industry || "Unknown";
  const age = persona.age || "Unknown";
  const city = persona.location?.city || "Unknown";
  const primaryGoals = persona.goals?.primary_goals || persona.goals as any as string[] || [];
  const painPoints = persona.pain_points || persona.frustrations || [];
  const motivations = persona.motivations || [];
  const techLiteracy = persona.technology?.tech_literacy || persona.tech_comfort || "Unknown";
  
  return `
Persona: ${persona.name}
Age: ${age}
Location: ${city}
Title: ${jobTitle}
Industry: ${industry}
Background: ${persona.background || "N/A"}
Goals: ${Array.isArray(primaryGoals) ? primaryGoals.join(", ") : "N/A"}
Pain Points: ${Array.isArray(painPoints) ? painPoints.join(", ") : "N/A"}
Motivations: ${Array.isArray(motivations) ? motivations.join(", ") : "N/A"}
Tech Literacy: ${techLiteracy}
${persona.user_story ? `User Story: ${persona.user_story}` : ""}
${persona.quote ? `Quote: "${persona.quote}"` : ""}
`.trim();
}

export function formatPersonaSummary(persona: Persona): any {
  return {
    id: persona.id,
    name: persona.name,
    age: persona.age,
    location: persona.location?.city ? `${persona.location.city}, ${persona.location.state || persona.location.country}` : "Unknown",
    job_title: persona.job?.title || persona.role || "Unknown",
    industry: persona.job?.industry || "Unknown",
    tech_literacy: persona.technology?.tech_literacy || persona.tech_comfort || "Unknown",
    primary_goals: persona.goals?.primary_goals || [],
    pain_points: persona.pain_points || persona.frustrations || [],
    user_story: persona.user_story || "",
  };
}

export function searchPersonas(
  personas: Map<string, Persona>,
  filters: {
    role?: string;
    industry?: string;
    age_range?: string;
    tech_literacy?: string;
    location?: string;
  }
): Persona[] {
  const results: Persona[] = [];
  
  for (const persona of personas.values()) {
    let matches = true;
    
    // Filter by role/job title
    if (filters.role) {
      const personaRole = (persona.job?.title || persona.role || "").toLowerCase();
      if (!personaRole.includes(filters.role.toLowerCase())) {
        matches = false;
      }
    }
    
    // Filter by industry
    if (filters.industry && matches) {
      const personaIndustry = (persona.job?.industry || "").toLowerCase();
      if (!personaIndustry.includes(filters.industry.toLowerCase())) {
        matches = false;
      }
    }
    
    // Filter by age range (e.g., "20-30", "30-40")
    if (filters.age_range && persona.age && matches) {
      const [minAge, maxAge] = filters.age_range.split("-").map(Number);
      if (persona.age < minAge || persona.age > maxAge) {
        matches = false;
      }
    }
    
    // Filter by tech literacy
    if (filters.tech_literacy && matches) {
      const personaTech = (persona.technology?.tech_literacy || persona.tech_comfort || "").toLowerCase();
      if (!personaTech.includes(filters.tech_literacy.toLowerCase())) {
        matches = false;
      }
    }
    
    // Filter by location
    if (filters.location && matches) {
      const personaLocation = `${persona.location?.city || ""} ${persona.location?.state || ""} ${persona.location?.country || ""}`.toLowerCase();
      if (!personaLocation.includes(filters.location.toLowerCase())) {
        matches = false;
      }
    }
    
    if (matches) {
      results.push(persona);
    }
  }
  
  return results;
}
