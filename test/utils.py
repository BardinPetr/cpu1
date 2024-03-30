def get_subs(root):
    return {i.name: i for i in root.subs}


def get_first_sub(root, name_prefix):
    subs = get_subs(root)
    try:
        name = next(filter(lambda x: x.startswith(name_prefix), subs.keys()))
        return subs[name]
    except:
        raise Exception(f"No submodule {name_prefix}*")


def get_signals(root):
    return root.sigdict
