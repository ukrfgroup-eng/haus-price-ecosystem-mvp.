touch BLOCK_B_BOT_AI/message_templates/templates.py
cat > BLOCK_B_BOT_AI/message_templates/templates.py << 'EOF'
def get_customer_messages(key):
    messages = {
        'welcome': 'Добро пожаловать! Я помогу найти исполнителя для вашего проекта.',
        'ask_project_type': 'Какой тип работ вас интересует?'
    }
    return messages.get(key, '')

def get_partner_messages(key):
    messages = {
        'welcome': 'Добро пожаловать! Я помогу зарегистрировать вашу компанию как партнера.',
        'ask_company_name': 'Введите название вашей компании:'
    }
    return messages.get(key, '')
EOF
