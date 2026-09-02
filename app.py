import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestor de Fretes - Peugeot Expert", page_icon="🚐", layout="wide")

st.markdown("""
<style>
    .main-header {
        font-size: 24px;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 14px;
        color: #4B5563;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🚐 Gestor de Fretes & Roteirizador (Peugeot Expert)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Controle com Custo x 3 automático, múltiplos complementos, verificação de piso por KM e simulador de cargas.</div>', unsafe_allow_html=True)

# Sidebar - Dados da Expert, Margem e Piso Mínimo por KM
st.sidebar.header("⚙️ Configurações do Veículo & Piso")
peso_max = st.sidebar.number_input("Peso Máximo Útil (kg)", value=1500.0, step=50.0)
comp_disp = st.sidebar.number_input("Comprimento Útil Baú (m)", value=2.80, step=0.1)
larg_disp = st.sidebar.number_input("Largura Útil Baú (m)", value=1.63, step=0.05)
alt_disp = st.sidebar.number_input("Altura Útil Baú (m)", value=1.39, step=0.05)
custo_km_estimado = st.sidebar.number_input("Custo Operacional (R$/km)", value=1.80, step=0.1)

# CAMPO DO PISO MÍNIMO AJUSTÁVEL POR KM
piso_minimo_km = st.sidebar.number_input(
    "Piso Mínimo Exigido (R$/km)", 
    value=1.80, 
    step=0.10, 
    format="%.2f",
    help="Valor mínimo por quilômetro rodado que você aceita cobrar na viagem."
)

margem_kg_personalizada = st.sidebar.number_input("Valor Base p/ Margem (R$/kg)", value=2.00, step=0.10)

# Cubagem total do baú em metros cúbicos
cubagem_max_m3 = comp_disp * larg_disp * alt_disp

tab1, tab2 = st.tabs(["🗺️ Viagem & Complementos", "⚖️ Simulador de Múltiplas Cargas"])

with tab1:
    st.subheader("1. Carga Principal (Dedicada)")
    col1, col2 = st.columns(2)
    with col1:
        km_principal = st.number_input("Km Total da Rota Principal", value=0.0, step=10.0, key="km_prin")
    with col2:
        valor_principal = st.number_input("Valor Frete Principal (R$)", value=0.0, step=50.0, key="val_prin")

    custo_viagem_manual = st.number_input("Custo Base da Viagem (R$)", value=1000.0, step=50.0, help="O programa multiplica por 3 para definir a meta ideal.")

    st.markdown("##### Dimensões e Peso da Carga Principal:")
    cp1, cp2, cp3, cp4 = st.columns(4)
    with cp1:
        p_peso = st.number_input("Peso Principal (kg)", value=600.0, step=50.0, key="p_peso")
    with cp2:
        p_comp = st.number_input("Comp. Principal (m)", value=1.0, step=0.1, key="p_comp")
    with cp3:
        p_larg = st.number_input("Largura Principal (m)", value=1.0, step=0.1, key="p_larg")
    with cp4:
        p_alt = st.number_input("Altura Principal (m)", value=1.0, step=0.1, key="p_alt")

    volume_principal = p_comp * p_larg * p_alt

    cabe_principal = (p_comp <= comp_disp) and (p_larg <= larg_disp) and (p_alt <= alt_disp) and (p_peso <= peso_max)
    if not cabe_principal:
        st.error("⚠️ Atenção: Carga principal excede o limite do baú!")
    else:
        st.success("✅ Carga principal cabe no baú.")

    st.markdown("---")
    st.subheader("2. Adicionar Complementos")
    
    if 'lista_complementos' not in st.session_state:
        st.session_state.lista_complementos = []

    c_km_extra = st.number_input("Km Extra / Desvio de Rota (km)", value=0.0, step=5.0, key="input_km_extra")
    c_valor_fechado = st.number_input("Valor Combinado do Complemento (R$)", value=0.0, step=50.0, key="input_valor")
    
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        c_peso = st.number_input("Peso do Complemento (kg)", value=44.0, step=1.0, key="input_peso")
    with sc2:
        c_comp = st.number_input("Comprimento (m)", value=0.6, step=0.1, key="input_comp")
    with sc3:
        c_larg = st.number_input("Largura (m)", value=0.6, step=0.1, key="input_larg")
    
    c_alt = st.number_input("Altura (m)", value=1.0, step=0.1, key="input_alt")

    f_temp = custo_viagem_manual * 3.0
    v_m3_temp = f_temp / cubagem_max_m3
    vol_temp = c_comp * c_larg * c_alt
    sug_p = c_peso * margem_kg_personalizada
    sug_m = vol_temp * v_m3_temp
    sug_final = max(sug_p, sug_m)
    
    st.info(f"💡 Sugestão de valor calculada para este item: **R$ {sug_final:,.2f}** (Vol: {vol_temp:.2f} m³)")

    if st.button("➕ Adicionar Este Complemento à Lista", type="secondary"):
        st.session_state.lista_complementos.append({
            "km_extra": c_km_extra,
            "valor": c_valor_fechado,
            "peso": c_peso,
            "comprimento": c_comp,
            "largura": c_larg,
            "altura": c_alt,
            "volume": vol_temp
        })
        st.success("Complemento adicionado com sucesso!")
        st.rerun()

    if st.session_state.lista_complementos:
        st.markdown("#### 📋 Complementos Cadastrados:")
        indices_remover = []
        for idx, item in enumerate(st.session_state.lista_complementos):
            col_v, col_info, col_del = st.columns([2, 3, 1])
            with col_v:
                novo_val = st.number_input(f"Valor Item {idx+1} (R$)", value=float(item['valor']), step=50.0, key=f"edit_val_{idx}")
                st.session_state.lista_complementos[idx]['valor'] = novo_val
            with col_info:
                st.markdown(f"<br>**Peso:** {item['peso']} kg | **Vol:** {item['volume']:.2f} m³<br>*Desvio:* +{item['km_extra']} km", unsafe_allow_html=True)
            with col_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Remover", key=f"del_{idx}"):
                    indices_remover.append(idx)
        
        if indices_remover:
            for i in sorted(indices_remover, reverse=True):
                st.session_state.lista_complementos.pop(i)
            st.rerun()

    st.markdown("---")
    
    executar_calculo = st.button("🧮 Calcular Dados Totais da Viagem", type="primary")

    if executar_calculo:
        val_prin_atual = st.session_state.get('val_prin', valor_principal)
        km_prin_atual = st.session_state.get('km_prin', km_principal)

        total_km_extra = sum(item['km_extra'] for item in st.session_state.lista_complementos)
        km_total_rodado = km_prin_atual + total_km_extra
        
        total_valor_comps = sum(item['valor'] for item in st.session_state.lista_complementos)
        faturamento_bruto_total = val_prin_atual + total_valor_comps
        
        total_peso_comp = sum(item['peso'] for item in st.session_state.lista_complementos)
        total_vol_comp = sum(item['volume'] for item in st.session_state.lista_complementos)
        
        peso_geral = p_peso + total_peso_comp
        volume_geral = volume_principal + total_vol_comp
        
        peso_restante = peso_max - peso_geral
        volume_restante = cubagem_max_m3 - volume_geral
        
        custo_total_ajustado = custo_viagem_manual + (total_km_extra * custo_km_estimado)
        faturamento_ideal_calc = custo_total_ajustado * 3.0
        
        receita_por_km = faturamento_bruto_total / km_total_rodado if km_total_rodado > 0 else 0

        # CÁLCULOS DO PISO MÍNIMO POR KM
        valor_minimo_piso_total = km_total_rodado * piso_minimo_km
        diferenca_piso = faturamento_bruto_total - valor_minimo_piso_total

        st.subheader("💰 Resumo Financeiro & Espaço Restante no Baú")
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Km Total Rodado", f"{km_total_rodado:.1f} km", f"+{total_km_extra} km desvios")
        with m2:
            st.metric("Faturamento Bruto", f"R$ {faturamento_bruto_total:,.2f}", f"Peso total: {peso_geral} kg")
        with m3:
            st.metric(
                "Receita por Km", 
                f"R$ {receita_por_km:.2f} / km",
                delta=f"R$ {(receita_por_km - piso_minimo_km):.2f} vs Piso"
            )
        with m4:
            st.metric("Custo Total Ajustado", f"R$ {custo_total_ajustado:,.2f}")

        st.markdown("#### 📦 Capacidade Restante Disponível no Baú")
        r1, r2 = st.columns(2)
        with r1:
            st.info(f"⚖️ **Peso Restante Livre:** {peso_restante:.1f} kg *(de {peso_max} kg)*")
        with r2:
            st.info(f"📐 **Volume Restante Livre:** {volume_restante:.2f} m³ *(de {cubagem_max_m3:.2f} m³)*")

        # ANÁLISE DO PISO MÍNIMO DE COBRANÇA
        st.markdown(f"#### 🛑 Análise de Piso Mínimo (R$ {piso_minimo_km:.2f} / km)")
        if faturamento_bruto_total < valor_minimo_piso_total:
            st.error(
                f"⚠️ **Frete Abaixo do Piso Mínimo!**\n\n"
                f"• Para **{km_total_rodado:.1f} km** rodados a R$ {piso_minimo_km:.2f}/km, o valor mínimo do frete deveria ser **R$ {valor_minimo_piso_total:,.2f}**.\n"
                f"• Falta **R$ {abs(diferenca_piso):,.2f}** para atingir esse piso."
            )
        else:
            st.success(
                f"✅ **Frete Aprovado pelo Piso Mínimo!**\n\n"
                f"• O valor mínimo recomendado para {km_total_rodado:.1f} km é **R$ {valor_minimo_piso_total:,.2f}**.\n"
                f"• Seu frete está **R$ {diferenca_piso:,.2f} acima** do piso (Média obtida: **R$ {receita_por_km:.2f}/km**)."
            )

        st.markdown("#### 🎯 Alvo da Viagem (Custo x 3)")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.info(f"💡 **Faturamento Ideal (Custo x 3):** R$ {faturamento_ideal_calc:,.2f}")
        with col_m2:
            quanto_falta_vezes_tres = faturamento_ideal_calc - faturamento_bruto_total
            if quanto_falta_vezes_tres > 0:
                st.warning(f"⚠️ Para atingir a meta de **Custo x 3** (R$ {faturamento_ideal_calc:,.2f}), falta conseguir mais **R$ {quanto_falta_vezes_tres:,.2f}** em complementos.")
            else:
                st.success(f"🎉 Meta de Custo x 3 batida com sucesso!")

with tab2:
    st.subheader("⚖️ Simulador de Múltiplas Cargas no Baú")
    st.write("Adicione caixas ou volumes um a um para simular a lotação completa da Peugeot Expert. O sistema mostrará o acumulado e o valor sugerido para cobrança.")

    if 'simulador_itens' not in st.session_state:
        st.session_state.simulador_itens = []

    sim_peso = st.number_input("Peso da Caixa (kg)", value=50.0, step=10.0, key="sim_peso_val")
    sim_comp = st.number_input("Comprimento (m)", value=0.8, step=0.1, key="sim_comp_val")
    sim_larg = st.number_input("Largura (m)", value=0.6, step=0.1, key="sim_larg_val")
    sim_alt = st.number_input("Altura (m)", value=0.5, step=0.1, key="sim_alt_val")

    if st.button("➕ Adicionar Caixa ao Simulador", type="secondary"):
        vol_calc = sim_comp * sim_larg * sim_alt
        st.session_state.simulador_itens.append({
            "peso": sim_peso,
            "comprimento": sim_comp,
            "largura": sim_larg,
            "altura": sim_alt,
            "volume": vol_calc
        })
        st.success("Caixa adicionada ao simulador!")
        st.rerun()

    if st.session_state.simulador_itens:
        st.markdown("#### 📦 Caixas Adicionadas na Simulação:")
        remover_sim = []
        for i, item in enumerate(st.session_state.simulador_itens):
            c_a, c_b = st.columns([4, 1])
            with c_a:
                st.markdown(f"**Caixa {i+1}:** {item['peso']} kg | Dimensões: {item['comprimento']}m x {item['largura']}m x {item['altura']}m (Volume: {item['volume']:.2f} m³)")
            with c_b:
                if st.button("Excluir", key=f"del_sim_{i}"):
                    remover_sim.append(i)
        
        if remover_sim:
            for idx_r in sorted(remover_sim, reverse=True):
                st.session_state.simulador_itens.pop(idx_r)
            st.rerun()

        if st.button("🗑️ Limpar Simulador"):
            st.session_state.simulador_itens = []
            st.rerun()

        st.markdown("---")
        
        total_peso_sim = sum(item['peso'] for item in st.session_state.simulador_itens)
        total_vol_sim = sum(item['volume'] for item in st.session_state.simulador_itens)
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("Peso Acumulado", f"{total_peso_sim:.1f} kg", f"Limite: {peso_max} kg")
        with col_res2:
            st.metric("Volume Acumulado", f"{total_vol_sim:.2f} m³", f"Limite: {cubagem_max_m3:.2f} m³")

        # CÁLCULO E EXIBIÇÃO DO VALOR SUGERIDO LOGO ABAIXO DOS TOTAIS
        faturamento_ideal_sim = custo_viagem_manual * 3.0
        v_por_m3_sim = faturamento_ideal_sim / cubagem_max_m3
        
        sugestao_peso_total = total_peso_sim * margem_kg_personalizada
        sugestao_vol_total = total_vol_sim * v_por_m3_sim
        valor_sugerido_simulador = max(sugestao_peso_total, sugestao_vol_total)

        st.markdown("---")
        st.success(f"💵 **Valor Sugerido para Cobrar por este Conjunto de Cargas:** R$ {valor_sugerido_simulador:,.2f}")

        # VERIFICAÇÕES DE ALERTA DE COMPATIBILIDADE LOGO APÓS O VALOR SUGERIDO
        tem_erro_dimensao = False
        for i, item in enumerate(st.session_state.simulador_itens):
            if item['comprimento'] > comp_disp or item['largura'] > larg_disp or item['altura'] > alt_disp:
                st.error(f"🚨 **Atenção:** A **Caixa {i+1}** possui dimensões individuais incompatíveis com o baú da Expert ({comp_disp}m x {larg_disp}m x {alt_disp}m).")
                tem_erro_dimensao = True

        if total_peso_sim > peso_max:
            st.error(f"🚨 **Alerta de Excesso de Peso:** O peso total acumulado ({total_peso_sim:.1f} kg) ultrapassa a capacidade máxima útil da van ({peso_max} kg)!")
        
        if total_vol_sim > cubagem_max_m3:
            st.error(f"🚨 **Alerta de Excesso de Cubagem:** O volume total acumulado ({total_vol_sim:.2f} m³) ultrapassa o volume útil do baú ({cubagem_max_m3:.2f} m³)!")

        if not tem_erro_dimensao and total_peso_sim <= peso_max and total_vol_sim <= cubagem_max_m3:
            st.success("🎉 **Carga perfeitamente compatível!** Todos os itens cabem no espaço e peso suportados pela Peugeot Expert.")
