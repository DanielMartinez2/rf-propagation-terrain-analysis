from pathlib import Path
import re
import xml.etree.ElementTree as ET


ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT_DIR / "data" / "raw" / "gpx"
OUTPUT_DIR = ROOT_DIR / "data" / "intermediate" / "gpx_txt_converted"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    arquivos_gpx = sorted(INPUT_DIR.glob("*.gpx"))

    if not arquivos_gpx:
        print(f"Nenhum arquivo .gpx encontrado em: {INPUT_DIR}")
        return

    for arquivo in arquivos_gpx:
        numero_linha = re.sub(r"\D+", "", arquivo.stem) or arquivo.stem
        nome_txt = f"arquivo_{numero_linha}.txt"
        analisa_xml_escreve_txt(arquivo, OUTPUT_DIR / nome_txt)

    print(f"{len(arquivos_gpx)} arquivo(s) GPX convertido(s) para TXT.")


def analisa_xml_escreve_txt(arquivo_gpx: Path, arquivo_saida: Path) -> None:
    mytree = ET.parse(arquivo_gpx)
    myroot = mytree.getroot()
    lat = []
    longitudes = []
    elev = []
    names = []
    description = []
    distance = []
    angles = []

    for wpt in myroot.findall("{http://www.topografix.com/GPX/1/1}wpt"):
        lat_long = wpt.attrib
        elevation = wpt.find("{http://www.topografix.com/GPX/1/1}ele").text
        desc = wpt.find("{http://www.topografix.com/GPX/1/1}desc").text
        name = wpt.find("{http://www.topografix.com/GPX/1/1}name").text
        dist = (
            desc.removeprefix(
                '<table cellspacing="0" cellpadding="2" border="1" style="border-collapse:collapse"><tr><td><b>distance</b></td><td>'
            )
            .removesuffix("</td></tr></table>")
            .rsplit("<td>")[0]
            .removesuffix("</td></tr><tr>")
        )
        angle = (
            desc.removeprefix(
                '<table cellspacing="0" cellpadding="2" border="1" style="border-collapse:collapse"><tr><td><b>distance</b></td><td>'
            )
            .removesuffix("</td></tr></table>")
            .rsplit("<td>")[-1]
        )

        lat.append(lat_long["lat"])
        longitudes.append(lat_long["lon"])
        elev.append(elevation)
        names.append(name)
        description.append(desc)
        distance.append(dist)
        angles.append(angle)

    if distance:
        distance[0] = 0

    header = "type\tlatitude\tlongitude\taltitude (m)\tdistance (km)\tname\tdesc\tangle \n"
    with arquivo_saida.open("w", encoding="utf-8") as file:
        file.write(header)
        for i in range(len(lat)):
            linha = (
                f"W\t{lat[i]}\t{longitudes[i]}\t{elev[i]}\t{distance[i]}\t"
                f"{names[i]}\t{description[i]}\t{angles[i]} \n"
            )
            file.write(linha)


if __name__ == "__main__":
    main()
