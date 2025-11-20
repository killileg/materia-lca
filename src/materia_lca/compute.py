# Calculate total impact
import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET
from materia_lca.constants import NS, NSgen, NSflow, MODULES, GWP_MAP, FLOW_PROPERTY_MAPPING

def get_A1_A3(file: Path | str):
    tree = ET.parse(file)
    root = tree.getroot()
    results = []
    for lcia in root.findall(".//ns0:LCIAResult", NSgen):
        desc = lcia.find(".//ns0:referenceToLCIAMethodDataSet/ns2:shortDescription", NSgen)
        if desc.text.strip() in GWP_MAP:
            a1_a3_value = lcia.find(".//ns3:amount[@ns3:module='A1-A3']", NSgen).text
            # For future generalizations : 
            #for module, specific_gwp in zip(MODULES, GWP_MAP[desc.text.strip()]): #specific_gwp = A1-A3tot, C1tot, etc
                #lcia.find(f".//ns3:amount[@ns3:module='{module}']", NSgen)
                #results.append((desc.text.strip(), a1_a3_value))
            results.append((desc.text.strip(), a1_a3_value))
    return results # pairs of (impact_name, a1_a3_value)  ex. ("Climate change total", 12.5)


def create_impacts_blockA(xml:Path):
    tree = ET.parse(xml)
    root = tree.getroot()
    for product in root.findall(".//ns:product", NS): 
        LCIA_info = ET.SubElement(product, f"{{{NS['ns']}}}LCIA")
        for impact_name in GWP_MAP:
            category = ET.SubElement(LCIA_info, f"{{{NS['ns']}}}category")
            cat_info = ET.SubElement(category, f"{{{NS['materia']}}}shortDescription", {"xml:lang":"en"})
            cat_info.text = str(impact_name)
            for mod in ["A1-A3", "A4", "A5"]:
                impact = ET.SubElement(category, f"{{{NS['materia']}}}module", {"materia:module":mod})
                impact.text = "0"
    ET.indent(tree, space="  ", level=0)
    tree.write(xml, encoding="utf-8", xml_declaration=True)


def verify_matching_unit(process: ET.Element, generic_xml: Path | str):     
    # xml building
    unit_product = process.find(".//builder:referenceUnit", NS).text
    expected_uuid = FLOW_PROPERTY_MAPPING.get(unit_product)

    # generic xml 
    tree_gen = ET.parse(generic_xml)
    root_gen = tree_gen.getroot()
    flow = root_gen.find(".//ns0:referenceToFlowDataSet", NSgen)
    flow_uuid = flow.get("refObjectId").strip()
    flow_file = Path(generic_xml).parent.parent / "flows" /  f"{flow_uuid}.xml"
    
    tree_flow = ET.parse(flow_file)
    root_flow = tree_flow.getroot()
    prop = root_flow.findall(".//ns0:flowProperty", NSflow)
    for property in prop:
        mean_values = property.findall(".//ns0:meanValue", NSflow)
        for mv in mean_values:
            if float(mv.text) != 0: # if True, we're in the right block
                flow_property_uuid = property.find(".//ns0:referenceToFlowPropertyDataSet", NSflow).get("refObjectId").strip()
                # unit validation
                #print("unit product : ", f"{unit_product}")
                #print("expected uuid : " f"{expected_uuid}")
                #print("flow property uuid : " f"{flow_property_uuid}")
                if expected_uuid == flow_property_uuid:
                    return True

def add_impact_A1_A3(xml_building : Path, generic_folder: Path):
    print("Adding impacts of all modules A1-A3...")
    create_impacts_blockA(xml_building)

    tree = ET.parse(xml_building)
    root = tree.getroot()    

    for product in root.findall(".//ns:product", NS):
        quantity = product.find(".builder:quantity", NS).text
        uuid = product.find(".materia:processUUID", NS).text

        #print(f"{uuid}")
        if "xxxxxxx" in uuid:
            continue  # skip this specific UUID

        generic_xml = generic_folder / f"{uuid}.xml"
        all_impact_A1_A3 = get_A1_A3(generic_xml)
        #print(all_impact_A1_A3)
        if verify_matching_unit(product, generic_xml):
            for gwp_type, a1_a3_value in all_impact_A1_A3:
                gwp_type = str(gwp_type).strip()
                category = product.find(f".ns:LCIA/ns:category[materia:shortDescription='{gwp_type}']", NS)
                module = category.find(".materia:module[@materia:module='A1-A3']", NS)
                impact = float(quantity)*float(a1_a3_value)
                module.text = str(float(impact))
        else:
            print(f"No matching unit for generic epd : {generic_xml}")
    tree.write(xml_building, encoding="utf-8", xml_declaration=True)
                
            
