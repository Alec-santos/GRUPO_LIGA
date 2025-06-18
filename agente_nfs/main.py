import csv
import json
import requests
from collections import defaultdict, Counter
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class NotaFiscalChatBot:
    def __init__(self, header_csv_path, items_csv_path, ollama_url="http://localhost:11434"):
        """
        Inicializa o chatbot com os dados das notas fiscais
        
        Args:
            header_csv_path: Caminho para o CSV de cabeçalho das notas
            items_csv_path: Caminho para o CSV de itens das notas
            ollama_url: URL do servidor Ollama (padrão: http://localhost:11434)
        """
        self.ollama_url = ollama_url
        self.data = []
        self.columns = []
        self.destinatario_cols = []
        self.emitente_cols = []
        self.load_data(header_csv_path, items_csv_path)
        
    def load_data(self, header_csv_path, items_csv_path):
        """Carrega e faz merge dos dados das notas fiscais"""
        try:
            print("Carregando dados das notas fiscais...")
            
            # Carrega CSV de cabeçalho
            header_data = {}
            with open(header_csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                header_columns = reader.fieldnames
                for row in reader:
                    chave = row.get('CHAVE_ACESSO')
                    if chave:
                        header_data[chave] = row
            
            print(f"Header: {len(header_data)} registros")
            
            # Carrega CSV de itens e faz o merge
            with open(items_csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                items_columns = reader.fieldnames
                
                for row in reader:
                    chave = row.get('CHAVE_ACESSO')
                    if chave and chave in header_data:
                        # Combina dados do header com itens
                        combined_row = {**header_data[chave], **row}
                        self.data.append(combined_row)
            
            print(f"Items: processados")
            print(f"Dados merged: {len(self.data)} registros")
            
            # Define colunas
            if self.data:
                self.columns = list(self.data[0].keys())
                
                # Identifica colunas de destinatário e emitente
                self.destinatario_cols = [col for col in self.columns if col.endswith('DESTINATARIO')]
                self.emitente_cols = [col for col in self.columns if col.endswith('EMITENTE')]
                
                print(f"Colunas de destinatário: {self.destinatario_cols}")
                print(f"Colunas de emitente: {self.emitente_cols}")
                print(f"Total de colunas: {len(self.columns)}")
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            raise
    
    def call_ollama(self, prompt, model="llama3"):
        """Chama a API do Ollama diretamente"""
        try:
            url = f"{self.ollama_url}/api/generate"
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.ConnectionError:
            return "❌ Erro: Não foi possível conectar ao Ollama. Certifique-se de que está rodando: ollama serve"
        except requests.exceptions.Timeout:
            return "❌ Erro: Timeout na resposta do Ollama. Tente novamente."
        except Exception as e:
            return f"❌ Erro ao chamar Ollama: {e}"
    
    def safe_float(self, value):
        """Converte valor para float de forma segura"""
        if value is None or value == '':
            return 0.0
        try:
            # Remove vírgulas e outros caracteres
            if isinstance(value, str):
                value = value.replace(',', '.').replace(' ', '')
            return float(value)
        except:
            return 0.0
    
    def safe_int(self, value):
        """Converte valor para int de forma segura"""
        if value is None or value == '':
            return 0
        try:
            return int(float(str(value).replace(',', '.')))
        except:
            return 0
    
    def get_data_summary(self):
        """Retorna um resumo dos dados para contexto"""
        summary = {
            "total_registros": len(self.data),
            "campos_nota_fiscal": [
                "NUMERO", "DATA_EMISSAO", "VALOR_NOTA_FISCAL", 
                "DESCRICAO_PRODUTO_SERVICO", "CODIGO_NCM_SH", 
                "NCM_SH_TIPO_PRODUTO", "CFOP", "QUANTIDADE", 
                "UNIDADE", "VALOR_UNITARIO", "VALOR_TOTAL"
            ],
            "campos_cliente": self.destinatario_cols,
            "campos_fornecedor": self.emitente_cols
        }
        return summary
    
    def analyze_query(self, user_query):
        """Analisa a query do usuário e determina o tipo de análise necessária"""
        query_lower = user_query.lower()
        
        analysis_type = "geral"
        target_fields = []
        
        # Identifica se é sobre cliente (destinatário)
        if any(word in query_lower for word in ["cliente", "destinatário", "comprador", "destinatario"]):
            analysis_type = "cliente"
            target_fields = self.destinatario_cols
            
        # Identifica se é sobre fornecedor (emitente)
        elif any(word in query_lower for word in ["fornecedor", "emitente", "vendedor"]):
            analysis_type = "fornecedor"
            target_fields = self.emitente_cols
            
        # Identifica se é sobre notas fiscais
        elif any(word in query_lower for word in ["nota", "fiscal", "produto", "valor", "quantidade"]):
            analysis_type = "nota_fiscal"
            target_fields = [
                "NUMERO", "DATA_EMISSAO", "VALOR_NOTA_FISCAL", 
                "DESCRICAO_PRODUTO_SERVICO", "CODIGO_NCM_SH", 
                "NCM_SH_TIPO_PRODUTO", "CFOP", "QUANTIDADE", 
                "UNIDADE", "VALOR_UNITARIO", "VALOR_TOTAL"
            ]
        
        return analysis_type, target_fields
    
    def group_by_field(self, field_name, value_field, operation="sum", limit=5):
        """Agrupa dados por campo e aplica operação"""
        if field_name not in self.columns or value_field not in self.columns:
            return []
        
        groups = defaultdict(list)
        for row in self.data:
            key = row.get(field_name, 'N/A')
            value = self.safe_float(row.get(value_field, 0))
            groups[key].append(value)
        
        # Aplica operação
        results = {}
        for key, values in groups.items():
            if operation == "sum":
                results[key] = sum(values)
            elif operation == "count":
                results[key] = len(values)
            elif operation == "avg":
                results[key] = sum(values) / len(values) if values else 0
        
        # Ordena e retorna top N
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:limit]
    
    def perform_data_analysis(self, user_query, analysis_type, target_fields):
        """Executa análise dos dados baseada na query do usuário"""
        try:
            query_lower = user_query.lower()
            results = []
            
            # Valor total das notas
            if "total" in query_lower and "valor" in query_lower:
                total_value = 0
                for row in self.data:
                    value = self.safe_float(row.get("VALOR_TOTAL", 0))
                    if value == 0:
                        value = self.safe_float(row.get("VALOR_NOTA_FISCAL", 0))
                    total_value += value
                results.append(f"💰 Valor total das notas fiscais: R$ {total_value:,.2f}")
                
            # Quantidade de notas
            if "quantidade" in query_lower and ("notas" in query_lower or "fiscal" in query_lower):
                unique_numbers = set()
                for row in self.data:
                    numero = row.get("NUMERO", "")
                    if numero:
                        unique_numbers.add(numero)
                results.append(f"📄 Total de notas fiscais únicas: {len(unique_numbers)}")
                
            # Top clientes
            if analysis_type == "cliente" and ("top" in query_lower or "maior" in query_lower):
                if self.destinatario_cols:
                    field = self.destinatario_cols[1]
                    value_field = "VALOR_TOTAL" if "VALOR_TOTAL" in self.columns else "VALOR_NOTA_FISCAL"
                    top_clients = self.group_by_field(field, value_field, "sum", 5)
                    
                    if top_clients:
                        results.append("🏆 Top 5 clientes por valor:")
                        for client, value in top_clients:
                            results.append(f"   • {client}: R$ {value:,.2f}")
                            
            # Top fornecedores
            elif analysis_type == "fornecedor" and ("top" in query_lower or "maior" in query_lower):
                if self.emitente_cols:
                    field = self.emitente_cols[1]
                    value_field = "VALOR_TOTAL" if "VALOR_TOTAL" in self.columns else "VALOR_NOTA_FISCAL"
                    top_suppliers = self.group_by_field(field, value_field, "sum", 5)
                    
                    if top_suppliers:
                        results.append("🏆 Top 5 fornecedores por valor:")
                        for supplier, value in top_suppliers:
                            results.append(f"   • {supplier}: R$ {value:,.2f}")
            
            # Top produtos
            if "produto" in query_lower and ("top" in query_lower or "maior" in query_lower):
                if "DESCRICAO_PRODUTO_SERVICO" in self.columns:
                    value_field = "VALOR_TOTAL" if "VALOR_TOTAL" in self.columns else "VALOR_NOTA_FISCAL"
                    top_products = self.group_by_field("DESCRICAO_PRODUTO_SERVICO", value_field, "sum", 5)
                    
                    if top_products:
                        results.append("🏆 Top 5 produtos por valor:")
                        for product, value in top_products:
                            product_name = str(product)[:50] + "..." if len(str(product)) > 50 else str(product)
                            results.append(f"   • {product_name}: R$ {value:,.2f}")
            
            # Se não encontrou análises específicas, retorna estatísticas gerais
            if not results:
                return self.get_general_stats()
                
            return "\n".join(results)
            
        except Exception as e:
            return f"❌ Erro ao analisar dados: {e}"
    
    def get_general_stats(self):
        """Retorna estatísticas gerais dos dados"""
        stats = []
        
        # Valor total
        total_value = 0
        for row in self.data:
            value = self.safe_float(row.get("VALOR_TOTAL", 0))
            if value == 0:
                value = self.safe_float(row.get("VALOR_NOTA_FISCAL", 0))
            total_value += value
        stats.append(f"💰 Valor total: R$ {total_value:,.2f}")
        
        # Total de notas únicas
        unique_numbers = set()
        for row in self.data:
            numero = row.get("NUMERO", "")
            if numero:
                unique_numbers.add(numero)
        stats.append(f"📄 Total de notas únicas: {len(unique_numbers)}")
        
        # Total de registros
        stats.append(f"📋 Total de registros: {len(self.data)}")
        
        # Total de itens
        total_quantity = 0
        for row in self.data:
            qty = self.safe_float(row.get("QUANTIDADE", 0))
            total_quantity += qty
        if total_quantity > 0:
            stats.append(f"📦 Total de itens: {total_quantity:,.0f}")
        
        # Período das notas (se possível determinar)
        dates = []
        for row in self.data:
            date_str = row.get("DATA_EMISSAO", "")
            if date_str:
                try:
                    # Tenta diferentes formatos de data
                    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"]:
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            dates.append(date_obj)
                            break
                        except:
                            continue
                except:
                    pass
        
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            stats.append(f"📅 Período: {min_date.strftime('%d/%m/%Y')} até {max_date.strftime('%d/%m/%Y')}")
        
        return "\n".join(stats)
    
    def create_prompt(self, user_query, data_analysis):
        """Cria o prompt para enviar ao Ollama"""
        context = json.dumps(self.get_data_summary(), indent=2, ensure_ascii=False)
        
        prompt = f"""Você é um assistente especializado em análise de notas fiscais brasileiras.

CONTEXTO DOS DADOS:
{context}

PERGUNTA DO USUÁRIO: {user_query}

ANÁLISE DOS DADOS REALIZADA:
{data_analysis}

INSTRUÇÕES:
- Responda de forma clara e objetiva baseado na análise dos dados
- Use linguagem profissional mas acessível
- Se apropriado, sugira outras análises que podem ser úteis
- Formate valores monetários em reais (R$)
- Se houver dados específicos, destaque os pontos principais
- Mantenha a resposta concisa e informativa

RESPOSTA:"""
        
        return prompt
    
    def chat(self, user_query):
        """Processa a pergunta do usuário e retorna a resposta"""
        try:
            print(f"\n🔍 Analisando: {user_query}")
            
            # Analisa a query do usuário
            analysis_type, target_fields = self.analyze_query(user_query)
            
            # Executa análise dos dados
            data_analysis = self.perform_data_analysis(user_query, analysis_type, target_fields)
            
            # Para perguntas simples, retorna análise direta
            simple_keywords = ["estatísticas", "resumo", "total", "quantidade", "valor"]
            if any(keyword in user_query.lower() for keyword in simple_keywords):
                return data_analysis
            
            # Para perguntas mais complexas, usa Ollama
            print("🤖 Gerando resposta com IA...")
            prompt = self.create_prompt(user_query, data_analysis)
            response = self.call_ollama(prompt)
            
            # Se Ollama falhou, retorna análise dos dados
            if "❌" in response:
                return data_analysis
            
            return response.strip() if response else data_analysis
            
        except Exception as e:
            return f"❌ Erro ao processar pergunta: {e}"
    
    def test_ollama_connection(self):
        """Testa a conexão com o Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]
                print(f"✅ Ollama conectado! Modelos disponíveis: {model_names}")
                return True
            else:
                print("❌ Ollama não está respondendo corretamente")
                return False
        except:
            print("❌ Não foi possível conectar ao Ollama")
            print("💡 Certifique-se de que o Ollama está rodando: ollama serve")
            return False
    
    def interactive_chat(self):
        """Interface interativa de chat"""
        print("=== Sistema de Chat - Análise de Notas Fiscais ===")
        print("Testando conexão com Ollama...")
        
        ollama_available = self.test_ollama_connection()
        if not ollama_available:
            print("⚠️  Ollama não disponível - funcionará apenas com análises básicas")
        
        print("\nComandos disponíveis:")
        print("• 'sair' - Encerrar o chat")
        print("• 'ajuda' - Ver exemplos de perguntas")
        print("• 'stats' - Ver estatísticas gerais")
        print("• 'colunas' - Ver colunas disponíveis")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n👤 Você: ").strip()
                
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    print("👋 Encerrando chat. Até logo!")
                    break
                    
                elif user_input.lower() in ['ajuda', 'help']:
                    self.show_help()
                    continue
                    
                elif user_input.lower() in ['stats', 'estatisticas']:
                    stats = self.get_general_stats()
                    print(f"\n📊 Estatísticas Gerais:\n{stats}")
                    continue
                    
                elif user_input.lower() in ['colunas', 'columns']:
                    print(f"\n📋 Colunas disponíveis ({len(self.columns)}):")
                    for i, col in enumerate(self.columns, 1):
                        print(f"{i:2d}. {col}")
                    continue
                    
                elif not user_input:
                    print("❌ Por favor, digite uma pergunta.")
                    continue
                
                # Processa a pergunta
                response = self.chat(user_input)
                print(f"\n🤖 Assistente:\n{response}")
                
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
            "Mostre os produtos mais vendidos",
            "Estatísticas gerais dos dados",
            "Qual cliente comprou mais?",
            "Quem são os maiores fornecedores?",
            "Resumo dos dados"
        ]
        
        print("\n📋 Exemplos de perguntas:")
        for i, example in enumerate(examples, 1):
            print(f"{i:2d}. {example}")
        
        print("\n💡 Dicas:")
        print("• Use 'cliente' para análises de destinatários")
        print("• Use 'fornecedor' para análises de emitentes")
        print("• Use 'produto' para análises de itens")
        print("• Use 'top' ou 'maior' para rankings")

# Função principal para inicializar o sistema
def main():
    """Função principal para executar o sistema"""
    
    # Caminhos dos arquivos CSV
    header_csv = "data/202401_NF_header.csv"
    items_csv = "data/202401_NF_items.csv"
    
    try:
        # Inicializa o chatbot
        print("🚀 Inicializando Sistema de Chat para Notas Fiscais...")
        chatbot = NotaFiscalChatBot(header_csv, items_csv)
        
        # Inicia o chat interativo
        chatbot.interactive_chat()
        
    except FileNotFoundError as e:
        print(f"❌ Arquivo não encontrado: {e}")
        print("Certifique-se de que os arquivos CSV estão no diretório correto:")
        print(f"• {header_csv}")
        print(f"• {items_csv}")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar sistema: {e}")

if __name__ == "__main__":
    main()
