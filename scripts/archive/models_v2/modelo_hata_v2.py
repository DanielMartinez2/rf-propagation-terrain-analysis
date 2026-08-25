from pathlib import Path

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[3]
INPUT_DIR = ROOT_DIR / "data" / "selected" / "calculation_points"
OUTPUT_FILE = ROOT_DIR / "results" / "propagation_models" / "tabela_modelo_hata.csv"


def main() -> None:
    arquivos = sorted(INPUT_DIR.glob("Line *.txt"))
    lista1 = []
    lista_3k = list(range(3000, 69960, 3000))

    for arquivo in arquivos:
        aux = analisa_txt(arquivo)
        df = pd.DataFrame(aux, columns=[arquivo.stem.replace(" ", "_")], index=lista_3k)
        lista1.append(df)

    new_df = pd.concat(lista1, sort=False, axis=1)
    new_df.to_csv(OUTPUT_FILE, sep=";", index=True)
    print(f"Resultado salvo em: {OUTPUT_FILE}")

def analisa_txt(caminho_arquivo: Path):
    df = pd.read_table(caminho_arquivo, sep=";")
    lista_3k_dBm = []
    altitude = df['altitude (m)'].values.tolist()
    distance_m = df['distance_m'].values.tolist()
    antena = 155.98
    cota_tx = 825.8
    soma_cot_tx = antena + cota_tx

    A_rx = 9.1

    P_rx = []    
    P_tx_Watts = 15000
    log_P_tx = 10*np.log10(P_tx_Watts)
    G_rx_dBi = 2.15
    G_tx_dBd = 9.29
    G_tx_dBi = G_tx_dBd + 2.5
    freq_MHz = 509
    log_freq = np.log10(freq_MHz)
    A_hrx = 3.2 * np.log10(11.75*A_rx)**2 - 4.97
    lista_3k = list(range(3000, 69960, 3000))
    
    for i in range(0, len(altitude)-1):
        tg_teta = (soma_cot_tx - altitude[i] - A_rx)/distance_m[i]
        x = tg_teta*distance_m[i]        
        
        hipotenusa = np.sqrt(x**2 + distance_m[i]**2)
        loss = 69.55 + 26.16*log_freq - 13.82*np.log10(antena) - A_hrx + (44.9-6.55*np.log10(antena))*np.log10(hipotenusa/1000)
        log_Prx = log_P_tx - loss
        Prx_W = 10**(log_Prx/10)
        Prx_dBm = 10*np.log10(Prx_W*1000)
        P_rx.append(Prx_dBm)

        if distance_m[i] in lista_3k:
            lista_3k_dBm.append(Prx_dBm)
    P_rx.append(P_rx[-1])
    lista_3k_dBm = reversed(lista_3k_dBm)     
    df.insert(7, "Okumura Hata", P_rx)

    return lista_3k_dBm
    
    
     
    
    
    #path_destino = './Corrigidos/{}.txt'.format(nome_arquivo.removesuffix('.txt'))
    #new_df = df.to_csv(path_or_buf=path_destino,sep=';', index=False)

if __name__ == "__main__":
    main()










