#!/bin/bash

echo "🇫🇷 AIDE FRANCE - Instalador"
echo "=========================="

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no instalado"
    exit 1
fi

# Instalar dependencias
pip3 install requests beautifulsoup4 flask lxml

# Crear carpetas
mkdir -p docs examples exports

# Ejecutar
python3 aide_france.py
