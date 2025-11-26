import {
  JourneyMapStory,
  generateStructuredResponse,
} from "../utils/helpers.js";
import { Persona, formatPersonaContext } from "../utils/persona_loader.js";
import { SYSTEM_PROMPT } from "../utils/prompts.js";

export interface JourneyMapStoryInput {
  stage: string;
  product: string;
  persona_id?: string;
  persona_override?: string;
}

export async function generateJourneyMapStory(
  input: JourneyMapStoryInput,
  persona?: Persona
): Promise<JourneyMapStory> {
  const personaContext = persona
    ? formatPersonaContext(persona)
    : input.persona_override || "Generic user";

  const userPrompt = `Create a journey map narrative for a specific stage:

${personaContext}

Product: ${input.product}
Journey Stage: ${input.stage}

Write a detailed narrative capturing the persona's experience, emotions, and interactions at this stage.`;

  return generateStructuredResponse<JourneyMapStory>({
    title: "journey_map_story",
    systemPrompt: SYSTEM_PROMPT,
    userPrompt,
    schema: {
      properties: {
        stage: { type: "string" },
        narrative: { type: "string" },
        touchpoints: {
          type: "array",
          items: { type: "string" },
          minItems: 3,
        },
        emotions: {
          type: "array",
          items: { type: "string" },
          minItems: 2,
        },
        breakdowns: {
          type: "array",
          items: { type: "string" },
          minItems: 2,
        },
        opportunities: {
          type: "array",
          items: { type: "string" },
          minItems: 2,
        },
      },
      required: [
        "stage",
        "narrative",
        "touchpoints",
        "emotions",
        "breakdowns",
        "opportunities",
      ],
    },
    fallback: () => ({
      stage: input.stage,
      narrative: `At the ${input.stage} stage, ${
        persona?.name || "the user"
      } is navigating their journey with ${input.product}. Their emotions are mixed—hopeful about the potential benefits, but uncertain about the complexity they might face.`,
      touchpoints: [
        "Landing page or app entry point",
        "Onboarding flow",
        "Primary feature interaction",
        "Support resources",
      ],
      emotions: [
        "Anticipation",
        "Confidence",
        "Occasional frustration",
        "Growing satisfaction",
      ],
      breakdowns: [
        "Unclear value proposition",
        "Complex setup process",
        "Insufficient documentation",
        "Slow initial results",
      ],
      opportunities: [
        "Streamline onboarding",
        "Provide quick wins",
        "Offer contextual guidance",
        "Build community support",
      ],
    }),
  });
}
