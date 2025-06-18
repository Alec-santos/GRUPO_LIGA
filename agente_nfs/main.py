import pandas as pd
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
import warnings

warnings.filterwarnings("ignore")


class NotaFiscalChatBot:
    def __init__(self, header_csv_path, items_csv_path, model_name="llama3"):
        """
        Inicializa o chatbot com os dados das notas fiscais

        Args:
            header_csv_path: Caminho para o CSV de cabeçalho das notas
            items_csv_path: Caminho para o CSV de itens das notas
            model_name: Nome do modelo Ollama (padrão: llama3)
        """
        self.llm = Ollama(model=model_name)
        self.df_merged = None
        self.load_data(header_csv_path, items_csv_path)
        self.setup_prompts()

    def load_data(self, header_csv_path, items_csv_path):
        """Carrega e faz merge dos dados das notas fiscais"""
        try:
            print("Carregando dados das notas fiscais...")

            # Carrega os CSVs
            df_header = pd.read_csv(header_csv_path)
            df_items = pd.read_csv(items_csv_path)

            print(f"\nHeader: {len(df_header)} registros")
            print(f"Items: {len(df_items)} registros")

            # Faz o merge pelos campos CHAVE_ACESSO
            self.df_merged = pd.merge(
                df_header, df_items, on="CHAVE_ACESSO", how="inner"
            )

            print(f"Dados merged: {len(self.df_merged)} registros")

            # Identifica colunas de destinatário e emitente
            self.destinatario_cols = [
                col for col in self.df_merged.columns if col.endswith("DESTINATARIO")
            ]
            self.emitente_cols = [
                col for col in self.df_merged.columns if col.endswith("EMITENTE")
            ]

            print(f"Colunas de destinatário: {self.destinatario_cols}")
            print(f"Colunas de emitente: {self.emitente_cols}")

        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            raise

    def get_data_summary(self):
        """Retorna um resumo dos dados para contexto"""
        summary = {
            "total_registros": len(self.df_merged),
            "colunas_disponíveis": list(self.df_merged.columns),
            "campos_nota_fiscal": [
                "NUMERO",
                "DATA_EMISSAO",
                "VALOR_NOTA_FISCAL",
                "DESCRICAO_PRODUTO_SERVICO",
                "CODIGO_NCM_SH",
                "NCM_SH_TIPO_PRODUTO",
                "CFOP",
                "QUANTIDADE",
                "UNIDADE",
                "VALOR_UNITARIO",
                "VALOR_TOTAL",
            ],
            "campos_cliente": self.destinatario_cols,
            "campos_fornecedor": self.emitente_cols,
        }
        return summary

    def analyze_query(self, user_query):
        """Analisa a query do usuário e determina o tipo de análise necessária"""
        query_lower = user_query.lower()

        analysis_type = "geral"
        target_fields = []

        # Identifica se é sobre cliente (destinatário)
        if any(
            word in query_lower for word in ["cliente", "destinatário", "comprador"]
        ):
            analysis_type = "cliente"
            target_fields = self.destinatario_cols

        # Identifica se é sobre fornecedor (emitente)
        elif any(
            word in query_lower for word in ["fornecedor", "emitente", "vendedor"]
        ):
            analysis_type = "fornecedor"
            target_fields = self.emitente_cols

        # Identifica se é sobre notas fiscais
        elif any(
            word in query_lower
            for word in ["nota", "fiscal", "produto", "valor", "quantidade"]
        ):
            analysis_type = "nota_fiscal"
            target_fields = [
                "NUMERO",
                "DATA_EMISSAO",
                "VALOR_NOTA_FISCAL",
                "DESCRICAO_PRODUTO_SERVICO",
                "CODIGO_NCM_SH",
                "NCM_SH_TIPO_PRODUTO",
                "CFOP",
                "QUANTIDADE",
                "UNIDADE",
                "VALOR_UNITARIO",
                "VALOR_TOTAL",
            ]

        return analysis_type, target_fields

    def perform_data_analysis(self, user_query, analysis_type, target_fields):
        """Executa análise dos dados baseada na query do usuário"""
        try:
            query_lower = user_query.lower()

            # Análises básicas comuns
            if "total" in query_lower and "valor" in query_lower:
                if "VALOR_TOTAL" in self.df_merged.columns:
                    total_value = self.df_merged["VALOR_TOTAL"].sum()
                    return f"Valor total das notas fiscais: R$ {total_value:,.2f}"

            elif "quantidade" in query_lower and "notas" in query_lower:
                total_notas = self.df_merged["NUMERO"].nunique()
                return f"Total de notas fiscais: {total_notas}"

            elif "top" in query_lower or "maior" in query_lower:
                if analysis_type == "cliente":
                    # Top clientes por valor
                    if (
                        self.destinatario_cols
                        and "VALOR_TOTAL" in self.df_merged.columns
                    ):
                        top_clients = (
                            self.df_merged.groupby(self.destinatario_cols[0])[
                                "VALOR_TOTAL"
                            ]
                            .sum()
                            .sort_values(ascending=False)
                            .head(5)
                        )
                        result = "Top 5 clientes por valor:\n"
                        for client, value in top_clients.items():
                            result += f"- {client}: R$ {value:,.2f}\n"
                        return result

                elif analysis_type == "fornecedor":
                    # Top fornecedores por valor
                    if self.emitente_cols and "VALOR_TOTAL" in self.df_merged.columns:
                        top_suppliers = (
                            self.df_merged.groupby(self.emitente_cols[0])["VALOR_TOTAL"]
                            .sum()
                            .sort_values(ascending=False)
                            .head(5)
                        )
                        result = "Top 5 fornecedores por valor:\n"
                        for supplier, value in top_suppliers.items():
                            result += f"- {supplier}: R$ {value:,.2f}\n"
                        return result

            # Se não encontrou análise específica, retorna estatísticas gerais
            return self.get_general_stats()

        except Exception as e:
            return f"Erro ao analisar dados: {e}"

    def get_general_stats(self):
        """Retorna estatísticas gerais dos dados"""
        stats = []

        if "VALOR_TOTAL" in self.df_merged.columns:
            total_value = self.df_merged["VALOR_TOTAL"].sum()
            stats.append(f"Valor total: R$ {total_value:,.2f}")

        if "NUMERO" in self.df_merged.columns:
            total_notas = self.df_merged["NUMERO"].nunique()
            stats.append(f"Total de notas: {total_notas}")

        if "QUANTIDADE" in self.df_merged.columns:
            total_items = self.df_merged["QUANTIDADE"].sum()
            stats.append(f"Total de itens: {total_items:,.0f}")

        return "\n".join(stats) if stats else "Dados carregados com sucesso!"

    def setup_prompts(self):
        """Configura os templates de prompt para o LLM"""
        self.analysis_prompt = PromptTemplate(
            input_variables=["user_query", "data_analysis", "context"],
            template="""
            Você é um assistente especializado em análise de notas fiscais brasileiras.
            
            Contexto dos dados:
            {context}
            
            Pergunta do usuário: {user_query}
            
            Análise dos dados realizada:
            {data_analysis}
            
            Com base na análise dos dados, forneça uma resposta clara e objetiva para o usuário.
            Formate valores monetários em reais (R$).
            Se necessário, sugira outras análises que podem ser úteis.
            
            Resposta:
            """,
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.analysis_prompt)

    def chat(self, user_query):
        """Processa a pergunta do usuário e retorna a resposta"""
        try:
            print(f"\n🤖 Processando: {user_query}")

            # Analisa a query do usuário
            analysis_type, target_fields = self.analyze_query(user_query)
            print(f"Tipo de análise: {analysis_type}")

            # Executa análise dos dados
            data_analysis = self.perform_data_analysis(
                user_query, analysis_type, target_fields
            )

            # Prepara contexto
            context = json.dumps(self.get_data_summary(), indent=2, ensure_ascii=False)

            # Gera resposta com LLM
            response = self.chain.run(
                user_query=user_query, data_analysis=data_analysis, context=context
            )

            return response.strip()

        except Exception as e:
            return f"Erro ao processar pergunta: {e}"

    def interactive_chat(self):
        """Interface interativa de chat"""
        print("\n=== Sistema de Chat - Análise de Notas Fiscais ===")
        print("\nDigite 'sair' para encerrar o chat")
        print("Digite 'ajuda' para ver exemplos de perguntas")
        print("=" * 50)

        while True:
            try:
                user_input = input("\n👤 Você: ").strip()

                if user_input.lower() in ["sair", "exit", "quit"]:
                    print("👋 Encerrando chat. Até logo!")
                    break

                elif user_input.lower() in ["ajuda", "help"]:
                    self.show_help()
                    continue

                elif not user_input:
                    print("❌ Por favor, digite uma pergunta.")
                    continue

                # Processa a pergunta
                response = self.chat(user_input)
                print(f"\n🤖 Assistente: {response}")

            except KeyboardInterrupt:
                print("\n👋 Encerrando chat. Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")

    def show_help(self):
        """Mostra exemplos de perguntas"""
        examples = [
            "Qual o valor total das notas fiscais?",
            "Quantas notas fiscais temos?",
            "Quais são os top 5 clientes por valor?",
            "Quais são os top 5 fornecedores por valor?",
            "Mostre estatísticas gerais dos dados",
        ]

        print("\n📋 Exemplos de perguntas:")
        for i, example in enumerate(examples, 1):
            print(f"{i}. {example}")


# Função principal para inicializar o sistema
def main():
    """Função principal para executar o sistema"""

    # Caminhos dos arquivos CSV
    header_csv = "data/202401_NF_header.csv"
    items_csv = "data/202401_NF_items.csv"

    try:
        # Inicializa o chatbot
        chatbot = NotaFiscalChatBot(header_csv, items_csv)

        # Inicia o chat interativo
        chatbot.interactive_chat()

    except FileNotFoundError as e:
        print(f"❌ Arquivo não encontrado: {e}")
        print("Certifique-se de que os arquivos CSV estão no diretório correto:")
        print(f"- {header_csv}")
        print(f"- {items_csv}")

    except Exception as e:
        print(f"❌ Erro ao inicializar sistema: {e}")


if __name__ == "__main__":
    main()
