from dataclasses import dataclass
from typing import Optional
from .point import Point

@dataclass
class SavingPair:
    point1: Point
    point2: Point
    saving_value: float
    
    def contains_point(self, point: Point) -> bool:
        return point in [self.point1, self.point2]
    
    def get_other_point(self, point: Point) -> Optional[Point]:
        if point == self.point1:
            return self.point2
        elif point == self.point2:
            return self.point1
        return None