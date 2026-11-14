
"""Gera mapas Folium do 1o turno presidencial em Divinopolis (2026).

Entradas (geradas por integrar_dados.py):
    dados/processados/votos_localizados_divinopolis_2026.csv
    dados/processados/resumo_secoes_divinopolis_2026.csv

Saidas:
    mapas/primeiro_turno/primeiro_turno_candidato_13.html
    mapas/primeiro_turno/primeiro_turno_candidato_22.html

As areas desenhadas sao celulas de Voronoi em torno dos locais de votacao,
recortadas a uma faixa de 1,2 km desses pontos. NAO sao limites oficiais
geograficos de secoes eleitorais. Secoes de um mesmo local sao agregadas
apenas para a cor do mapa; os resultados por secao aparecem no popup.

Execute na raiz do projeto: python gerar_mapas_primeiro_turno.py
"""

from __future__ import annotations

from html import escape
from pathlib import Path

import folium
import geopandas as gpd
import pandas as pd
from branca.colormap import LinearColormap
from shapely.geometry import MultiPoint, Point
from shapely.ops import unary_union, voronoi_diagram


RAIZ = Path(__file__).resolve().parent
DADOS = RAIZ / "dados" / "processados"
DESTINO = RAIZ / "mapas" / "primeiro_turno"
ARQUIVO_VOTOS = DADOS / "votos_localizados_divinopolis_2026.csv"
ARQUIVO_SECOES = DADOS / "resumo_secoes_divinopolis_2026.csv"
CHAVES = ["CD_MUNICIPIO", "NR_TURNO", "NR_ZONA", "NR_SECAO"]

# 1200 m de entorno dos locais, apenas para limitar a area de visualizacao.
RAIO_VISUALIZACAO_METROS = 1200

PALETAS = {
    13: ["#fff5f5", "#fecaca", "#f87171", "#dc2626", "#7f1d1d"],
    22: ["#eff6ff", "#bfdbfe", "#60a5fa", "#2563eb", "#1e3a8a"],
}
PALETA_GENERICA = ["#f0fdf4", "#bbf7d0", "#4ade80", "#16a34a", "#14532d"]


def ler_arquivo(caminho: Path) -> pd.DataFrame:
    if not caminho.is_file():
        raise FileNotFoundError(
            f"Nao encontrei {caminho}. Rode antes: python integrar_dados.py"
        )
    return pd.read_csv(caminho, sep=";", encoding="utf-8-sig")


def validar_entradas(votos: pd.DataFrame, secoes: pd.DataFrame) -> None:
    campos_votos = CHAVES + [
        "NR_VOTAVEL", "NM_VOTAVEL", "QT_VOTOS", "latitude", "longitude"
    ]
    campos_secoes = CHAVES + [
        "NM_LOCAL_VOTACAO", "total_validos", "candidato_lider",
        "percentual_lider", "latitude", "longitude",
    ]
    for nome, dados, campos in [
        ("votos", votos, campos_votos), ("secoes", secoes, campos_secoes)
    ]:
        faltam = sorted(set(campos) - set(dados.columns))
        if faltam:
            raise ValueError(f"Arquivo de {nome}: colunas ausentes: {faltam}")

    if secoes.duplicated(CHAVES).any():
        raise ValueError("O resumo tem secoes/turnos duplicados.")
    if votos.duplicated(CHAVES + ["NR_VOTAVEL"]).any():
        raise ValueError("O arquivo tem votos duplicados por candidato e secao.")
    if votos[["latitude", "longitude"]].isna().any().any():
        raise ValueError("Ha votos sem coordenadas validas.")
    if secoes[["latitude", "longitude"]].isna().any().any():
        raise ValueError("Ha secoes sem coordenadas validas.")
    if not (votos.NR_TURNO == 1).any() or not (secoes.NR_TURNO == 1).any():
        raise ValueError("Os arquivos nao contem dados do 1o turno.")


def preparar_pontos(votos: pd.DataFrame, secoes: pd.DataFrame):
    # Apenas votos nominais; 95 = branco, 96 = nulo.
    v = votos.loc[(votos.NR_TURNO == 1) & votos.NR_VOTAVEL.between(10, 94)].copy()
    s = secoes.loc[secoes.NR_TURNO == 1].copy()

    v["latitude"] = v["latitude"].round(7)
    v["longitude"] = v["longitude"].round(7)
    s["latitude"] = s["latitude"].round(7)
    s["longitude"] = s["longitude"].round(7)

    # Cada escola recebe varias secoes; locais distintos podem compartilhar coordenadas.
    # Por isso a geometria e criada por coordenada fisica distinta.
    campos_ponto = ["latitude", "longitude"]
    votos_ponto = (
        v.groupby(campos_ponto + ["NR_VOTAVEL", "NM_VOTAVEL"], as_index=False)
        ["QT_VOTOS"].sum()
    )
    totais_ponto = (
        votos_ponto.groupby(campos_ponto, as_index=False)["QT_VOTOS"]
        .sum().rename(columns={"QT_VOTOS": "TOTAL_VALIDOS"})
    )
    candidatos = (
        votos_ponto.groupby(["NR_VOTAVEL", "NM_VOTAVEL"], as_index=False)
        ["QT_VOTOS"].sum().sort_values("QT_VOTOS", ascending=False)
        .head(2)
    )

    if len(candidatos) < 2:
        raise ValueError("Nao foram encontrados dois candidatos no 1o turno.")

    # Todos os votos de todas as secoes precisam ser preservados.
    if int(totais_ponto.TOTAL_VALIDOS.sum()) != int(v.QT_VOTOS.sum()):
        raise AssertionError("Os votos mudaram durante o agrupamento por local.")
    if len(s) != s[CHAVES].drop_duplicates().shape[0]:
        raise AssertionError("As secoes nao sao unicas no 1o turno.")
    if int(s.total_validos.sum()) != int(v.QT_VOTOS.sum()):
        raise AssertionError("Total de votos validos difere entre os arquivos.")

    # Preserva informacoes individuais das secoes para os popups do Folium.
    s = s.sort_values(["NR_ZONA", "NR_SECAO"])
    secoes_por_ponto = {
        chave: bloco.copy()
        for chave, bloco in s.groupby(campos_ponto, sort=False)
    }
    votos_por_ponto = {
        chave: bloco.copy()
        for chave, bloco in votos_ponto.groupby(campos_ponto, sort=False)
    }
    return totais_ponto, votos_por_ponto, secoes_por_ponto, candidatos


def construir_voronoi(totais_ponto: pd.DataFrame) -> gpd.GeoDataFrame:
    # Calcula distancias em metros; EPSG:32723 corresponde a UTM 23S (WGS84).
    pontos = gpd.GeoDataFrame(
        totais_ponto.copy(),
        geometry=gpd.points_from_xy(totais_ponto.longitude, totais_ponto.latitude),
        crs="EPSG:4326",
    ).to_crs("EPSG:32723")

    if len(pontos) < 3:
        raise ValueError("Sao necessarios tres locais distintos para o Voronoi.")
    pontos["ID_PONTO"] = range(len(pontos))

    # Voronoi define a area mais proxima de cada local. Uma faixa de entorno
    # impede que as celulas se estendam indefinidamente para zonas sem dados.
    areas_visiveis = unary_union([
        geom.buffer(RAIO_VISUALIZACAO_METROS) for geom in pontos.geometry
    ])
    diagrama = voronoi_diagram(MultiPoint(list(pontos.geometry)), edges=False)

    registro = []
    for celula in diagrama.geoms:
        interior = celula.representative_point()
        indice = min(
            range(len(pontos)),
            key=lambda i: interior.distance(pontos.geometry.iloc[i])
        )
        recorte = celula.intersection(areas_visiveis)
        if not recorte.is_empty:
            registro.append({
                "ID_PONTO": int(pontos.iloc[indice].ID_PONTO),
                "geometry": recorte
            })

    regioes = gpd.GeoDataFrame(registro, geometry="geometry", crs=pontos.crs)
    if regioes.ID_PONTO.duplicated().any() or len(regioes) != len(pontos):
        raise RuntimeError("Falha na construcao das celulas de Voronoi.")

    return regioes.merge(
        pontos.drop(columns="geometry"),
        on="ID_PONTO", how="inner", validate="one_to_one"
    ).to_crs("EPSG:4326")


def formatar_pontuacao(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ==========================
# TOOLTIP AO PASSAR O MOUSE
# ==========================

def tooltip_secoes(grupo: pd.DataFrame, nome_local: str) -> folium.Tooltip:
    linhas = []

    for s in grupo.sort_values(["NR_ZONA", "NR_SECAO"]).head(8).itertuples(index=False):
        nome = str(s.candidato_lider)
        if "LULA" in nome.upper():
            nome = "Lula"
        elif "BOLSONARO" in nome.upper():
            nome = "Flavio Bolsonaro"

        linhas.append(
            "<tr>"
            f"<td>{int(s.NR_ZONA)}/{int(s.NR_SECAO)}</td>"
            f"<td>{escape(nome)}</td>"
            f"<td style='text-align:right'>{formatar_pontuacao(s.percentual_lider)}%</td>"
            "</tr>"
        )

    restantes = max(0, len(grupo) - 8)
    aviso = (
        f"<p style='margin:6px 0 0;color:#64748b'>"
        f"+{restantes} secoes. Clique no ponto para ver todas.</p>"
        if restantes else ""
    )

    html = (
        "<div style='width:380px;max-width:75vw;font:12px Arial;white-space:normal'>"
        f"<b style='font-size:13px'>{escape(nome_local)}</b>"
        f"<p style='margin:5px 0'>{len(grupo)} secoes eleitorais</p>"
        "<table style='width:100%;border-collapse:collapse'>"
        "<tr style='background:#f1f5f9'>"
        "<th>Zona/Secao</th><th>Lider</th><th>% lider</th></tr>"
        + "".join(linhas) +
        "</table>" + aviso + "</div>"
    )

    return folium.Tooltip(
        html, sticky=True,
        style="background:white;color:#1f2937;padding:10px;"
              "border:1px solid #cbd5e1;border-radius:8px;"
              "white-space:normal;"
    )


def popup_secoes(grupo: pd.DataFrame, nome_local: str) -> folium.Popup:
    cabecalho = (
        "<div style='font:13px Arial,sans-serif; min-width:365px;'>"
        f"<h3 style='margin:0 0 8px'>{escape(nome_local)}</h3>"
        "<p style='margin:0 0 9px'>Resultados por secao - 1o turno<br>"
        "<small>Os limites coloridos sao estimados, nao sao limites oficiais das secoes.</small></p>"
        "<div style='max-height:250px;overflow:auto'>"
        "<table style='border-collapse:collapse;width:100%;font-size:12px'>"
        "<tr style='background:#f0f0f0'><th>Zona</th><th>Secao</th><th>Lider</th><th>Votos validos</th><th>% lider</th></tr>"
    )
    linhas = []
    for item in grupo.itertuples(index=False):
        lider = escape(str(item.candidato_lider))
        percentual = formatar_pontuacao(item.percentual_lider)
        linhas.append(
            "<tr>"
            f"<td style='padding:3px;border-bottom:1px solid #ddd'>{item.NR_ZONA}</td>"
            f"<td style='padding:3px;border-bottom:1px solid #ddd'>{item.NR_SECAO}</td>"
            f"<td style='padding:3px;border-bottom:1px solid #ddd'>{lider}</td>"
            f"<td style='padding:3px;border-bottom:1px solid #ddd'>{item.total_validos}</td>"
            f"<td style='padding:3px;border-bottom:1px solid #ddd'>{percentual}%</td>"
            "</tr>"
        )
    conteudo = cabecalho + "".join(linhas) + "</table></div></div>"
    return folium.Popup(
        folium.IFrame(html=conteudo, width=520, height=320), max_width=550
    )


def gerar_mapa(
    base: gpd.GeoDataFrame,
    secoes_por_ponto: dict,
    votos_por_ponto: dict,
    numero_candidato: int,
    nome_candidato: str,
) -> Path:
    cores = PALETAS.get(numero_candidato, PALETA_GENERICA)
    cor_forte = cores[-2]
    escala = LinearColormap(cores, vmin=0, vmax=100)
    escala.caption = f"Porcentagem dos votos validos - {nome_candidato}"

    # Cada mapa e gerado independentemente para permitir a entrega em HTML.
    mapa = folium.Map(
        location=[base.latitude.mean(), base.longitude.mean()],
        zoom_start=12,
        tiles="OpenStreetMap",
        control_scale=True,
    )
    camada = folium.FeatureGroup(name=f"Votacao de {nome_candidato}", show=True)
    pontos = folium.FeatureGroup(name="Locais e secoes (clique nos pontos)", show=True)

    for item in base.itertuples(index=False):
        chave = (item.latitude, item.longitude)
        grupo_secoes = secoes_por_ponto[chave]
        votos_local = votos_por_ponto[chave]

        qtd = votos_local.loc[
            votos_local.NR_VOTAVEL == numero_candidato, "QT_VOTOS"
        ].sum()
        total = int(item.TOTAL_VALIDOS)
        percentagem = 100.0 * qtd / total if total else 0.0

        # Lider do local com todos os votos de suas secoes somados.
        lider = votos_local.sort_values(
            ["QT_VOTOS", "NR_VOTAVEL"], ascending=[False, True]
        ).iloc[0]
        porcentagem_lider = 100 * lider.QT_VOTOS / total if total else 0

        nomes_local = (
            grupo_secoes.NM_LOCAL_VOTACAO.dropna().astype(str).unique().tolist()
        )
        nome_local = " / ".join(nomes_local)

        propriedades = {
            "LOCAL": nome_local,
            "LIDER": str(lider.NM_VOTAVEL),
            "PERCENTUAL_LIDER": f"{formatar_pontuacao(porcentagem_lider)}%",
            "CANDIDATO": nome_candidato,
            "VOTOS_CANDIDATO": int(qtd),
            "PERCENTUAL_CANDIDATO": f"{formatar_pontuacao(percentagem)}%",
            "TOTAL_VALIDOS": total,
        }
        area = {
            "type": "Feature",
            "properties": propriedades,
            "geometry": item.geometry.__geo_interface__,
        }

        geo = folium.GeoJson(
            area,
            style_function=lambda feat, escala=escala: {
                "fillColor": escala(
                    float(
                        feat["properties"]["PERCENTUAL_CANDIDATO"]
                        .replace("%", "").replace(",", ".")
                    )
                ),
                "fillOpacity": 0.70,
                "color": "#ffffff",
                "weight": 1.4,
            },
            highlight_function=lambda feat: {
                "weight": 3, "color": "#111827", "fillOpacity": 0.87
            },
            tooltip=tooltip_secoes(grupo_secoes, nome_local),
            popup=folium.GeoJsonPopup(
                fields=[
                    "LOCAL", "LIDER", "PERCENTUAL_LIDER",
                    "VOTOS_CANDIDATO", "TOTAL_VALIDOS"
                ],
                aliases=[
                    "Local:", "Lider:", "% lider:",
                    "Votos do candidato:", "Votos validos:"
                ],
                max_width=360,
            ),
        )
        geo.add_to(camada)

        folium.CircleMarker(
            location=[item.latitude, item.longitude], radius=4,
            color="#ffffff", weight=1.5, fill=True, fill_color=cor_forte,
            fill_opacity=0.95,
            tooltip=f"Clique: {escape(nome_local)} ({len(grupo_secoes)} secoes)",
            popup=popup_secoes(grupo_secoes, nome_local),
        ).add_to(pontos)

    camada.add_to(mapa)
    pontos.add_to(mapa)
    escala.add_to(mapa)
    folium.LayerControl(collapsed=False).add_to(mapa)

    # Deixa explicita a natureza estimada das manchas espaciais.
    aviso = """
    <div style="position:fixed;bottom:20px;left:20px;z-index:9999;
                background:rgba(255,255,255,.96);padding:9px 12px;max-width:325px;
                border:1px solid #cbd5e1;border-radius:6px;
                box-shadow:0 1px 5px #0002;font:12px Arial,sans-serif">
    <strong>Divinopolis - presidencial 2026 - 1o turno</strong><br>
    Areas: influencia aproximada por proximidade (Voronoi),
    <strong>nao</strong> limites eleitorais oficiais.<br>
    Passe o mouse nas areas e clique nos pontos para ver cada secao.
    </div>"""
    mapa.get_root().html.add_child(folium.Element(aviso))

    mapa.fit_bounds([
        [base.latitude.min(), base.longitude.min()],
        [base.latitude.max(), base.longitude.max()]
    ])

    DESTINO.mkdir(parents=True, exist_ok=True)
    caminho = DESTINO / f"primeiro_turno_candidato_{numero_candidato}.html"
    mapa.save(str(caminho))
    return caminho


def main() -> None:
    votos = ler_arquivo(ARQUIVO_VOTOS)
    secoes = ler_arquivo(ARQUIVO_SECOES)
    validar_entradas(votos, secoes)
    totais, votos_ponto, secoes_ponto, candidatos = preparar_pontos(votos, secoes)
    regioes = construir_voronoi(totais)

    print("\nMAPAS DO 1o TURNO")
    print(f"Secoes eleitorais: {len(secoes.loc[secoes.NR_TURNO == 1])}")
    print(f"Coordenadas distintas: {len(regioes)}")

    for candidato in candidatos.itertuples(index=False):
        numero = int(candidato.NR_VOTAVEL)
        nome = str(candidato.NM_VOTAVEL)
        destino = gerar_mapa(
            regioes, secoes_ponto, votos_ponto, numero, nome
        )
        print(f"{nome} - {int(candidato.QT_VOTOS):,} votos: {destino}")

    print("Mapas gerados. Abra os arquivos HTML em um navegador.")


if __name__ == "__main__":
    main()
