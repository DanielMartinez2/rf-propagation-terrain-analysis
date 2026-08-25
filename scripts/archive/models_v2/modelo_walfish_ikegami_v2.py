from pathlib import Path

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[3]
INPUT_DIR = ROOT_DIR / "data" / "selected" / "calculation_points"
OUTPUT_FILE = ROOT_DIR / "results" / "propagation_models" / "tabela_walfish_ikegami.csv"


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
    obstruct = df['obstrucao'].values.tolist()
    
    antena = 155.98
    cota_tx = 825.8
    soma_cot_tx = antena + cota_tx

    A_rx = 9.1

    P_rx = []    
    P_tx_Watts = 15000
    log_P_tx = 10*np.log10(P_tx_Watts)
    G_rx_dBi = 2.15
    G_rx_dBd = G_rx_dBi - 2.5
    G_tx_dBd = 9.29
    G_tx_dBi = G_tx_dBd + 2.5
    freq_MHz = 509
    log_freq = np.log10(freq_MHz)
    freq_Hz = freq_MHz * 10**6
    c_metro_seg = 299792458
    lambda1 = c_metro_seg/freq_Hz
    b = 35
    w = b/2
    fi = 90
    n = 16
    Hroof = 3*n + 3
    L_ori = 4.0 - 0.114*(fi-55)
    hm = A_rx
    delta_hm = Hroof - hm
    delta_hb = antena - Hroof
    ka = 54
    kd = 18
    kf = -4 + 1.5*(freq_MHz/925 - 1)
    lista_3k = list(range(3000, 69960, 3000))

    
    for i in range(0, len(altitude)-1):
        tg_teta = (soma_cot_tx - altitude[i] - A_rx)/distance_m[i]
        x = tg_teta*distance_m[i]        
        
        hipotenusa = np.sqrt(x**2 + distance_m[i]**2)
        
        if(obstruct[i] == 0):
            Lp = 43.6 + 26*np.log10(hipotenusa/1000) + 20*log_freq
            
        else:
                     
            L0 = 32.45 + 20*np.log10(hipotenusa/1000) + 20*np.log10(freq_MHz)
            
            L_rts = -16.9 - 10*np.log10(w) + 10*log_freq + 20*np.log10(delta_hm) + L_ori
            Lbsh = -18*np.log10(1+delta_hb)
            L_msd = Lbsh + ka + kd*np.log10(hipotenusa/1000) + kf*log_freq - 9*np.log10(b)
            
            if (L_rts + L_msd >= 0):
                Lp = L0 + L_rts + L_msd
                
            elif (L_rts + L_msd < 0):
                Lp = L0            
        Prx_dbm = 10*np.log10(P_tx_Watts*1000) - Lp
        P_rx.append(Prx_dbm)               
        if distance_m[i] in lista_3k:
            lista_3k_dBm.append(Prx_dbm)

    P_rx.append(P_rx[-1])    
    df.insert(7, 'Walfish Ikegami', P_rx)
    lista_3k_dBm = reversed(lista_3k_dBm) 
    
    return lista_3k_dBm
 

if __name__ == "__main__":
    main()










