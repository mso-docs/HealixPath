import "dotenv/config";
import {
  loadPersonas,
  getPersona,
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

interface ToolSchema {
  name: string;
  description: string;
  input_schema: {
    type: string;
    properties: Record<string, any>;
    required: string[];
  };
}

class HealixPathServer {
  private personas: Map<string, Persona>;

  constructor() {
    this.personas = loadPersonas();
  }

  getTools(): ToolSchema[] {
    return [
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
                "ID of the persona to use (busy_parent, ops_engineer, product_manager)",
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
    ];
  }

  async processTool(
    toolName: string,
    toolInput: Record<string, unknown>
  ): Promise<string> {
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

  console.log("\n\nAvailable Personas:");
  console.log(
    "- busy_parent: Working parent juggling multiple responsibilities"
  );
  console.log("- ops_engineer: On-call SRE managing infrastructure");
  console.log("- product_manager: PM at a healthcare startup");

  console.log("\n\n📝 Example Tool Calls:");
  console.log("---");

  // Example 1: User Story
  const userStoryResult = await server.processTool("user_story", {
    product: "Healthcare appointment scheduling app",
    persona_id: "busy_parent",
  });
  console.log("\n1. User Story for Busy Parent:");
  console.log(userStoryResult);

  // Example 2: Customer Experience Tale
  const taleResult = await server.processTool("customer_experience_tale", {
    problem: "Mobile app crashes during checkout",
    persona_id: "busy_parent",
  });
  console.log("\n2. Customer Experience Tale:");
  console.log(taleResult);

  // Example 3: Feature Impact Story
  const impactResult = await server.processTool("feature_impact_story", {
    feature_description: "One-click scheduling with automatic reminders",
    persona_id: "busy_parent",
  });
  console.log("\n3. Feature Impact Story:");
  console.log(impactResult);

  // Example 4: Journey Map Story
  const journeyResult = await server.processTool("journey_map_story", {
    stage: "adoption",
    product: "Healthcare platform",
    persona_id: "ops_engineer",
  });
  console.log("\n4. Journey Map Story:");
  console.log(journeyResult);

  console.log("\n\n✅ HealixPath Server is ready to serve MCP clients!");
}

main().catch(console.error);
