# HealixPath - Quick Start Guide

## 🚀 30-Second Setup

```bash
# 1. Install dependencies
npm install
pip install -r requirements.txt

# 2. Build TypeScript
npm run build

# 3. Run Gradio App
python app.py

# 4. Open browser to http://localhost:7860
```

## 📖 60-Second Demo

1. **Open the Gradio UI** at `http://localhost:7860`
2. **Navigate to "User Story" tab**
3. **Enter Product**: "Healthcare appointment scheduling app"
4. **Select Persona**: "Busy Parent"
5. **Click "Generate User Story"**
6. **See the generated narrative and acceptance criteria!**

## 🔧 MCP Server Usage

### Start the Server

```bash
# Terminal 1: Start MCP Server
npm run start
```

### Use with Claude (Terminal 2)

```bash
# Example: Call user_story tool
curl -X POST http://localhost:3000/tool/user_story \
  -H "Content-Type: application/json" \
  -d '{
    "product": "Healthcare platform",
    "persona_id": "busy_parent"
  }'
```

## 📁 Key Files to Modify

### Add Custom Personas
Edit `data/personas.json`:
```json
{
  "id": "custom_persona",
  "name": "Custom Name",
  "role": "Role description",
  "goals": ["goal 1", "goal 2"],
  "frustrations": ["frustration 1"],
  "tech_comfort": "medium",
  "quote": "Inspirational quote"
}
```

### Connect Claude API
In `src/tools/user_story.ts`:
```typescript
// Replace placeholder with actual Claude call
import Anthropic from "@anthropic-sdk/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const response = await client.messages.create({
  model: "claude-3-5-sonnet-20241022",
  max_tokens: 1024,
  messages: [{ role: "user", content: userPrompt }],
});
```

## 🌐 Deploy to Hugging Face Spaces

### 1. Create Space
- Go to [huggingface.co/new-space](https://huggingface.co/new-space)
- Choose "Gradio" as SDK
- Name it "healixpath"

### 2. Push Code
```bash
git clone https://huggingface.co/spaces/<username>/healixpath
cd healixpath
# Copy all files from local repo
git add .
git commit -m "Deploy HealixPath"
git push
```

### 3. Space Auto-Deploys
- Hugging Face automatically builds and deploys
- Your app is live at `huggingface.co/spaces/<username>/healixpath`

## 🎯 Tool Examples

### Generate User Story
**Input:**
```json
{
  "product": "Mental health mobile app",
  "persona_id": "busy_parent"
}
```

**Output:**
```json
{
  "story": "As a busy parent...",
  "acceptance_criteria": ["...", "...", "..."],
  "risks": ["..."]
}
```

### Generate Experience Tale
**Input:**
```json
{
  "problem": "App crashes when uploading large files",
  "persona_id": "ops_engineer"
}
```

### Generate Feature Impact
**Input:**
```json
{
  "feature_description": "Offline mode with sync",
  "persona_id": "busy_parent"
}
```

### Generate Journey Map
**Input:**
```json
{
  "stage": "adoption",
  "product": "Healthcare platform",
  "persona_id": "product_manager"
}
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 7860
# Windows:
netstat -ano | findstr :7860
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:7860 | xargs kill -9
```

### Missing Dependencies
```bash
# Reinstall all
rm -rf node_modules
npm install
pip install -r requirements.txt --force-reinstall
```

### Gradio Won't Start
```bash
# Check Python version
python --version  # Should be 3.10+

# Check Gradio installation
pip show gradio
```

### Build Errors
```bash
# Check TypeScript syntax
npm run build

# View error details
cat dist/*.d.ts
```

## 📚 Documentation

- **Full Documentation**: See `README.md`
- **Project Summary**: See `PROJECT_SUMMARY.md`
- **Deployment Guide**: See `DEPLOYMENT.md`
- **API Reference**: Check `src/index.ts` for tool definitions

## 🎓 Learning Resources

### Understanding Personas
Each persona has:
- **Goals**: What they want to achieve
- **Frustrations**: What blocks them
- **Quote**: Their perspective
- **Tech Comfort**: Skill level (low/medium/high)

### Story Generation Workflow
1. Load persona data → 2. Create context → 3. Generate with AI → 4. Format output → 5. Return JSON

### MCP Protocol
- Tools are registered with name, description, input schema
- Input schema defines required/optional parameters
- Output is always JSON
- Errors are caught and returned as JSON

## 🚀 Next Steps

1. ✅ Get it running locally
2. ✅ Try each tool with different personas
3. ✅ Customize personas for your domain
4. ✅ Deploy to Hugging Face Spaces
5. ✅ Integrate Claude API for real generations
6. ✅ Share with your team!

## 💡 Tips & Tricks

- **Persona Override**: Use custom persona text if ID not found
- **Batch Generation**: Call tools multiple times for different personas
- **JSON Export**: Copy generated JSON for further processing
- **Gradio Sharing**: Use `demo.share()` in `app.py` for public URL

## 📞 Support

For issues or questions:
1. Check `DEPLOYMENT.md` for deployment issues
2. Review `PROJECT_SUMMARY.md` for architecture details
3. Inspect `src/index.ts` for MCP implementation
4. Check Gradio docs at [gradio.app](https://www.gradio.app)

---

**Happy Storytelling! 🎭**
