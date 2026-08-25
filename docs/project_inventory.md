# Inventario do Projeto

## Resumo por categoria

- Codigo Python: 16 arquivos
- Dados TXT: 1095 arquivos
- Dados CSV: 3 arquivos
- Documentos PDF: 3 arquivos
- Ambiente local: `.venv/` (ignorado no Git)
- Arquivos `*_generated`: saidas auxiliares de validacao, ignoradas no Git

## Organizacao atual

### Codigo

- `scripts/processing/`: 3 scripts de conversao e tratamento
- `scripts/models/`: 5 scripts de modelos de propagacao
- `scripts/selection/`: 3 scripts utilitarios
- `scripts/archive/`: 5 scripts de experimentos antigos

### Dados

- `data/raw/gpx/`: pasta reservada para entradas GPX futuras
- `data/intermediate/gpx_txt_converted/`: 357 arquivos TXT convertidos a partir de GPX
- `data/processed/line_profiles/`: 357 arquivos TXT de perfis tratados
- `data/processed/corrected_profiles/`: 357 arquivos TXT com obstrucao recalculada
- `data/selected/calculation_points/`: 18 arquivos TXT de linhas selecionadas
- `data/auxiliary/`: arquivos auxiliares de coordenadas geograficas

### Resultados

- `results/propagation_models/`: 5 resultados TXT e 3 tabelas PDF
- `results/selected_points/`: 2 arquivos CSV gerados a partir da selecao de pontos

## Leitura da estrutura

O repositorio agora separa claramente:

- entrada de dados
- processamento
- selecao de pontos
- resultados finais
- experimentos historicos

Essa divisao facilita publicar o projeto no GitHub e explicar o fluxo de trabalho para outras pessoas.
