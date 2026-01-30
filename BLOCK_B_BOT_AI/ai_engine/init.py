mkdir -p BLOCK_B_BOT_AI/ai_engine
touch BLOCK_B_BOT_AI/ai_engine/__init__.py
cat > BLOCK_B_BOT_AI/ai_engine/__init__.py << 'EOF'
from .request_analyzer import RequestAnalyzer
EOF
