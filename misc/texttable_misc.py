from texttable import Texttable
from math import ceil
from re import split as re_split


def get_string_wrapped(table: Texttable, size: int, fixed_col=0) -> str:
    """
    Only works with deco types of VLINES and default. Splits the table to multiple lines with a maximum size of
    'size'. Then returns the string which would be returned by draw
    :param table: Table to split
    :param size: What is the maximum size in characters
    :param fixed_col: If you want some columns from the start to be fixed at the start of each line then pass how
    many you want fixed
    :return: A string of the table split
    """
    out: [str] = []
    line_i = 0
    for line in table.draw().splitlines():
        # at the first line we append hopefully enough strings to out
        if line_i is 0:
            for i in range(int(ceil(len(line) / size)) * 2):
                out.append("")

        split = re_split(r"[\+\|]", line)
        curr_length = 0
        curr_line = 0

        # we need to skip the "" ones in the front in case there are any
        real_fixed_col = fixed_col
        while split[real_fixed_col - fixed_col] is "":
            real_fixed_col += 1
        fixed_in_line = split[:real_fixed_col]

        # go through the cols in this line of table
        for col in split:
            # we can fit this col in the current line
            if curr_length + len(col) + 1 < size:
                out[curr_line] += col + "|"
            else:
                # we can no longer fit this col in the current line -> append it to the next one
                curr_line += 1

                # but first append the fixed cols
                if fixed_col > 0:
                    fixed_string = "|".join(fixed_in_line) + "|"
                    out[curr_line] += fixed_string
                    curr_length = len(fixed_string)  # we set this here
                else:
                    curr_length = 0  # we haven't set it in if, but we still need to reset it

                out[curr_line] += col + "|"

            curr_length += len(col) + 1

        line_i += 1
        # append a line break at the end of each line
        for i in range(len(out)):
            out[i] += "\n"

    return "\n".join(list(filter(lambda s: s.replace("\n", "") is not "", out)))
