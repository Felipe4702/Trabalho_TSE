
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components


RAIZ = Path(__file__).resolve().parent
DADOS = RAIZ / "dados" / "processados"

NOMES = {
    13: "Lula",
    22: "Flavio Bolsonaro",
}

CORES = {
    "Lula": "#dc2626",
    "Flavio Bolsonaro": "#2563eb",
}

st.set_page_config(
    page_title="Eleicoes 2026 - Divinopolis",
    page_icon="🗳️",
    layout="wide",
)


@st.cache_data
def carregar_dados():
    votos = pd.read_csv(
        DADOS / "votos_divinopolis_2026.csv",
        sep=";",
        encoding="utf-8-sig",
    )
    secoes = pd.read_csv(
        DADOS / "resumo_secoes_divinopolis_2026.csv",
        sep=";",
        encoding="utf-8-sig",
    )
    return votos, secoes


def formatar_numero(numero):
    return f"{numero:,.0f}".replace(",", ".")


def tabela_candidatos(dados):
    validos = dados[dados["NR_VOTAVEL"].between(10, 94)]
    tabela = (
        validos.groupby(["NR_VOTAVEL", "NM_VOTAVEL"], as_index=False)
        ["QT_VOTOS"].sum()
    )
    total = tabela["QT_VOTOS"].sum()

    tabela["Percentual"] = tabela["QT_VOTOS"] / total * 100
    tabela["Candidato"] = tabela.apply(
        lambda r: NOMES.get(
            int(r["NR_VOTAVEL"]), r["NM_VOTAVEL"]
        ),
        axis=1,
    )
    return tabela.sort_values("QT_VOTOS", ascending=False)


votos, secoes = carregar_dados()

# ==========================
# BARRA LATERAL
# ==========================

st.sidebar.title("Filtros eleitorais")

turno = st.sidebar.radio(
    "Turno da eleicao",
    options=[1, 2],
    format_func=lambda x: f"{x}º turno",
)

zona = st.sidebar.selectbox(
    "Zona eleitoral (indicadores e tabelas)",
    options=["Todas", 102, 103],
)

candidato_mapa = 13
if turno == 1:
    candidato_mapa = st.sidebar.selectbox(
        "Mapa do candidato",
        options=[13, 22],
        format_func=lambda n: NOMES[n],
    )

# O filtro de zona afeta os indicadores e tabelas.
# Os mapas HTML preservam a visualizacao de toda a cidade.
filtrados = votos[votos["NR_TURNO"] == turno].copy()
secoes_filtradas = secoes[secoes["NR_TURNO"] == turno].copy()

if zona != "Todas":
    filtrados = filtrados[filtrados["NR_ZONA"] == zona]
    secoes_filtradas = secoes_filtradas[
        secoes_filtradas["NR_ZONA"] == zona
    ]

validos = filtrados[filtrados["NR_VOTAVEL"].between(10, 94)]
total_validos = int(validos["QT_VOTOS"].sum())
brancos = int(
    filtrados.loc[filtrados["NR_VOTAVEL"] == 95, "QT_VOTOS"].sum()
)
nulos = int(
    filtrados.loc[filtrados["NR_VOTAVEL"] == 96, "QT_VOTOS"].sum()
)

candidatos = tabela_candidatos(filtrados)
lider = candidatos.iloc[0]

# ==========================
# CABECALHO E INDICADORES
# ==========================

st.title("🗳️ Eleicoes Presidenciais 2026")
st.subheader("Divinopolis - Minas Gerais")

st.caption(
    "Analise dos dados oficiais do TSE por secao e local de votacao."
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Votos validos", formatar_numero(total_validos))
col2.metric("Votos brancos", formatar_numero(brancos))
col3.metric("Votos nulos", formatar_numero(nulos))
col4.metric("Secoes", len(secoes_filtradas))
col5.metric("Mais votado", NOMES.get(
    int(lider["NR_VOTAVEL"]), str(lider["NM_VOTAVEL"])
))

st.divider()

aba_mapa, aba_resultados, aba_secoes, aba_metodologia = st.tabs([
    "Mapa interativo",
    "Resultados e graficos",
    "Secoes eleitorais",
    "Metodologia",
])

# ==========================
# MAPAS FOLIUM
# ==========================

with aba_mapa:
    st.subheader(f"Mapa eleitoral - {turno}º turno")

    if turno == 1:
        caminho_mapa = (
            RAIZ / "mapas" / "primeiro_turno"
            / f"primeiro_turno_candidato_{candidato_mapa}.html"
        )
    else:
        caminho_mapa = (
            RAIZ / "mapas" / "segundo_turno"
            / "segundo_turno_comparativo.html"
        )

    st.info(
        "O mapa representa os resultados agregados por local "
        "de votacao. Os poligonos sao aproximacoes de Voronoi, "
        "nao limites oficiais de secoes eleitorais."
    )

    if zona != "Todas":
        st.caption(
            "Observacao: o filtro de zona afeta os indicadores, "
            "graficos e tabelas, mas o mapa continua mostrando "
            "todos os locais de Divinopolis."
        )

    if caminho_mapa.exists():
        components.html(
            caminho_mapa.read_text(encoding="utf-8"),
            height=680,
            scrolling=False,
        )
    else:
        st.error(
            f"Mapa nao encontrado: {caminho_mapa.name}. "
            "Execute os scripts de geracao dos mapas."
        )

# ==========================
# GRAFICOS E COMPARACOES
# ==========================

with aba_resultados:
    st.subheader("Votacao por candidato")

    fig = px.bar(
        candidatos,
        x="QT_VOTOS",
        y="Candidato",
        color="Candidato",
        orientation="h",
        color_discrete_map=CORES,
        labels={"QT_VOTOS": "Votos", "Candidato": ""},
        hover_data={"Percentual": ":.2f"},
        height=max(360, len(candidatos) * 38),
    )
    fig.update_layout(
        showlegend=False,
        yaxis={"categoryorder": "total ascending"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Comparacao entre os turnos")

    comparacao = votos.copy()
    if zona != "Todas":
        comparacao = comparacao[comparacao["NR_ZONA"] == zona]

    votos_validos = comparacao[
        comparacao["NR_VOTAVEL"].between(10, 94)
    ].groupby("NR_TURNO")["QT_VOTOS"].sum()

    comparacao = comparacao[
        comparacao["NR_VOTAVEL"].isin([13, 22])
    ]
    comparacao = (
        comparacao.groupby(["NR_TURNO", "NR_VOTAVEL"], as_index=False)
        ["QT_VOTOS"].sum()
    )
    comparacao["Percentual"] = comparacao.apply(
        lambda r: 100 * r["QT_VOTOS"] / votos_validos.loc[r["NR_TURNO"]],
        axis=1,
    )
    comparacao["Turno"] = comparacao["NR_TURNO"].map({
        1: "1º turno", 2: "2º turno"
    })
    comparacao["Candidato"] = comparacao["NR_VOTAVEL"].map(NOMES)

    fig2 = px.bar(
        comparacao,
        x="Turno",
        y="Percentual",
        color="Candidato",
        barmode="group",
        color_discrete_map=CORES,
        labels={"Percentual": "% dos votos validos"},
        text_auto=".1f",
    )
    fig2.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig2, use_container_width=True)

    st.caption(
        "No primeiro turno, os percentuais dos dois finalistas "
        "nao somam 100%, pois havia outros candidatos."
    )

    st.dataframe(
        candidatos[["Candidato", "QT_VOTOS", "Percentual"]]
        .rename(columns={"QT_VOTOS": "Votos"})
        .style.format({"Percentual": "{:.2f}%"}),
        use_container_width=True,
        hide_index=True,
    )

# ==========================
# TABELA DE SECOES
# ==========================

with aba_secoes:
    st.subheader("Resultados por secao eleitoral")

    colunas = [
        "NR_ZONA", "NR_SECAO", "NM_LOCAL_VOTACAO",
        "candidato_lider", "total_validos", "percentual_lider",
    ]

    tabela = secoes_filtradas[colunas].copy().rename(columns={
        "NR_ZONA": "Zona",
        "NR_SECAO": "Secao",
        "NM_LOCAL_VOTACAO": "Local de votacao",
        "candidato_lider": "Candidato lider",
        "total_validos": "Votos validos",
        "percentual_lider": "Percentual do lider",
    })

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Baixar tabela CSV",
        data=tabela.to_csv(
            index=False, sep=";"
        ).encode("utf-8-sig"),
        file_name=f"secoes_turno_{turno}.csv",
        mime="text/csv",
    )

# ==========================
# METODOLOGIA
# ==========================

with aba_metodologia:
    st.subheader("Origem dos dados")
    st.markdown(
        "Os resultados foram obtidos do Portal de Dados Abertos "
        "do Tribunal Superior Eleitoral (TSE). Foram utilizados "
        "os dados de votacao por secao e de locais de votacao."
    )

    st.subheader("Tratamento e integracao")
    st.markdown(
        "As bases foram filtradas para Divinopolis/MG. "
        "Os registros foram relacionados por municipio, "
        "turno, zona e secao eleitoral. "
        "Votos brancos e nulos nao entram no calculo "
        "dos percentuais de votos validos."
    )

    st.subheader("Representacao geografica")
    st.markdown(
        "Os mapas utilizam poligonos de Voronoi, limitados "
        "a 1.200 metros de proximidade dos locais de votacao. "
        "Eles nao representam limites eleitorais oficiais. "
        "As cores mostram resultados agregados das secoes "
        "que compartilham a mesma coordenada."
    )

    st.markdown(
        "[Portal de Dados Abertos do TSE]"
        "(https://dadosabertos.tse.jus.br/)"
    )
