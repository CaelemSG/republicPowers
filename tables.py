import properties

# table rendering !!

currency_prefix = "X"


def ellipsis(s: str, max_width: int) -> str:
    if len(s) > max_width:
        return s[: max_width - 3] + "..."
    else:
        return s


def table_properties(p: list[properties.PlayerProperty], cpl: int = 64) -> str:
    margin = 0
    columns = 7
    separators = columns - 1
    usable_cpl = cpl - (margin * 2)
    single_column_size = usable_cpl // separators
    output = f'{" " * margin}{"name":^{single_column_size}}|{"type":^{single_column_size}}|{"product":^{single_column_size}}|{"size":^{single_column_size}}|{"location":^{single_column_size}}|{"value":^{single_column_size}}|{"income":^{single_column_size}}'
    for row in p:
        output += f'\n{" " * margin}{ellipsis(row.name, single_column_size):{single_column_size}}|{ellipsis(row.property_type, single_column_size):{single_column_size}}|{ellipsis(row.product, single_column_size):{single_column_size}}|{row.size:{single_column_size}}|{ellipsis(row.location, single_column_size):{single_column_size}}|{row.value:{single_column_size}}|{row.income:{single_column_size}}'
    return output
