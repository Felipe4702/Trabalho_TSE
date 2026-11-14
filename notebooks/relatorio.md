
# Analise eleitoral de Divinopolis - 2026

**Disciplina:** Ferramentas para Data Science - UFSJ

**Municipio:** Divinopolis, Minas Gerais

**Objetivo:** analisar a distribuicao espacial dos votos
presidenciais nos dois turnos da eleicao de 2026.

O trabalho utiliza Pandas, GeoPandas e Folium, com dados
obtidos do Portal de Dados Abertos do TSE.


---


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


---


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


---


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


---


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


---


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
