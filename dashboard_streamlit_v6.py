# =====================================================================================
# DASHBOARD COMERCIAL – FIBERPRO
# Versión FINAL VISUAL DEFINITIVA
# =====================================================================================

import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================================================
# CONFIGURACIÓN GENERAL
# =====================================================================================

st.set_page_config(
    page_title="Dashboard Comercial FiberPro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================================
# ESTILOS GLOBALES
# =====================================================================================

st.markdown("""
<style>
.main { background-color: #f4f6fb; }
h1 { color: #0b5ed7; font-weight: 800; }
h2 { color: #0b5ed7; font-weight: 700; }
h3 { color: #1f2937; font-weight: 700; }

.section-box {
    background: white;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,.08);
    margin-bottom: 22px;
}

.kpi-card {
    background: white;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,.08);
    border-left: 6px solid #0b5ed7;
}

.kpi-title {
    font-size: 0.85rem;
    color: #6b7280;
    font-weight: 600;
}

.kpi-value {
    font-size: 1.6rem;
    font-weight: 800;
    color: #111827;
}

section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e5e7eb;
}

.sidebar-box {
    background: #f9fafb;
    padding: 14px;
    border-radius: 14px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================================================
# HEADER
# =====================================================================================

st.markdown("""
<div class="section-box">
    <h1>📊 Dashboard Comercial – FiberPro</h1>
    <p style="color:#6b7280">
        Análisis de ventas, cobertura geográfica y desempeño comercial
    </p>
</div>
""", unsafe_allow_html=True)

# =====================================================================================
# SIDEBAR – CARGA
# =====================================================================================

st.sidebar.markdown("## 📂 Carga de información")
files = st.sidebar.file_uploader(
    "Sube uno o varios archivos Excel",
    type=["xlsx"],
    accept_multiple_files=True
)

if not files:
    st.info("⬅️ Sube archivos Excel para comenzar")
    st.stop()

# =====================================================================================
# LECTURA
# =====================================================================================

dfs = [pd.read_excel(f) for f in files]
data = pd.concat(dfs, ignore_index=True)

# =====================================================================================
# NORMALIZACIÓN
# =====================================================================================

data.columns = (
    data.columns.str.strip()
    .str.upper()
    .str.replace(" ", "_")
    .str.replace("/", "_")
)

# =====================================================================================
# DETECCIÓN DE COLUMNAS CLAVE
# =====================================================================================

col_fecha = next((c for c in data.columns if "FECHA" in c), None)
col_canal = next((c for c in data.columns if "CANAL" in c), None)
col_servicio = "SERVICIO_SOLICITADO" if "SERVICIO_SOLICITADO" in data.columns else None


# =====================================================================================
# CAST FECHA
# =====================================================================================

if col_fecha:
    data[col_fecha] = pd.to_datetime(data[col_fecha], errors="coerce")

# =====================================================================================
# LIMPIEZA TEXTO
# =====================================================================================

for campo in ["DISTRITO", "VENDEDOR", "GRUPO_DE_COMISION", col_servicio]:
    if campo and campo in data.columns:
        data[campo] = data[campo].astype(str).str.upper().str.strip()

# =====================================================================================
# SIDEBAR – FILTROS
# =====================================================================================

st.sidebar.markdown("## 🎛️ Filtros")
with st.sidebar.container():
    st.markdown('<div class="sidebar-box">', unsafe_allow_html=True)

    if col_fecha:
        fechas = st.date_input(
            "Rango de fechas",
            [data[col_fecha].min(), data[col_fecha].max()]
        )
        data = data[
            (data[col_fecha] >= pd.to_datetime(fechas[0])) &
            (data[col_fecha] <= pd.to_datetime(fechas[1]))
        ]

    grupo_sel = st.multiselect(
        "Grupo de comisión",
        sorted(data["GRUPO_DE_COMISION"].dropna().unique())
    )
    if grupo_sel:
        data = data[data["GRUPO_DE_COMISION"].isin(grupo_sel)]

    vendedor_sel = st.multiselect(
        "Vendedor",
        sorted(data["VENDEDOR"].dropna().unique())
    )
    if vendedor_sel:
        data = data[data["VENDEDOR"].isin(vendedor_sel)]

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================================
# EVOLUCIÓN DE VENTAS POR MES (LÍNEAS)
# =====================================================================================

if col_fecha:
    st.markdown("## 📈 Evolución de Ventas por Mes")

    data["MES"] = data[col_fecha].dt.to_period("M").astype(str)

    ventas_mes = (
        data.groupby("MES")
        .size()
        .reset_index(name="VENTAS")
        .sort_values("MES")
    )

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    fig = px.line(
        ventas_mes,
        x="MES",
        y="VENTAS",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================================
# KPIs
# =====================================================================================

st.markdown("## 🔢 Indicadores Clave")
k1, k2, k3, k4 = st.columns(4)

def kpi(col, title, value):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

kpi(k1, "📈 Total de Ventas", len(data))
kpi(k2, "👥 Vendedores", data["VENDEDOR"].nunique())
kpi(k3, "📍 Distritos", data["DISTRITO"].nunique())
kpi(k4, "📦 Servicios", data[col_servicio].nunique() if col_servicio else 0)

# =====================================================================================
# VENTAS POR DISTRITO – BARRAS
# =====================================================================================

st.markdown("## 📍 Ventas por Distrito")

ventas_dist = (
    data.groupby("DISTRITO")
    .size()
    .reset_index(name="VENTAS")
    .sort_values("VENTAS")
)

st.markdown('<div class="section-box">', unsafe_allow_html=True)
fig = px.bar(
    ventas_dist,
    x="VENTAS",
    y="DISTRITO",
    orientation="h",
    text="VENTAS",
    height=max(420, len(ventas_dist) * 22)
)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================================
# DESEMPEÑO POR GRUPO – BARRAS
# =====================================================================================

st.markdown("## 📈 Desempeño por Tipo de Vendedor")

mapa_grupos = {
    "ASISTENTE DE VENTA": "ASISTENTE",
    "VENDEDOR EXTERNO": "EXTERNO",
    "VENDEDOR INTERNO": "INTERNO",
    "TECNICO": "TECNIC"
}

for titulo, clave in mapa_grupos.items():
    df_g = data[data["GRUPO_DE_COMISION"].str.contains(clave, na=False)]
    if df_g.empty:
        continue

    ventas_v = (
        df_g.groupby("VENDEDOR")
        .size()
        .reset_index(name="VENTAS")
        .sort_values("VENTAS")
    )

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown(f"### {titulo}")
    fig = px.bar(
        ventas_v,
        x="VENTAS",
        y="VENDEDOR",
        orientation="h",
        text="VENTAS",
        height=max(380, len(ventas_v) * 22)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================================
# SERVICIO SOLICITADO – CANTIDAD DE VENTAS (CADA FILA = 1 VENTA)
# =====================================================================================

# =====================================================================================
# SERVICIO SOLICITADO – CANTIDAD DE VENTAS (CADA FILA = 1 VENTA)
# =====================================================================================

if col_servicio:
    st.markdown("## 📦 Ventas por Servicio Solicitado")

    ventas_servicio = (
        data
        .groupby(col_servicio)
        .size()
        .reset_index(name="VENTAS")
        .sort_values("VENTAS", ascending=True)
    )

    st.markdown('<div class="section-box">', unsafe_allow_html=True)

    fig = px.bar(
        ventas_servicio,
        x="VENTAS",
        y=col_servicio,
        orientation="h",
        text="VENTAS",
        height=max(420, len(ventas_servicio) * 26)
    )

    fig.update_layout(
        xaxis_title="Cantidad de Ventas",
        yaxis_title="Servicio Solicitado",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================================
# CANAL DE PEDIDO – CIRCULAR
# =====================================================================================

if col_canal:
    st.markdown("## 🧭 Canal de Pedido")

    canales = (
        data.groupby(col_canal)
        .size()
        .reset_index(name="VENTAS")
    )

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    fig = px.pie(
        canales,
        names=col_canal,
        values="VENTAS",
        hole=0.5
    )
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================================
# GRUPO DE COMISIÓN – CIRCULAR
# =====================================================================================

st.markdown("## 💼 Participación por Grupo de Comisión")

grupo_pie = (
    data.groupby("GRUPO_DE_COMISION")
    .size()
    .reset_index(name="VENTAS")
)

st.markdown('<div class="section-box">', unsafe_allow_html=True)
fig = px.pie(
    grupo_pie,
    names="GRUPO_DE_COMISION",
    values="VENTAS",
    hole=0.5
)
fig.update_traces(textinfo="percent+label")
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================================
# FOOTER
# =====================================================================================

st.markdown("---")
st.caption("FiberPro • Dashboard Comercial • Versión Final Ejecutiva")
