import streamlit as st
import pandas as pd
import json
from datetime import datetime, date
import plotly.express as px
from financial_transactions import FinancialRecord
import locale
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import random
from datetime import datetime, timedelta
from decimal import Decimal
import altair as alt
from pages.report_por_categoria import report_por_categoria

# Configure o locale para português do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Function to load transactions from JSON file
def load_transactions():
    try:
        with open('transactions.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Function to save transactions to JSON file
def save_transactions(transacoes):
    with open('transactions.json', 'w') as file:
        json.dump(transacoes, file, indent=2)

# Function to format currency
def format_currency(value):
    if value < 0:
        return f"-R$ {abs(value):,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    else:
        return f"R$ {value:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

# Load transactions
transacoes = load_transactions()

# Adicione esta função no início do arquivo, junto com as outras funções auxiliares
def zerar_transacoes():
    st.session_state.financial_record = FinancialRecord()
    save_transactions([])  # Salva uma lista vazia no arquivo JSON
    st.success("Todas as transações foram removidas.")

# Adicione esta função no início do arquivo, junto com as outras funções auxiliares
def update_category_options():
    if st.session_state.transaction_type == "Despesa":
        st.session_state.categories = ["Comida", "Supermercado", "Veículo", "Lazer"]
    else:  # Receita
        st.session_state.categories = ["Salário", "Venda", "Bônus", "Caixa 2", "Propina"]

    if transaction_type == "Despesa":
        return ["Comida", "Supermercado", "Veículo", "Lazer"]
    else:  # Receita
        return ["Salário", "Venda", "Bônus", "Investimentos", "Outros"]

# Configuração da página
st.set_page_config(page_title="Gerenciador Financeiro", layout="wide", initial_sidebar_state="expanded")

if 'financial_record' not in st.session_state:
    st.session_state.financial_record = FinancialRecord()

# Sidebar com título ajustado
st.sidebar.markdown('<p class="sidebar-title">Gerenciador Financeiro</p>', unsafe_allow_html=True)

# Definição das categorias
CATEGORIES = ['Alimentação', 'Transporte', 'Moradia', 'Saúde', 'Educação', 'Lazer', 'Outros Despesas']

# Opções do menu
menu_options = ["Dashboard", "Adicionar Transação", "Listar Transações", "Report por Categorias", "Zerar Banco de Dados", "Gerar Transações de Exemplo"]

# Função para zerar o banco de dados
def zerar_banco_dados():
    if 'financial_record' in st.session_state:
        st.session_state.financial_record = FinancialRecord()

    # Limpar o arquivo JSON
    with open('transactions.json', 'w') as file:
        file.write('[]')

    st.success("Todas as transações foram removidas e o banco de dados foi zerado.")
    st.rerun()  # Força um rerun para atualizar a interface

# Função para gerar transações de exemplo
def generate_sample_transactions():
    descriptions = {
        'Comida': ['Restaurante', 'Lanchonete', 'Padaria', 'Feira'],
        'Supermercado': ['Compras mensais', 'Compras semanais', 'Itens de limpeza', 'Produtos de higiene'],
        'Veículo': ['Combustível', 'Manutenção', 'Seguro', 'Estacionamento'],
        'Lazer': ['Cinema', 'Teatro', 'Viagem', 'Parque de diversões'],
        'Salário': ['Salário mensal', 'Bônus anual', 'Hora extra'],
        'Investimentos': ['Dividendos', 'Juros de poupança', 'Venda de ações'],
        'Bônus': ['Participação nos lucros', 'Prêmio por desempenho'],
        'Propina': ['Pagamento irregular', 'Suborno'],
        'Caixa 2': ['Venda não declarada', 'Serviço sem nota'],
        'Outros Despesas': ['Assinatura de streaming', 'Doação'],
        'Outros Receitas':['Venda de item usado', 'Freelance', 'Presente em dinheiro'],
    }

    receita_categories = ['Salário', 'Investimentos', 'Bônus', 'Propina', 'Caixa 2', 'Outros Receitas']

    transactions = []
    start_date = datetime(2024, 1, 1)

    for month in range(1, 13):  # Para cada mês de 2024
        for category in descriptions.keys():
            for _ in range(2):  # 3 transações por categoria por mês
                date = start_date + timedelta(days=random.randint(0, 30))
                description = random.choice(descriptions[category])
                amount = Decimal(random.uniform(50.00, 5000.00)).quantize(Decimal('0.01'))

                if category in receita_categories:
                    transaction_type = 'Receita'
                else:
                    transaction_type = 'Despesa'

                transactions.append({
                    'data': date,
                    'categoria': category,
                    'descricao': description,
                    'valor': amount,
                    'tipo': transaction_type
                })

        start_date = start_date.replace(month=month+1) if month < 12 else start_date

    return transactions

# Código principal do Streamlit
def main():
    # Criar botões para cada opção de menu
    for option in menu_options:
        if st.sidebar.button(option, key=option):
            st.session_state.current_page = option

    # Inicializar a página atual se não estiver definida
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"

    # Conteúdo principal baseado na página selecionada
    if st.session_state.current_page == "Dashboard":
        st.title("Dashboard Financeiro")

        col1, col2 = st.columns(2)

        with col1:
            with st.container():
                st.subheader("Resumo Financeiro")

                balance = st.session_state.financial_record.get_balance()
                balance_color = "green" if balance >= 0 else "red"
                st.markdown(f"<h4 style='color: {balance_color};'>Saldo Atual: {format_currency(balance)}</h4>", unsafe_allow_html=True)

                report = st.session_state.financial_record.report_by_category()
                if not isinstance(report, str):
                    total_expenses = -abs(report['Total de Despesas'])
                    total_income = report['Total de Receitas']  # Definindo total_income aqui
                    st.markdown(f"<h4 style='color: red;'>Total de Despesas: {format_currency(total_expenses)}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<h4 style='color: green;'>Total de Receitas: {format_currency(total_income)}</h4>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            with st.container():
                st.subheader("Distribuição de Receitas e Despesas")

                if not isinstance(report, str):
                    # Criar dados para o gráfico de pizza
                    pie_data = pd.DataFrame({
                        'Tipo': ['Receitas', 'Despesas'],
                        'Valor': [abs(total_income), abs(total_expenses)]
                    })

                    # Criar o gráfico de pizza
                    fig = px.pie(pie_data, values='Valor', names='Tipo',
                                 color='Tipo',
                                 color_discrete_map={'Receitas': 'green', 'Despesas': 'red'})

                    # Atualizar o layout para melhor visualização
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=True,
                        margin=dict(l=20, r=20, t=30, b=20),
                        height=300
                    )

                    # Exibir o gráfico
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Não há dados suficientes para gerar o gráfico.")

                st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.current_page == "Adicionar Transação":
        st.title("Adicionar Transação")

        # Tipo de transação
        transaction_type = st.selectbox("Tipo de Transação", ["Receita", "Despesa"])

        # Data da transação
        date = st.date_input(
            "Data da Transação",
            format="DD/MM/YYYY"
        )

        # Descrição
        description = st.text_input("Descrição")

        # Categoria
        if transaction_type == "Despesa":
            category = st.selectbox("Categorias", ['Alimentação', 'Transporte', 'Moradia', 'Saúde', 'Educação', 'Lazer', 'Outros Despesas'])
        else:  # Receita
            category = st.selectbox("Categorias", ["Salário", "Investimentos", "Bônus", "Propina", "Caixa 2", "Outros Receitas"])

        # Valor
        amount = st.number_input("Valor", min_value=0.01, format="%.2f")

        if st.button("Adicionar Transação"):
            if 'financial_record' not in st.session_state:
                st.session_state.financial_record = FinancialRecord()

            # Converter a data para o formato esperado pela classe FinancialRecord
            date_formatted = date.strftime("%Y-%m-%d")

            st.session_state.financial_record.add_transaction(
                date_formatted,
                description,
                category,
                amount,
                transaction_type
            )
            st.success("Transação adicionada com sucesso!")

    elif st.session_state.current_page == "Listar Transações":
        def list_transactions():
            st.title("Listar Transações")

            if 'financial_record' in st.session_state and st.session_state.financial_record.transactions:
                # Criar um DataFrame com as transações
                df = pd.DataFrame([
                    {
                        'date': t.date,
                        'descricao': t.description,
                        'categoria': t.category,
                        'tipo': t.transaction_type,
                        'valor': t.amount if t.transaction_type == 'Receita' else -abs(t.amount)
                    } for t in st.session_state.financial_record.transactions
                ])

                # Converter a coluna 'date' para datetime
                df['date'] = pd.to_datetime(df['date'])

                # Ordenar o DataFrame pela data, da mais recente para a mais antiga
                df = df.sort_values('date', ascending=False)

                # Formatar a data para o padrão brasileiro
                df['data_formatada'] = df['date'].dt.strftime('%d/%m/%Y')

                # Reordenar as colunas
                df = df[['data_formatada', 'descricao', 'categoria', 'tipo', 'valor']]

                # Renomear as colunas para melhor apresentação
                df.columns = ['Data', 'Descrição', 'Categoria', 'Tipo', 'Valor']

                # Formatar a coluna de valor como moeda brasileira
                df['Valor'] = df['Valor'].apply(lambda x: f"R$ {x:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'))

                # Função para colorir o texto da coluna Tipo
                def color_tipo(val):
                    color = 'green' if val == 'Receita' else 'red'
                    return f'color: {color}'

                # Aplicar o estilo à tabela
                styled_df = df.style.applymap(color_tipo, subset=['Tipo'])

                # Exibir o DataFrame estilizado
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma transação registrada.")

        # Verificar se estamos na página correta antes de chamar a função
        if st.session_state.current_page == "Listar Transações":
            list_transactions()

    elif st.session_state.current_page == "Report por Categorias":
        # Chama a função report_por_categoria do arquivo pages/report_por_categoria.py
        report_por_categoria()

    elif st.session_state.current_page == "Zerar Banco de Dados":
        st.title("Zerar Banco de Dados")
        st.error("Atenção: Esta ação irá remover todas as transações do banco de dados. Esta ação não pode ser desfeita.")
        if st.button("Zerar Banco de Dados"):
            zerar_banco_dados()
    elif st.session_state.current_page == "Gerar Transações de Exemplo":
        st.title("Gerar Transações de Exemplo")
        if st.button("Gerar Transações"):
            sample_transactions = generate_sample_transactions()
            for transaction in sample_transactions:
                st.session_state.financial_record.add_transaction(
                    transaction['data'],
                    transaction['descricao'],
                    transaction['categoria'],
                    transaction['valor'],
                    transaction['tipo']
                )
            st.success(f"{len(sample_transactions)} transações de exemplo foram geradas e adicionadas ao banco de dados.")

if __name__ == "__main__":
    main()