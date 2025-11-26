# HealixPath Deployment Guide

## Hugging Face Spaces Deployment

### Prerequisites
- Hugging Face account
- Git installed locally
- Node.js 18+ and npm
- Python 3.10+

### Step 1: Create a Hugging Face Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in the details:
   - **Space name**: `healixpath`
   - **License**: MIT
   - **Space SDK**: Docker (recommended for better control)

### Step 2: Clone Your Space Repository

```bash
git clone https://huggingface.co/spaces/<your-username>/healixpath
cd healixpath
```

### Step 3: Copy Project Files

Copy all files from this repository to your Space repository:

```bash
# From your local HealixPath directory
cp -r src/ package.json tsconfig.json data/ app.py requirements.txt .gitignore README.md /path/to/space/healixpath/
```

### Step 4: Build and Test Locally

#### Test Node.js MCP Server

```bash
npm install
npm run build
npm run start
```

#### Test Gradio App

```bash
pip install -r requirements.txt
python app.py
```

The app will be available at `http://localhost:7860`

### Step 5: Deploy to Hugging Face Spaces

```bash
cd /path/to/space/healixpath
git add .
git commit -m "Initial HealixPath deployment"
git push
```

Spaces will automatically build and deploy your application. Check the build logs in the Space settings.

## Docker Deployment (Alternative)

If you want to use Docker, create a `Dockerfile` in your Space repository:

```dockerfile
FROM node:20

WORKDIR /app

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip

# Copy project files
COPY . .

# Install Node dependencies
RUN npm install
RUN npm run build

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose ports
EXPOSE 7860 3000

# Start Gradio app (can be modified to run MCP server)
CMD ["python", "app.py"]
```

## Environment Variables

Create a `.env` file for production (not committed to repo):

```env
ANTHROPIC_API_KEY=your_api_key_here
HF_TOKEN=your_huggingface_token
```

## Monitoring & Logs

In Hugging Face Spaces:
1. Go to your Space settings
2. View "Space runtime" for deployment status
3. Check "Logs" for error messages and debugging

## Scaling Considerations

- **Gradio Interface**: Runs on port 7860 by default
- **MCP Server**: Can be run on port 3000 (configure as needed)
- **Persistent Storage**: Use Hugging Face persistent storage if needed
- **Hardware**: Start with CPU-basic, upgrade to GPU if needed

## Troubleshooting

### Build Fails
- Check logs for missing dependencies
- Verify all files are in the Space repository
- Ensure `package.json` and `requirements.txt` are correct

### App Won't Start
- Verify `app_file: app.py` in README.md frontmatter
- Check Python dependencies with `pip list`
- Verify data files are present and readable

### Slow Performance
- Check Space logs for errors
- Consider upgrading hardware (GPU)
- Optimize Claude API calls

## Next Steps

1. **Integrate Claude API**: Replace placeholder functions in tools with actual Claude API calls
2. **Add Custom Personas**: Extend `data/personas.json` with your domain-specific personas
3. **Implement Persistence**: Add database for storing generated stories
4. **Add Authentication**: Secure your Space with Hugging Face OAuth
5. **Create CI/CD Pipeline**: Automate testing and deployment
