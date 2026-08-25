# Scripts de propagacao

Esta e a versao ativa e corrigida dos scripts de processamento, modelos de
propagacao e visualizacao. A implementacao historica foi preservada em
`scripts_original/` e esta fora do versionamento.

## Correcoes aplicadas

- A linha de visada usa `distance_m = 0` no transmissor e a distancia maxima no receptor.
- A altura do receptor vem de `models/study_parameters.py` em todas as etapas.
- O recálculo de obstrucao usa o maior angulo de terreno entre transmissor e receptor.
- Todos os modelos calculam potencia recebida com potencia do transmissor, ganho de transmissao e ganho de recepcao.
- A conversao de dBd para dBi usa `2,15 dB`.
- Os cabecalhos dos perfis sao normalizados antes de consolidar resultados.

## Execucao

```powershell
python processing/process_txt_profiles.py
python processing/recalculate_obstructions.py
python models/modelo_espaco_livre.py
python models/modelo_lee.py
python models/modelo_hata.py
python models/modelo_walfish_ikegami.py
python models/modelo_analitico.py
python visualize_coverage.py
```

Os perfis e resultados sao gravados em `results/` nesta pasta e sao ignorados
pelo Git, pois podem ser reproduzidos pelos scripts.
Walfisch-Ikegami permanece fora da faixa de validade para os parametros atuais;
ele foi mantido apenas para comparar o efeito das correcoes de implementacao.
O ultimo comando gera `results/coverage_comparison.png`, com relevo,
obstrucoes, anéis de distancia e os cinco modelos na mesma escala de dBm.
