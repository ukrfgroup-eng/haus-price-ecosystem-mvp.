mkdir -p BLOCK_B_BOT_AI/scenarios
touch BLOCK_B_BOT_AI/scenarios/__init__.py
cat > BLOCK_B_BOT_AI/scenarios/__init__.py << 'EOF'
from .base_scenario import BaseScenario
from .customer_scenario import CustomerScenario
from .partner_scenario import PartnerScenario
EOF
