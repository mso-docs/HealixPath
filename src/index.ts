import "dotenv/config";
import {
  loadPersonas,
  getPersona,
  formatPersonaSummary,
  searchPersonas,
  type Persona,
} from "./utils/persona_loader.js";
import { generateUserStory, type UserStoryInput } from "./tools/user_story.js";
import {
  generateCustomerExperienceTale,
  type CustomerExperienceTaleInput,
} from "./tools/customer_experience_tale.js";
import {
  generateFeatureImpactStory,
  type FeatureImpactStoryInput,
} from "./tools/feature_impact_story.js";
import {
  generateJourneyMapStory,
  type JourneyMapStoryInput,
} from "./tools/journey_map_story.js";
import { generatePersonas } from "./tools/generate_personas.js";

interface ToolSchema {
  name: string;
  description: string;
  input_schema: {
    type: string;
    properties: Record<string, any>;
    required: string[];
  };
}

interface ResourceSchema {
  uri: string;
  name: string;
  description: string;
  mimeType: string;
}

class HealixPathServer {
  private personas: Map<string, Persona>;

  constructor() {
    this.personas = loadPersonas();
  }

  getTools(): ToolSchema[] {
    return [
      {
        name: "list_personas",
        description:
          "List all available personas with their key attributes (id, name, age, location, job title, industry, tech literacy, goals, pain points)",
        input_schema: {
          type: "object",
          properties: {
            limit: {
              type: "number",
              description: "Optional: Maximum number of personas to return (default: all)",
            },
          },
          required: [],
        },
      },
      {
        name: "search_personas",
        description:
          "Search and filter personas by role/job title, industry, age range, tech literacy, or location",
        input_schema: {
          type: "object",
          properties: {
            role: {
              type: "string",
              description: "Filter by job title or role (partial match, case-insensitive)",
            },
            industry: {
              type: "string",
              description: "Filter by industry (partial match, case-insensitive)",
            },
            age_range: {
              type: "string",
              description: "Filter by age range (format: 'min-max', e.g., '25-35')",
            },
            tech_literacy: {
              type: "string",
              description: "Filter by tech literacy level (e.g., 'high', 'moderate', 'low')",
            },
            location: {
              type: "string",
              description: "Filter by location - city, state, or country (partial match)",
            },
          },
          required: [],
        },
      },
      {
        name: "user_story",
        description:
          "Generate a structured narrative user story with acceptance criteria and risks",
        input_schema: {
          type: "object",
          properties: {
            product: {
              type: "string",
              description: "Description of the product or feature",
            },
            persona_id: {
              type: "string",
              description:
                "ID of the persona to use (use list_personas to see available IDs)",
            },
            persona_override: {
              type: "string",
              description:
                "Custom persona description if persona_id is not provided",
            },
          },
          required: ["product"],
        },
      },
      {
        name: "customer_experience_tale",
        description:
          "Create a narrative describing a persona experiencing a specific problem",
        input_schema: {
          type: "object",
          properties: {
            problem: {
              type: "string",
              description: "The problem the persona is experiencing",
            },
            persona_id: {
              type: "string",
              description: "ID of the persona to use",
            },
            persona_override: {
              type: "string",
              description:
                "Custom persona description if persona_id is not provided",
            },
          },
          required: ["problem"],
        },
      },
      {
        name: "feature_impact_story",
        description:
          "Show the before and after of a persona interacting with a feature",
        input_schema: {
          type: "object",
          properties: {
            feature_description: {
              type: "string",
              description: "Description of the feature",
            },
            persona_id: {
              type: "string",
              description: "ID of the persona to use",
            },
            persona_override: {
              type: "string",
              description:
                "Custom persona description if persona_id is not provided",
            },
          },
          required: ["feature_description"],
        },
      },
      {
        name: "journey_map_story",
        description:
          "Generate a narrative for a specific stage of the user journey",
        input_schema: {
          type: "object",
          properties: {
            stage: {
              type: "string",
              description:
                "Journey stage (e.g., awareness, consideration, adoption, retention)",
            },
            product: {
              type: "string",
              description: "Description of the product",
            },
            persona_id: {
              type: "string",
              description: "ID of the persona to use",
            },
            persona_override: {
              type: "string",
              description:
                "Custom persona description if persona_id is not provided",
            },
          },
          required: ["stage", "product"],
        },
      },
      {
        name: "generate_personas",
        description:
          "Generate random user personas based on a natural language description. Creates realistic, diverse personas matching the specified criteria with randomized attributes for variety.",
        input_schema: {
          type: "object",
          properties: {
            description: {
              type: "string",
              description:
                "Natural language description of the personas to generate (e.g., 'people who love to cook but never have time to in their 20-30s', 'sandwich enthusiasts who are 50+ years old')",
            },
            count: {
              type: "number",
              description:
                "Number of personas to generate (minimum: 1, maximum: 5, default: 1)",
            },
          },
          required: ["description", "count"],
        },
      },
    ];
  }

  getResources(): ResourceSchema[] {
    const resources: ResourceSchema[] = [
      {
        uri: "personas://all",
        name: "All Personas",
        description: "Complete list of all available personas with their full details",
        mimeType: "application/json",
      },
    ];

    // Add individual persona resources
    for (const [id, persona] of this.personas.entries()) {
      resources.push({
        uri: `personas://${id}`,
        name: `${persona.name} - ${persona.job?.title || persona.role || "User"}`,
        description: `Detailed information about ${persona.name}`,
        mimeType: "application/json",
      });
    }

    return resources;
  }

  async readResource(uri: string): Promise<string> {
    if (uri === "personas://all") {
      const allPersonas = Array.from(this.personas.values()).map(formatPersonaSummary);
      return JSON.stringify(allPersonas, null, 2);
    }

    // Handle individual persona URIs
    if (uri.startsWith("personas://")) {
      const personaId = uri.replace("personas://", "");
      const persona = this.personas.get(personaId);
      
      if (!persona) {
        return JSON.stringify({ error: `Persona not found: ${personaId}` });
      }

      return JSON.stringify(persona, null, 2);
    }

    return JSON.stringify({ error: `Unknown resource URI: ${uri}` });
  }

  async processTool(
    toolName: string,
    toolInput: Record<string, unknown>
  ): Promise<string> {
    // Handle list_personas tool
    if (toolName === "list_personas") {
      const limit = typeof toolInput.limit === "number" ? toolInput.limit : undefined;
      const allPersonas = Array.from(this.personas.values()).map(formatPersonaSummary);
      const personas = limit ? allPersonas.slice(0, limit) : allPersonas;
      return JSON.stringify({ personas, total: this.personas.size }, null, 2);
    }

    // Handle search_personas tool
    if (toolName === "search_personas") {
      const filters = {
        role: typeof toolInput.role === "string" ? toolInput.role : undefined,
        industry: typeof toolInput.industry === "string" ? toolInput.industry : undefined,
        age_range: typeof toolInput.age_range === "string" ? toolInput.age_range : undefined,
        tech_literacy: typeof toolInput.tech_literacy === "string" ? toolInput.tech_literacy : undefined,
        location: typeof toolInput.location === "string" ? toolInput.location : undefined,
      };

      const results = searchPersonas(this.personas, filters);
      const summaries = results.map(formatPersonaSummary);
      
      return JSON.stringify({ 
        personas: summaries, 
        count: summaries.length,
        filters: Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== undefined))
      }, null, 2);
    }

    let persona: Persona | undefined;

    // Load persona if specified
    if (typeof toolInput.persona_id === "string") {
      const loadedPersona = getPersona(toolInput.persona_id, this.personas);
      if (!loadedPersona) {
        return JSON.stringify({
          error: `Persona not found: ${toolInput.persona_id}`,
        });
      }
      persona = loadedPersona;
    }

    try {
      switch (toolName) {
        case "user_story": {
          const input = toolInput as unknown as UserStoryInput;
          const userStory = await generateUserStory(input, persona);
          return JSON.stringify(userStory);
        }

        case "customer_experience_tale": {
          const input = toolInput as unknown as CustomerExperienceTaleInput;
          const tale = await generateCustomerExperienceTale(input, persona);
          return JSON.stringify(tale);
        }

        case "feature_impact_story": {
          const input = toolInput as unknown as FeatureImpactStoryInput;
          const impactStory = await generateFeatureImpactStory(input, persona);
          return JSON.stringify(impactStory);
        }

        case "journey_map_story": {
          const input = toolInput as unknown as JourneyMapStoryInput;
          const journeyStory = await generateJourneyMapStory(input, persona);
          return JSON.stringify(journeyStory);
        }

        case "generate_personas": {
          const description = typeof toolInput.description === "string" ? toolInput.description : "";
          const count = typeof toolInput.count === "number" ? toolInput.count : 1;
          
          if (!description) {
            return JSON.stringify({ error: "Description is required" });
          }
          
          const personas = await generatePersonas({ description, count });
          return personas; // Already JSON stringified
        }

        default:
          return JSON.stringify({ error: `Unknown tool: ${toolName}` });
      }
    } catch (error) {
      return JSON.stringify({
        error: `Failed to process tool: ${error instanceof Error ? error.message : String(error)}`,
      });
    }
  }
}

// Example usage and server setup
async function main(): Promise<void> {
  const server = new HealixPathServer();

  console.log("🚀 HealixPath MCP Server");
  console.log("=======================");
  console.log("\nAvailable Tools:");
  server.getTools().forEach((tool) => {
    console.log(`\n- ${tool.name}`);
    console.log(`  ${tool.description}`);
  });

  console.log("\n\nAvailable Resources:");
  server.getResources().slice(0, 5).forEach((resource) => {
    console.log(`\n- ${resource.uri}`);
    console.log(`  ${resource.description}`);
  });
  console.log(`\n... and ${server.getResources().length - 5} more persona resources`);

  console.log("\n\n📝 Example Tool Calls:");
  console.log("---");

  // Example 0: List Personas
  const listResult = await server.processTool("list_personas", { limit: 3 });
  console.log("\n0. List Personas (first 3):");
  console.log(listResult);

  // Example 0b: Search Personas
  const searchResult = await server.processTool("search_personas", {
    industry: "healthcare",
    tech_literacy: "moderate"
  });
  console.log("\n0b. Search Personas (Healthcare + Moderate Tech):");
  console.log(searchResult);

  // Example 0c: Read Resource
  const resourceResult = await server.readResource("personas://all");
  console.log("\n0c. Read Resource (all personas summary - truncated):");
  console.log(resourceResult.substring(0, 500) + "...");

  // Example 1: User Story
  const userStoryResult = await server.processTool("user_story", {
    product: "Healthcare appointment scheduling app",
    persona_id: "persona-001",
  });
  console.log("\n1. User Story:");
  console.log(userStoryResult);

  // Example 2: Customer Experience Tale
  const taleResult = await server.processTool("customer_experience_tale", {
    problem: "Mobile app crashes during checkout",
    persona_id: "persona-001",
  });
  console.log("\n2. Customer Experience Tale:");
  console.log(taleResult);

  // Example 3: Feature Impact Story
  const impactResult = await server.processTool("feature_impact_story", {
    feature_description: "One-click scheduling with automatic reminders",
    persona_id: "persona-001",
  });
  console.log("\n3. Feature Impact Story:");
  console.log(impactResult);

  // Example 4: Journey Map Story
  const journeyResult = await server.processTool("journey_map_story", {
    stage: "adoption",
    product: "Healthcare platform",
    persona_id: "persona-003",
  });
  console.log("\n4. Journey Map Story:");
  console.log(journeyResult);

  // Example 5: Generate Personas
  const generateResult = await server.processTool("generate_personas", {
    description: "people who love to cook but never have time to in their 20-30s",
    count: 2,
  });
  console.log("\n5. Generate Personas (cooking enthusiasts, 20-30s, time-constrained):");
  console.log(generateResult);

  console.log("\n\n✅ HealixPath Server is ready to serve MCP clients!");
}

main().catch(console.error);
