mkdir -p BLOCK_B_BOT_AI/message_templates
touch BLOCK_B_BOT_AI/message_templates/__init__.py
cat > BLOCK_B_BOT_AI/message_templates/__init__.py << 'EOF'
from .templates import get_customer_messages, get_partner_messages
EOF
