from src.config import DATA_BITS

DIM = DATA_BITS

UINT_MIN = 0
UINT_MAX = (1 << DIM) - 1
SINT_MAX = (1 << (DIM - 1)) - 1
SINT_MIN = -(1 << (DIM - 1))


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


def trunc(x, n=DIM):
    return x & ((1 << n) - 1)


def negate(x, n=DIM):
    return trunc(~x + 1, n)


def set_signed(sig, val):
    sig.next = trunc(~abs(val) + 1) if val < 0 else val
