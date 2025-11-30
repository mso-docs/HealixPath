import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

interface GeneratePersonasParams {
  description: string;
  count: number;
}

export async function generatePersonas(params: GeneratePersonasParams): Promise<string> {
  const { description, count } = params;

  // Validate count
  if (count < 1 || count > 5) {
    return "Error: Count must be between 1 and 5 personas.";
  }

  const systemPrompt = `You are a persona generation expert. Generate realistic, diverse user personas based on the provided description.

CRITICAL REQUIREMENTS:
1. Return ONLY valid JSON - no markdown, no code blocks, no explanations
2. Return a JSON array of persona objects
3. Each persona must follow the exact structure provided in the example
4. Ensure diversity in all randomized fields (location, income, education, tech literacy, devices, etc.)
5. All personas must match the core description provided by the user
6. Generate exactly the number of personas requested

PERSONA STRUCTURE (follow this exactly):
{
  "id": "UUID (e.g., 'a1b2c3d4-e5f6-7890-abcd-ef1234567890')",
  "name": "Full Name",
  "age": number,
  "gender": "Male/Female/Nonbinary",
  "location": {
    "address": "street address",
    "city": "city",
    "state": "state/province",
    "country": "country"
  },
  "demographics": {
    "income": "$XX,000/year",
    "education_level": "education level",
    "marital_status": "status",
    "household_size": number
  },
  "job": {
    "title": "job title",
    "industry": "industry",
    "experience_years": number,
    "employment_type": "Full-time/Part-time/Freelance/etc"
  },
  "background": "brief background description",
  "interests": ["interest1", "interest2", "interest3"],
  "purchasing_habits": {
    "online_shopping_frequency": "frequency",
    "preferred_platforms": ["platform1", "platform2"],
    "average_spend_per_month": "$XXX",
    "brand_loyalty_level": "Low/Medium/High/Very High"
  },
  "technology": {
    "tech_literacy": "Low/Medium/High/Very High",
    "devices_used": ["device1", "device2"],
    "favorite_apps": ["app1", "app2", "app3"]
  },
  "goals": {
    "primary_goals": ["goal1", "goal2"],
    "secondary_goals": ["goal1", "goal2"]
  },
  "pain_points": ["pain1", "pain2"],
  "motivations": ["motivation1", "motivation2"],
  "personality": {
    "traits": ["trait1", "trait2"],
    "communication_style": "style description"
  },
  "user_story": "As a [role], I want [goal] so [benefit].",
  "acceptance_criteria": ["criteria1", "criteria2"]
}`;

  const userPrompt = `Generate ${count} diverse user persona${count > 1 ? 's' : ''} that match this description:

"${description}"

Requirements:
- Generate exactly ${count} persona${count > 1 ? 's' : ''}
- Each persona MUST match the core description: "${description}"
- Randomize other attributes for diversity (locations worldwide, various incomes, different tech literacy levels, diverse jobs/industries, etc.)
- Ensure realistic consistency within each persona
- Use diverse names from various cultures
- Return ONLY the JSON array, no other text

Return format: [persona1, persona2, ...]`;

  try {
    const message = await client.messages.create({
      model: "claude-3-5-sonnet-20241022",
      max_tokens: 8000,
      messages: [
        {
          role: "user",
          content: `${systemPrompt}\n\n${userPrompt}`,
        },
      ],
    });

    const responseText = message.content[0].type === "text" ? message.content[0].text : "";
    
    // Clean up response (remove markdown code blocks if present)
    let cleanedResponse = responseText.trim();
    if (cleanedResponse.startsWith("```json")) {
      cleanedResponse = cleanedResponse.replace(/^```json\s*/, "").replace(/```\s*$/, "").trim();
    } else if (cleanedResponse.startsWith("```")) {
      cleanedResponse = cleanedResponse.replace(/^```\s*/, "").replace(/```\s*$/, "").trim();
    }

    // Validate JSON
    try {
      const personas = JSON.parse(cleanedResponse);
      if (!Array.isArray(personas)) {
        throw new Error("Response is not an array");
      }
      
      // Return formatted JSON
      return JSON.stringify(personas, null, 2);
    } catch (parseError) {
      console.error("JSON Parse Error:", parseError);
      console.error("Response:", cleanedResponse);
      return `Error: Failed to parse generated personas. Raw response:\n${cleanedResponse}`;
    }

  } catch (error: any) {
    console.error("Error generating personas:", error);
    
    // Fallback response
    return JSON.stringify([
      {
        error: "Failed to generate personas with AI",
        message: error.message || "Unknown error",
        fallback_note: "The persona generation tool requires a valid Anthropic API key and internet connection."
      }
    ], null, 2);
  }
}
