import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Gestor de Fretes - Peugeot Expert",
    page_icon="🚚",
    layout="centered"
)

st.title("🚚 Gestor e Calculador de Fretes")
st.markdown("---")

# --- SEÇÃO 1: PARÂMETROS E CONFIGURAÇÕES ---
st.subheader("⚙️ 1. Parâmetros da Viagem")

col_config1, col_config2 = st.columns(2)

with col_config1:
    # Piso Mínimo Editável (Ex: R$ 1,80/km)
    taxa_minima_km = st.number_input(
        "Piso Mínimo Exigido por KM (R$):",
        min_value=0.50,
        value=1.80,
        step=0.10,
        format="%.2f",
        help="Valor mínimo por quilômetro que você aceita cobrar na viagem."
    )

with col_config2:
    # Distância Total
    km_total = st.number_input(
        "Distância Total Ida e Volta (KM):",
        min_value=1.0,
        value=1000.0,
        step=10.0
    )

# --- SEÇÃO 2: VALOR DO FRETE E COMBUSTÍVEL ---
st.subheader("💰 2. Ofertado & Custos Estimados")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    valor_frete = st.number_input(
        "Valor Total do Frete (R$):",
        min_value=0.0,
        value=3000.0,
        step=100.0
    )

with col_f2:
    preco_combustivel = st.number_input(
        "Preço do Diesel (R$/L):",
        min_value=1.0,
        value=6.10,
        step=0.05,
        format="%.2f"
    )

with col_f3:
    consumo_veiculo = st.number_input(
        "Consumo Média (KM/L):",
        min_value=1.0,
        value=11.0,
        step=0.5,
        format="%.1f"
    )

pedagio = st.number_input(
    "Estimativa de Pedágios / Outras Despesas (R$):",
    min_value=0.0,
    value=150.0,
    step=10.0
)

st.markdown("---")

# --- SEÇÃO 3: CÁLCULO E EXIBIÇÃO DOS TOTAIS ---
if st.button("📊 Calcular Dados Totais da Viagem", type="primary", use_container_width=True):
    
    # Cálculos operacionais
    litros_necessarios = km_total / consumo_veiculo if consumo_veiculo > 0 else 0
    custo_combustivel = litros_necessarios * preco_combustivel
    custo_total_operacional = custo_combustivel + pedagio
    
    # Lucro e métricas por KM
    lucro_liquido = valor_frete - custo_total_operacional
    valor_km_real = valor_frete / km_total if km_total > 0 else 0
    
    # Regra do Piso Mínimo
    valor_minimo_piso = km_total * taxa_minima_km
    diferenca_piso = valor_frete - valor_minimo_piso

    st.subheader("📈 Resumo da Viagem")

    # Métricas Principais
    col_m1, col_m2, col_m3 = st.columns(3)
    
    col_m1.metric(
        label="Valor Bruto Cobrado",
        value=f"R$ {valor_frete:,.2f}"
    )
    
    col_m2.metric(
        label="Valor Real por KM",
        value=f"R$ {valor_km_real:.2f} / km",
        delta=f"R$ {(valor_km_real - taxa_minima_km):.2f} / km vs Piso"
    )
    
    col_m3.metric(
        label=f"Piso Mínimo (R$ {taxa_minima_km:.2f}/km)",
        value=f"R$ {valor_minimo_piso:,.2f}"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Métricas de Custos e Lucro Líquido
    col_m4, col_m5 = st.columns(2)
    
    col_m4.metric(
        label="Gasto Estimado (Combustível + Pedágio)",
        value=f"R$ {custo_total_operacional:,.2f}",
        delta=f"-{litros_necessarios:.1f} Litros Diesel",
        delta_color="inverse"
    )
    
    col_m5.metric(
        label="Lucro Líquido Estimado",
        value=f"R$ {lucro_liquido:,.2f}"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Análise em Relação ao Piso Mínimo Configurado
    if valor_frete < valor_minimo_piso:
        st.error(
            f"🚫 **Frete Abaixo do Piso Mínimo!**\n\n"
            f"• Para cobrir seu piso de **R$ {taxa_minima_km:.2f}/km**, o valor mínimo deste frete deveria ser **R$ {valor_minimo_piso:,.2f}**.\n"
            f"• Está faltando **R$ {abs(diferenca_piso):,.2f}** para atingir a sua meta de cobrança."
        )
    else:
        st.success(
            f"✅ **Frete Aprovado dentro do Piso!**\n\n"
            f"• Este frete está **R$ {diferenca_piso:,.2f} acima** do piso mínimo exigido de R$ {valor_minimo_piso:,.2f}."
        )
