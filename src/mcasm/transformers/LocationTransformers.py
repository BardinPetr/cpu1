from typing import Dict

from lark import Transformer, v_args, Tree

from mcasm.utils import Location


class LocationResolver(Transformer):
    def __init__(self):
        super().__init__()
        self.labels: Dict[str, int] = {}

    @v_args(tree=True)
    def start(self, lines: Tree):
        pos = 0

        lines.children = lines.children[0]  # remove top block_content

        for line in lines.children:
            label = next(line.find_data("label"), None)
            if label is not None:
                loc: Location = label.children[0]
                self.labels[loc.name] = pos
                loc.pos = pos
            else:
                pos += 1

        for i in lines.find_data("jump_target"):
            loc: Location = i.children[0]
            if loc.pos is not None:
                continue
            if loc.name not in self.labels:
                raise RuntimeError(f"Unable to resolve location {loc}")

            loc.pos = self.labels[loc.name]

        lines.children = [i for i in lines.children if i.children[0].data != "label"]
        return lines
