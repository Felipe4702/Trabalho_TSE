"""Gera um mapa Folium combinado para o 2o turno presidencial de 2026.

Cores: azul = vantagem de Flavio Bolsonaro; vermelho = vantagem de Lula;
cinza/branco = resultado equilibrado. As cores mostram os percentuais de votos
VALIDOS agregados por coordenada fisica de local de votacao.

As areas sao celulas de Voronoi recortadas a um raio de 1,2 km dos locais,
NAO limites oficiais de secoes eleitorais. Os dados por secao aparecem no
popup de cada ponto.

Entradas: dados/processados/votos_localizados_divinopolis_2026.csv
          dados/processados/resumo_secoes_divinopolis_2026.csv
Saida:    mapas/segundo_turno/segundo_turno_comparativo.html

Uso: python gerar_mapa_segundo_turno.py
"""

from __future__ import annotations

from html import escape
from pathlib import Path

import folium
import pandas as pd
from branca.colormap import LinearColormap

# Reutiliza exatamente o mesmo algoritmo de Voronoi do 1o turno, garantindo
# a mesma metodologia e um projeto com menos codigo repetido.
from gerar_mapas_primeiro_turno import (
    CHAVES,
    construir_voronoi,
    formatar_pontuacao,
    ler_arquivo,
    validar_entradas,
)

RAIZ = Path(__file__).resolve().parent
DADOS = RAIZ / "dados" / "processados"
DESTINO = RAIZ / "mapas" / "segundo_turno"
ARQUIVO_VOTOS = DADOS / "votos_localizados_divinopolis_2026.csv"
ARQUIVO_SECOES = DADOS / "resumo_secoes_divinopolis_2026.csv"
CANDIDATO_LULA = 13
CANDIDATO_FLAVIO = 22


def preparar_dados(votos: pd.DataFrame, secoes: pd.DataFrame):
    """Prepara totais por ponto e tabela completa de secoes para os popups."""
    validar_entradas(votos, secoes)

    v = votos.loc[
        (votos["NR_TURNO"] == 2) &
        (votos["NR_VOTAVEL"].between(10, 94))
    ].copy()
    s = secoes.loc[secoes["NR_TURNO"] == 2].copy()
    if v.empty or s.empty:
        raise ValueError("Nao foram encontrados votos/secoes do 2o turno.")

    encontrados = set(v["NR_VOTAVEL"].astype(int).unique())
    esperados = {CANDIDATO_LULA, CANDIDATO_FLAVIO}
    if encontrados != esperados:
        raise ValueError(
            f"Esperados candidatos 13 e 22 no segundo turno; encontrados: {encontrados}"
        )

    for df in (v, s):
        df["latitude"] = df["latitude"].round(7)
        df["longitude"] = df["longitude"].round(7)

    # Agregacao por coordenada fisica: varias secoes podem usar a mesma escola;
    # escolas diferentes tambem podem compartilhar coordenadas.
    pontos = ["latitude", "longitude"]
    soma = (v.groupby(pontos + ["NR_VOTAVEL"], as_index=False)["QT_VOTOS"]
              .sum())
    piv = (soma.pivot_table(index=pontos, columns="NR_VOTAVEL",
                            values="QT_VOTOS", aggfunc="sum", fill_value=0)
              .reset_index())
    piv["VOTOS_LULA"] = piv[CANDIDATO_LULA].astype(int)
    piv["VOTOS_FLAVIO"] = piv[CANDIDATO_FLAVIO].astype(int)
    piv["TOTAL_VALIDOS"] = piv["VOTOS_LULA"] + piv["VOTOS_FLAVIO"]
    if (piv["TOTAL_VALIDOS"] <= 0).any():
        raise ValueError("Algum local possui zero votos validos.")
    piv["PCT_LULA"] = 100 * piv["VOTOS_LULA"] / piv["TOTAL_VALIDOS"]
    piv["PCT_FLAVIO"] = 100 * piv["VOTOS_FLAVIO"] / piv["TOTAL_VALIDOS"]
    piv["MARGEM_PP"] = piv["PCT_LULA"] - piv["PCT_FLAVIO"]
    piv["LIDER"] = piv["PCT_LULA"].apply(
        lambda p: "Lula" if p > 50 else ("Flavio Bolsonaro" if p < 50 else "Empate")
    )

    if int(piv["TOTAL_VALIDOS"].sum()) != int(v["QT_VOTOS"].sum()):
        raise AssertionError("Total de votos mudou durante a agregacao por local.")
    if int(s["total_validos"].sum()) != int(v["QT_VOTOS"].sum()):
        raise AssertionError("Total de votos e resumo de secoes nao conferem.")

    # Detalhes por secao: preserva os votos de ambos os candidatos.
    votos_secao = (v.groupby(CHAVES + ["NR_VOTAVEL"], as_index=False)["QT_VOTOS"]
                    .sum())
    votos_secao = (
        votos_secao.pivot_table(index=CHAVES, columns="NR_VOTAVEL",
                               values="QT_VOTOS", aggfunc="sum", fill_value=0)
        .reset_index()
        .rename(columns={CANDIDATO_LULA: "votos_lula",
                         CANDIDATO_FLAVIO: "votos_flavio"})
    )
    if s.duplicated(CHAVES).any() or votos_secao.duplicated(CHAVES).any():
        raise ValueError("Ha secoes duplicadas; impossivel unir corretamente.")
    detalhes = s.merge(votos_secao, on=CHAVES, how="left", validate="one_to_one")
    if detalhes[["votos_lula", "votos_flavio"]].isna().any().any():
        raise ValueError("Secoes sem votos para os dois candidatos.")
    if not (detalhes.votos_lula + detalhes.votos_flavio == detalhes.total_validos).all():
        raise AssertionError("Os votos nao conferem em alguma secao.")

    por_ponto = {
        chave: grupo.sort_values(["NR_ZONA", "NR_SECAO"]).copy()
        for chave, grupo in detalhes.groupby(pontos, sort=False)
    }
    coordenadas_votos = set(zip(piv.latitude, piv.longitude))
    coordenadas_secoes = set(por_ponto)
    if coordenadas_votos != coordenadas_secoes:
        raise ValueError("Coordenadas de votos e secoes nao correspondem.")
    return piv, por_ponto


def popup_secoes(grupo: pd.DataFrame, nome_local: str) -> folium.Popup:
    """Tabela de votos nas secoes vinculadas ao ponto do mapa."""
    partes = [
        "<div style='font:13px Arial,sans-serif;min-width:460px'>",
        f"<h3 style='margin:0 0 8px'>{escape(nome_local)}</h3>",
        "<p>Presidencial 2026 - 2o turno. "
        "<small>Regioes aproximadas (Voronoi), nao limites oficiais.</small></p>",
        "<div style='max-height:285px;overflow:auto'>",
        "<table style='border-collapse:collapse;width:100%;font-size:12px'>",
        "<thead><tr style='background:#f1f5f9'>"
        "<th>Zona</th><th>Secao</th><th>Lula</th><th>Flavio</th>"
        "<th>Validos</th><th>Lider</th><th>% lider</th>"
        "</tr></thead><tbody>",
    ]
    for r in grupo.itertuples(index=False):
        celulas = [
            int(r.NR_ZONA), int(r.NR_SECAO), int(r.votos_lula),
            int(r.votos_flavio), int(r.total_validos),
            str(r.candidato_lider), f"{formatar_pontuacao(r.percentual_lider)}%",
        ]
        partes.append("<tr>" + "".join(
            f"<td style='padding:4px;border-bottom:1px solid #e2e8f0'>{escape(str(c))}</td>"
            for c in celulas
        ) + "</tr>")
    partes.append("</tbody></table></div></div>")
    return folium.Popup(
        folium.IFrame(html="".join(partes), width=640, height=360),
        max_width=680,
    )


def gerar_mapa(pontos: pd.DataFrame, secoes_por_ponto: dict) -> Path:
    regioes = construir_voronoi(pontos)
    # 0% Lula = 100% Flavio (azul). 50% = equilibrio (cinza).
    # 100% Lula = vermelho. Apenas votos validos sao considerados.
    escala = LinearColormap(
        colors=["#1e3a8a", "#60a5fa", "#f8fafc", "#f87171", "#991b1b"],
        index=[0, 25, 50, 75, 100],
        vmin=0, vmax=100,
        caption="2o turno - % votos validos para Lula (0=Flavio, 50=empate, 100=Lula)",
    )
    mapa = folium.Map(
        location=[regioes.latitude.mean(), regioes.longitude.mean()],
        zoom_start=12, tiles="OpenStreetMap", control_scale=True,
    )
    areas = folium.FeatureGroup(name="Vantagem entre candidatos", show=True)
    marcadores = folium.FeatureGroup(name="Locais de votacao (clique para secoes)", show=True)

    for r in regioes.itertuples(index=False):
        chave = (r.latitude, r.longitude)
        grupo = secoes_por_ponto[chave]
        nomes = grupo["NM_LOCAL_VOTACAO"].dropna().astype(str).unique().tolist()
        nome_local = " / ".join(nomes)
        zonas_secoes = ", ".join(
            f"{int(s.NR_ZONA)}/{int(s.NR_SECAO)}" for s in grupo.itertuples(index=False)
        )
        pct_lula = formatar_pontuacao(r.PCT_LULA)
        pct_flavio = formatar_pontuacao(r.PCT_FLAVIO)
        margem = formatar_pontuacao(abs(r.MARGEM_PP))
        props = {
            "LOCAL": nome_local,
            "ZONAS_SECOES": zonas_secoes,
            "SECOES": int(len(grupo)),
            "LIDER": r.LIDER,
            "PCT_LULA": f"{pct_lula}%",
            "PCT_FLAVIO": f"{pct_flavio}%",
            "VOTOS_LULA": int(r.VOTOS_LULA),
            "VOTOS_FLAVIO": int(r.VOTOS_FLAVIO),
            "VOTOS_VALIDOS": int(r.TOTAL_VALIDOS),
            "MARGEM": f"{margem} p.p.",
        }
        feicao = {
            "type": "Feature", "properties": props,
            "geometry": r.geometry.__geo_interface__,
        }
        folium.GeoJson(
            feicao,
            style_function=lambda f, c=escala: {
                "fillColor": c(float(f["properties"]["PCT_LULA"].replace("%", "").replace(",", "."))),
                "fillOpacity": 0.73,
                "color": "#ffffff",
                "weight": 1.3,
            },
            highlight_function=lambda f: {
                "weight": 2.8, "color": "#172554", "fillOpacity": 0.90,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["LOCAL", "ZONAS_SECOES", "LIDER", "PCT_LULA", "PCT_FLAVIO", "MARGEM"],
                aliases=["Local: ", "Zonas/secoes: ", "Lider: ", "Lula: ", "Flavio: ", "Vantagem: "],
                labels=True, sticky=True,
                style="background:white;color:#1f2937;font:12px Arial;padding:8px;max-width:450px",
            ),
            popup=folium.GeoJsonPopup(
                fields=["LOCAL", "SECOES", "LIDER", "VOTOS_LULA", "VOTOS_FLAVIO", "VOTOS_VALIDOS"],
                aliases=["Local:", "Secoes:", "Lider:", "Votos Lula:", "Votos Flavio:", "Validos:"],
                max_width=400,
            ),
        ).add_to(areas)

        folium.CircleMarker(
            location=[r.latitude, r.longitude],
            radius=4, weight=1.5, color="#ffffff", fill=True,
            fill_color="#0f172a", fill_opacity=0.95,
            tooltip=f"Clique: {escape(nome_local)} ({len(grupo)} secoes)",
            popup=popup_secoes(grupo, nome_local),
        ).add_to(marcadores)

    areas.add_to(mapa)
    marcadores.add_to(mapa)
    escala.add_to(mapa)
    folium.LayerControl(collapsed=False).add_to(mapa)
    aviso = """
    <div style="position:fixed;bottom:18px;left:18px;z-index:9999;
      background:rgba(255,255,255,.96);padding:10px 12px;max-width:360px;
      border:1px solid #cbd5e1;border-radius:6px;
      box-shadow:0 1px 5px #0002;font:12px Arial,sans-serif">
      <strong>Divinopolis - presidencial 2026 - 2o turno</strong><br>
      <span style="color:#1e3a8a;font-weight:bold">Azul: Flavio</span> &nbsp;|
      <span style="color:#991b1b;font-weight:bold">Vermelho: Lula</span><br>
      Cor = percentual de votos validos, agregado por local.<br>
      As manchas sao areas de proximidade (Voronoi),
      <strong>nao limites eleitorais oficiais</strong>.<br>
      Passe o mouse sobre uma area ou clique nos pontos para ver as secoes.
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(aviso))
    mapa.fit_bounds([
        [regioes.latitude.min(), regioes.longitude.min()],
        [regioes.latitude.max(), regioes.longitude.max()],
    ])
    DESTINO.mkdir(parents=True, exist_ok=True)
    caminho = DESTINO / "segundo_turno_comparativo.html"
    mapa.save(str(caminho))
    return caminho


def main():
    votos = ler_arquivo(ARQUIVO_VOTOS)
    secoes = ler_arquivo(ARQUIVO_SECOES)
    pontos, por_ponto = preparar_dados(votos, secoes)
    print("\nMAPA DO 2o TURNO")
    print(f"Secoes eleitorais: {len(secoes[secoes.NR_TURNO == 2])}")
    print(f"Coordenadas distintas: {len(pontos)}")
    print(f"Lula: {int(pontos.VOTOS_LULA.sum()):,} votos validos")
    print(f"Flavio: {int(pontos.VOTOS_FLAVIO.sum()):,} votos validos")
    print(f"Total validos: {int(pontos.TOTAL_VALIDOS.sum()):,}")
    caminho = gerar_mapa(pontos, por_ponto)
    print(f"Mapa salvo em: {caminho}")


if __name__ == "__main__":
    main()
