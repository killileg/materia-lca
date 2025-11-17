from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd
from materia_lca.constants import NS, NSgen, MODULES, GWP_MAP
from materia_lca.utils import handle_produit_type, UUID_finder

for p, uri in NS.items():
        ET.register_namespace(p, uri)

def define_project(root, projectID: str):   # default name for the moment
    project = root.find(".//ns:buildingInformation", NS)
    project.find(".//builder:buildingID", NS).text = "buildingID"
    project.find(".//builder:buildingName", NS).text = "Projet LDC"
    project.find(".//builder:location", NS).text = "FC Junglinster"  
    project.find(".//builder:buildingYear", NS).text = "2030"
    #proc.find(".//materia:processUUID", NS).text = str(match_row["ID"])

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


def EXTRA_UUID_filler(xml_building, excel_with_GWPs): 
    print("Doing tht eextra unnecessary avoidable task of finding and writing the product's UUDI in the building xml")
    df_gen = pd.read_excel(excel_with_GWPs) 

    tree = ET.parse(xml_building)
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

    tree.write(xml_building, encoding="utf-8", xml_declaration=True)
    


def store_GWP_impact_xml(impact_row: list[float], generic_xml: Path | str):
    tree = ET.parse(generic_xml)
    root = tree.getroot()

    for lcia in root.findall(".//ns0:LCIAResult", NSgen):
        desc = lcia.find(".//ns2:shortDescription", NSgen)
        if desc.text.strip() in GWP_MAP:
            for module, specific_gwp in zip(MODULES, GWP_MAP[desc.text.strip()]): #specific_gwp = A1-A3tot, C1tot, etc
                
                lcia.find(f".//ns3:amount[@ns3:module='{module}']", NSgen).text = str(impact_row[specific_gwp])

    tree.write(generic_xml, encoding="utf-8", xml_declaration=True)


def GWP_filler(generic_folder: Path | str, excel_with_GWPs: Path | str):
    print("Filling impacts in generic xml files...")
    df = pd.read_excel(excel_with_GWPs)
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

    