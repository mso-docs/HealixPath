import {
  CustomerExperienceTale,
  generateStructuredResponse,
} from "../utils/helpers.js";
import { Persona, formatPersonaContext } from "../utils/persona_loader.js";
import {
  SYSTEM_PROMPT,
  CUSTOMER_EXPERIENCE_FEW_SHOT,
} from "../utils/prompts.js";

export interface CustomerExperienceTaleInput {
  persona_id?: string;
  persona_override?: string;
  problem: string;
}

export async function generateCustomerExperienceTale(
  input: CustomerExperienceTaleInput,
  persona?: Persona
): Promise<CustomerExperienceTale> {
  const personaContext = persona
    ? formatPersonaContext(persona)
    : input.persona_override || "Generic user";

  const userPrompt = `Create a customer experience tale for this scenario:

${personaContext}

Problem: ${input.problem}

Write a realistic, detailed narrative that captures the emotional and practical dimensions of this problem.

${CUSTOMER_EXPERIENCE_FEW_SHOT}`;

  return generateStructuredResponse<CustomerExperienceTale>({
    title: "customer_experience_tale",
    systemPrompt: SYSTEM_PROMPT,
    userPrompt,
    schema: {
      properties: {
        title: { type: "string" },
        narrative: { type: "string" },
        pain_points: {
          type: "array",
          items: { type: "string" },
          minItems: 3,
        },
        opportunities: {
          type: "array",
          items: { type: "string" },
          minItems: 2,
        },
      },
      required: ["title", "narrative", "pain_points", "opportunities"],
    },
    fallback: () => ({
      title: `${persona?.name || "User"} Faces: ${input.problem}`,
      narrative: `${
        persona?.name || "The user"
      } encounters ${input.problem}. This experience is frustrating because it directly conflicts with their need for efficiency and simplicity. The lack of clear guidance leaves them uncertain about next steps, adding to their stress.`,
      pain_points: [
        "Ambiguous problem messaging",
        "Lack of clear resolution path",
        "Time wasted troubleshooting",
      ],
      opportunities: [
        "Implement proactive error prevention",
        "Provide contextual help and guidance",
        "Streamline the recovery process",
      ],
    }),
  });
}
