#!/bin/bash
# Обновляет requirements.txt

cat > requirements.txt << 'EOF'
openai>=1.0.0
google-genai>=1.0.0
httpx>=0.27.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
PyYAML>=6.0
allure-pytest>=2.13.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
EOF

echo "requirements.txt updated."