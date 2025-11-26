#!/bin/bash
# HealixPath WSL Setup Helper

echo "🚀 HealixPath WSL Environment Setup"
echo "===================================="

# Activate Python virtual environment
echo "Activating Python virtual environment..."
source /mnt/c/Users/rarev/Code/TeamHealix/venv/bin/activate

# Check Node and Python
echo ""
echo "✅ Environment Ready:"
echo "   Node.js: $(node --version)"
echo "   npm: $(npm --version)"
echo "   Python: $(python3 --version)"
echo ""

# Show available commands
echo "📝 Available Commands:"
echo ""
echo "  npm run build      - Build TypeScript to JavaScript"
echo "  npm run start      - Run MCP Server"
echo "  python app.py      - Run Gradio Web Interface"
echo ""
echo "🌐 Web Interface: http://localhost:7860"
echo "📡 MCP Server: Runs on configurable port"
echo ""
