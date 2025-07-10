from .base import DistanceCalculator
from models.point import Point

class EuclideanDistanceCalculator(DistanceCalculator):
    def calculate_distance(self, p1: Point, p2: Point) -> float:
        return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5