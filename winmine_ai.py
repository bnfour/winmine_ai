# artificial «intelligence» file

from winmine_util import get_field_flat, in_all
from winmine_const import UNKNOWN, FLAGGED, DELTA

from itertools import combinations
from random import choice


# trivial AI, looks for obviously mined or obviously free cells
#   for instance, if a "1" cell has a flag near it, it is safe to open
#   every other cell around
#   or if a "2" cell has exacty two undiscovered cells and no flags around,
#   it is save to flag these unknown cells
# return two sets: cells to flag and cells to open
def trivial(field):
    to_flag = set()
    to_open = set()

    for cell in get_field_flat(field):
        if cell.content > 0:
            # unknown cells count equals cell number, flag them
            if cell.invisible_neighbors() == cell.content:
                for neigbor in cell.get_neighbors():
                    if not neigbor.is_visible() and not neigbor.is_flagged():
                        to_flag.add(neigbor)
            # flag count equals cell number, open non-flags around
            elif cell.flagged_neighbors() == cell.content:
                for neigbor in cell.get_neighbors():
                    if not neigbor.is_visible() and not neigbor.is_flagged():
                        to_open.add(neigbor)

    return (to_flag, to_open)


# non-trivial AI, works by iteration over possible mine layout around the cell
# if a trivial algorithm returns the same cell for every single permutation,
#   it is added to output
# return two sets: cells to flag and cells to open
def nontrivial(cell, field):
    # sets to return
    ret_flags = set()
    ret_opens = set()
    # if cell is viable for permutation tests
    if cell.is_visible() and cell.content - cell.flagged_neighbors() > 0:
        group = cell.get_suspects()
        if group:
            # lists that hold results for every permutation
            to_flags = []
            to_opens = []
            # generate all possible permutations with length equal to unflagged mines around
            for combo in combinations(group, cell.content - cell.flagged_neighbors()):
                # for each permutation, flag corresponding cells
                for another_cell in combo:
                    another_cell.set_content(FLAGGED)
                # then run trivial AI
                to_flag_i, to_open_i = trivial(field)
                # then reset the flags that were placed
                for another_cell in combo:
                    another_cell.set_content(UNKNOWN)
                # append iteration's results to lists
                to_flags.append(to_flag_i)
                to_opens.append(to_open_i)
            # if there are some results, check for cells that are in every set returned
            # these cells should be returned
            if to_flags:
                if to_flags[0]:
                    for element in to_flags[0]:
                        if in_all(element, to_flags):
                            ret_flags.add(element)
            if to_opens:
                if to_opens[0]:
                    for element in to_opens[0]:
                        if in_all(element, to_opens):
                            ret_opens.add(element)

    return (ret_flags, ret_opens)


# main AI function, utilises both "trivial" and "nontrivial" algorithms
def do_ai(field):
    # first, try trivial AI If there are results, return them
    to_flag, to_open = trivial(field)
    if to_flag or to_open:
        return (to_flag, to_open)
    # else try nontrivial AI
    else:
        for cell in get_field_flat(field):
            cell_flags, cell_opens = nontrivial(cell, field)
            to_flag = to_flag | cell_flags
            to_open = to_open | cell_opens
        if to_flag or to_open:
            return (to_flag, to_open)
        # if nontrivial AI fails, time to glorious random
        # algorithm picks known cell with the least chance to blow up around it
        #   and opens a random closed neighbor cell
        else:
            # init with max value since we search for minimum
            chance = 1
            possible = set()
            for cell in get_field_flat(field):
                # if cell is known and there are some non-flagged mines around
                if cell.is_visible() and cell.content - cell.flagged_neighbors() > 0:
                    # calculate the chances as number of mines around by number of unknown cells around
                    num = cell.content - cell.flagged_neighbors()
                    denum = cell.invisible_neighbors() - cell.flagged_neighbors()
                    if denum > 0:
                        # if we found a new minimum, store it
                        current_chance = num / denum
                        if chance - current_chance > DELTA:
                            chance = current_chance
                            possible = set((cell,))
                        # else if chance is equal to current minimum, append cell to list 
                        elif abs(chance - current_chance) <= DELTA:
                            possible.add(cell)
            # if there are possibilities to random,
            # choose a random unopened cell around a random cell with the least chance to fail
            if possible:
                cell = possible.pop()
                to_open = choice(cell.get_suspects())
                return (set(), set((to_open,)))
            # this is used when all three algorithms above fail
            # opens every single unopened cell
            # useful for unopened cells on field border
            else:
                to_open = set()
                for cell in get_field_flat(field):
                    if not cell.is_visible():
                        to_open.add(cell)
                return (set(), to_open)
