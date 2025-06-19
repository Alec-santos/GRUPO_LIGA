# Desafio 2 - 18/06

# Projeto de ChatBot para notas fiscais.

* Observação:
  - A maquina precisa ter 5.9 GiB de memoria Live só para o OLLAMA server executar,
  caso contratio ele vai gerar um erro:
  
  - Assistente: 
  Erro ao processar pergunta: Ollama call failed with status code 500. Details: 
  {"error":"model requires more system memory (5.9 GiB) than is available (2.5 GiB)"}

* Para executar o sistema abra um terminal e faça um clone da pasta [GRUPO_LIGA] em seguida acesse a pasta [agente_nfs] e execute o comando abaixo:

  - Para essa execução e nesserario baixar codigo fonte e criar um ambinete virtual no python 3.12.11  

    python main.py

  - Para essa execução e nesserario apenas instalar o servidor do OLLAMA 

    - Instalar o OLLAMA no PC

      curl -fsSL https://ollama.com/install.sh | sh
    
    - Executrar o serviço do Ollama
    
      ollama run llama3

    - Executrar o arquivo binario do ChatBot de notas fiscais, baixe o sistema do google drive 

      Link dogoogle drive:

        https://drive.google.com/drive/folders/11OEEUWhiPTQOOtvTxx5xGFoG68qJkH98

      Executar o sistema no Linux ou no Windows: 

        ./main

