"""Extrai os registros eleitorais de Divinopolis (MG) dos ZIPs oficiais do TSE.

Coloque em dados/brutos/:
    votacao_secao_2026_BR.zip
    eleitorado_local_votacao_2026.zip

Execute na pasta do projeto:
    python filtrar_divinopolis.py
"""

from pathlib import Path
from zipfile import ZipFile
import unicodedata

import pandas as pd


PASTA_PROJETO = Path(__file__).resolve().parent
PASTA_BRUTOS = PASTA_PROJETO / "dados" / "brutos"
PASTA_PROCESSADOS = PASTA_PROJETO / "dados" / "processados"
TAMANHO_BLOCO = 100_000


def normalizar_cidade(coluna):
    """Compara nomes ignorando acentos e diferencas entre maiusculas/minusculas."""
    return (
        coluna.fillna("")
        .astype(str)
        .map(lambda texto: "".join(
            caractere for caractere in unicodedata.normalize("NFKD", texto)
            if not unicodedata.combining(caractere)
        ))
        .str.strip()
        .str.upper()
    )


def extrair_cidade(nome_zip, apenas_presidente=False):
    """Filtra registros sem descompactar os CSVs gigantes na memoria."""
    caminho_zip = PASTA_BRUTOS / nome_zip
    if not caminho_zip.is_file():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {caminho_zip}\n"
            "Baixe o ZIP oficial e coloque-o na pasta dados/brutos."
        )

    registros = []
    total_lido = 0
    with ZipFile(caminho_zip) as zip_tse:
        nomes_csv = [nome for nome in zip_tse.namelist() if nome.lower().endswith(".csv")]
        if not nomes_csv:
            raise ValueError(f"O arquivo {nome_zip} nao contem CSV.")

        for nome_csv in nomes_csv:
            print(f"Lendo {nome_csv} dentro de {nome_zip}...")
            with zip_tse.open(nome_csv) as csv_tse:
                partes = pd.read_csv(
                    csv_tse,
                    sep=";",
                    encoding="latin-1",
                    dtype=str,
                    chunksize=TAMANHO_BLOCO,
                    low_memory=False,
                )

                for parte in partes:
                    necessarias = {"SG_UF", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO"}
                    ausentes = necessarias.difference(parte.columns)
                    if ausentes:
                        raise ValueError(
                            f"O CSV {nome_csv} nao possui as colunas: {sorted(ausentes)}. "
                            f"Colunas encontradas: {list(parte.columns)}"
                        )

                    filtro = (
                        parte["SG_UF"].str.strip().str.upper().eq("MG")
                        & normalizar_cidade(parte["NM_MUNICIPIO"]).eq("DIVINOPOLIS")
                    )

                    if apenas_presidente:
                        # CD_CARGO=1 e o codigo oficial para Presidente.
                        if "CD_CARGO" in parte.columns:
                            filtro &= parte["CD_CARGO"].str.strip().eq("1")
                        elif "DS_CARGO" in parte.columns:
                            filtro &= parte["DS_CARGO"].str.strip().str.upper().eq("PRESIDENTE")
                        # O arquivo *_BR ja e especifico do cargo Presidente.

                    selecionados = parte.loc[filtro].copy()
                    if not selecionados.empty:
                        registros.append(selecionados)

                    total_lido += len(parte)
                    if total_lido // TAMANHO_BLOCO % 20 == 0:
                        print(f"  {total_lido:,} linhas lidas".replace(",", "."))

    if not registros:
        raise ValueError(
            f"Nenhuma linha de Divinopolis foi encontrada em {nome_zip}. "
            "Confira se o arquivo e o ano estao corretos."
        )

    dados = pd.concat(registros, ignore_index=True)
    print(f"Encontradas {len(dados):,} linhas de Divinopolis.".replace(",", "."))
    return dados


def main():
    PASTA_PROCESSADOS.mkdir(parents=True, exist_ok=True)

    # 1. Votos do primeiro e segundo turnos para Presidente.
    votos = extrair_cidade("votacao_secao_2026_BR.zip", apenas_presidente=True)
    if "NR_TURNO" in votos.columns:
        votos = votos[votos["NR_TURNO"].isin(["1", "2"])].copy()
    votos["QT_VOTOS"] = pd.to_numeric(votos["QT_VOTOS"], errors="raise")

    # Mantem identificadores, incluindo numero do candidato e turno.
    colunas_agrupamento = [
        "SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_TURNO",
        "NR_ZONA", "NR_SECAO", "NR_VOTAVEL", "NM_VOTAVEL"
    ]
    colunas_agrupamento = [c for c in colunas_agrupamento if c in votos.columns]
    colunas_indispensaveis = {"NR_TURNO", "NR_ZONA", "NR_SECAO", "NR_VOTAVEL"}
    if not colunas_indispensaveis.issubset(votos.columns):
        raise ValueError(f"Faltam colunas importantes nos votos: {colunas_indispensaveis - set(votos.columns)}")

    votos_agrupados = (
        votos.groupby(colunas_agrupamento, as_index=False, dropna=False)["QT_VOTOS"]
        .sum()
    )
    destino_votos = PASTA_PROCESSADOS / "votos_divinopolis_2026.csv"
    votos_agrupados.to_csv(destino_votos, sep=";", encoding="utf-8-sig", index=False)

    # 2. Enderecos e coordenadas dos locais de votacao.
    locais = extrair_cidade("eleitorado_local_votacao_2026.zip")
    destino_locais = PASTA_PROCESSADOS / "locais_divinopolis_2026.csv"
    locais.to_csv(destino_locais, sep=";", encoding="utf-8-sig", index=False)

    print("\nPROCESSAMENTO CONCLUIDO")
    print(f"Votos: {destino_votos} ({len(votos_agrupados)} linhas)")
    print(f"Locais: {destino_locais} ({len(locais)} linhas)")
    print("Turnos encontrados:", sorted(votos_agrupados["NR_TURNO"].dropna().unique()))
    print("Colunas do arquivo de locais:", ", ".join(locais.columns))
    print("\nAgora os arquivos pequenos estao prontos para a proxima etapa.")


if __name__ == "__main__":
    main()
