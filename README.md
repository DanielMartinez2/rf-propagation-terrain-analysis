# Linhas TXT

Projeto para processamento de perfis de linha, analise de obstrucao e comparacao entre modelos de propagacao a partir de arquivos GPX/TXT.

## Estrutura do repositorio

```text
linhas_txt/
|-- data/
|   |-- raw/gpx/
|   |-- intermediate/gpx_txt_converted/
|   |-- processed/line_profiles/
|   |-- processed/corrected_profiles/
|   |-- selected/calculation_points/
|   `-- auxiliary/
|-- results/propagation_models/
|-- results/selected_points/
|-- scripts/
|   |-- processing/
|   |-- models/
|   |-- selection/
|   `-- archive/
`-- docs/
```

## Fluxo do projeto

1. Coloque arquivos `.gpx` em `data/raw/gpx/`.
2. Execute `scripts/processing/convert_gpx_to_txt.py` para gerar os TXT intermediarios.
3. Execute `scripts/processing/process_txt_profiles.py` para montar os perfis de linha.
4. Execute `scripts/processing/recalculate_obstructions.py` para recalcular as obstrucoes.
5. Execute os scripts em `scripts/models/` para gerar as comparacoes de propagacao em `results/propagation_models/`.

## Scripts principais

- `scripts/processing/convert_gpx_to_txt.py`: converte arquivos GPX para TXT.
- `scripts/processing/process_txt_profiles.py`: trata os perfis e gera distancia, obstrucao e colunas auxiliares.
- `scripts/processing/recalculate_obstructions.py`: recalcula obstrucoes com ajuste adicional.
- `scripts/models/`: contem os modelos de espaco livre, Lee, Okumura-Hata, Walfish-Ikegami e um modelo analitico.
- `scripts/selection/`: contem utilitarios para selecionar pontos e atualizar altitudes.
- `results/selected_points/`: recebe os CSVs derivados da selecao de pontos.

## Dependencias

Instale as dependencias com:

```bash
pip install -r requirements.txt
```

## Parametros do estudo

Os dados da antena e do transmissor ficam centralizados em
`scripts/models/study_parameters.py`. Para analisar outra instalacao, ajuste
esse arquivo antes de executar o fluxo: altura da antena, cota do terreno do
transmissor, altura do receptor, potencia, frequencia e ganhos.

## Chave da API do Google Maps

O script `scripts/selection/fetch_elevation.py` nao guarda mais chave no codigo. Antes de executar, defina:

```bash
set GOOGLE_MAPS_API_KEY=sua_chave
```

No PowerShell:

```powershell
$env:GOOGLE_MAPS_API_KEY="sua_chave"
```

## Observacoes

- O ambiente local foi movido para `.venv/` e esta ignorado no Git.
- Arquivos `*_generated` podem aparecer quando um arquivo final ja estiver em uso; eles tambem estao ignorados no Git.
- Os arquivos em `scripts/archive/` foram mantidos como historico de experimentos.
- O inventario resumido dos arquivos esta em `docs/project_inventory.md`.
