import streamlit as st
import numpy as np
from itertools import combinations

st.set_page_config(page_title="Bibi's AHP", page_icon="", layout="wide")
st.title("Método AHP")

# --- INICIALIZANDO A MEMÓRIA DO APP ---
if 'etapa_2_liberada' not in st.session_state:
    st.session_state.etapa_2_liberada = False

# 1. Definição da Quantidade
n = st.number_input("Insira o número de critérios:", min_value=0, max_value=15, value=0)

if n <= 1:
    st.session_state.etapa_2_liberada = False

if n > 1:
    # --- ETAPA 1: ENTRADA DE NOMES ---
    st.subheader("Insira os critérios:")
    nomes = []
    
    cols = st.columns(n)
    for i in range(n):
        nome = cols[i].text_input(f"C{i+1}", value=f"Critério {i+1}", key=f"nome_{i}")
        nomes.append(nome)

    if st.button("Confirmar Critérios"):
        st.session_state.etapa_2_liberada = True

    # --- ETAPA 2: COMPARAÇÃO ---
    if st.session_state.etapa_2_liberada:
        st.divider()
        st.subheader("Comparação de importância")
        st.info("Deslize para a esquerda para o 1º critério ou para a direita para o 2º.")

        pares = list(combinations(range(n), 2))
        escolhas = {}

        for i, j in pares:
            st.write(f"### {nomes[i]} vs {nomes[j]}")
            valor = st.select_slider(
                "Qual critério é mais importante?",
                options=list(range(-8, 9)),
                value=0,
                format_func=lambda x: f"{abs(x)+1}" if x != 0 else "Igual",
                key=f"comp_{i}_{j}"
            )
            
            if valor >= 0:
                escolhas[(i, j)] = float(valor + 1)
            else:
                escolhas[(i, j)] = 1.0 / float(abs(valor) + 1)

        # --- ETAPA 3: A MATEMÁTICA DO AHP ---
        if st.button("Calcular Resultados"):
            matriz = np.ones((n, n))
            for (i, j), v in escolhas.items():
                matriz[i, j] = v
                matriz[j, i] = 1 / v
            
            st.divider()
            st.subheader("Resultados")
            
            autovalores, autovetores = np.linalg.eig(matriz)
            
            autovalores_reais = np.real(autovalores)
            indice_max = np.argmax(autovalores_reais)
            lambda_max = autovalores_reais[indice_max]
            
            vetor_principal = np.real(autovetores[:, indice_max])
            pesos = vetor_principal / np.sum(vetor_principal)
            
            st.write("### Pesos dos Critérios:")
            for i in range(n):
                porcentagem = pesos[i] * 100
                st.write(f"**{nomes[i]}**: {porcentagem:.2f}%")
                st.progress(float(pesos[i]))

            ci = (lambda_max - n) / (n - 1)
            
            tabela_ri = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12, 
                         6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
            ri = tabela_ri[n]
            
            if n <= 2:
                cr = 0.0
            else:
                cr = ci / ri
                
            st.write("### Análise de Consistência")
            col1, col2, col3 = st.columns(3)
            col1.metric("Autovalor Máximo (λ)", f"{lambda_max:.4f}")
            col2.metric("Índice de Consistência (CI)", f"{ci:.4f}")
            col3.metric("Razão de Consistência (CR)", f"{cr * 100:.2f}%")
            
            if cr <= 0.10:
                st.success("A matriz é consistente.")
            else:
                st.error("A matriz é inconsistente (CR > 10%).")

            # --- ETAPA 4: EXPORTAÇÃO PARA CSV ---
            st.divider()
            st.subheader("4. Exportar Dados")
            
            # 1. Montamos o texto no formato CSV (Critério, Peso)
            # O \n serve para "pular linha" no arquivo final
            csv_conteudo = "Criterio,Peso_Percentual\n"
            for i in range(n):
                csv_conteudo += f"{nomes[i]},{pesos[i]*100:.2f}%\n"
            
            # 2. Criamos o botão de download mágico do Streamlit
            st.download_button(
                label="📥 Baixar Pesos em CSV",
                data=csv_conteudo,
                file_name="resultados_ahp.csv",
                mime="text/csv"
            )