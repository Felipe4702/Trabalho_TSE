# Trabalho_TSE — Análise Eleitoral de Divinópolis (2026)

Projeto desenvolvido para a disciplina **Ferramentas para Data Science**, da Universidade Federal de São João del-Rei (UFSJ), ministrada pela professora Carolina Xavier.

O objetivo é analisar a distribuição espacial dos votos da eleição presidencial de 2026 no município de **Divinópolis, Minas Gerais**, considerando o primeiro e o segundo turnos.

O trabalho utiliza dados oficiais do Tribunal Superior Eleitoral (TSE), processamento em Python e mapas interativos construídos com Folium.

## 1. Situação atual do projeto

| Etapa | Situação |
|---|---|
| Obtenção dos dados eleitorais do TSE | Concluído |
| Filtragem dos dados de Divinópolis | Concluído |
| Integração de votos e locais de votação | Concluído |
| Mapas do primeiro turno | Concluído |
| Mapa comparativo do segundo turno | Concluído |
| Tooltips e popups por seção eleitoral | Implementados |
| Relatório de análise eleitoral | Pendente |
| Jupyter Notebook com relatório | Pendente |
| Dashboard Streamlit | Pendente |
| Deploy no Streamlit Community Cloud | Pendente |

## 2. Tecnologias utilizadas

- **Python:** linguagem principal.
- **Pandas:** leitura, limpeza, filtragem e agrupamento dos dados.
- **GeoPandas:** manipulação das informações geográficas.
- **Folium:** geração dos mapas interativos.
- **Shapely:** construção de polígonos de Voronoi.
- **Conda:** gerenciamento do ambiente e das dependências.
- **Streamlit:** framework previsto para o dashboard.
- **Plotly:** gráficos interativos previstos para o dashboard.

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
│
├── filtrar_divinopolis.py
├── integrar_dados.py
├── gerar_mapas_primeiro_turno.py
├── gerar_mapa_segundo_turno.py
│
├── environment.yml
├── requirements.txt
├── .gitignore
└── README.md
```

Os arquivos ZIP originais do TSE são mantidos localmente e não são enviados ao GitHub devido ao tamanho. Os dados processados de Divinópolis são utilizados para reproduzir as visualizações.

## 4. Como visualizar os mapas

**Os mapas HTML já estão gerados e não precisam ser recriados para visualização.**

O GitHub armazena os arquivos HTML, mas não apresenta automaticamente os mapas interativos ao clicar neles.

Para visualizar os resultados, é possível clonar o repositório e iniciar um servidor local.

### Passo 1 — Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/Trabalho_TSE.git
cd Trabalho_TSE
```

Substitua `SEU_USUARIO` pelo proprietário do repositório.

### Passo 2 — Iniciar o servidor

Com Python instalado, execute na raiz do projeto:

```bash
python -m http.server 8000 --bind 127.0.0.1
```

O terminal deverá indicar que o servidor está funcionando na porta 8000.

Mantenha o terminal aberto enquanto estiver visualizando os mapas.

**Não é necessário instalar Folium, Pandas ou Conda apenas para abrir os HTMLs já gerados.**

### Passo 3 — Abrir os mapas no navegador

**Primeiro turno — Lula**

http://127.0.0.1:8000/mapas/primeiro_turno/primeiro_turno_candidato_13.html

**Primeiro turno — Flávio Bolsonaro**

http://127.0.0.1:8000/mapas/primeiro_turno/primeiro_turno_candidato_22.html

**Segundo turno — Comparativo**

http://127.0.0.1:8000/mapas/segundo_turno/segundo_turno_comparativo.html

Esses endereços funcionam no computador em que o servidor foi iniciado. Eles não são links públicos da internet.

É necessário ter conexão com a internet para carregar as imagens do mapa-base OpenStreetMap.

Para encerrar o servidor, pressione `Ctrl + C` no terminal.

## 5. Como utilizar os mapas

### Primeiro turno

Foram gerados dois mapas separados:

- Lula: regiões representadas em tons de vermelho.
- Flávio Bolsonaro: regiões representadas em tons de azul.

A intensidade da cor representa o percentual de votos válidos recebido pelo candidato em cada local de votação.

Quanto maior o percentual, mais intensa será a cor.

### Segundo turno

Foi criado um único mapa comparativo utilizando uma escala divergente:

- **Azul:** vantagem de Flávio Bolsonaro.
- **Vermelho:** vantagem de Lula.
- **Branco/cinza:** votação equilibrada.
- **Cores mais intensas:** maior vantagem do candidato correspondente.

O mapa permite visualizar as diferenças espaciais entre os resultados dos dois candidatos finalistas.

### Interatividade

Nos três mapas, é possível:

1. Aproximar e afastar o mapa.
2. Passar o mouse sobre as regiões para visualizar informações eleitorais.
3. Consultar zona, seção, candidato líder e percentual de votos em tooltips.
4. Clicar nos marcadores para abrir tabelas completas com os resultados das seções.
5. Utilizar o controle de camadas para ativar ou desativar elementos.

## 6. Metodologia geográfica

Os dados oficiais do TSE permitem identificar as seções eleitorais e seus respectivos locais de votação.

Entretanto, não são fornecidos limites geográficos individuais para cada seção.

Por isso, os mapas utilizam **diagramas de Voronoi**, construídos a partir das coordenadas dos locais de votação.

Esses diagramas dividem o espaço em regiões de proximidade. Cada região está associada ao local de votação mais próximo.

Para evitar regiões excessivamente grandes, os polígonos são limitados a uma faixa de aproximadamente 1.200 metros dos locais de votação.

**Importante:** os polígonos são aproximações geográficas e não representam limites eleitorais oficiais, bairros ou áreas de residência dos eleitores.

Quando várias seções compartilham uma coordenada, seus votos são agregados para determinar a cor da região. Os resultados individuais continuam disponíveis nos tooltips e popups.
