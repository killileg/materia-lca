import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
from writer import define_project, add_process, EXTRA_UUID_filler, GWP_filler


excel = Path(r"P:\Construction Durable Economie Circulaire\Internships\2025_Killian_Legrand\Part II\Adm_Gol_01.xlsx")         
xml = Path(r"C:\Users\RFW474\Documents\MaterIA_LCA\xml_building.xml")
#modules = ["Projet", "Tier 3", "Tier 4", "Classe Mat n°", "Catégorie classe de matériaux", "Produit Type", "unité", "Quantité"]  # columns in Excel
GenPro_with_GWPs = Path(r"P:\Construction Durable Economie Circulaire\Internships\2025_Killian_Legrand\Part II\GenProducts_with_GWP.xlsx")
generic_epds = Path(r"C:\Users\RFW474\Documents\MaterIA_LCA\GenPro\generic")

# ------------------------- XML writer --------------------------

def convert(xml_path, xlsx_path):

    df = pd.read_excel(xlsx_path, sheet_name="Données")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Fill in xml
    define_project(root, str(df.loc[0, "Projet"]))

    df_ref = pd.read_excel(xlsx_path, sheet_name="Produits types") 
    for _, row in df.iterrows():
        add_process(row, root, df_ref)

    # End
    ET.indent(tree, space="  ", level=0)
    tree.write(xml, encoding="utf-8", xml_declaration=True)
    

    tree.write(xml_path, encoding="utf-8", xml_declaration=True)




    tree.write(generic_xml, encoding="utf-8", xml_declaration=True)



# ------------------------- main --------------------------

if __name__ == "__main__":
    
    convert(xml, excel)
    EXTRA_UUID_filler(xml, GenPro_with_GWPs)
    GWP_filler(generic_epds, GenPro_with_GWPs)





