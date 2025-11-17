import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path

MODULES = ["A1-A3", "C1", "C2", "C3", "C4", "D"]
    # TYPES = ["tot", fossil", "bio", "luluc"]
GWP_MAP = {
    "Climate change-Total":   [m + "tot"    for m in MODULES],
    "Climate change-Fossil":  [m + "fossil" for m in MODULES],
    "Climate change-Biogenic":[m + "bio"    for m in MODULES],
    "Climate change-Land use and land use change":   [m + "luluc"  for m in MODULES],
}


excel = Path(r"P:\Construction Durable Economie Circulaire\Internships\2025_Killian_Legrand\Part II\Adm_Gol_01.xlsx")         
xml = Path(r"C:\Users\RFW474\Documents\MaterIA_LCA\xml_building.xml")
#modules = ["Projet", "Tier 3", "Tier 4", "Classe Mat n°", "Catégorie classe de matériaux", "Produit Type", "unité", "Quantité"]  # columns in Excel
GenPro_with_GWPs = Path(r"P:\Construction Durable Economie Circulaire\Internships\2025_Killian_Legrand\Part II\GenProducts_with_GWP.xlsx")
generic_epds = Path(r"C:\Users\RFW474\Documents\MaterIA_LCA\GenPro\generic")

# ------------------------- XML writer --------------------------
# NS / Constants 
NS = {
    'ns': 'http://materia.eco.lu/ns',
    'builder' : "https://materia.eco.lu/element",
    'materia': "https://materia.eco.lu/materia",
    'genepd': "https://materia.eco.lu/generic"
}
for p, uri in NS.items():
    ET.register_namespace(p, uri)

NSgen = {
    "ns0": "http://lca.jrc.it/ILCD/Process",
    "ns1": "http://www.indata.network/EPD/2019",
    "ns2": "http://lca.jrc.it/ILCD/Common",
    "ns3": "http://www.iai.kit.edu/EPD/2013",
}

def define_project(root, projectID: str): # give information about the project
    # find the place where to put our project definition
    project = root.find(".//ns:buildingInformation", NS)
    project.find(".//builder:buildingID", NS).text = "buildingID"
    project.find(".//builder:buildingName", NS).text = "Projet LDC"
    project.find(".//builder:location", NS).text = "Paris"  
    project.find(".//builder:buildingYear", NS).text = "2025"
    #proc.find(".//materia:processUUID", NS).text = str(match_row["ID"])

def handle_produit_type(text: str):
    # split into left (classification) / right (process name)
    if "-" in text:
        left, right = text.split("-", 1)
    process_name = right.strip()
    parts = [p.strip() for p in left.split("/") if p.strip()]

    return parts, process_name

def UUID_finder(process_name, df_ref) -> str:   # call this function after add_process, right structure ?
    column = df_ref["Produits (nouvelle dénomination)"].astype(str).str.strip() # gets rid of whitespaces in cells of column
    match_row = df_ref.loc[column == process_name].iloc[0] #returns first matching row
    return str(match_row["Identifiant UUID"])



# Create the process information block of a product
def add_process(row, root, df_ref) -> ET.Element:
    # find the place where to put our process
    processes = root.find(".//ns:processes", NS)

    parts, process_name = handle_produit_type(str(row["Produit type"]))

    # Create <ns:process>
    proc = ET.SubElement(processes, f"{{{NS['ns']}}}process")
    ET.SubElement(proc, f"{{{NS['materia']}}}processUUID").text = UUID_finder(process_name, df_ref) #str(row["UUID"])
    ET.SubElement(proc, f"{{{NS['builder']}}}processName").text = str(process_name)


    # --- Classification section (builder + materia) ---
    cls = ET.SubElement(proc, f"{{{NS['ns']}}}classification")

    b_info = ET.SubElement(cls, f"{{{NS['builder']}}}elementClass")
    ET.SubElement(b_info, f"{{{NS['builder']}}}class", {"level":"3"}).text = str(row["Tier 3"])
    ET.SubElement(b_info, f"{{{NS['builder']}}}class", {"level":"4"}).text = str(row["Tier 4"])

    m_info = ET.SubElement(cls, f"{{{NS['builder']}}}materialClass")
    m_cls  = ET.SubElement(m_info, f"{{{NS['builder']}}}classification", {"name": "EE Classification"}).text = str(row["Classe Mat n°"])
   
    # --- Product info ---
    prod = ET.SubElement(proc, f"{{{NS['ns']}}}product")
    ET.SubElement(prod, f"{{{NS['builder']}}}referenceUnit").text = str(row["unité"])
    ET.SubElement(prod, f"{{{NS['builder']}}}quantity").text = str(float(row["Quantité"]))

    


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
    

def EXTRA_UUID_filler(xml_path, GenPro_xlsx_path):
    df_gen = pd.read_excel(GenPro_xlsx_path) 

    tree = ET.parse(xml_path)
    root = tree.getroot()

    column = df_gen["Produit"].astype(str).str.strip() # gets rid of whitespaces in cells of column
    for proc in root.findall(".//ns:process", NS):
        process_name = str(proc.find(".//builder:processName", NS).text).strip()

        matches = df_gen.loc[column == process_name]
        if not matches.empty:
            match_row = matches.iloc[0]          # only executes if a match exists
            proc.find(".//materia:processUUID", NS).text = str(match_row["ID"])
        else:
            print(f"No match found for: {process_name}")

    tree.write(xml_path, encoding="utf-8", xml_declaration=True)


def store_GWP_impact_xml(impact_row: list[float], generic_xml: Path | str):
    tree = ET.parse(generic_xml)
    root = tree.getroot()

    for lcia in root.findall(".//ns0:LCIAResult", NSgen):
        desc = lcia.find(".//ns2:shortDescription", NSgen)
        if desc.text.strip() in GWP_MAP:
            for module, specific_gwp in zip(MODULES, GWP_MAP[desc.text.strip()]): #specific_gwp = A1-A3tot, C1tot, etc
                
                lcia.find(f".//ns3:amount[@ns3:module='{module}']", NSgen).text = str(impact_row[specific_gwp])

    tree.write(generic_xml, encoding="utf-8", xml_declaration=True)

    
def GWP_filler(generic_folder: Path | str, GenPro_xlsx: Path | str):
    
    df = pd.read_excel(GenPro_xlsx)
    df.columns = df.columns.str.strip()
    df["ID"] = df["ID"].astype(str).str.strip()
    df = df.set_index("ID")
    UUIDs = df.index.str.strip()

    for uuid in UUIDs: 
        if "xxxxxxx" in uuid:
            continue  # skip this specific UUID
        generic_file = generic_folder / f"{uuid}.xml"
        # Maybe add line in case file is not found
        impact_row = df.loc[uuid]
        store_GWP_impact_xml(impact_row, generic_file)



# ------------------------- main --------------------------

if __name__ == "__main__":
    convert(xml, excel)
    EXTRA_UUID_filler(xml, GenPro_with_GWPs)
    GWP_filler(generic_epds, GenPro_with_GWPs)





