import {
  FeatureImpactStory,
  generateStructuredResponse,
} from "../utils/helpers.js";
import { Persona, formatPersonaContext } from "../utils/persona_loader.js";
import { SYSTEM_PROMPT } from "../utils/prompts.js";

export interface FeatureImpactStoryInput {
  feature_description: string;
  persona_id?: string;
  persona_override?: string;
}

export async function generateFeatureImpactStory(
  input: FeatureImpactStoryInput,
  persona?: Persona
): Promise<FeatureImpactStory> {
  const personaContext = persona
    ? formatPersonaContext(persona)
    : input.persona_override || "Generic user";

  const userPrompt = `Create a before/after feature impact story:

${personaContext}

Feature: ${input.feature_description}

Show how this feature transforms the user's experience and removes pain points.`;

  return generateStructuredResponse<FeatureImpactStory>({
    title: "feature_impact_story",
    systemPrompt: SYSTEM_PROMPT,
    userPrompt,
    schema: {
      properties: {
        before_story: { type: "string" },
        after_story: { type: "string" },
        key_benefits: {
          type: "array",
          items: { type: "string" },
          minItems: 3,
        },
        success_metrics: {
          type: "array",
          items: { type: "string" },
          minItems: 3,
        },
      },
      required: [
        "before_story",
        "after_story",
        "key_benefits",
        "success_metrics",
      ],
    },
    fallback: () => ({
      before_story: `Before this feature, ${
        persona?.name || "the user"
      } struggled with inefficient workflows. The process was manual, time-consuming, and error-prone, leaving them frustrated and exhausted.`,
      after_story: `After implementing this feature, ${
        persona?.name || "the user"
      } experiences a dramatically improved workflow. Tasks that once took hours now take minutes, allowing them to focus on what truly matters.`,
      key_benefits: [
        "Significant time savings",
        "Reduced manual effort",
        "Improved accuracy and consistency",
        "Enhanced user satisfaction",
      ],
      success_metrics: [
        "Task completion time: -60%",
        "User satisfaction score: +40%",
        "Error rate reduction: -85%",
      ],
    }),
  });
}
