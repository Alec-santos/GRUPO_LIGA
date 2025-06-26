@echo off

echo === 1. Verificando Docker ===
where docker >nul 2>&1
if errorlevel 1 (
	echo Docker não encontrado. Por favor, instale o Docker Desktop manualmente.
	pause
	exit /b
) else (
	echo Docker encontrado.
)

echo === 2. Verificando Ollama ===
where ollama >nul 2>&1
if errorlevel 1 (
	echo Ollama não encontrado. Por favor, instale manualmente em: https://ollama.com
	pause
	exit /b
) else (
	echo Ollama encontrado.
)

echo === 3. Redirecionando porta 11434 para permitir acesso do Docker
netsh interface portproxy add v4tov4 listenport=11434 listenaddress=0.0.0.0 connectport=11434 connectaddress=127.0.0.1

echo === 4. Rodando modelo llama3 com Ollama
start /B cmd /C "ollama run llama3"

echo === 5. Iniciando LangFlow no Docker
docker run -it --rm -p 7860:7860 langflowai/langflow:latest

echo Acesse LangFlow em http://localhost:7860
pause

