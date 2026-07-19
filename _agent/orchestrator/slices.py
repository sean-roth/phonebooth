"""The sweep queue: metro x corridor x category, Chicago first then Detroit.
Mirrors ../skills/leads/sweep-matrix.md in full — the matrix is the map, this
is the queue. When territory changes, change both in the same commit."""

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
    "food packaging",
    "welding fabrication",
]

# metro -> list of corridors ("City ST"). List order = work order in the metro.
METROS = {
    "Chicago": [
        # O'Hare / Elk Grove belt
        "Elk Grove Village IL", "Bensenville IL", "Wood Dale IL", "Addison IL",
        "Itasca IL",
        # Near-west inner ring
        "Franklin Park IL", "Schiller Park IL", "Melrose Park IL", "Northlake IL",
        "Stone Park IL", "Bellwood IL",
        # South / southwest corridor
        "Broadview IL", "Hillside IL", "Bedford Park IL", "McCook IL",
        "Summit IL", "Cicero IL", "Berwyn IL", "Alsip IL", "Bridgeview IL",
        # North / northwest suburbs
        "Des Plaines IL", "Mount Prospect IL", "Arlington Heights IL",
        "Niles IL", "Skokie IL", "Morton Grove IL",
        # Far west
        "Elgin IL", "South Elgin IL", "Carol Stream IL", "Bloomingdale IL",
        "Glendale Heights IL",
        # Chicago city industrial
        "Clearing Chicago IL", "Archer Heights Chicago IL", "Pilsen Chicago IL",
        "Ravenswood Chicago IL",
    ],
    "Detroit": [
        # Macomb supplier belt
        "Warren MI", "Sterling Heights MI", "Center Line MI", "Roseville MI",
        "Fraser MI", "Clinton Township MI",
        # Oakland inner ring
        "Madison Heights MI", "Hazel Park MI", "Ferndale MI",
        # Oakland north / west
        "Troy MI", "Auburn Hills MI", "Rochester Hills MI",
        "Farmington Hills MI", "Novi MI", "Wixom MI",
        # Wayne belt
        "Livonia MI", "Plymouth MI", "Canton MI", "Redford MI", "Romulus MI",
        "Taylor MI", "Dearborn MI", "Wyandotte MI",
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
