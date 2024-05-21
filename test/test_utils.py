def push_stack(stack, x):
    stack.mem[stack.sp]._val = x
    stack.sp._val = stack.sp + 1


def pop_stack(stack) -> int:
    stack.sp._val = stack.sp - 1
    return stack.mem[stack.sp].val


def reset_stack(stack):
    stack.sp._val = 0
    for i in stack.mem:
        i._val = 0
