"""The sweep queue: metro x corridor x category, Chicago first then Detroit.
Mirrors ../skills/leads/sweep-matrix.md. Edit the lists to expand territory."""

CATEGORIES = [
    "machine shop",
    "CNC machining",
    "screw machine products manufacturer",
    "metal fabrication",
    "sheet metal fabrication",
    "metal stamping",
    "tool and die",
    "injection molding",
    "plastics manufacturer",
    "spring wire forming manufacturer",
    "precision grinding manufacturer",
    "powder coating metal finishing",
    "food processing",
]

# metro -> list of corridors ("City ST")
METROS = {
    "Chicago": [
        "Elk Grove Village IL", "Bensenville IL", "Wood Dale IL", "Addison IL",
        "Franklin Park IL", "Schiller Park IL", "Melrose Park IL", "Northlake IL",
        "Bedford Park IL", "Cicero IL", "Bridgeview IL", "Alsip IL",
        "Des Plaines IL", "Mount Prospect IL", "Elgin IL", "Carol Stream IL",
    ],
    "Detroit": [
        "Warren MI", "Sterling Heights MI", "Roseville MI", "Clinton Township MI",
        "Madison Heights MI", "Troy MI", "Auburn Hills MI", "Livonia MI",
        "Plymouth MI", "Canton MI", "Redford MI", "Taylor MI", "Dearborn MI",
        "Wyandotte MI", "Farmington Hills MI", "Novi MI",
    ],
}

# Work order: finish Chicago, then Detroit.
METRO_ORDER = ["Chicago", "Detroit"]


def all_slices():
    """Yield (metro, corridor, category, query, slice_id) in work order."""
    for metro in METRO_ORDER:
        for corridor in METROS[metro]:
            for category in CATEGORIES:
                query = f"{category} {corridor}"
                slice_id = f"{metro} x {corridor} x {category}"
                yield metro, corridor, category, query, slice_id
