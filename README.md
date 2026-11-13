# Trabalho TSE — Eleições Presidenciais 2026 em Divinópolis/MG

Atividade de Ferramentas para Data Science (UFSJ): tratamento de dados eleitorais do TSE,
mapas interativos com **Folium** e dashboard com **Streamlit**.

## Organização

```text
Trabalho_TSE/
├── dados/
│   ├── brutos/          # ZIPs oficiais do TSE (locais, ignorados pelo Git)
│   └── processados/     # CSVs filtrados para Divinópolis
├── notebooks/           # Análise em Jupyter (.ipynb)
├── mapas/               # Mapas exportados (.html)
├── filtrar_divinopolis.py
├── environment.yml      # Ambiente Conda
├── requirements.txt     # Dependências para deploy futuro
├── .gitignore
└── README.md
```

## Configuração

```bash
conda env create -f environment.yml
conda activate eleicoes2026
```

## Dados oficiais

Baixe os arquivos oficiais do [Portal de Dados Abertos do TSE](https://dadosabertos.tse.jus.br/):

- **Votação presidencial por seção (2026)**: `votacao_secao_2026_BR.zip`
- **Eleitorado por local de votação (2026)**: `eleitorado_local_votacao_2026.zip`

Coloque ambos os arquivos ZIP, sem extrair, na pasta `dados/brutos/`.

Os ZIPs oficiais podem ser grandes e estão excluídos do Git pelo `.gitignore`.
Após a filtragem, os CSVs reduzidos de Divinópolis podem ser versionados para
permitir a reprodução das visualizações e o deploy do dashboard.

## Gerar os dados de Divinópolis

Execute a partir da pasta raiz do repositório:

```bash
python filtrar_divinopolis.py
```

Arquivos esperados:

- `dados/processados/votos_divinopolis_2026.csv`
- `dados/processados/locais_divinopolis_2026.csv`

## Próximas etapas

- Validar os CSVs gerados e relacionar votação com localização por zona/seção.
- Desenvolver os mapas em Folium e as análises no notebook Jupyter.
- Criar o dashboard Streamlit e publicá-lo no Community Cloud.

> Os ZIPs completos são obtidos na fonte oficial; este repositório não é um espelho
> integral da base nacional do TSE.
