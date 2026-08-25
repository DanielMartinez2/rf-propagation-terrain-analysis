from pathlib import Path
import math


ROOT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_FILE = ROOT_DIR / "data" / "auxiliary" / "coordenadas_geo.txt"


def calcular_novos_pontos(latitude_inicial: float, longitude_inicial: float, distancia_km: float):
    raio_terra_km = 6371.0
    latitude_inicial_rad = math.radians(latitude_inicial)
    longitude_inicial_rad = math.radians(longitude_inicial)
    novas_localizacoes = []
    lat = []
    lng = []

    for angulo in range(360):
        angulo_rad = math.radians(angulo)
        nova_latitude_rad = math.asin(
            math.sin(latitude_inicial_rad) * math.cos(distancia_km / raio_terra_km)
            + math.cos(latitude_inicial_rad) * math.sin(distancia_km / raio_terra_km) * math.cos(angulo_rad)
        )
        nova_longitude_rad = longitude_inicial_rad + math.atan2(
            math.sin(angulo_rad) * math.sin(distancia_km / raio_terra_km) * math.cos(latitude_inicial_rad),
            math.cos(distancia_km / raio_terra_km) - math.sin(latitude_inicial_rad) * math.sin(nova_latitude_rad),
        )

        nova_latitude = math.degrees(nova_latitude_rad)
        nova_longitude = math.degrees(nova_longitude_rad)
        lat.append(nova_latitude)
        lng.append(nova_longitude)
        novas_localizacoes.append((nova_latitude, nova_longitude))

    return novas_localizacoes, lat, lng


def main() -> None:
    latitude_inicial = -23.550520
    longitude_inicial = -46.633308
    distancia_km = 70
    _, lat, lng = calcular_novos_pontos(latitude_inicial, longitude_inicial, distancia_km)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        file.write("Latitude; Longitude\n")
        for latitude, longitude in zip(lat, lng):
            file.write(f"{latitude};{longitude}\n")

    print(f"Coordenadas salvas em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
