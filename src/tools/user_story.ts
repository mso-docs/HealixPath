import { UserStory, generateStructuredResponse } from "../utils/helpers.js";
import { Persona, formatPersonaContext } from "../utils/persona_loader.js";
import { SYSTEM_PROMPT } from "../utils/prompts.js";

export interface UserStoryInput {
  product: string;
  persona_id?: string;
  persona_override?: string;
}

export async function generateUserStory(
  input: UserStoryInput,
  persona?: Persona
): Promise<UserStory> {
  const personaContext = persona
    ? formatPersonaContext(persona)
    : input.persona_override || "Generic user";

  const userPrompt = `Generate a user story for a ${input.product}.

${personaContext}

Create an actionable narrative that incorporates the persona's goals, frustrations, and perspective.`;

  return generateStructuredResponse<UserStory>({
    title: "user_story",
    systemPrompt: SYSTEM_PROMPT,
    userPrompt,
    schema: {
      properties: {
        story: { type: "string" },
        acceptance_criteria: {
          type: "array",
          items: { type: "string" },
          minItems: 3,
        },
        risks: {
          type: "array",
          items: { type: "string" },
          minItems: 2,
        },
      },
      required: ["story", "acceptance_criteria", "risks"],
    },
    fallback: () => ({
      story: `As ${persona?.name || "a user"}, I want to use ${
        input.product
      } to achieve my goals efficiently and without frustration.`,
      acceptance_criteria: [
        "Clear, intuitive interface that requires minimal clicks",
        "Fast loading times and responsive feedback",
        "Easy-to-understand error messages",
      ],
      risks: [
        "User may abandon if onboarding is too complex",
        "Performance issues could lead to negative perception",
        "Unclear messaging might cause support tickets",
      ],
    }),
  });
}
