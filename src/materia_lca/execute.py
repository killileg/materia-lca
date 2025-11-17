import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
from materia_lca.writer import define_project, add_process, EXTRA_UUID_filler, GWP_filler

def convert(xml_building, excel_builder):
    print("Starting convert()...")
    df = pd.read_excel(excel_builder, sheet_name="Données")
    tree = ET.parse(xml_building)
    root = tree.getroot()

    # Fill in xml
    define_project(root, str(df.loc[0, "Projet"]))

    df_ref = pd.read_excel(excel_builder, sheet_name="Produits types") 
    for _, row in df.iterrows():
        add_process(row, root, df_ref)

    # End
    ET.indent(tree, space="  ", level=0)
    tree.write(xml_building, encoding="utf-8", xml_declaration=True)
    print("Written !")
    

def run_materia_lca(xml_building: Path, excel_builder: Path, generic_epds: Path, excel_with_GWPs: Path):
    """Process the given file or folder path."""
    convert(xml_building, excel_builder)
    EXTRA_UUID_filler(xml_building, excel_with_GWPs)
    GWP_filler(generic_epds, excel_with_GWPs)

