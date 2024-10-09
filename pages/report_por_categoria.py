import streamlit as st
import pandas as pd
import plotly.express as px

def report_por_categoria():
    st.title("Report por Categoria")

    if 'financial_record' in st.session_state and st.session_state.financial_record.transactions:
        # Preparar dados para o gráfico
        df = pd.DataFrame([
            {
                'categoria': t.category,
                'valor': abs(t.amount),
                'tipo': t.transaction_type
            } for t in st.session_state.financial_record.transactions
        ])

        # Agrupar por categoria e tipo, somando os valores
        df_grouped = df.groupby(['categoria', 'tipo'])['valor'].sum().reset_index()

        # Criar o gráfico
        fig = px.bar(df_grouped, x='categoria', y='valor', color='tipo', barmode='group',
                     labels={'valor': 'Valor Total', 'categoria': 'Categoria', 'tipo': 'Tipo'},
                     color_discrete_map={'Receita': 'green', 'Despesa': 'red'})

        # Atualizar o layout para centralizar
        fig.update_layout(
            autosize=False,
            width=800,
            height=500,
            margin=dict(l=50, r=50, b=100, t=100, pad=4)
        )

        # Exibir o gráfico centralizado
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma transação registrada.")

if __name__ == "__main__":
    report_por_categoria()