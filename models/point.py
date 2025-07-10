from dataclasses import dataclass

@dataclass
class Point:
    x : int
    y : int
    demand : int

    def __post_init__(self):
        self.coordinates = (self.x, self.y)

    def __hash__(self):
        return hash(self.coordinates)
    
    def __eq__(self, other):
        return isinstance(other, Point) and self.coordinates == other.coordinates
    
    def __repr__(self):
        return f"Point({self.x}, {self.y}, demand={self.demand})"

    