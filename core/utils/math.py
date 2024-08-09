def round_to_value(source_value: int, round_to: int):
    residue = source_value % round_to
    if residue == 0:
        return source_value
    if residue == source_value:  # 8 % 10 = 8
        return round_to

    lack = round_to - residue
    return source_value + lack
