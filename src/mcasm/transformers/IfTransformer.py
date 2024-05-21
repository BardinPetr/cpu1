from functools import reduce
from typing import List, Dict

from lark import Transformer, Tree, v_args

from mcasm.utils import Location, gen_jump, gen_tree, gen_line


class IfTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.__if_id = 0

    def block_content(self, tree: List[Tree]):
        return reduce(
            lambda acc, cur: acc + (self.block_content(line.children) if (line := cur.children[0]).data == 'block' else [cur]),
            tree, []
        )

    @v_args(inline=True)
    def if_check(self, alu, pos, cmp):
        return dict(alu=alu, cmp_pos=pos, cmp_val=cmp)

    @v_args(inline=True)
    def instr_if(self, check: Dict, true_branch_block, false_branch_block):
        base_label = f"__if_{self.__if_id}"
        true_label = Location(name=f"{base_label}_on_true")
        end_loc = Location(name=f"{base_label}_end")
        self.__if_id += 1

        jump_instr = gen_jump(
            **check,
            target=true_label  # jump if TRUE!
        )
        false_exit_instr = gen_jump(
            target=end_loc
        )
        return gen_tree(
            "block",
            [
                gen_line(jump_instr),
                *false_branch_block,
                gen_line(false_exit_instr),
                gen_line(label=true_label),
                *true_branch_block,
                gen_line(label=end_loc)
            ]
        )
