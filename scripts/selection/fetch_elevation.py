from pathlib import Path
import os

import googlemaps
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT_DIR / "data" / "auxiliary" / "coordenadas_geo.csv"
OUTPUT_FILE = ROOT_DIR / "data" / "auxiliary" / "coordenadas_geo_atualizado.csv"
API_KEY_ENV = "GOOGLE_MAPS_API_KEY"


def main() -> None:
    api_key = os.getenv(API_KEY_ENV)
    if not api_key:
        raise EnvironmentError(f"Defina a variavel de ambiente {API_KEY_ENV} antes de executar este script.")

    gmaps = googlemaps.Client(key=api_key)
    df = pd.read_csv(INPUT_FILE, sep=";")
    new_df = df.drop(columns="Altitude", axis=1, errors="ignore")

    lat = df[df.keys()[0]].values.tolist()
    lng = df[df.keys()[1]].values.tolist()
    list_tuples_lat_lng = list(zip(lat, lng))
    elevation = gmaps.elevation(locations=list_tuples_lat_lng)
    alt = [item["elevation"] for item in elevation]

    new_df.insert(2, "Altitude", alt)
    new_df.to_csv(OUTPUT_FILE, sep=";", index=False)
    print(f"Arquivo atualizado salvo em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
