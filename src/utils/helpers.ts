import Anthropic from "@anthropic-ai/sdk";

export interface UserStory {
  story: string;
  acceptance_criteria: string[];
  risks: string[];
}

export interface CustomerExperienceTale {
  title: string;
  narrative: string;
  pain_points: string[];
  opportunities: string[];
}

export interface FeatureImpactStory {
  before_story: string;
  after_story: string;
  key_benefits: string[];
  success_metrics: string[];
}

export interface JourneyMapStory {
  stage: string;
  narrative: string;
  touchpoints: string[];
  emotions: string[];
  breakdowns: string[];
  opportunities: string[];
}

interface StructuredGenerationOptions<T> {
  title: string;
  systemPrompt: string;
  userPrompt: string;
  schema: {
    properties: Record<string, unknown>;
    required?: string[];
  };
  fallback: () => T;
}

const anthropicApiKey = process.env.ANTHROPIC_API_KEY;
const anthropicModel =
  process.env.ANTHROPIC_MODEL || "claude-3-5-sonnet-20241022";
const anthropicClient = anthropicApiKey
  ? new Anthropic({ apiKey: anthropicApiKey })
  : null;

export async function generateStructuredResponse<T>(
  options: StructuredGenerationOptions<T>
): Promise<T> {
  const { title, systemPrompt, userPrompt, schema, fallback } = options;

  if (!anthropicClient) {
    console.warn(
      "ANTHROPIC_API_KEY not set. Returning fallback output for",
      title
    );
    return fallback();
  }

  try {
    const response = await anthropicClient.messages.create({
      model: anthropicModel,
      max_tokens: 1024,
      system: systemPrompt,
      messages: [{ role: "user", content: userPrompt }],
    });

    const [firstChunk] = response.content;
    if (firstChunk?.type === "text") {
      return JSON.parse(firstChunk.text);
    }

    if (firstChunk?.type === "tool_use") {
      return firstChunk.input as T;
    }

    throw new Error("Anthropic returned an unsupported content type");
  } catch (error) {
    console.error(
      `Structured generation failed for ${title}:`,
      error instanceof Error ? error.message : error
    );
    return fallback();
  }
}
