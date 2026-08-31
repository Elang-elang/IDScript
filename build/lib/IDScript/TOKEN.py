"IDVM (InDonesian Virtual Machine)"
ALL_TOKEN = [
    "decl_var",
    "decl_const",
    "decl_func",
    
    "unary",
    "bool",
    "comp",
    "bin",

    "to_bool",
    
    "type_ann",
    
    "load_name",
    "load_const",

    "arg",
    "param",

]

for i, TOKEN in enumerate(
    ALL_TOKEN, start=1
):
    globals()[TOKEN] = i
    globals()[str(i)] = TOKEN

del i