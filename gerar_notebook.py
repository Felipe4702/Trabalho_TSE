
from pathlib import Path
import json
import textwrap
import pandas as pd


RAIZ = Path(__file__).resolve().parent
DESTINO = RAIZ / "notebooks"
DESTINO.mkdir(exist_ok=True)

VOTOS = RAIZ / "dados/processados/votos_divinopolis_2026.csv"


def markdown(texto):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": textwrap.dedent(texto).strip() + "\n",
    }


def codigo(texto):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": textwrap.dedent(texto).strip() + "\n",
    }


# Confere os valores utilizados no relatorio.
votos = pd.read_csv(VOTOS, sep=";", encoding="utf-8-sig")
validos = votos[votos["NR_VOTAVEL"].between(10, 94)]
totais = validos.groupby("NR_TURNO")["QT_VOTOS"].sum()

if totais.to_dict() != {1: 132409, 2: 139034}:
    raise ValueError("Os totais nao correspondem aos dados analisados.")


introducao = """
# Analise eleitoral de Divinopolis - 2026

**Disciplina:** Ferramentas para Data Science - UFSJ

**Municipio:** Divinopolis, Minas Gerais

**Objetivo:** analisar a distribuicao espacial dos votos
presidenciais nos dois turnos da eleicao de 2026.

O trabalho utiliza Pandas, GeoPandas e Folium, com dados
obtidos do Portal de Dados Abertos do TSE.
"""

metodologia = """
## Metodologia

Foram utilizadas duas bases oficiais do TSE: votacao por
secao eleitoral e eleitorado por local de votacao.

Primeiro, os dados foram filtrados para Divinopolis/MG,
municipio de codigo 44458.

Posteriormente, os registros foram associados utilizando
municipio, turno, zona e secao eleitoral.

Os votos nominais foram separados dos votos brancos e
nulos para calcular os percentuais de votos validos.

Como diversas secoes compartilham o mesmo local de
votacao, os votos foram agregados por coordenada geografica
para definir as cores dos mapas.

As regioes foram construidas utilizando diagramas de
Voronoi no sistema UTM 23S (EPSG:32723), com limite
visual de aproximadamente 1.200 metros dos locais.

**Limitacao:** essas regioes representam proximidade
geografica, nao limites eleitorais oficiais ou locais de
residencia dos eleitores.
"""

primeiro_flavio = """
## Mapa 1 - Flavio Bolsonaro, primeiro turno

### O fato

Flavio Bolsonaro recebeu 71.478 votos, equivalentes a
53,98% dos 132.409 votos validos de Divinopolis.

Na zona 102, alcancou 56,29% dos votos validos,
enquanto na zona 103 obteve 50,75%.

Entre os locais com maior percentual para Flavio,
destacam-se o Instituto Nossa Senhora do Sagrado
Coracao, com 68,91%, e o Colegio Roberto Carneiro,
com 66,17%, ambos no Centro.

Os resultados demonstram variacao espacial no apoio
ao candidato, com diferencas importantes entre locais.

### O design

Foi utilizada uma paleta sequencial azul, com cinco
cores de referencia e interpolacao continua de 0% a
100%. Portanto, nao foram definidas classes discretas.

A opacidade de 70% permite observar as vias e outras
referencias do mapa-base OpenStreetMap.

A representacao utiliza poligonos GeoJSON, Voronoi,
tooltips e popups interativos do Folium.
"""

primeiro_lula = """
## Mapa 2 - Lula, primeiro turno

### O fato

Lula recebeu 49.403 votos, correspondentes a 37,31%
dos votos validos no municipio.

Na zona 102, obteve 35,32% dos votos validos;
na zona 103, obteve 40,11%.

Entre os locais com maior percentual para Lula,
destacam-se a Escola Municipal Benjamim Constant,
no Buritis, com 56,55%, e a Escola Municipal Joao
Gontijo da Fonseca, no Primavera, com 53,69%.

A comparacao com o mapa de Flavio evidencia que o
apoio aos candidatos nao se distribuiu uniformemente
pelos locais de votacao.

### O design

Foi utilizada uma escala sequencial vermelha,
com cinco cores de referencia e interpolacao
continua entre 0% e 100%.

A transparencia de 70% preserva a leitura do
mapa-base e permite identificar referencias
geograficas proximas aos locais de votacao.

Os tooltips exibem resultados por secao, enquanto os
popups permitem consultar informacoes adicionais.
"""

segundo_turno = """
## Mapa 3 - Comparacao do segundo turno

### O fato

No segundo turno, Flavio recebeu 76.540 votos
(55,05%) e Lula recebeu 62.494 votos (44,95%).

A diferenca entre os candidatos foi de 14.046 votos,
menor que a diferenca de 22.075 votos observada
no primeiro turno.

A participacao de Lula aumentou 7,64 pontos
percentuais e a de Flavio aumentou 1,07 ponto
percentual em relacao aos votos validos do
primeiro turno.

Na zona 103, a votacao foi mais equilibrada:
51,59% para Flavio e 48,41% para Lula.

Entre os locais com maior percentual para Lula
estao a Escola Municipal Benjamim Constant
(64,80%) e a Escola Municipal Antonieta Fonseca
(63,97%).

Para Flavio, destacam-se o Instituto Nossa Senhora
do Sagrado Coracao (70,97%) e o Colegio Roberto
Carneiro (68,94%).

Esses resultados evidenciam diferencas territoriais
entre os locais de votacao. Entretanto, nao permitem
identificar transferencias individuais de votos.

### O design

Foi utilizada uma paleta divergente:
azul para vantagem de Flavio, vermelho para
vantagem de Lula e tons claros para equilibrio.

A escala utiliza cinco cores de referencia, com
interpolacao continua de 0% a 100% de votos validos
para Lula. O ponto neutro corresponde a 50%.

A opacidade das regioes e de 73%.

O mapa utiliza Folium, poligonos GeoJSON,
controle de camadas, tooltips e popups.
"""

conclusao = """
## Conclusao

A analise demonstrou que Flavio Bolsonaro liderou
a votacao presidencial de Divinopolis nos dois turnos.

Embora Lula tenha aumentado sua participacao percentual
entre os turnos, Flavio permaneceu com a maior parcela
dos votos validos no municipio.

As diferencas entre as zonas 102 e 103 e entre os locais
de votacao mostram a importancia da representacao
espacial para interpretar dados eleitorais.

Os mapas interativos permitiram examinar os resultados
em diferentes escalas de detalhe, associando os valores
estatisticos a pontos geograficos.

A principal limitacao metodologica esta no uso de
regioes aproximadas de Voronoi. Por isso, a analise
descreve resultados dos locais de votacao e nao
preferencias de todos os moradores de determinada area.

### Fontes

- Tribunal Superior Eleitoral (TSE):
  https://dadosabertos.tse.jus.br/
- Votacao por secao eleitoral - 2026.
- Eleitorado por local de votacao - 2026.
"""

celulas = [
    markdown(introducao),

    codigo("""
        from pathlib import Path
        import sys
        import pandas as pd
        from IPython.display import display

        RAIZ = (
            Path.cwd().parent
            if Path.cwd().name == "notebooks"
            else Path.cwd()
        )
        sys.path.insert(0, str(RAIZ))

        DADOS = RAIZ / "dados" / "processados"
        votos = pd.read_csv(
            DADOS / "votos_divinopolis_2026.csv",
            sep=";", encoding="utf-8-sig"
        )
        locais = pd.read_csv(
            DADOS / "locais_divinopolis_2026.csv",
            sep=";", encoding="utf-8-sig"
        )
        resumo = pd.read_csv(
            DADOS / "resumo_secoes_divinopolis_2026.csv",
            sep=";", encoding="utf-8-sig"
        )
        display(votos.head())
    """),

    markdown(metodologia),

    codigo("""
        chaves = [
            "CD_MUNICIPIO", "NR_TURNO",
            "NR_ZONA", "NR_SECAO"
        ]

        print("Registros de votos:", len(votos))
        print("Registros de locais:", len(locais))
        print("Secoes por turno:")
        print(resumo.groupby("NR_TURNO").size())

        assert not resumo.duplicated(chaves).any()
        assert not resumo[["latitude", "longitude"]].isna().any().any()
    """),

    codigo("""
        # Os scripts abaixo contem o processamento completo.
        # Com os ZIPs oficiais em dados/brutos, pode-se
        # reproduzir a filtragem e a integracao desde o inicio.

        from filtrar_divinopolis import main as filtrar
        from integrar_dados import main as integrar

        # filtrar()
        # integrar()

        # Os arquivos processados ja incluidos no repositorio
        # permitem executar as analises sem baixar os ZIPs.
    """),

    codigo("""
        votos_validos = votos[
            votos["NR_VOTAVEL"].between(10, 94)
        ].copy()

        resultados = (
            votos_validos.groupby(
                ["NR_TURNO", "NR_VOTAVEL", "NM_VOTAVEL"],
                as_index=False
            )["QT_VOTOS"].sum()
        )

        totais = (
            votos_validos.groupby("NR_TURNO")["QT_VOTOS"]
            .sum()
        )

        resultados["percentual"] = resultados.apply(
            lambda r: 100 * r.QT_VOTOS / totais.loc[r.NR_TURNO],
            axis=1
        )
        display(resultados.sort_values(
            ["NR_TURNO", "QT_VOTOS"],
            ascending=[True, False]
        ))
    """),

    codigo("""
        zonas = (
            votos_validos.groupby(
                ["NR_TURNO", "NR_ZONA", "NR_VOTAVEL"],
                as_index=False
            )["QT_VOTOS"].sum()
        )

        zonas["total_zona"] = zonas.groupby(
            ["NR_TURNO", "NR_ZONA"]
        )["QT_VOTOS"].transform("sum")

        zonas["percentual"] = (
            100 * zonas.QT_VOTOS / zonas.total_zona
        )
        display(zonas[zonas.NR_VOTAVEL.isin([13, 22])])
    """),

    markdown(primeiro_flavio),
    markdown(primeiro_lula),

    codigo("""
        from gerar_mapas_primeiro_turno import main as gerar_primeiro
        gerar_primeiro()
    """),

    markdown(segundo_turno),

    codigo("""
        from gerar_mapa_segundo_turno import main as gerar_segundo
        gerar_segundo()
    """),

    codigo("""
        # Confere os arquivos HTML produzidos.
        mapas = sorted((RAIZ / "mapas").rglob("*.html"))
        for mapa in mapas:
            print(mapa.relative_to(RAIZ))
    """),

    markdown(conclusao),
]

notebook = {
    "cells": celulas,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

caminho_notebook = DESTINO / "analise_eleitoral_divinopolis.ipynb"
caminho_notebook.write_text(
    json.dumps(notebook, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

# Salva tambem o relatorio como Markdown independente.
relatorio = "\n\n---\n\n".join([
    introducao, metodologia, primeiro_flavio,
    primeiro_lula, segundo_turno, conclusao,
])

caminho_relatorio = DESTINO / "relatorio.md"
caminho_relatorio.write_text(relatorio, encoding="utf-8")

print("Notebook criado:", caminho_notebook)
print("Relatorio criado:", caminho_relatorio)
