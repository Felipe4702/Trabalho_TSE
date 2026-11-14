# Trabalho_TSE — Análise Eleitoral de Divinópolis (2026)

O objetivo é analisar a distribuição espacial dos votos da eleição presidencial de 2026 no município de **Divinópolis, Minas Gerais**, considerando o primeiro e o segundo turnos.

O trabalho utiliza dados oficiais do Tribunal Superior Eleitoral (TSE), processamento e análise em Python, mapas interativos com Folium e um dashboard web desenvolvido com Streamlit.

## Dashboard interativo

**[Acessar o Dashboard Eleitoral de Divinópolis 2026](https://trabalhotse-47.streamlit.app/)**

O dashboard permite visualizar os resultados eleitorais diretamente pelo navegador, sem necessidade de instalar Python, Conda ou executar qualquer código.

A aplicação contém:

- Mapas interativos do primeiro e segundo turnos.
- Indicadores de votos válidos, brancos e nulos.
- Resultados por candidato e zona eleitoral.
- Gráficos comparativos entre os turnos.
- Filtros para seleção de turno, candidato e zona eleitoral.
- Tabelas detalhadas dos resultados por seção.
- Informações sobre a metodologia e as fontes dos dados.

Os filtros de zona eleitoral afetam os indicadores, gráficos e tabelas. Os mapas HTML apresentam a visão geral do município.

## 1. Situação atual do projeto

| Etapa | Situação |
|---|---|
| Obtenção dos dados eleitorais do TSE | Concluído |
| Filtragem dos dados de Divinópolis | Concluído |
| Integração de votos e locais de votação | Concluído |
| Mapas do primeiro turno | Concluído |
| Mapa comparativo do segundo turno | Concluído |
| Tooltips e popups por seção eleitoral | Concluído |
| Relatório de análise eleitoral | Elaborado |
| Jupyter Notebook com análises | Elaborado |
| Dashboard Streamlit | Concluído |
| Deploy no Streamlit Community Cloud | Publicado |

## 2. Tecnologias utilizadas

- **Python:** linguagem principal utilizada no desenvolvimento.
- **Pandas:** leitura, limpeza, filtragem, agrupamento e análise dos dados eleitorais.
- **GeoPandas:** processamento e manipulação de informações geográficas.
- **Folium:** construção dos mapas interativos.
- **Shapely:** geração dos polígonos de Voronoi.
- **Plotly:** criação dos gráficos interativos.
- **Streamlit:** desenvolvimento e publicação do dashboard web.
- **Jupyter Notebook:** documentação do processamento e das análises.
- **Conda:** gerenciamento do ambiente de desenvolvimento.
- **Git e GitHub:** versionamento e disponibilização do projeto.

## 3. Estrutura do projeto

```text
Trabalho_TSE/
│
├── dados/
│   ├── brutos/
│   └── processados/
│       ├── locais_divinopolis_2026.csv
│       ├── votos_divinopolis_2026.csv
│       ├── votos_localizados_divinopolis_2026.csv
│       └── resumo_secoes_divinopolis_2026.csv
│
├── mapas/
│   ├── primeiro_turno/
│   │   ├── primeiro_turno_candidato_13.html
│   │   └── primeiro_turno_candidato_22.html
│   │
│   └── segundo_turno/
│       └── segundo_turno_comparativo.html
│
├── notebooks/
│   ├── analise_eleitoral_divinopolis.ipynb
│   └── relatorio.md
│
├── app.py
├── filtrar_divinopolis.py
├── integrar_dados.py
├── gerar_mapas_primeiro_turno.py
├── gerar_mapa_segundo_turno.py
├── gerar_notebook.py
│
├── ambiente/
│   └── environment.yml
│
├── requirements.txt
├── .gitignore
└── README.md
```

Os arquivos ZIP originais do TSE são mantidos localmente e não são enviados ao GitHub devido ao tamanho.

Os arquivos processados de Divinópolis são disponibilizados para permitir a reprodução das análises e dos mapas.

## 4. Como visualizar os resultados

Existem três maneiras de consultar os resultados do projeto.

### Opção 1 — Dashboard público (recomendado)

A maneira mais simples é acessar:

**https://trabalhotse-47.streamlit.app**

O dashboard reúne os mapas, gráficos, indicadores e tabelas eleitorais.

Não é necessário baixar o repositório ou instalar bibliotecas.

### Opção 2 — Visualizar os arquivos HTML localmente

Os três mapas Folium também estão disponíveis separadamente em arquivos HTML.

Para visualizá-los, primeiro clone o repositório:

```bash
git clone https://github.com/felipe4702/trabalho_tse.git
cd trabalho_tse
```

Em seguida, com Python instalado, inicie um servidor local na raiz do projeto:

```bash
python -m http.server 8000 --bind 127.0.0.1
```

Mantenha o terminal aberto enquanto estiver utilizando os mapas.

Agora acesse os seguintes endereços no navegador:

**Primeiro turno — Lula**

http://127.0.0.1:8000/mapas/primeiro_turno/primeiro_turno_candidato_13.html

**Primeiro turno — Flávio Bolsonaro**

http://127.0.0.1:8000/mapas/primeiro_turno/primeiro_turno_candidato_22.html

**Segundo turno — Comparativo**

http://127.0.0.1:8000/mapas/segundo_turno/segundo_turno_comparativo.html

Esses endereços funcionam apenas no computador em que o servidor local está sendo executado.

Não é necessário instalar Folium, Pandas ou Conda somente para visualizar os arquivos HTML já gerados.

É necessária conexão com a internet para carregar o mapa-base OpenStreetMap e outros recursos externos utilizados pelo Folium.

Para encerrar o servidor, pressione `Ctrl + C` no terminal.

### Opção 3 — Consultar o Jupyter Notebook

O notebook está disponível em:

`notebooks/analise_eleitoral_divinopolis.ipynb`

Ele apresenta o processamento e a análise dos dados eleitorais, contendo células Python, tabelas de resultados e explicações em Markdown.

O relatório também pode ser consultado separadamente em:

`notebooks/relatorio.md`

Para executar o notebook, é necessário configurar o ambiente Python descrito na seção 8.

## 5. Resultados eleitorais

A análise considera as zonas eleitorais 102 e 103 de Divinópolis, totalizando 501 seções por turno.

### Primeiro turno

| Indicador | Resultado |
|---|---:|
| Votos válidos | 132.409 |
| Flávio Bolsonaro | 71.478 (53,98%) |
| Lula | 49.403 (37,31%) |
| Outros candidatos | 11.528 (8,71%) |
| Votos brancos | 3.081 |
| Votos nulos | 4.206 |

### Segundo turno

| Indicador | Resultado |
|---|---:|
| Votos válidos | 139.034 |
| Flávio Bolsonaro | 76.540 (55,05%) |
| Lula | 62.494 (44,95%) |
| Votos brancos | 1.827 |
| Votos nulos | 3.211 |

Flávio Bolsonaro apresentou a maior votação no município nos dois turnos.

A diferença entre os candidatos diminuiu de 22.075 votos no primeiro turno para 14.046 votos no segundo turno.

A participação de Lula passou de 37,31% para 44,95% dos votos válidos. Entretanto, esses resultados agregados não permitem determinar o comportamento individual dos eleitores entre os turnos.

## 6. Como utilizar os mapas

### Primeiro turno

Foram gerados dois mapas separados:

- **Lula:** regiões em tons de vermelho.
- **Flávio Bolsonaro:** regiões em tons de azul.

A intensidade da cor representa o percentual de votos válidos recebido pelo candidato em cada local de votação.

Quanto maior o percentual, mais intensa será a cor.

As escalas são sequenciais e permitem comparar a intensidade da votação entre diferentes locais.

### Segundo turno

Foi criado um único mapa comparativo utilizando uma escala divergente:

- **Azul:** vantagem de Flávio Bolsonaro.
- **Vermelho:** vantagem de Lula.
- **Branco/cinza:** resultados próximos do equilíbrio.
- **Cores mais intensas:** maior vantagem do candidato correspondente.

A escala permite visualizar diferenças espaciais entre os resultados dos candidatos finalistas.

### Recursos interativos

Nos três mapas, é possível:

1. Aproximar e afastar a visualização.
2. Passar o mouse sobre uma região colorida para consultar os resultados das seções.
3. Visualizar zona, seção, candidato líder e percentual de votos em tooltips personalizados.
4. Clicar nos marcadores para abrir tabelas completas com os resultados das seções associadas ao local.
5. Clicar nas regiões para consultar os resultados agregados do local.
6. Ativar ou desativar elementos pelo controle de camadas do Folium.

## 7. Metodologia geográfica

Os dados oficiais do TSE identificam as seções eleitorais e seus respectivos locais de votação.

Entretanto, a base utilizada não fornece os limites geográficos individuais de cada seção eleitoral.

Por isso, os mapas utilizam **diagramas de Voronoi**, construídos com base nas coordenadas dos locais de votação.

O Voronoi divide o espaço em regiões de proximidade, associando cada área ao ponto geográfico mais próximo.

Para evitar regiões excessivamente extensas, os polígonos são limitados a uma faixa de aproximadamente 1.200 metros dos locais de votação.

O processamento geográfico utiliza o sistema de coordenadas UTM 23S (EPSG:32723) para realizar os cálculos de distância em metros.

### Agregação dos votos

Quando várias seções compartilham a mesma coordenada geográfica, seus votos são agregados para determinar a cor da região.

Entretanto, os resultados individuais das seções permanecem disponíveis nos tooltips e popups.

**Importante:** os polígonos de Voronoi são aproximações geográficas. Não representam limites eleitorais oficiais, bairros ou áreas de residência dos eleitores.

Assim, os mapas permitem analisar a distribuição dos resultados por local de votação, mas não identificar diretamente as preferências eleitorais dos moradores de cada região.

## 8. Como executar o projeto Python

### Criar o ambiente Conda

Com Conda instalado, execute na raiz do repositório:

```bash
conda env create -f ambiente/environment.yml
conda activate eleicoes2026
```

O arquivo `environment.yml` contém as dependências necessárias ao processamento geográfico.

### Preparar os dados

Para executar novamente o processamento desde os arquivos originais do TSE:

```bash
python filtrar_divinopolis.py
python integrar_dados.py
```

Os arquivos ZIP originais devem estar disponíveis na pasta `dados/brutos/`.

Caso os CSVs processados já estejam disponíveis, não é necessário repetir essas etapas.

### Gerar os mapas

Execute:

```bash
python gerar_mapas_primeiro_turno.py
python gerar_mapa_segundo_turno.py
```

Os três arquivos HTML serão atualizados automaticamente nas pastas `mapas/primeiro_turno/` e `mapas/segundo_turno/`.

### Gerar o notebook e o relatório

Execute:

```bash
python gerar_notebook.py
```

Esse comando gera os arquivos `.ipynb` e `.md` na pasta `notebooks/`.

O notebook pode ser aberto no VS Code com a extensão Jupyter.

### Executar o dashboard localmente

Com as dependências instaladas:

```bash
streamlit run app.py
```

O aplicativo será disponibilizado localmente, normalmente no endereço:

http://localhost:8501

O dashboard utiliza os CSVs processados e os mapas HTML já gerados.

## 9. Publicação no Streamlit Community Cloud

O dashboard foi publicado utilizando o Streamlit Community Cloud, integrado ao repositório do projeto no GitHub.

A plataforma instala as dependências necessárias, executa o arquivo `app.py` e disponibiliza a aplicação através de um endereço público.

**Link da aplicação:**

https://trabalhotse-eleicoes-divinopolis-2026-47.streamlit.app/

O dashboard é atualizado a partir do código disponível na branch utilizada para a publicação.

## 10. Origem dos dados

Os dados utilizados são provenientes do **Portal de Dados Abertos do Tribunal Superior Eleitoral (TSE)**.

Fonte oficial:

https://dadosabertos.tse.jus.br/

Foram utilizadas informações referentes a:

- Votação por seção eleitoral — eleições presidenciais de 2026.
- Eleitorado por local de votação — 2026.

O processamento considera o município de Divinópolis/MG, as zonas eleitorais 102 e 103 e os dois turnos da eleição presidencial.

## 11. Finalidade acadêmica

O projeto foi desenvolvido para fins acadêmicos, com foco em:

- Tratamento e integração de bases de dados.
- Análise exploratória de resultados eleitorais.
- Manipulação de informações geográficas.
- Construção de visualizações interativas.
- Desenvolvimento de dashboards com Python.
- Divulgação e reprodutibilidade de análises de dados.

Os resultados apresentados são baseados nos dados do TSE utilizados no trabalho e devem ser interpretados considerando as limitações metodológicas descritas neste documento.

