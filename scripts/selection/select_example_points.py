from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT_DIR / "data" / "selected" / "calculation_points"
OUTPUT_FILE = ROOT_DIR / "results" / "selected_points" / "pontos_selecionados.csv"


def salvar_dataframe(df: pd.DataFrame, output_path: Path) -> Path:
    try:
        df.to_csv(output_path, sep=";", index=False)
        return output_path
    except PermissionError:
        fallback_path = output_path.with_name(f"{output_path.stem}_generated{output_path.suffix}")
        df.to_csv(fallback_path, sep=";", index=False)
        return fallback_path


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    arquivos = sorted(INPUT_DIR.glob("Line *.txt"))
    if not arquivos:
        print(f"Nenhuma linha de exemplo encontrada em: {INPUT_DIR}")
        return

    lista_pontos = []
    for arquivo in arquivos:
        df = pd.read_csv(arquivo, sep=";")
        lista_pontos.append(df.values.tolist()[0])

    df_pontos = pd.DataFrame(
        lista_pontos,
        columns=["latitude", "longitude", "altitude (m)", "distance_m", "name", "obstrucao", "angle"],
    )
    output_path = salvar_dataframe(df_pontos, OUTPUT_FILE)
    print(f"Pontos salvos em: {output_path}")


if __name__ == "__main__":
    main()
