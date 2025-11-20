import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
from materia_lca.writer import define_project, add_product, EXTRA_UUID_filler, GWP_filler
from materia_lca.compute import add_impact_A1_A3

def convert(xml_building, excel_builder):
    print("Starting convert()...")
    df = pd.read_excel(excel_builder, sheet_name="Données")
    # Sort the tier4 values before calling code !
    df.sort_values(by="Tier 4", ascending=True)
    tree = ET.parse(xml_building)
    root = tree.getroot()

    # Add function create_skeleton() : create the template of the xml 

    # Fill in xml
    define_project(root, str(df.loc[0, "Projet"]))

    df_ref = pd.read_excel(excel_builder, sheet_name="Produits types")     

    for _, row in df.iterrows():
        #add_process(row, root, df_ref)
        add_product(row, root, df_ref)

    # End
    ET.indent(tree, space="  ", level=0)
    tree.write(xml_building, encoding="utf-8", xml_declaration=True)
    

def run_materia_lca(xml_building: Path, excel_builder: Path, generic_epds: Path, excel_with_GWPs: Path):
    """Process the given file or folder path."""
    convert(xml_building, excel_builder)
    EXTRA_UUID_filler(xml_building, excel_with_GWPs)
    GWP_filler(generic_epds, excel_with_GWPs)
    add_impact_A1_A3(xml_building, generic_epds)

