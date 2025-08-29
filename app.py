import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------
# Cargar dataset
# ----------------------------------------------------


@st.cache_data
def load_data():
    df = pd.read_csv("vgsales.csv")
    # limpiar datos: quitar nulos y mantener años válidos
    df = df.dropna(subset=["Year"])
    df["Year"] = df["Year"].astype(int)
    return df


df = load_data()

# ----------------------------------------------------
# Configuración de la página
# ----------------------------------------------------
st.set_page_config(
    page_title="📊 Dashboard de Videojuegos",
    layout="wide"
)

st.title("🎮 Dashboard de Ventas de Videojuegos")
st.markdown("Exploración interactiva de datos de ventas de videojuegos desde el año 2000 (dataset Kaggle - vgchartz.com)")

# ----------------------------------------------------
# Filtros en la barra lateral
# ----------------------------------------------------
st.sidebar.header("🔍 Filtros")

year_range = st.sidebar.slider(
    "Selecciona rango de años:",
    min_value=int(df["Year"].min()),
    max_value=int(df["Year"].max()),
    value=(2000, 2015)
)

platforms = st.sidebar.multiselect(
    "Selecciona plataformas:",
    options=sorted(df["Platform"].unique()),
    default=[]
)

publishers = st.sidebar.multiselect(
    "Selecciona publishers:",
    options=sorted(df["Publisher"].dropna().unique()),
    default=[]
)

# aplicar filtros
df_filtered = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

if platforms:
    df_filtered = df_filtered[df_filtered["Platform"].isin(platforms)]

if publishers:
    df_filtered = df_filtered[df_filtered["Publisher"].isin(publishers)]

st.sidebar.markdown("---")
st.sidebar.write(f"🎯 Juegos filtrados: **{len(df_filtered)}**")

# ----------------------------------------------------
# KPIs principales
# ----------------------------------------------------
total_sales = df_filtered["Global_Sales"].sum()
top_game = df_filtered.loc[df_filtered["Global_Sales"].idxmax()]["Name"]
top_platform = df_filtered.groupby("Platform")["Global_Sales"].sum().idxmax()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Ventas Globales (millones)", f"{total_sales:,.0f}")
col2.metric("🏆 Juego más vendido", top_game)
col3.metric("🎮 Plataforma líder", top_platform)

# ----------------------------------------------------
# Visualizaciones
# ----------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Evolución temporal", "🎮 Ventas por consola", "🌍 Comparativa regional", "🏢 Publishers"])

with tab1:
    st.subheader("Evolución de ventas globales en el tiempo")
    ventas_por_anio = df_filtered.groupby(
        "Year")["Global_Sales"].sum().reset_index()
    fig1 = px.line(ventas_por_anio, x="Year", y="Global_Sales", markers=True,
                   title="Ventas globales por año")
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.subheader("Ventas totales por plataforma")
    ventas_por_plataforma = df_filtered.groupby(
        "Platform")["Global_Sales"].sum().reset_index()
    fig2 = px.bar(ventas_por_plataforma.sort_values("Global_Sales", ascending=False),
                  x="Platform", y="Global_Sales",
                  title="Ventas globales por plataforma")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("Distribución de ventas por región")
    regiones = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
    ventas_por_region = df_filtered[regiones].sum().reset_index()
    ventas_por_region.columns = ["Region", "Sales"]

    fig3 = px.pie(ventas_por_region, names="Region", values="Sales",
                  title="Porcentaje de ventas por región")
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    st.subheader("Top publishers por ventas globales")
    top_publishers = df_filtered.groupby(
        "Publisher")["Global_Sales"].sum().reset_index()
    top_publishers = top_publishers.sort_values(
        "Global_Sales", ascending=False).head(15)

    fig4 = px.bar(top_publishers, x="Publisher", y="Global_Sales",
                  title="Top 15 publishers")
    st.plotly_chart(fig4, use_container_width=True)

# ----------------------------------------------------
# Tabla interactiva
# ----------------------------------------------------
st.subheader("📋 Juegos en el dataset filtrado")
st.dataframe(df_filtered[["Name", "Platform", "Year", "Genre", "Publisher",
             "Global_Sales"]].sort_values("Global_Sales", ascending=False).head(50))
