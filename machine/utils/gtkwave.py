import os.path
from typing import Type, List

from machine.utils.enums import CtrlEnum, CEnumS, CEnumM


def _translate_pairs(enum: Type[CtrlEnum]) -> List[str]:
    if issubclass(enum, CEnumS):
        return [f"{val:x} {enum(val).name}" for val in enum]
    elif issubclass(enum, CEnumM):
        def names(val) -> List[str]:
            all_names = [enum(i).name for i in list(enum)]
            res = [
                all_names[pos]
                for pos, _ in enumerate(enum)
                if val & (1 << pos)
            ]
            return res if res else ['NONE']

        return [
            f"{i:x} {'|'.join(names(i))}"
            for i in range(1 << enum.encoded_len())
        ]
    return []


def gtkwave_generate_translation(enum: Type[CtrlEnum]):
    text = '\n'.join(_translate_pairs(enum))

    filename = f"gtkwave_translate_{enum.__name__.lower()}"
    filename = os.path.join('./dist', filename)
    filename = os.path.abspath(filename)

    with open(filename, 'w') as f:
        f.write(text)

    return filename
