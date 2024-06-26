from functools import reduce
from typing import Optional, List, Dict

from lark import Token, Tree


def merge_dicts(x: List[Dict]) -> Dict:
    return reduce(lambda acc, i: {**acc, **i}, x, {})


class Location:
    def __init__(self, name: str = None, pos: Optional[int] = None):
        self.name = name
        self.pos = pos

    def __repr__(self):
        return f"L<{self.name}@{self.pos if self.pos is not None else 'UNDEF'}>"

    def __str__(self):
        return self.__repr__()


def gen_tree(root_name, children) -> Tree:
    return Tree(Token("RULE", root_name), children)


def gen_line(line: Optional[Tree] = None, label: Optional[Location] = None) -> Tree:
    if line is not None:
        content = line
    elif label is not None:
        content = _gen_label(label)
    else:
        raise ValueError("Invalid line generated")
    return gen_tree("line", [content])


def _gen_label(loc: Location) -> Tree:
    return gen_tree("label", [loc])


def gen_jump(
    target: Location, cmp_pos: int = 0, cmp_val: int = 0, alu: Optional[Tree] = None
) -> Tree:
    return gen_tree(
        "instr_jump",
        [
            *([alu] if alu is not None else []),
            gen_tree("jump_cmp_pos", [cmp_pos]),
            gen_tree("jump_cmp", [cmp_val]),
            gen_tree("jump_target", [target]),
        ],
    )


def gen_if(alu: Tree, bit: int, value_true: int, br_true: List, br_false: List) -> Tree:
    return gen_tree(
        "instr_if",
        [
            gen_tree("if_check", [alu, bit, value_true]),
            gen_tree("block_content", br_true),
            gen_tree("block_content", br_false),
        ],
    )


def collect_bit_tree(bit, cases: Dict[int, List]):
    if bit == -1:
        return list(cases.values())
    return {
        val: collect_bit_tree(
            bit - 1, {k: v for k, v in cases.items() if not (1 & (k >> bit) ^ val)}
        )
        for val in range(2)
    }
