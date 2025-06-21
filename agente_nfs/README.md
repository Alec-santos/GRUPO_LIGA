# Desafio 2 - 18/06

# Projeto de ChatBot para notas fiscais.

* Observação:

  - Para o sistema de chatbot de notas fiscais funcionar é preciso instalar o Ollama no computador.
  
  - O computador precisa ter 6 Gib de memória Live só para o Ollama server executar,
    caso contrário ele vai gerar um erro:
    
		Assistente:			
		Erro ao processar pergunta: Ollama call failed with status code 500. Details: 
		{"error":"model requires more system memory (5.9 GiB) than is available (2.5 GiB)"}


* Instalar o servidor OLLAMA no computador
	
		curl -fsSL https://ollama.com/install.sh | sh

  - Executrar o serviço llama3 no Ollama
	
		ollama run llama3


* Código fonte e o executável do sistema chatbot de notas fiscais: 

  - Em um terminal e faça o clone da pasta [GRUPO_LIGA]
  	
  	Em seguida acesse a pasta [agente_nfs] onde econtra-se o codigo fonte, 
    e na pasta [agente_nfs/dist] encotrara o executavel do chatbot um arquivo binario [main].

		./agente_nfs/dist/main
		ou 
		./main
  	
    Obs.: Para compilar o codifo fonte é preciso criar um ambinete virtual no python 3.12.11.

  - Caso tenha algum problema para executar o sistema de chatbot, baixe o sistema do google drive 
	
		https://drive.google.com/drive/folders/11OEEUWhiPTQOOtvTxx5xGFoG68qJkH98

  - O sistema pode ser executado no Linux e no Windows: 
	
		./main
		

