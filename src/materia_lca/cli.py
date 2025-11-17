import click
from pathlib import Path
from materia_lca.execute import run_materia_lca

@click.command()
@click.argument("xml_building", type=click.Path(exists=True, path_type=Path))
@click.argument("excel_builder", type=click.Path(exists=True, path_type=Path))
@click.argument("generic_epd_folder", type=click.Path(exists=True, path_type=Path))
@click.argument("excel_with_gwps", type=click.Path(path_type=Path))
def main(
    xml_building: Path,
    excel_builder: Path,
    generic_epd_folder: Path,
    excel_with_gwps: Path,
) -> None:
    """Process the given file or folder path."""
    run_materia_lca(xml_building, excel_builder, generic_epd_folder, excel_with_gwps)
