# Configuração do ambiente do LangFlow

Este é um guia para realizar as configurações necessárias para que o LangFlow seja executado em uma máquina local, e na mesma maquina também executando o servidor do Ollama e seus serviços, no caso o modelo de sua escolha como, (llama3, llama4, mistral, gemma, qwen, etc).

## Configurando no ambiente: 

 * [Linux](#Sistema-Linux-UbuntuDebian) - sistema operacional.

 * [Windows](#Sistema-Windows-1011) - sistema operacional. 


***

## Sistema Linux (Ubuntu/Debian)	

## 1. Precisa ter o docker instalado na máquina, caso não, segue abaixo a instalação.

 - Configurar o docker apt repositório:
  
		# Add Docker's official GPG key:
		sudo apt-get update
		sudo apt-get install ca-certificates curl
		sudo install -m 0755 -d /etc/apt/keyrings
		sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
		sudo chmod a+r /etc/apt/keyrings/docker.asc

		# Add the repository to Apt sources:
		echo \
			"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
			$(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
			sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
		sudo apt-get update

 - Para instalar a versão mais recente, execute:
  
		sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

 - Verifique se a instalação foi bem-sucedida executando o hello-worldimagem:
  
		sudo docker run hello-world

 - Para maiores detalhes segue o link abaixo:

    https://docs.docker.com/engine/install/ubuntu/


## 2. Baixar as imagens do LangFlow do repositório do docker hub.

 - Em um terminal baixe a imagem correspondente à ultima versão,
   o comando irá verificar se a imagem existe, caso não, irá fazer o download e em seguida executar o Langflow:
   
		sudo docker run -it --rm -p 7860:7860 langflowai/langflow:latest
   
 - Acesse o Langflow com o link abaixo no seu navegador da web:

		http://localhost:7860

 - Para maiores detalhes segue o link abaixo:

    https://hub.docker.com/r/langflowai/langflow

 - Para verificar as imagens que existe na maquina:

		sudo docker images

## 3. Baixe o Ollama e os modelos LLM do site oficial.

 - Execute o comando abaixo para instalar o servidor Ollama:

		curl -fsSL https://ollama.com/install.sh | sh

 - Para executar o servidor Ollama;
   A execução é automática porém o servidor só libera a porta 11434 para o IP localhost e como o 
   Langflow está em um docker ele não vai enxergar o Ollama, Segue abaixo a correção para isso:
  
		# Pare o servidor ollama:
		
		sudo systemctl stop ollama
		
		# Force o servidor ollama a liberar o IP da sua maquina na porta 11434:
		
		OLLAMA_HOST=0.0.0.0:11434 ollama serve

 - Segue o link do site oficial para escolher o modelo LLM que desejar:

    https://ollama.com/search

 - Para executar o modelo, o comando verificará se existe o modelo no local, caso não, 
   irá fazer o download e em seguida executar:

		ollama run llama3

 - Para verificar os modelos que existem na maquina:

		ollama list

## 4. Segue o link para a documentação do Langflow.

 - Agora é só estudar e ficar, expert... ;)

    https://docs.langflow.org/


---


## Sistema Windows (10/11)


