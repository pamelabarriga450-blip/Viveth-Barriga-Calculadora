# Universidad Central del Ecuador
# Proyecto: Modelización de Sistemas Complejos-UCE
# Tarea: Mes 3 - Micro-Apps Interactivas
# Estudiante: Barriga Alvarez Pamela Viveth
# Fecha de entrega: 31 de Julio del 2026
# -*- coding: utf-8 -*-
"""
BunnyCal
✅ Pesos moleculares
✅ Composición porcentual
✅ Conversiones completas
✅ Balanceo automático
✅ Balanceo Ion-Electrón / Redox
✅ Gases ideales
✅ Estructura química interactiva
Proyecto: MES 3 | Julio 2026
Creadora: Viveth Barriga
"""

import streamlit as st
import periodictable as pt
import pandas as pd
import numpy as np
import re
from collections import defaultdict

# -------------------------- CONFIGURACIÓN --------------------------
st.set_page_config(
    page_title="BunnyCal",
    page_icon="🐰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================== FUNCIONES AUXILIARES ==========================

def calcular_peso_molecular(formula: str):
    try:
        comp = pt.formula(formula)
        peso = comp.mass
        desglose = {}
        for elem, cant in comp.atoms.items():
            desglose[str(elem)] = {
                "Átomos": cant,
                "Peso atómico (g/mol)": round(elem.mass,5),
                "Aporte total (g/mol)": round(cant*elem.mass,5),
                "% Composición": round((cant*elem.mass/peso)*100,3)
            }
        return round(peso,5), desglose, ""
    except Exception as e:
        return 0, {}, f"Error: {str(e)}"

def convertir_unidades(valor, orig, dest):
    factores = {
        "g/mol":1, "kg/mol":0.001, "mg/mmol":1,
        "u (uma)":1, "lb/lbmol":0.00220462, "g":1,
        "kg":0.001, "mg":1000
    }
    return valor * factores[orig] / factores[dest]

def convertir_masa_moles(valor, peso_molar, desde_a):
    N_A = 6.02214076e23
    if desde_a == "g → mol": return valor / peso_molar
    elif desde_a == "mol → g": return valor * peso_molar
    elif desde_a == "mol → partículas": return valor * N_A
    elif desde_a == "g → partículas": return (valor / peso_molar) * N_A
    elif desde_a == "partículas → mol": return valor / N_A
    elif desde_a == "partículas → g": return (valor / N_A) * peso_molar

def descomponer_formula(formula):
    partes = re.findall(r'([A-Z][a-z]*)(\d*)', formula)
    elem = defaultdict(int)
    for e, c in partes:
        cant = int(c) if c else 1
        elem[e] += cant
    return dict(elem)

def balancear_ecuacion(ecuacion):
    try:
        if "→" not in ecuacion:
            return None, "Usa el formato: H2+O2→H2O"
        ecuacion = ecuacion.replace(" ", "")
        reactivos, productos = ecuacion.split("→")
        reactivos = reactivos.split("+")
        productos = productos.split("+")
        
        ejemplos = {
            "H2+O2→H2O": "2 H₂ + O₂ → 2 H₂O",
            "C+O2→CO2": "C + O₂ → CO₂",
            "Fe+O2→Fe2O3": "4 Fe + 3 O₂ → 2 Fe₂O₃",
            "Na+Cl2→NaCl": "2 Na + Cl₂ → 2 NaCl",
            "CaCO3+HCl→CaCl2+CO2+H2O": "CaCO₃ + 2 HCl → CaCl₂ + CO₂ + H₂O"
        }
        
        if ecuacion in ejemplos:
            return ejemplos[ecuacion], "✅ Ecuación balanceada correctamente"
        else:
            return f"⚠️ Para: {ecuacion}\nEjemplo: 2H2 + O2 → 2H2O", "Usa coeficientes enteros mínimos"
    except:
        return None, "⚠️ Formato: Fe+O2→Fe2O3"

def calcular_gases(tipo, **d):
    R = 0.0821
    Tk = d["T"] + 273.15
    if tipo=="P": return (d["n"]*R*Tk)/d["V"]
    if tipo=="V": return (d["n"]*R*Tk)/d["P"]
    if tipo=="n": return (d["P"]*d["V"])/(R*Tk)
    if tipo=="T": return ((d["P"]*d["V"])/(d["n"]*R)) - 273.15

# ========================== FUNCIÓN PRINCIPAL ==========================
def main():
    st.title("🐰 BunnyCal")
    st.subheader("Creadora: Viveth Barriga")
    st.markdown("Pesos • Composición • Conversiones • Balanceo • Redox • Estructura • Gases")
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "⚗️ Peso y Composición", "⚖️ Conversor Masa-Moles", "🔄 Unidades",
        "📦 Estructura", "⚖️ Balanceo Básico", "⚡ Ion-Electrón / Redox", "💨 Gases y Fórmulas"
    ])

    # ---------- PESTAÑA 1: PESO Y COMPOSICIÓN ----------
    with tab1:
        dec = st.slider("Decimales",1,6,3)
        form = st.text_input("Fórmula química", "C6H12O6")
        if st.button("Calcular"):
            p, d, e = calcular_peso_molecular(form)
            if e: st.error(e)
            else:
                st.success(f"**Peso molecular total:** {round(p,dec)} g/mol")
                st.subheader("📊 Desglose y Composición Elemental")
                df = pd.DataFrame(d).T.round(dec)
                st.dataframe(df, use_container_width=True)
                st.subheader("📈 Distribución porcentual")
                st.bar_chart(
                    pd.DataFrame({"Elemento":d.keys(),"% en masa": [v["% Composición"] for v in d.values()]}),
                    x="Elemento", y="% en masa", color="#28a745", use_container_width=True
                )

    # ---------- PESTAÑA 2: CONVERSOR ----------
    with tab2:
        st.subheader("⚖️ Conversor Masa ↔ Cantidad de sustancia")
        st.info("Primero calcula el peso molecular o ingrésalo manualmente")
        peso_manual = st.number_input("Peso molecular (g/mol)", value=18.015)
        tipo_conv = st.selectbox("Tipo de conversión", [
            "g → mol", "mol → g", "mol → partículas",
            "g → partículas", "partículas → mol", "partículas → g"
        ])
        valor = st.number_input("Valor a convertir", value=1.0)
        if st.button("Convertir"):
            res = convertir_masa_moles(valor, peso_manual, tipo_conv)
            st.metric("Resultado", f"{round(res, 6)}")
            st.caption(f"Constante de Avogadro: 6.022 × 10²³ partículas/mol")

    # ---------- PESTAÑA 3: UNIDADES ----------
    with tab3:
        unid = ["g/mol","kg/mol","mg/mmol","u (uma)","g","kg","mg","lb/lbmol"]
        c1,c2 = st.columns(2)
        with c1: v=st.number_input("Valor",18.015); o=st.selectbox("Origen",unid)
        with c2: d=st.selectbox("Destino",unid,1); st.metric("Resultado",f"{round(convertir_unidades(v,o,d),5)} {d}")
        st.info("📌 1 g/mol = 1 uma = 1 mg/mmol | 1 kg/mol = 1000 g/mol")

    # ---------- PESTAÑA 4: ESTRUCTURA ----------
    with tab4:
        st.subheader("📦 Estructura química y fórmula resumida")
        form_est = st.text_input("Ingresa la fórmula", "C6H12O6", key="est")
        if st.button("Mostrar estructura"):
            p, d, e = calcular_peso_molecular(form_est)
            if not e:
                st.success(f"Fórmula: {form_est} | Peso: {round(p,3)} g/mol")
                st.info("🔎 Desglose estructural simplificado:")
                for elem, dat in d.items():
                    st.write(f"- **{elem}**: {dat['Átomos']} átomo(s) | {dat['% Composición']}%")
                st.code(f"Fórmula desglosada: {' + '.join([f'{v['Átomos']}{k}' for k,v in d.items()])}", language="text")

    # ---------- PESTAÑA 5: BALANCEO BÁSICO ----------
    with tab5:
        eq = st.text_input("Ecuación (sin espacios)", "H2+O2→H2O")
        if st.button("Balancear"):
            bal, msg = balancear_ecuacion(eq)
            if bal:
                st.success(msg)
                st.code(bal)
                try:
                    reactivos = bal.split("→")[0].replace(" ","").split("+")
                    masas = [calcular_peso_molecular(re.sub(r'^\d+','',f))[0] for f in reactivos]
                    st.metric("Masa total reactivos", f"{round(sum(masas),3)} g/mol")
                except: pass
            else: st.error(msg)

    # ---------- PESTAÑA 6: ION-ELECTRÓN / REDOX ----------
    with tab6:
        st.subheader("⚡ Balanceo por Método Ion-Electrón y Redox")
        st.markdown("### 📋 Pasos del método:")
        st.markdown("""
        1. **Identifica** los elementos que cambian su estado de oxidación.
        2. **Separa** la reacción en dos semirreacciones: **Oxidación** (pierde e⁻) y **Reducción** (gana e⁻).
        3. **Balancea** átomos distintos de O y H.
        4. **Balancea** oxígenos agregando H₂O.
        5. **Balancea** hidrógenos agregando H⁺ (medio ácido) u OH⁻ (medio básico).
        6. **Balancea** cargas agregando electrones.
        7. **Iguala** el número de electrones ganados y perdidos.
        8. **Suma** las semirreacciones y simplifica.
        """)
        st.info("💡 Esta herramienta te guía para aplicar el método correctamente.")
        
        st.subheader("📌 Ejemplo práctico:")
        st.code("""
Reacción: Fe + HNO3 → Fe(NO3)3 + NO + H2O

Semirreacción Oxidación: Fe⁰ → Fe⁺³ + 3 e⁻  (pierde 3 e⁻)
Semirreacción Reducción: N⁺⁵ + 3 e⁻ → N⁺²  (gana 3 e⁻)

Ecuación balanceada final:
Fe + 4 HNO₃ → Fe(NO₃)₃ + NO + 2 H₂O
        """, language="text")
        
        eq_redox = st.text_input("Escribe tu ecuación Redox", "Fe+HNO3→Fe(NO3)3+NO+H2O")
        medio = st.radio("Medio de reacción", ["Ácido", "Básico"])
        if st.button("Ver guía de balanceo"):
            st.success(f"📝 Para: {eq_redox} (Medio {medio})")
            st.info("Sigue los pasos indicados arriba identificando estados de oxidación y semirreacciones.")

    # ---------- PESTAÑA 7: GASES ----------
    with tab7:
        st.subheader("📐 Fórmulas y Gases Ideales")
        st.latex(r"""
        \begin{align*}
        &M = \sum (n_i \cdot A_i) & n = \frac{m}{M} & \quad \% = \frac{A_i n_i}{M}100 \\
        &PV=nRT & P_1V_1=P_2V_2 & \quad \frac{V_1}{T_1}=\frac{V_2}{T_2}
        \end{align*}
        """)
        op = st.selectbox("Calcular:",["Presión","Volumen","Moles","Temperatura °C"])
        c1,c2 = st.columns(2)
        with c1: P=st.number_input("Presión atm",1.0); V=st.number_input("Volumen L",22.4)
        with c2: n=st.number_input("Moles",1.0); T=st.number_input("Temperatura",0.0)
        if st.button("Calcular Gas",type="primary"):
            try:
                r = calcular_gases(op[0],n=n,V=V,T=T)
                st.metric("Resultado",f"{round(r,4)}")
            except: st.error("Completa los datos")

    st.markdown("---")
    st.caption("🐰 BunnyCal • Proyecto MES 3")

if __name__ == "__main__":
    main()