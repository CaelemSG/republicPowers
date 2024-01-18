import csv

class PlayerProperty:
    name: str = 'invalid'
    property_type: str = 'invalid'
    product: str = 'invalid'
    size: int = 0
    location: str = 'invalid'
    value: float = 0.0
    income: float = 0.0

def deserialize_properties() -> dict[str, list[PlayerProperty]]:
    properties = dict()
    try:
        with open('properties.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                p = PlayerProperty()
                p.name = row[1]
                p.property_type = row[2]
                p.product = row[3]
                p.size = int(row[4])
                p.location = str(row[5])
                p.value = float(row[6])
                p.income = float(row[7])
                if row[0] in properties:
                    properties[row[0]].append(p)
                else:
                    properties[row[0]] = [p]
        print(f"succesfully loaded {len(properties)} properties")
    except OSError as error:
        print(f"could not deserialize properties: {error}")
    except ValueError:
        print("could not deserialize properties: csv is malformed")
    return properties

def serialize_properties(prop: dict[str, PlayerProperty]):
    with open('properties.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for (owner, props) in prop.items():
            for p in props:
                writer.writerow([owner, p.name, p.property_type, p.product, p.size, p.location, p.value, p.income])
