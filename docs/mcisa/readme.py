from typing import Type

from tabulate import tabulate

from machine.mc.mcinstr import MCInstructionExec, MCInstructionJump, MCInstruction

DESCRIPTION = {
    "instr_type":      "Тип инструкции",
    "alu_ctrl":        "Управление операций АЛУ",
    "alu_port_a_ctrl": "Операция на входе А АЛУ",
    "alu_port_b_ctrl": "Операция на входе B АЛУ",
    "bus_a_in_ctrl":   "Выбор источника данных для шины А",
    "bus_b_in_ctrl":   "Выбор источника данных для шины В",
    "jmp_cmp_bit":     "Бит для компаратора при сравнении для условного перехода",
    "jmp_cmp_val":     "Значение бита сравнения для условного перехода, при котором он совершается",
    "jmp_target":      "Смещение в микро-инструкциях для условного перехода",
    "alu_flag_ctrl":   "Управление сохранением флагов АЛУ",
    "bus_c_out_ctrl":  "Выбор получателя значения с шины C",
    "mem_ctrl":        "Управление записью в память",
    "stack_d_ctrl":    "Управление стеком данных",
    "stack_r_ctrl":    "Управление стеком возврата",
    "machine_ctrl":    "Управление исполнением",
    "io_ctrl":         "Управление контроллером ввода-вывода"
}


def describe_mc_md(x: Type[MCInstruction]) -> str:
    rows = [
        (
            f"[{loc.loc_start:2d}:{loc.loc_end:2d})",
            f"{loc.size}b",
            annot.__args__[0].__name__,
            name,
            DESCRIPTION.get(name, "")
        )
        for name, annot, loc in x.inspect_fields()
    ]

    table = tabulate(
        rows,
        headers=["Loc", "Size", "Type", "Name", "Description"],
        tablefmt="github",
        stralign="left",
    )

    return f"### {x.__name__.replace('MCInstruction', '')}\n\n" + table


def gen_doc_mcisa():
    return '\n\n'.join([describe_mc_md(i)
                        for i in (MCInstructionJump, MCInstructionExec)])


if __name__ == "__main__":
    with open("readme.md", "w") as f:
        res = gen_doc_mcisa()
        f.write(res)
        print(res)
