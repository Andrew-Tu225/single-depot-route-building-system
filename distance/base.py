from abc import ABC, abstractmethod
from models.point import Point

class DistanceCalculator(ABC):
    @abstractmethod
    def calculate_distance(self, p1: Point, p2: Point) -> float:
        """Calculate distance between two points."""
        pass