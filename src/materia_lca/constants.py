MODULES = ["A1-A3", "C1", "C2", "C3", "C4", "D"]
    # TYPES = ["tot", fossil", "bio", "luluc"]

GWP_MAP = {
    "Climate change-Total":   [m + "tot"    for m in MODULES],
    "Climate change-Fossil":  [m + "fossil" for m in MODULES],
    "Climate change-Biogenic":[m + "bio"    for m in MODULES],
    "Climate change-Land use and land use change":   [m + "luluc"  for m in MODULES],
}

NS = {
    'ns': 'http://materia.eco.lu/ns',
    'builder' : "https://materia.eco.lu/element",
    'materia': "https://materia.eco.lu/materia",
}


NSgen = {
    "ns0": "http://lca.jrc.it/ILCD/Process",
    "ns1": "http://www.indata.network/EPD/2019",
    "ns2": "http://lca.jrc.it/ILCD/Common",
    "ns3": "http://www.iai.kit.edu/EPD/2013",
}

NSflow = {
    "ns0": "http://lca.jrc.it/ILCD/Flow",
    "common": "http://lca.jrc.it/ILCD/Common",
}

FLOW_PROPERTY_MAPPING = {
    "kg": "93a60a56-a3c8-11da-a746-0800200b9a66",
    "m": "838aaa23-0117-11db-92e3-0800200c9a66",
    "m^2": "93a60a56-a3c8-19da-a746-0800200c9a66",
    "m^3": "93a60a56-a3c8-22da-a746-0800200c9a66",
    "unit": "01846770-4cfe-4a25-8ad9-919d8d378345",
}