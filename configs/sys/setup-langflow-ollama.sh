#!/bin/bash

echo "=== 1. Verificando instalação do Docker ==="
if ! command -v docker &> /dev/null; then
	echo "Docker não encontrado. Instalando..."
	sudo apt-get update
	sudo apt-get install -y ca-certificates curl gnupg lsb-release

	# Cria diretório para chaves do Docker
	sudo install -m 0755 -d /etc/apt/keyrings

	# Baixa a chave GPG oficial
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
			sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
	sudo chmod a+r /etc/apt/keyrings/docker.gpg

	# Adiciona repositório do Docker
	echo \
		"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
		https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
		sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

	# Atualiza repositórios e instala Docker
	sudo apt-get update
	sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

	# Verifica se Docker está OK
	sudo docker run hello-world
else
	echo "Docker já instalado."
fi

echo "=== 2. Instalando Ollama se necessário ==="
if ! command -v ollama &> /dev/null; then
	curl -fsSL https://ollama.com/install.sh | sh
else
	echo "Ollama já instalado."
fi

echo "=== 3. Configurando Ollama para escutar em 0.0.0.0 ==="
sudo systemctl stop ollama
sudo sed -i '/^ExecStart=/c\ExecStart=/usr/bin/env OLLAMA_HOST=0.0.0.0:11434 /usr/local/bin/ollama serve' /etc/systemd/system/ollama.service
sudo systemctl daemon-reload
sudo systemctl restart ollama

echo "=== 4. Baixando modelo llama3 ==="
ollama run llama3

echo "=== 5. Executando LangFlow no Docker ==="
docker run -it --rm -p 7860:7860 langflowai/langflow:latest

echo "Acesse LangFlow em http://localhost:7860"

