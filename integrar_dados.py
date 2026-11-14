"""Integra votos presidenciais e locais de votacao de Divinopolis (2026).

Entradas (geradas por filtrar_divinopolis.py):
    dados/processados/votos_divinopolis_2026.csv
    dados/processados/locais_divinopolis_2026.csv

Saidas:
    dados/processados/votos_localizados_divinopolis_2026.csv
    dados/processados/resumo_secoes_divinopolis_2026.csv

Execute na raiz do projeto: python integrar_dados.py
"""

from pathlib import Path
import pandas as pd


BASE = Path(__file__).resolve().parent / "dados" / "processados"
CHAVE = ["CD_MUNICIPIO", "NR_TURNO", "NR_ZONA", "NR_SECAO"]
CAMPOS_LOCAL = [
    "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_ENDERECO",
    "NM_BAIRRO", "NR_LATITUDE", "NR_LONGITUDE",
]


def ler_csv(nome):
    caminho = BASE / nome
    if not caminho.exists():
        raise FileNotFoundError(
            f"Nao encontrei {caminho}. Rode antes: python filtrar_divinopolis.py"
        )
    return pd.read_csv(caminho, sep=";", encoding="utf-8-sig", dtype=str)


def padronizar_chaves(df, descricao):
    faltam = [col for col in CHAVE if col not in df.columns]
    if faltam:
        raise ValueError(f"{descricao}: faltam as colunas {faltam}. Disponiveis: {list(df.columns)}")
    df = df.copy()
    for col in CHAVE:
        df[col] = pd.to_numeric(df[col].str.strip(), errors="coerce").astype("Int64")
    invalidas = df[CHAVE].isna().any(axis=1)
    if invalidas.any():
        raise ValueError(f"{descricao}: {invalidas.sum()} linhas tem chaves invalidas. Exemplo:\n{df.loc[invalidas, CHAVE].head()}")
    return df


def coordenada(coluna):
    """Converte coordenadas com separador decimal ponto ou virgula."""
    return pd.to_numeric(
        coluna.astype("string").str.strip().str.replace(",", ".", regex=False),
        errors="coerce",
    )


def main():
    votos = padronizar_chaves(ler_csv("votos_divinopolis_2026.csv"), "Votos")
    locais = padronizar_chaves(ler_csv("locais_divinopolis_2026.csv"), "Locais")

    for campo in ["NR_VOTAVEL", "QT_VOTOS"]:
        if campo not in votos.columns:
            raise ValueError(f"Faltou a coluna {campo} no arquivo de votos.")

    # Converter votos e numeros dos candidatos antes de calcular percentuais.
    votos["NR_VOTAVEL"] = pd.to_numeric(votos["NR_VOTAVEL"], errors="coerce").astype("Int64")
    votos["QT_VOTOS"] = pd.to_numeric(votos["QT_VOTOS"], errors="coerce")
    if votos[["NR_VOTAVEL", "QT_VOTOS"]].isna().any().any():
        raise ValueError("Existe numero de candidato ou quantidade de votos invalida.")
    if (votos["QT_VOTOS"] < 0).any():
        raise ValueError("O arquivo contem valores negativos de votos.")
    if "NM_VOTAVEL" not in votos.columns:
        votos["NM_VOTAVEL"] = votos["NR_VOTAVEL"].astype(str)

    # A base dos locais pode repetir uma secao com a mesma informacao.
    # Nunca remover duplicatas conflitantes sem avisar: isso multiplicaria os votos.
    disponiveis = [c for c in CAMPOS_LOCAL if c in locais.columns]
    if not disponiveis:
        raise ValueError("O CSV de locais nao possui informacoes de endereco ou coordenadas.")
    locais = locais[CHAVE + disponiveis].drop_duplicates()
    conflito = locais.duplicated(CHAVE, keep=False)
    if conflito.any():
        exemplo = locais.loc[conflito, CHAVE + disponiveis].head(8)
        raise ValueError(
            "Uma secao tem mais de um registro de local diferente para o mesmo turno.\n"
            "Confira os dados antes de prosseguir. Exemplos:\n" + exemplo.to_string(index=False)
        )

    # Mantem TODAS as linhas de votacao, mesmo quando falta local de votacao.
    integrado = votos.merge(locais, on=CHAVE, how="left", validate="many_to_one", indicator=True)
    sem_local = integrado.loc[integrado["_merge"] == "left_only", CHAVE].drop_duplicates()
    integrado = integrado.drop(columns="_merge")

    if "NR_LATITUDE" in integrado.columns and "NR_LONGITUDE" in integrado.columns:
        integrado["latitude"] = coordenada(integrado["NR_LATITUDE"])
        integrado["longitude"] = coordenada(integrado["NR_LONGITUDE"])
        invalidas = (
            ~integrado["latitude"].between(-90, 90)
            | ~integrado["longitude"].between(-180, 180)
            | ((integrado["latitude"] == 0) & (integrado["longitude"] == 0))
        )
        integrado.loc[invalidas, ["latitude", "longitude"]] = float("nan")
    else:
        integrado["latitude"] = float("nan")
        integrado["longitude"] = float("nan")
        print("AVISO: latitude/longitude nao encontradas na base de locais.")

    # NR_VOTAVEL 95 = branco; 96 = nulo. Numeros de candidatos a
    # Presidencia sao codigos de dois digitos; nao os confundir com esses votos.
    integrado["voto_valido"] = integrado["NR_VOTAVEL"].between(10, 94)
    validos = integrado.loc[integrado["voto_valido"]].copy()

    # Totais de votos validos por turno/zona/secao.
    totais = (
        validos.groupby(CHAVE, as_index=False)["QT_VOTOS"]
        .sum().rename(columns={"QT_VOTOS": "total_validos"})
    )
    # Escolhe lider por secao; empate resolve pelo menor numero do candidato.
    lideres = (
        validos.sort_values(["QT_VOTOS", "NR_VOTAVEL"], ascending=[False, True])
        .drop_duplicates(CHAVE)
        [CHAVE + ["NR_VOTAVEL", "NM_VOTAVEL", "QT_VOTOS"]]
        .rename(columns={
            "NR_VOTAVEL": "numero_lider",
            "NM_VOTAVEL": "candidato_lider",
            "QT_VOTOS": "votos_lider",
        })
    )
    # Um registro por secao e turno, para usar em mapas e indicadores.
    secoes = integrado[CHAVE + disponiveis + ["latitude", "longitude"]].drop_duplicates(CHAVE)
    resumo = secoes.merge(totais, on=CHAVE, how="left", validate="one_to_one")
    resumo = resumo.merge(lideres, on=CHAVE, how="left", validate="one_to_one")
    resumo["total_validos"] = resumo["total_validos"].fillna(0).astype(int)
    resumo["percentual_lider"] = (
        (100 * resumo["votos_lider"] / resumo["total_validos"])
        .where(resumo["total_validos"] > 0)
        .round(2)
    )

    # Guarda os votos por candidato e os indicadores por secao.
    caminho_integrado = BASE / "votos_localizados_divinopolis_2026.csv"
    caminho_resumo = BASE / "resumo_secoes_divinopolis_2026.csv"
    integrado.drop(columns=["voto_valido"]).to_csv(
        caminho_integrado, sep=";", encoding="utf-8-sig", index=False
    )
    resumo.to_csv(caminho_resumo, sep=";", encoding="utf-8-sig", index=False)

    print("\nINTEGRACAO CONCLUIDA")
    print(f"Votos individuais por candidato: {len(integrado)} linhas")
    print(f"Resumo por turno/zona/secao: {len(resumo)} secoes/turnos")
    print("Turnos encontrados:", sorted(resumo["NR_TURNO"].unique().tolist()))
    print("Secoes por turno:")
    print(resumo.groupby("NR_TURNO").size().to_string())
    print(f"Secoes/turnos sem local correspondente: {len(sem_local)}")
    print(f"Secoes/turnos sem coordenadas validas: {resumo['latitude'].isna().sum()}")
    if not sem_local.empty:
        print("Exemplos sem local:\n", sem_local.head(10).to_string(index=False))
    print("Arquivos criados:", caminho_integrado.name, "e", caminho_resumo.name)


if __name__ == "__main__":
    main()
