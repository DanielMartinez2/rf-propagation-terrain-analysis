from pathlib import Path

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[3]
INPUT_DIR = ROOT_DIR / "data" / "selected" / "calculation_points"
OUTPUT_FILE = ROOT_DIR / "results" / "propagation_models" / "tabela_espaco_livre.csv"


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
    lista_3k_dist = []
    A_rx = 9.1

    P_rx = []    
    P_tx_Watts = 15000
    G_rx_dBi = 2.15
    G_tx_dBd = 9.29
    G_tx_dBi = G_tx_dBd + 2.5
    freq_Hz = 509 * 10**6
    c_metro_seg = 299792458
    lambda1 = c_metro_seg/freq_Hz
    '''lambda_quad = lambda1**2
    G_tx_Watts = 10**(G_tx_dBi/10) * 0.001
    G_rx_Watts = 10**(G_rx_dBi/10) * 0.001
    pi_2 = (4*np.pi) **2'''
    lista_3k = list(range(3000, 69960, 3000))
    for i in range(0, len(altitude)-1):
        tg_teta = (soma_cot_tx - altitude[i] - A_rx)/distance_m[i]
        x = tg_teta*distance_m[i]        

        hipotenusa = np.sqrt(x**2 + distance_m[i]**2)
            
        P_rx_tf = 10*np.log10(P_tx_Watts) + G_rx_dBi + G_tx_dBi + 20*np.log10(lambda1) - 20*np.log10(4*np.pi) - 20*np.log10(hipotenusa)
        P_rx_W = 10**(P_rx_tf/10)
        P_rx_dBm = 10*np.log10(P_rx_W*1000)
        
        P_rx.append(P_rx_dBm)
        if distance_m[i] in lista_3k:
            lista_3k_dBm.append(P_rx_dBm)
            lista_3k_dist.append(altitude[i])
    P_rx.append(P_rx[-1])    
    lista_3k_dBm = reversed(lista_3k_dBm)       
    df.insert(7, "Espaco Livre", P_rx)
    return lista_3k_dBm
     
    
    
    #path_destino = './Corrigidos/{}.txt'.format(nome_arquivo.removesuffix('.txt'))
    #new_df = df.to_csv(path_or_buf=path_destino,sep=';', index=False)

if __name__ == "__main__":
    main()










