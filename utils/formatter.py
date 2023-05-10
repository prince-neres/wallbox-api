from unidecode import unidecode


def format_alias_string(string):
    return unidecode(string).lower().replace(" ", "-")
