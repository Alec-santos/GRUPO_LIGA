# ==========================================================================
# Painel de Análise de Notas Fiscais Eletrônicas (NFe)
# Versão com Sidebar (menus e filtros) + Interatividade e Correção de Datas
# Banco de dados: analisenfe.db (SQLite)
# ==========================================================================
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from datetime import datetime
from types import SimpleNamespace
import plotly.express as px
import streamlit as st
import pandas as pd
import requests
import sqlite3
import base64
import locale
import json
import os
import re

def loadjson(pfile: str):
    with open(pfile, "r", encoding="utf-8") as f:
        return json.load(f, object_hook=lambda d: SimpleNamespace(**d))

def format_texto(txt):
    rst = txt.replace("\n","").replace("  "," ")
    rst = rst.replace("¨","“").replace("“ ","” ").replace("“,","”,").replace("“.","”.")
    rst = rst.replace(". ",". \n")
    return rst

def format_valor(txt):
    def formatar(match):
        valor_str = match.group()
        valor = float(valor_str)
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    rst = re.sub(r'\d+\.\d+', formatar, txt)
    return rst

@st.cache_data(ttl=300)
def carregar_dados(path_file): 
    conn = sqlite3.connect(path_file)
    analise = pd.read_sql_query("SELECT * FROM vw_analise", conn)
    itens = pd.read_sql_query("SELECT * FROM vw_itens", conn)
    notasfiscal = pd.read_sql_query("SELECT * FROM notafiscal", conn)
    clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
    produtos = pd.read_sql_query("SELECT * FROM produtos", conn)
    logs = pd.read_sql_query("SELECT * FROM logs", conn)
    conn.close()

    # Renomeia colunas para minúsculas
    analise.columns = analise.columns.str.lower()
    itens.columns = itens.columns.str.lower()
    logs.columns = logs.columns.str.lower()

    # Conversão de data nas tabelas analise
    analise["data_emissao"] = pd.to_datetime(analise["data_emissao"], format="%Y-%m-%d", errors="coerce")

    # Converter campo data para datetime legível
    logs["data"] = pd.to_datetime(logs["data"], format="%Y%m%d%H%M%S", errors="coerce")

    return analise, itens, notasfiscal, clientes, produtos, logs,  

# ======================================
# --- Configuração inicial da página ---
# ======================================
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

config = loadjson("config.json") 
analise, itens, notasfiscal, clientes, produtos, logs = carregar_dados(config.path+config.dbname)
logs_filtro = logs.copy()

st.set_page_config(page_title="Painel de Análise NFe", layout="wide")
col1, col2 = st.columns([0.4,5])
with col1:
    st.image("logo.png", width=85)
with col2:
    st.header("FiscalFlow AI - Sistema inteligente de análise e auditoria de Fiscal")
st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;L.I.G.A&nbsp;&nbsp;-&nbsp;&nbsp;Laboratório de Inteligência Generativa Artificial</span>
        <span>⏱️ Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</span>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("""<style>            
    section[data-testid="stSidebar"] {
        width: 300px; 
        min-width: 300px; 
        max-width: 500px; 
        resize: horizontal; 
        overflow: auto; 
    }
    /* Alinhar o conteúdo dos botões da sidebar à esquerda */
    section[data-testid="stSidebar"] div.stButton > button {
        width: 100% !important;
        display: flex !important;
        justify-content: flex-start !important;
        text-align: left !important;
        align-items: center !important;
        padding-left: 0.6rem !important;
    }
    /* Alinha também o conteúdo interno (div) do botão */
    section[data-testid="stSidebar"] div.stButton > button > div {
        justify-content: flex-start !important;
    }
    /* Exemplo estilo ativo – pode precisar ajustar seletor real */
    section[data-testid="stSidebar"] div.stButton button:focus,
    section[data-testid="stSidebar"] div.stButton button[aria-expanded="true"] {
        background-color: #13486D;
        color: white;
    }
    /* sespaçamento entre botões */
    section[data-testid="stSidebar"] div.stButton button {
        width: 100% !important;
        margin-bottom: 4px;
    }    
    </style>""",
    unsafe_allow_html=True
)

st.sidebar.header("🎛️&nbsp;&nbsp;Menu de navegação")
if st.sidebar.button("📥&nbsp;&nbsp;Upload dos arquivos NFe", key="btn_upload", width="stretch"):
    st.session_state["menu"] = "Upload dos arquivos NFe"
if st.sidebar.button("🕵️&nbsp;&nbsp;Agentes de analise NFe", key="btn_config", width="stretch"):
    st.session_state["menu"] = "Agentes de analise NFe"
if st.sidebar.button("📊&nbsp;&nbsp;Gráficos Analíticos", key="btn_graficos", width="stretch"):
    st.session_state["menu"] = "Gráficos Analíticos"
if st.sidebar.button("🚨&nbsp;&nbsp;Relatório de Divergências", key="btn_relatorios", width="stretch"):
    st.session_state["menu"] = "Relatórios de Divergências"
if st.sidebar.button("🔍&nbsp;&nbsp;Detalhes da NFe", key="btn_analise", width="stretch"):
    st.session_state["menu"] = "Detalhes da NFe"
if st.sidebar.button("📜&nbsp;&nbsp;Histórico dos arquivos NFe", key="btn_logs", width="stretch"):
    st.session_state["menu"] = "Histórico dos arquivos NFe"
if "menu" not in st.session_state:
    st.session_state["menu"] = "Gráficos Analíticos"

# ==========================
# --- Campos dos filtros ---
# ==========================
st.sidebar.markdown("---")
if st.session_state["menu"] == "Gráficos Analíticos" or st.session_state["menu"] == "Relatórios de Divergências":

    situacoes = ["Todas"] + sorted(analise["situacao"].unique())
    filtro_situacao = st.sidebar.selectbox("Filtrar por situação:", situacoes)
    if filtro_situacao != "Todas":
        analise = analise[analise["situacao"] == filtro_situacao]

    tipoNFe = ["Todas"] + sorted(analise["tipo_nfe"].unique())
    filtro_tipoNFe = st.sidebar.selectbox("Filtrar por tipo de NFe:", tipoNFe)
    if filtro_tipoNFe != "Todas":
        analise = analise[analise["tipo_nfe"] == filtro_tipoNFe]

    cfop = ["Todas"] + sorted(analise["cfop"].unique())
    filtro_cfop = st.sidebar.selectbox("Filtrar a situação do CFOP:", cfop)
    if filtro_cfop != "Todas":
        analise = analise[analise["cfop"] == filtro_cfop]

    cst = ["Todas"] + sorted(analise["cst"].unique())
    filtro_cst = st.sidebar.selectbox("Filtrar a situação do CST:", cst)
    if filtro_cst != "Todas":
        analise = analise[analise["cst"] == filtro_cst]

    ncm = ["Todas"] + sorted(analise["ncm"].unique())
    filtro_ncm = st.sidebar.selectbox("Filtrar a situação do NCM:", ncm)
    if filtro_ncm != "Todas":
        analise = analise[analise["ncm"] == filtro_ncm]

# ======================================
# --- Menu: Configuração dos Agentes ---
# ======================================
if st.session_state["menu"] == "Agentes de analise NFe":
    st.info("#### 🕵️&nbsp;&nbsp;Agentes de análise dos arquivos NFe")
    
    # --- URLs dos agentes ---
    AGENTES = {"🧠 Agente de análise das NFe em XML": config.endpoint_xml, "🧠 Agente de análise das NFe em PDF": config.endpoint_pdf}

    # --- Estado global de logs ---
    if "logs_exec_simples" not in st.session_state:
        st.session_state["logs_exec_simples"] = []

    # --- Layout em duas colunas ---
    colA, colB, colC = st.columns([0.5, 0.02, 0.3])  # proporção aproximada de 300px e 900px

    # --- Coluna A - Controles e resultados ---
    with colA:
        # Seleção de agentes
        st.subheader("Selecione os Agentes para Executar:")
        agentes_escolhidos = st.multiselect(
            "Escolha um ou mais agentes para rodar:",
            options=list(AGENTES.keys()),
            default=[],
            help="Você pode selecionar múltiplos agentes segurando CTRL (ou CMD no mac)."
        )
        # Função auxiliar para executar um agente
        def executar_agente(nome_agente, url):
            """Envia um POST para o agente e retorna o resultado formatado."""
            payload = {"input_value": "hello", "output_type": "text", "input_type": "text"}
            headers = {"Content-Type": "application/json"}

            data_api = datetime.now().strftime("%d/%m/%Y %H:%M")
            codigo_api = "000"
            texto_api = "Sem resposta da API."

            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=900)
                codigo_api = resp.status_code
                resp.raise_for_status()
                #data = resp.json()
                if codigo_api == 200:
                    texto_api = "✅ Sucesso no fluxo"
                else:
                    texto_api = "⚠️ Falha no fluxo"
            except Exception as e:
                codigo_api = "000"
                texto_api = f"❌ Erro ao chamar a API: {e}"

            # Registra log
            st.session_state["logs_exec_simples"].append({
                "Data/Hora": data_api,
                "Agente": nome_agente,
                "Código": codigo_api,
                "Mensagens": texto_api
            })

        # --- Botão isolado dentro de container identificado ---
        executar_container = st.container()
        executar_container.markdown('<div data-testid="executar-agentes">', unsafe_allow_html=True)
        executar = st.button("▶️&nbsp;&nbsp;Executar os Agentes de análise das NFe", key="executar_agentes")
        executar_container.markdown('</div>', unsafe_allow_html=True)

        # --- Execução ---
        if executar:
            if not agentes_escolhidos:
                st.warning("⚠️ Selecione ao menos um agente antes de executar.")
            else:
                st.info(f"⚡ Executando {len(agentes_escolhidos)} agente(s)... aguarde.")
                for agente in agentes_escolhidos:
                    url = AGENTES[agente]
                    executar_agente(agente, url)
                st.success("✅ Execução concluída!")

        st.markdown("---")

        # --- Exibição dos resultados ---
        if st.session_state["logs_exec_simples"]:
            st.subheader("⚙️ Resultados das Execuções")
            df_logs = pd.DataFrame(st.session_state["logs_exec_simples"])
            gb = GridOptionsBuilder.from_dataframe(df_logs)
            gb.configure_default_column(filter=False, suppressMenu=True)
            gb.configure_column("Data/Hora", width=60)
            gb.configure_column("Agente", width=115)
            gb.configure_column("Código", width=35, filter=False)
            gb.configure_column("Mensagens", width=200)
            AgGrid(
                df_logs,
                gridOptions=gb.build(),
                fit_columns_on_grid_load=True,
                height=325,
            )
        else:
            st.info("Nenhum agente foi executado ainda. Selecione e clique em **Executar Agentes Selecionados**.")

    with colB:
        st.empty()  # apenas para ocupar espaço e separar as colunas

    with colC:
        st.subheader("💡 Como funcionam os Agentes")
        st.markdown("###### Nesta página você pode executar os Agentes de Análise de NFe, responsáveis por processar os arquivos XML e PDF já importados para o sistema.")
        st.markdown("""
        Os **Agentes de IA** são fluxos inteligentes criados no **Langflow**, desenvolvidos para **ler, interpretar e extrair informações estruturadas das Notas Fiscais Eletrônicas (NFe)**.

        ⚙️ **Fluxo geral de funcionamento:**
        1. **Seleção dos agentes:**  
        Escolha um ou mais agentes disponíveis na lista.  
        - 🧠 *Agente de análise das NFe em XML* - interpreta arquivos **.xml**, identificando campos fiscais e estruturando os dados.  
        - 🧠 *Agente de análise das NFe em PDF* - realiza leitura e extração de informações diretamente de documentos PDF.

        2. **Execução dos fluxos:**  
        Ao clicar em **▶️ Executar os Agentes**, o sistema envia uma **requisição HTTP (POST)** para a API de cada agente selecionado.  
        Essa chamada aciona o fluxo no Langflow, que processa as entradas e retorna o resultado da operação.

        3. **Monitoramento e logs:**  
        Cada execução gera um **registro automático de log**, exibido em uma tabela no painel principal.  
        Os logs incluem:
        - 📅 Data e hora da execução  
        - 🧠 Nome do agente chamado  
        - 🔢 Código de resposta da API (ex: 200 para sucesso)  
        - 🧾 Mensagem de status do resultado  

        Dessa forma, é possível acompanhar o histórico completo das execuções e diagnosticar eventuais falhas de comunicação.

        4. **Resultados e status:**  
        O painel de logs apresenta o resumo de cada tentativa:
        - ✅ *Sucesso no fluxo* - o agente foi executado corretamente e respondeu à requisição.  
        - ⚠️ *Falha no fluxo* - a API respondeu com erro.  
        - ❌ *Erro ao chamar a API* - ocorreu falha na comunicação com o endpoint do agente.

        ---
        🧭 **Como usar na prática:**  
        1. Selecione os agentes desejados.  
        2. Clique em **Executar** para iniciar a análise.  
        3. Acompanhe o resultado e o status na tabela de logs.  
        4. Repita quantas vezes quiser, comparando o desempenho e a confiabilidade entre agentes.

        ---
        📂 **Processo de Armazenamento dos Arquivos:**  
        Os arquivos importados através do módulo “Upload dos Arquivos NFe” são organizados automaticamente em pastas, conforme o resultado do processamento:  
        📁 **/NFe**&nbsp;&nbsp;→&nbsp;&nbsp;Pasta principal onde todos os arquivos enviados inicialmente são armazenados.  
        🗂️ **/NFe/old**&nbsp;&nbsp;→&nbsp;&nbsp;Contém os arquivos que foram processados com sucesso (✅ Sucesso no fluxo).  
        🚫 **/NFe/erro**&nbsp;&nbsp;→&nbsp;&nbsp;Armazena os arquivos que tiveram algum problema na leitura ou no processamento (⚠️ Falha no fluxo).  

        ---
        ❗ **Dica:**  
        Você pode rodar múltiplos agentes simultaneamente para comparar a performance e o retorno de cada um.  
        Essa página serve como um **painel de controle central** para acionar, monitorar e validar os resultados dos fluxos de análise das NFe.
        """)

# =====================================
# --- Menu: Upload dos arquivos NFe ---
# =====================================
elif st.session_state["menu"] == "Upload dos arquivos NFe":

    st.info("#### 📥&nbsp;&nbsp;Upload - importação dos arquivos NFe para o sistema")

    # --- Diretório de destino ---
    os.makedirs(config.path+"NFe/", exist_ok=True)

    colA, colB, colC = st.columns([0.5, 0.02, 0.3])  # proporção aproximada de 300px e 900px
    with colA:
        # --- Etapa 1 - Upload de seleção ---
        arquivos = st.file_uploader(
            "Arraste e solte ou selecione arquivos:",
            type=["xml", "pdf"],
            accept_multiple_files=True
        )
        if arquivos:
            st.success(f"{len(arquivos)} arquivo(s) selecionado(s).")
            df_atualizado = None

            # --- Etapa 2 - Validação dos arquivos ---
            resultados = []
            for arquivo in arquivos:
                nome_arquivo = arquivo.name
                caminho_destino = os.path.join(config.path+"NFe/", nome_arquivo)

                if os.path.exists(caminho_destino):
                    status = "⚠️ Já existe na pasta"
                    substituir = False
                else:
                    status = "🆕 Novo arquivo"
                    substituir = False

                resultados.append({
                    "Arquivo": nome_arquivo,
                    "Status": status,
                    "Substituir": substituir
                    }
                )
            df_resultados = pd.DataFrame(resultados)
            gb = GridOptionsBuilder.from_dataframe(df_resultados)
            gb.configure_column("Arquivo", header_name="Nome do Arquivo", editable=False, width=300)
            gb.configure_column("Status", header_name="Situação", editable=False, width=100)
            gb.configure_column(
                "Substituir",
                header_name="Deseja substituir?",
                editable=True,
                cellEditor="agCheckboxCellEditor",
                width=90
            )
            grid_response = AgGrid(
                df_resultados,
                gridOptions=gb.build(),
                fit_columns_on_grid_load=True,
                enable_enterprise_modules=False,
                height=325,
            )
            df_atualizado = grid_response["data"]

            # --- Etapa 4 - Confirmação de upload ---
            if st.button("📤&nbsp;&nbsp;Confirmar Upload e Substituições"):
                progresso = st.progress(0)
                total = len(df_atualizado)
                sucesso = 0
                for i, row in enumerate(df_atualizado.itertuples(), start=1):
                    nome_arquivo = row.Arquivo
                    caminho_destino = os.path.join(config.path+"NFe/", nome_arquivo)
                    arquivo_obj = next((a for a in arquivos if a.name == nome_arquivo), None)
                    try:
                        if os.path.exists(caminho_destino):
                            if row.Substituir:
                                with open(caminho_destino, "wb") as f:
                                    f.write(arquivo_obj.getbuffer())
                                sucesso += 1
                                df_atualizado.loc[df_atualizado["Arquivo"] == nome_arquivo, "Status"] = "♻️ Substituído com sucesso"
                            else:
                                df_atualizado.loc[df_atualizado["Arquivo"] == nome_arquivo, "Status"] = "⏩ Mantido o que já existe"
                        else:
                            with open(caminho_destino, "wb") as f:
                                f.write(arquivo_obj.getbuffer())
                            sucesso += 1
                            df_atualizado.loc[df_atualizado["Arquivo"] == nome_arquivo, "Status"] = "✅ Importado com sucesso"
                    except Exception as e:
                        df_atualizado.loc[df_atualizado["Arquivo"] == nome_arquivo, "Status"] = f"❌ Erro: {e}"
                    progresso.progress(i / total)
                progresso.empty()
                st.success(f"✅&nbsp;&nbsp;**[{sucesso}] Arquivo(s)** importado(s) e/ou substituído(s) com sucesso.")

                # --- Atualiza grid final com resultados ---
                gb_final = GridOptionsBuilder.from_dataframe(df_atualizado)
                gb_final.configure_column("Arquivo", header_name="Nome do Arquivo", editable=False, width=300)
                gb_final.configure_column("Status", header_name="Situação Final", editable=False, width=100)
                gb_final.configure_column("Substituir", header_name="Substituidos", editable=False, width=90)
                AgGrid(
                    df_atualizado,
                    gridOptions=gb_final.build(),
                    fit_columns_on_grid_load=True,
                    enable_enterprise_modules=False,
                    height=325,
                )
        else:
            st.info("Nenhum arquivo selecionado. Escolha arquivos XML ou PDF para iniciar o processo.")

    with colB:
        st.empty()  # apenas para ocupar espaço e separar as colunas

    with colC:
        st.subheader("💡 Como funcionam os Uploads")
        st.markdown("###### Nesta página você pode importar os arquivos de Notas Fiscais Eletrônicas (NFe) para o sistema, tanto em formato XML quanto PDF.")
        st.markdown("""
        O objetivo desta seção é **enviar e gerenciar os arquivos de NFe** que serão posteriormente analisados pelos agentes de IA.

        ⚙️ **Fluxo geral do processo:**
        1. **Seleção dos arquivos:**  
        Utilize o campo de upload para **selecionar manualmente** os arquivos **.xml** ou **.pdf**.  
        É possível enviar múltiplos arquivos de uma só vez.
        
        2. **Validação automática:**  
        Após o upload, o sistema **verifica se o arquivo já existe** na pasta de destino **(/NFe)**.  
        Cada arquivo é exibido em uma tabela (grid) com informações sobre o seu **status atual**:
        - 🆕 *Novo arquivo* - ainda não existe na pasta.  
        - ⚠️ *Já existe na pasta* - o sistema detectou um arquivo com o mesmo nome.

        3. **Controle de substituições:**  
        Na coluna **“Deseja substituir?”**, o usuário pode marcar quais arquivos existentes devem ser sobrescritos.  
        Essa opção é **interativa**, permitindo revisar e ajustar antes da confirmação.

        4. **Confirmação do upload:**  
        Ao clicar no botão **📤 “Confirmar Upload e Substituições”**, o sistema inicia o processo de gravação:
        - Arquivos novos são **importados** para o diretório de destino.  
        - Arquivos já existentes e marcados são **substituídos**.  
        - Os não marcados permanecem inalterados.  
        Durante a execução, uma **barra de progresso** indica o andamento da operação.

        5. **Resultados finais:**  
        Após o término, o grid é atualizado com o **status final** de cada arquivo:
        - ✅ *Importado com sucesso*  
        - ♻️ *Substituído com sucesso*  
        - ⏩ *Mantido o que já existe*  
        - ❌ *Erro* (caso ocorra alguma falha durante o upload)

        ---
        📂 **Local de armazenamento:**  
        Todos os arquivos são gravados automaticamente na pasta:
        ```
        /NFe
        ```

        ---
        ❗ **Dica:**  
        Essa etapa é fundamental antes da análise - pois é aqui que os arquivos são organizados e disponibilizados para os agentes de processamento de NFe.  
        Mantenha o diretório atualizado para garantir que apenas as versões corretas dos documentos sejam utilizadas.
        """)

# =================================
# --- Menu: Gráficos Analíticos --- 
# =================================
elif st.session_state["menu"] == "Gráficos Analíticos":

    st.info("#### 📊&nbsp;&nbsp;Gráficos Analíticos das Notas Fiscais eletrônicas (NFe)")
    total_nf = len(analise)
    total_conforme = len(analise[analise["situacao"] == "CONFORME"])
    total_divergente = len(analise[analise["situacao"] == "DIVERGENTE"])
    valor_total = analise["valor_nfe"].sum()
    perc_conforme = (total_conforme / total_nf * 100) if total_nf > 0 else 0
    perc_div = (total_divergente / total_nf * 100) if total_nf > 0 else 0
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("NFes Analisadas", total_nf)
    col2.metric("Conformes (%)", f"{perc_conforme:.1f}%")
    col3.metric("Divergentes (%)", f"{perc_div:.1f}%")
    col4.metric("Valor Total (R$)", f"{valor_total:,.2f}")
    st.markdown("---")

    # --- Distribuição das NFes por Situação + Tipos de Erros ---
    colA, colB = st.columns(2)
    with colA:
        st.subheader("⚠️ Distribuição das NFes por Situação")
        situacao_df = analise["situacao"].value_counts().reset_index()
        situacao_df.columns = ["Situação", "Quantidade"]
        fig1 = px.bar(
            situacao_df, 
            x="Situação", 
            y="Quantidade", 
            color="Situação", 
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig1.update_layout(
            title= dict(text="Situação das NFes (Conforme x Divergente)", x=0.5, xanchor='center'),
            plot_bgcolor="#4F4F4F", 
            paper_bgcolor="#363636"
        )               
        st.plotly_chart(fig1, use_container_width=True)

    with colB:
        st.subheader("🚨 Tipos de Erros Encontrados")
        erros = {
            "NCM": (analise["ncm"] == "ERRO").sum(),
            "CST": (analise["cst"] == "ERRO").sum(),
            "CFOP": (analise["cfop"] == "ERRO").sum()
        }
        erro_df = pd.DataFrame(erros.items(), columns=["Tipo", "Erros"])
        fig2 = px.pie(
            erro_df, 
            names="Tipo", 
            values="Erros", 
            color_discrete_sequence=px.colors.sequential.RdBu
        )        
        fig2.update_layout(
            title= dict(text="Proporção dos erros encotrados nos código CFOP/CST/CNM", x=0.5, xanchor='center'),
            plot_bgcolor="#4F4F4F", 
            paper_bgcolor="#363636"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # --- Evolução das NFes + Análise por Tipo de NFe ---
    colC, colD = st.columns(2)
    st.subheader("🕒 Evolução das NFes analisadas por mês")

    # --- Agrupa por ano/mês ---
    evolucao = (analise.dropna(subset=["data_emissao"]).groupby(analise["data_emissao"].dt.to_period("M")).size().reset_index(name="Quantidade")) 

    # --- Converte Period -> datetime garantido ---
    #evolucao["data_emissao"] = evolucao["data_emissao"].apply(lambda x: x.to_timestamp())
    evolucao["data_emissao"] = evolucao["data_emissao"].dt.to_timestamp()

    evolucao = evolucao.sort_values("data_emissao")
    evolucao["Categoria"] = "Qde NFes"
    fig3 = px.line(
        evolucao, 
        x="data_emissao", 
        y="Quantidade", 
        color="Categoria", 
        markers=True,                    
        labels={"data_emissao": "Período mensal", "Quantidade": "NFes"}
    )
    fig3.update_layout(
        title= dict(text="Evolução das NFes ao longo do tempo", x=0.5, xanchor='center'),
        legend_title_text="Evolução",
        plot_bgcolor="#4F4F4F", 
        paper_bgcolor="#363636"
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("---")
    st.info("#### 📦&nbsp;&nbsp;Análise gráfica dos tipos Notas Fiscais (Entrada x Saída)")
    col_tipo_nfe = next((c for c in analise.columns if c.lower() == "tipo_nfe"), None)
    if col_tipo_nfe is None:
        st.warning("⚠️ Coluna 'tipo_nfe' não encontrada na tabela 'analise'. Verifique o nome no banco.")
    else:
        analise["tipo_nfe_normalizado"] = analise[col_tipo_nfe].astype(str).str.strip().str.upper()
        analise["tipo_nfe_categoria"] = analise["tipo_nfe_normalizado"].apply(
            lambda x: "ENTRADA" if "ENTRADA" in x else ("SAÍDA" if "SAIDA" in x or "SAÍDA" in x else "OUTRO")
        )
        total_entrada = len(analise[analise["tipo_nfe_categoria"] == "ENTRADA"])
        total_saida = len(analise[analise["tipo_nfe_categoria"] == "SAÍDA"])
        valor_entrada = analise.loc[analise["tipo_nfe_categoria"] == "ENTRADA", "valor_nfe"].sum()
        valor_saida = analise.loc[analise["tipo_nfe_categoria"] == "SAÍDA", "valor_nfe"].sum()

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("NFes de Entrada", total_entrada)
        col6.metric("NFes de Saída", total_saida)
        col7.metric("Valor Total Entradas (R$)", f"{valor_entrada:,.2f}")
        col8.metric("Valor Total Saídas (R$)", f"{valor_saida:,.2f}")
        st.markdown("---")

        # --- Gráficos em duas colunas ---
        colD, colE = st.columns(2)
        with colD:
            # --- Gráfico de quantidade por tipo de NFe ---
            tipo_df = analise["tipo_nfe_categoria"].value_counts().reset_index()
            tipo_df.columns = ["Tipo NFe", "Quantidade"]
            fig4 = px.bar(
                tipo_df, 
                x="Tipo NFe", 
                y="Quantidade", 
                color="Tipo NFe", 
                color_discrete_sequence=px.colors.qualitative.Pastel1, 
            )
            fig4.update_layout(
                title= dict(text="Distribuição de NFes por tipo (Entrada x Saída)", x=0.5, xanchor='center'),
                plot_bgcolor="#4F4F4F", 
                paper_bgcolor="#363636"
            )       
            st.plotly_chart(fig4, use_container_width=True)

        with colE:
            # --- Gráfico de valor total por tipo ---
            valor_tipo = analise.groupby("tipo_nfe_categoria")["valor_nfe"].sum().reset_index()
            fig5 = px.pie(
                valor_tipo, 
                names="tipo_nfe_categoria", 
                values="valor_nfe", 
                color_discrete_sequence=px.colors.qualitative.Pastel
            )            
            fig5.update_layout(
                title= dict(text="Participação no valor total (Entrada x Saída)", x=0.5, xanchor='center'), 
                plot_bgcolor="#4F4F4F", 
                paper_bgcolor="#363636"
            )
            st.plotly_chart(fig5, use_container_width=True)

        # --- Evolução temporal por tipo de NFe (linha única abaixo das colunas) ---
        st.subheader("📈 Evolução temporal por tipo das NFe por mês")
        
        evolucao_tipo = (
            analise.groupby([analise["data_emissao"].dt.to_period("M"), "tipo_nfe_categoria"])
            .size()
            .reset_index(name="Quantidade")
        )
        evolucao_tipo["data_emissao"] = evolucao_tipo["data_emissao"].dt.to_timestamp()
        evolucao_tipo.columns = ["data_emissao", "tipo_nfe_categoria", "Quantidade"]
        evolucao_tipo = evolucao_tipo.sort_values("data_emissao")

        fig6 = px.line(
            evolucao_tipo,
            x="data_emissao",
            y="Quantidade",
            color="tipo_nfe_categoria",
            markers=True,
            labels={"data_emissao": "Data Emissão", "Quantidade": "NFes", "tipo_nfe_categoria": "Tipo de Nota"}
        )

        fig6.update_layout(
            title= dict(text="Evolução das NFes por tipo (Entrada x Saída)", x=0.5, xanchor='center'), 
            plot_bgcolor="#4F4F4F", 
            paper_bgcolor="#363636"
        )

        st.plotly_chart(fig6, use_container_width=True)

# ========================================
# --- Menu: RELATÓRIOS DE DIVERGÊNCIAS ---
# ========================================
elif st.session_state["menu"] == "Relatórios de Divergências":

    st.info("#### 🚨&nbsp;&nbsp;Relatório de Divergências e Alertas")

    # --- NFes divergentes ---
    st.subheader("📚 Notas Fiscais identificadas com Divergências")
    
    analise_div = analise[analise["situacao"] == "DIVERGENTE"][["data", "chave", "nro_nfe", "tipo_nfe", "cnpj_cpf", "razao_social", "operacao", "data_emissao", "valor_nfe", "base_icms", "valor_icms", "valor_tributos", "obs", "situacao"]]

    # --- Configuração da tabela analise_div com AgGrid (sem checkbox) ---
    gb_analise = GridOptionsBuilder.from_dataframe(analise_div)
    gb_analise.configure_selection(selection_mode="single", use_checkbox=False)
    gb_analise.configure_default_column(filter=False, suppressMenu=True)
    gb_analise.configure_column("data", hide=True)
    gb_analise.configure_column("obs", hide=True)
    gb_analise.configure_column("situacao", hide=True)
    gb_analise.configure_column("chave", header_name="Chave acesso", width=240, filter=True)
    gb_analise.configure_column("nro_nfe", header_name="Nro. da NFe", width=70, filter=True)
    gb_analise.configure_column("tipo_nfe", header_name="Tipo da NFe", width=55)
    gb_analise.configure_column("cnpj_cpf", header_name="CNPJ/CPF", width=100)
    gb_analise.configure_column("razao_social", header_name="Razão Social", width=170)
    gb_analise.configure_column("operacao", header_name="Natureza de Operação", width=100)
    gb_analise.configure_column("data_emissao", header_name="Data Emissão", width=80, filter=False)
    gb_analise.configure_column("valor_nfe", header_name="Valor NFe", width=70, type=["numericColumn"],valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})",precision=2)
    gb_analise.configure_column("base_icms", header_name="Base ICMS", width=70, type=["numericColumn"],valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})",precision=2)
    gb_analise.configure_column("valor_icms", header_name="Valor ICMS", width=70, type=["numericColumn"],valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})",precision=2)
    gb_analise.configure_column("valor_tributos", header_name="Valor Tributos", width=70, type=["numericColumn"],valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})",precision=2)

    grid_analise = AgGrid(
        analise_div,
        gridOptions=gb_analise.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=False,
        enable_enterprise_modules=False,
        allow_unsafe_jscode=True,
        height=325,
    )

    selected_analise = pd.DataFrame(grid_analise["selected_rows"])

    # --- Exibe observação da linha selecionada na tabela analise_div ---
    if not selected_analise.empty:
        chave_sel = selected_analise.iloc[0]["chave"]
        data_sel = selected_analise.iloc[0]["data"]
        obs_analise = selected_analise.iloc[0]["obs"]
        nroNF_analise = selected_analise.iloc[0]["nro_nfe"]
        razao_analise = selected_analise.iloc[0]["razao_social"]
        cnpj_analise = selected_analise.iloc[0]["cnpj_cpf"]
        status_analise = selected_analise.iloc[0]["situacao"]
        st.markdown(f"### 🧠 (IA) - Análise e observação da Nota Fiscal ( {status_analise} )\n\n##### NFe Nro.:&nbsp;&nbsp;{nroNF_analise}&nbsp;&nbsp;&nbsp;&nbsp;Razão Social.:&nbsp;&nbsp;{razao_analise}&nbsp;&nbsp;&nbsp;&nbsp;CNPJ/CPF.:&nbsp;&nbsp;{cnpj_analise}")
        st.text(format_texto(obs_analise))
    else:
        st.info("Selecione uma linha na tabela acima para ver a análise interpretativa.")

    st.markdown("---")

    # --- Itens com divergência ---
    st.subheader("📦 Itens da Nota Fiscal com Divergências Tributárias")

    # --- Filtra itens pela chave e data selecionadas acima ---
    if not selected_analise.empty:
        itens_filtrados = itens[(itens["chave"] == chave_sel) & (itens["data"] == data_sel)][["data", "chave", "codigo", "descricao", "ncm", "orig_cst", "cfop", "obs"]]

        gb_itens = GridOptionsBuilder.from_dataframe(itens_filtrados)
        gb_itens.configure_selection(selection_mode="single", use_checkbox=False)
        gb_itens.configure_default_column(filter=False, suppressMenu=True)        
        gb_itens.configure_column("data", hide=True)
        gb_itens.configure_column("chave", hide=True)
        gb_itens.configure_column("obs", hide=True)
        gb_itens.configure_column("codigo", header_name="Código do item", width=70)
        gb_itens.configure_column("descricao", header_name="Descrição do item", width=300)
        gb_itens.configure_column("ncm", header_name="Código do NCM", width=70)
        gb_itens.configure_column("orig_cst", header_name="Código do CST", width=70)
        gb_itens.configure_column("cfop", header_name="Código do CFOP", width=70)

        grid_itens = AgGrid(
            itens_filtrados,
            gridOptions=gb_itens.build(),
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            fit_columns_on_grid_load=True,
            enable_enterprise_modules=False,
            allow_unsafe_jscode=True,
            height=325,
        )

        selected_itens = pd.DataFrame(grid_itens["selected_rows"])

        # --- Exibe observação da linha selecionada na tabela itens ---
        if not selected_itens.empty:
            obs_item = selected_itens.iloc[0]["obs"]
            nro_item = selected_itens.iloc[0]["codigo"]
            desc_item = selected_itens.iloc[0]["descricao"]
            st.markdown(f"### 🧠 (IA) - Analise e observação do Item da Nota Fiscal\n\n ##### Item Nro.:&nbsp;&nbsp;{nro_item}&nbsp;&nbsp;&nbsp;&nbsp;Descrição.:&nbsp;&nbsp;{desc_item}")
            st.text(format_texto(obs_item))
        else:
            st.info("Selecione um item na tabela acima para ver a análise interpretativa.")

    # --- Exibe arquivo PDF da NFe (DANFE) ---
    st.markdown("---")
    st.subheader("🔍 Visualização do arquivo da DANFE")

    if not selected_analise.empty:
        nome_arquivo_pdf = f"{data_sel}-NFE-{chave_sel}.pdf"
        caminho_pdf = os.path.join(config.path+"NFe/olds", nome_arquivo_pdf)

        if os.path.exists(caminho_pdf):
            st.success(f"📄 Visualizando o arquivo: `{nome_arquivo_pdf}`")

            with open(caminho_pdf, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")

            pdf_display = f"""
            <iframe 
                src="data:application/pdf;base64,{base64_pdf}" 
                width="100%" height="850" 
                type="application/pdf">
            </iframe>
            """
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Arquivo PDF da NFe não encontrado.")

# =============================
# --- Menu: Detalhes da NFe ---
# =============================
elif st.session_state["menu"] == "Detalhes da NFe":

    st.info("#### 🔍&nbsp;&nbsp;Dados detalhados da Nota Fiscal")

    # --- Grid da tabela "analise" com seleção de linha ---
    st.subheader("📓 Tabela detalhada da NFe")

    gb = GridOptionsBuilder.from_dataframe(notasfiscal)
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gb.configure_default_column(filter=False, suppressMenu=True)
    gb.configure_column("data", hide=True)
    gb.configure_column("origem_dados", hide=True)
    gb.configure_column("dados_adicionais", hide=True)
    gb.configure_column("impostos_adicionais", hide=True)
    
    gb.configure_column("chave", header_name="Chave de acesso", width=150, filter=True)
    gb.configure_column("numero", header_name="Nro. NFe", width=60, filter=True)
    gb.configure_column("tipo_nfe", header_name="Tipo NFe", width=30)
    gb.configure_column("serie", header_name="Série", width=30)
    gb.configure_column("natureza_operacao", header_name="Natureza Operação", width=100)
    gb.configure_column("data_emissao", header_name="Data Emissão", width=60)
    gb.configure_column("data_saida", header_name="Data Saida", width=60)
    gb.configure_column("hora_saida", header_name="Hora Saida", width=60)
    gb.configure_column("valor_nfe", header_name="Valor NFe", width=70, filter=False, type=["numericColumn"],valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2})",precision=2)
    gb.configure_column("valor_produto", header_name="Valor Produto", width=70, filter=False, type=["numericColumn"],valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2})",precision=2)
    gb.configure_column("base_icms", header_name="Base ICMS", width=70, filter=False, type=["numericColumn"],valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2})",precision=2)
    gb.configure_column("valor_icms", header_name="Valor ICMS", width=70, filter=False, type=["numericColumn"],valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2})",precision=2)
    gb.configure_column("valor_tributos", header_name="Valor Tributos", width=70, filter=False, type=["numericColumn"],valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2})",precision=2)

    gridOptions = gb.build()    
    grid_response = AgGrid(
        notasfiscal,
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=False,
        enable_enterprise_modules=False,
        update_mode='MODEL_CHANGED',
        height=325,
    )
    selected_rows = pd.DataFrame(grid_response['selected_rows'])
    st.text("📦 Itens detalhados da nota")
    if not selected_rows.empty:
        chave_sel = selected_rows.iloc[0]['chave']
        data_sel = selected_rows.iloc[0]['data']

        itens_filtrados = produtos[(produtos["chave"] == chave_sel) & (produtos["data"] == data_sel)][["data", "chave", "codigo", "descricao", "ncm", "orig_cst", "cfop", "unidade", "quantidade", "valor_unitario", "valor_total", "valor_icms", "valor_ipi", "aliquota_icms", "aliquota_ipi"]]
        gb_itens = GridOptionsBuilder.from_dataframe(itens_filtrados)
        gb_itens.configure_selection(selection_mode="single", use_checkbox=False)
        gb_itens.configure_default_column(filter=False, suppressMenu=True)        
        gb_itens.configure_column("data", hide=True)
        gb_itens.configure_column("chave", hide=True)
        
        gb_itens.configure_column("codigo", header_name="Código do item", width=90)
        gb_itens.configure_column("descricao", header_name="Descrição do item", width=250)
        gb_itens.configure_column("ncm", header_name="NCM", width=55)
        gb_itens.configure_column("orig_cst", header_name="CST", width=40)
        gb_itens.configure_column("cfop", header_name="CFOP", width=40)
        gb_itens.configure_column("unidade", header_name="Unid.", width=40)
        gb_itens.configure_column("quantidade", header_name="Qde", width=35, filter=False)
        gb_itens.configure_column("valor_unitario", header_name="Valor Unid.", width=60, filter=False, type=["numericColumn"],valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2})",precision=2)
        gb_itens.configure_column("valor_total", header_name="Valor Total", width=60, filter=False, type=["numericColumn"],valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2})",precision=2)
        gb_itens.configure_column("valor_icms", header_name="Valor ICMS", width=50, filter=False, type=["numericColumn"],valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2})",precision=2)
        gb_itens.configure_column("valor_ipi", header_name="Valor IPI", width=50, filter=False, type=["numericColumn"],valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2})",precision=2)
        gb_itens.configure_column("aliquota_icms", header_name="Aliquota ICMS", width=65, filter=False, type=["numericColumn"],valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2})",precision=2)
        gb_itens.configure_column("aliquota_ipi", header_name="Aliquota IPI", width=55, filter=False, type=["numericColumn"],valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2})",precision=2)

        grid_itens = AgGrid(
            itens_filtrados,
            gridOptions=gb_itens.build(),
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            fit_columns_on_grid_load=True,
            enable_enterprise_modules=False,
            allow_unsafe_jscode=True,
            height=210,
        )

    if not selected_rows.empty:
        imposto = selected_rows.iloc[0]['impostos_adicionais'].strip() or ""
        dados = (selected_rows.iloc[0]['dados_adicionais'].strip() or "").replace("|"," » ").replace(";","; ")

        clientes = clientes[(clientes["chave"] == chave_sel) & (clientes["data"] == data_sel)]
        colA, colB = st.columns([0.3, 0.5])  # proporção aproximada de 300px e 900px
        with colA:
            st.markdown(f"#### 🪪 Dados do {clientes.iloc[0]['tipo']} da nota")        
            st.text(f"CNPJ/CPF: {clientes.iloc[0]['cnpj_cpf']} - {clientes.iloc[0]['razao_social']}\nInsc. Estadual.: {clientes.iloc[0]['inscricao_estadual']}  Insc. Municipal.: {clientes.iloc[0]['inscricao_municipal']}  Fone.: {clientes.iloc[0]['telefone']}\n{clientes.iloc[0]['endereco']} - cep: {clientes.iloc[0]['cep']} - {clientes.iloc[0]['bairro']} - {clientes.iloc[0]['municipio']} - {clientes.iloc[0]['uf']}")
            st.markdown(f"#### 🪪 Dados do {clientes.iloc[1]['tipo']} da nota")        
            st.text(f"CNPJ/CPF: {clientes.iloc[1]['cnpj_cpf']} - {clientes.iloc[1]['razao_social']}\nInsc. Estadual.: {clientes.iloc[1]['inscricao_estadual']}  Insc. Municipal.: {clientes.iloc[1]['inscricao_municipal']}  Fone.: {clientes.iloc[1]['telefone']}\n{clientes.iloc[1]['endereco']} - cep: {clientes.iloc[1]['cep']} - {clientes.iloc[1]['bairro']} - {clientes.iloc[1]['municipio']} - {clientes.iloc[1]['uf']}")
            
        with colB:
            st.markdown(f"##### 🧾 Dados adicionais da nota ({selected_rows.iloc[0]['origem_dados']})")        
            if imposto != "":
                imposto = "\n💰 Impostos dicionais:   " + format_valor(imposto)
            if dados != "":
                st.text(format_texto(dados)+imposto)  

        # --- Exibe arquivo PDF da NFe (DANFE) ---
        st.markdown("---")
        st.subheader("🔍 Visualização do arquivo da DANFE")

        if not selected_rows.empty:
            nome_arquivo_pdf = f"{data_sel}-NFE-{chave_sel}.pdf"
            caminho_pdf = os.path.join(config.path+"NFe/olds", nome_arquivo_pdf)

            if os.path.exists(caminho_pdf):
                st.success(f"📄 Visualizando o arquivo: `{nome_arquivo_pdf}`")

                with open(caminho_pdf, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                pdf_display = f"""
                <iframe 
                    src="data:application/pdf;base64,{base64_pdf}" 
                    width="100%" height="850" 
                    type="application/pdf">
                </iframe>"""
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Arquivo PDF da NFe não encontrado.")
    else:
        st.info("Selecione uma linha na tabela acima para visualizar os itens da NFe.")

# ========================================
# --- Menu: Histórico dos arquivos NFe ---
# ========================================
elif st.session_state["menu"] == "Histórico dos arquivos NFe":

    st.info("#### 📜&nbsp;&nbsp;Histórico dos arquivos NFe analisados e processados")

    # --- Gráficos Analíticos do Log ---
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Distribuição dos logs por situação")
        situacao_df = logs["situacao"].value_counts().reset_index()
        situacao_df.columns = ["Situação", "Quantidade"]
        fig_pizza = px.pie(
            situacao_df,
            names="Situação",
            values="Quantidade",
            color_discrete_sequence=px.colors.qualitative.Pastel            
        )
        fig_pizza.update_layout(
            title= dict(text="Proporção de situações dos logs", x=0.5, xanchor='center'),
            plot_bgcolor="#4F4F4F", 
            paper_bgcolor="#363636"
        )
        st.plotly_chart(fig_pizza, use_container_width=True)

    with colB:
        st.subheader("Evolução dos logs ao longo do tempo")
        evolucao = (
            logs.dropna(subset=["data"])
            .groupby([logs["data"].dt.to_period("D"), "situacao"])
            .size()
            .reset_index(name="Quantidade")
        )
        evolucao["data"] = evolucao["data"].dt.to_timestamp()
        fig_bar = px.bar(            
            evolucao,
            x="data",
            y="Quantidade",
            color="situacao",
            barmode="group",
            labels={"data": "Período diário", "Quantidade": "Qtd. Registros", "situacao": "Situação"},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bar.update_layout(
            title= dict(text="Evolução diária dos logs por situação", x=0.5, xanchor='center'),
            plot_bgcolor="#4F4F4F", 
            paper_bgcolor="#363636"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("🗃️ Tabela dos arquivos analizados e processados no sistema")

    # --- Filtros ---
    situacoes_logs = ["Todas"] + sorted(logs["situacao"].unique())
    
    if "filtro_situacao_logs" not in st.session_state:
        st.session_state["filtro_situacao_logs"] = "ERRO"

    filtro_situacao_logs = st.selectbox(
        "Filtrar a situação do log:", 
        situacoes_logs,
        index=situacoes_logs.index(st.session_state["filtro_situacao_logs"])
    )

    st.session_state["filtro_situacao_logs"] = filtro_situacao_logs
    
    if filtro_situacao_logs != "Todas":
        logs_filtro = logs_filtro[logs_filtro["situacao"] == filtro_situacao_logs]

    # --- Tabela de Logs ---
    gb_logs = GridOptionsBuilder.from_dataframe(logs)
    gb_logs.configure_selection(selection_mode="single", use_checkbox=False)
    gb_logs.configure_default_column(filter=False, suppressMenu=True)
    gb_logs.configure_column("data", header_name="Data do processamento", width=100, filter=False)
    gb_logs.configure_column("chave", header_name="Arquivo/Chave", width=200, filter=True)
    gb_logs.configure_column("situacao", header_name="Situação", width=70)
    gb_logs.configure_column("obs", header_name="Observação do arquivo", wrapText=False, autoHeight=False)
    grid_logs = AgGrid(
        logs_filtro,
        gridOptions=gb_logs.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=False,
        allow_unsafe_jscode=True,
        height=325,
    )
    selected_log = pd.DataFrame(grid_logs["selected_rows"])
    if not selected_log.empty:
        data_sel = selected_log.iloc[0]["data"]
        chave_sel = selected_log.iloc[0]["chave"]
        obs_sel = selected_log.iloc[0]["obs"]
        status_sel = selected_log.iloc[0]["situacao"]
        icon = "✅  " if status_sel == "OK" else "❌  "
        st.markdown(f"### ⚠️  Observação do arquivo processado ( {status_sel} ) \n\n##### Data: {data_sel.replace('T',' ')} \n##### Arquivo/Chave: {chave_sel}")
        st.text(icon+format_texto(obs_sel))                
    else:
        st.info("Selecione uma linha na tabela acima para ver os detalhes do log.")

# ==============
# --- Rodapé --- 
# ==============
st.markdown("---")
st.caption("**Desenvolvido em Streamlit + SQLite + IA Tributária**")
st.caption("Os dados são carregados automaticamente do banco `analisenfe.db` (atualização a cada 5 minutos).")
