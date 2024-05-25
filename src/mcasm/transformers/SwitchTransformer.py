from typing import Dict, List

from lark import Transformer, v_args, Tree

from mcasm.utils import merge_dicts, collect_bit_tree, Location, gen_if, gen_tree, gen_line


class SwitchTransformer(Transformer):
    case_body = lambda self, x: x

    def __init__(self):
        super().__init__()
        self.__switch_id = 0

    @v_args(inline=True)
    def case_def(self, val, body):
        return {val: body}

    def switch_body(self, body):
        body_cases = merge_dicts(body)
        max_val = max(body_cases.keys())
        res = collect_bit_tree(max(1, max_val.bit_length()) - 1, body_cases)
        return res

    @staticmethod
    def __convert_to_if(alu: Tree, bit: int, cases: Dict, exit_label: Location):
        cases = [cases.get(i, []) for i in range(2)]
        if all(map(lambda x: not x, cases)):
            return gen_line(label=Location(name="__swif_nop"))
        branches = [
            [SwitchTransformer.__convert_to_if(alu, bit - 1, cases[br], exit_label)]
            if isinstance(cases[br], dict) else
            (cases[br][0].children if cases[br] else [])
            for br in range(2)
        ]
        return gen_line(gen_if(alu, bit, 0, *branches))

    @v_args(inline=True)
    def instr_switch(self, alu: Tree, pos_end: int, pos_start: int, body: Dict[int, Dict | List]):
        if pos_end < pos_start:
            raise ValueError(f"Invalid ranges for switch {pos_end}:{pos_start}")
        exit_label = Location(name=f"__switch_{self.__switch_id}_end")
        self.__switch_id += 1

        res = gen_tree(
            "block",
            [
                self.__convert_to_if(alu, pos_end, body, exit_label),
                gen_line(label=exit_label),
            ]
        )
        return res
