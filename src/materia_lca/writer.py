import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
from materia_lca.constants import NS, NSgen, MODULES, GWP_MAP
from materia_lca.utils import handle_produit_type, UUID_finder


for p, uri in NS.items():
        ET.register_namespace(p, uri)


def create_xml_template(folder: str | Path, filename: str = "xml_building.xml"):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)

    path = Path(folder / filename)

    root = ET.Element(f"{{{NS['ns']}}}buildingDataSet")

    binfo = ET.SubElement(root, f"{{{NS['ns']}}}buildingInformation")
    ET.SubElement(binfo, f"{{{NS['builder']}}}buildingID").text = "buildingID"
    ET.SubElement(binfo, f"{{{NS['builder']}}}buildingName").text = "Sample Building"
    ET.SubElement(binfo, f"{{{NS['builder']}}}location").text = "Sample Location"
    ET.SubElement(binfo, f"{{{NS['builder']}}}buildingYear").text = "buildingYear"

    ET.SubElement(root, f"{{{NS['ns']}}}building")

    tree = ET.ElementTree(root)
    ET.indent(tree, "  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)
    
    print(f"XML created at: {path}")
    return path


def define_project(root, projectID: str):   # default name for the moment
    project = root.find(".//ns:buildingInformation", NS)
    project.find(".//builder:buildingID", NS).text = "buildingID"
    project.find(".//builder:buildingName", NS).text = "Projet LDC"
    project.find(".//builder:location", NS).text = "FC Junglinster"  
    project.find(".//builder:buildingYear", NS).text = "2030"
    #proc.find(".//materia:processUUID", NS).text = str(match_row["ID"])



def add_product(row, root, df_ref) -> ET.Element:
    # find the place where to put our process
    category = row["Tier 4"]
    if "---" in category:
        category = row["Tier 3"]

    #level1, level2, level3, level4 = str(category.split(".")[0]), str(category.split(".")[1]), str(category.split(".")[2]), str(category.split(".")[3])
    a, b, c, d = str(category.split(".")[0]), str(category.split(".")[1]), str(category.split(".")[2]), str(category.split(".")[3])
    level1, level2, level3, level4 = str(a), str(a + "." + b), str(a + "." + b + "." + c), str(a + "." + b + "." + c + "." + d)

    building = root.find(f".//ns:building", NS)
    existing_parts = building.findall(".ns:Part", NS)
    part = next((p for p in existing_parts if p.find("builder:classification", NS).text.strip() == str(level1)), None)
    if part is None:
        part = ET.SubElement(building, f"{{{NS['ns']}}}Part")
        cls = ET.SubElement(part, f"{{{NS['builder']}}}classification", {"level": "1"})
        cls.text = str(level1)

    existing_systems = part.findall(".ns:System", NS)
    system = next((s for s in existing_systems if s.find("builder:classification", NS).text.strip() == str(level2)), None)
    if system is None:
        system = ET.SubElement(part, f"{{{NS['ns']}}}System")
        cls = ET.SubElement(system, f"{{{NS['builder']}}}classification", {"level": "2"})
        cls.text = str(level2)
        

    existing_elements = system.findall(".ns:Element", NS)
    element = next((e for e in existing_elements if e.find("builder:classification", NS).text.strip() == str(level3)), None)
    if element is None:
        element = ET.SubElement(system, f"{{{NS['ns']}}}Element")
        cls = ET.SubElement(element, f"{{{NS['builder']}}}classification", {"level": "3"})
        cls.text = str(level3)

    existing_subelements = element.findall(".ns:SubElement", NS)
    subelement = next((se for se in existing_subelements if se.find("builder:classification", NS).text.strip() == str(level4)), None)
    if subelement is None:
        subelement = ET.SubElement(element, f"{{{NS['ns']}}}SubElement")
        cls = ET.SubElement(subelement, f"{{{NS['builder']}}}classification", {"level": "4"})
        cls.text = str(level4)

    opfjwa, process_name = handle_produit_type(str(row["Produit type"]))
    product = ET.SubElement(subelement, f"{{{NS['ns']}}}product")
    ET.SubElement(product, f"{{{NS['materia']}}}processUUID").text = UUID_finder(process_name, df_ref)
    ET.SubElement(product, f"{{{NS['builder']}}}processName").text = str(process_name)
    ET.SubElement(product, f"{{{NS['builder']}}}classification", {"name": "EE Classification"}).text = str(row["Classe Mat n°"])
    ET.SubElement(product, f"{{{NS['builder']}}}referenceUnit").text = str(row["unité"])
    ET.SubElement(product, f"{{{NS['builder']}}}quantity").text = str(float(row["Quantité"]))


def EXTRA_UUID_filler(xml_building, excel_with_GWPs): 
    print("Doing the extra unnecessary avoidable task of finding and writing the product's UUID in the building xml")
    df_gen = pd.read_excel(excel_with_GWPs) 

    tree = ET.parse(xml_building)
    root = tree.getroot()

    column = df_gen["Produit"].astype(str).str.strip() # gets rid of whitespaces in cells of column
    for prod in root.findall(".//ns:product", NS):
        process_name = str(prod.find(".//builder:processName", NS).text).strip()

        matches = df_gen.loc[column == process_name]
        if not matches.empty:
            match_row = matches.iloc[0]          # only executes if a match exists
            prod.find(".//materia:processUUID", NS).text = str(match_row["ID"])
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
