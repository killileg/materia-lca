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
    'genepd': "https://materia.eco.lu/generic"
}


NSgen = {
    "ns0": "http://lca.jrc.it/ILCD/Process",
    "ns1": "http://www.indata.network/EPD/2019",
    "ns2": "http://lca.jrc.it/ILCD/Common",
    "ns3": "http://www.iai.kit.edu/EPD/2013",
}