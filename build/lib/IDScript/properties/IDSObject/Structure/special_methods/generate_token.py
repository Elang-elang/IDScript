import json
RAW = json.load(open("./RAW_TOKEN.json"))

TOKEN: list[dict[str, str]] = []
for py_name, ids_name in RAW.items():
    alias = f'__{py_name}__'
    d = {
        'python':  py_name,
        'alias':   alias,
        'idscript': ids_name,
    }
    TOKEN.append(d)


RESOLVE_TOKEN = {
    'names': TOKEN.copy()
}
json.dump(
    RESOLVE_TOKEN,
    open('./TOKEN.json', 'w'),
    indent=4,
)