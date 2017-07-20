# class of a field cell is the only custom class used
from winmine_const import FLAGGED


class Cell(object):
    # offsets to every neighbor cell, excluding the cell itself
    deltas = tuple((i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i or j))

    def __init__(self, x, y, content):
        self.x = x
        self.y = y
        # 0..8 — numeric content, also FLAGGED and UNKNOWN constants
        self.content = content
        # pointer to a parent field
        self.parent = None

    def __str__(self):
        if self.is_flagged():
            return 'F'
        elif not self.is_visible():
            return '#'
        else:
            return str(self.content)

    def set_content(self, new_value):
        self.content = new_value

    def get_coords(self):
        return (self.x, self.y)

    def set_parent(self, parent_field):
        self.parent = parent_field

    # returns cell at offset or None if coordinates are invalid
    def get_neighbor(self, dx, dy):
        max_x = len(self.parent[0])
        max_y = len(self.parent)

        if 0 <= (self.x + dx) < max_x and 0 <= (self.y + dy) < max_y:
            return self.parent[self.y + dy][self.x + dx]
        else:
            return None

    # returns a list of all neighbors
    def get_neighbors(self):
        ret = []
        for dx, dy in self.deltas:
            n = self.get_neighbor(dx, dy)
            if n:
                ret.append(n)
        return ret

    # UNKNOWN and FLAGGED are both < 0
    def is_visible(self):
        return self.content >= 0

    def is_flagged(self):
        return self.content == FLAGGED

    def flagged_neighbors(self):
        ret = 0
        for neighbor in self.get_neighbors():
            if neighbor.is_flagged():
                ret += 1
        return ret

    def invisible_neighbors(self):
        ret = 0
        for neighbor in self.get_neighbors():
            if not neighbor.is_visible():
                ret += 1
        return ret

    # return a list of clickable neighbors
    def get_suspects(self):
        ret = []
        for cell in self.get_neighbors():
            if not cell.is_visible() and not cell.is_flagged():
                ret.append(cell)
        return ret
