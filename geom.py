import math

def is_point_in_rectangle(point, rect):
    """Проверяет, находится ли точка в прямоугольнике"""
    px, py = point
    x_min, y_min, x_max, y_max = rect
    return x_min <= px <= x_max and y_min <= py <= y_max

def line_intersection(p1, p2, q1, q2):
    def det(a, b, c, d):
        return a * d - b * c

    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = q1
    x4, y4 = q2

    denom = det(x1 - x2, y1 - y2, x3 - x4, y3 - y4)

    if denom == 0:
        return None

    px = det(det(x1, y1, x2, y2), x1 - x2, det(x3, y3, x4, y4), x3 - x4) / denom
    py = det(det(x1, y1, x2, y2), y1 - y2, det(x3, y3, x4, y4), y3 - y4) / denom

    if (min(x1, x2) <= px <= max(x1, x2) and 
        min(y1, y2) <= py <= max(y1, y2) and
        min(x3, x4) <= px <= max(x3, x4) and 
        min(y3, y4) <= py <= max(y3, y4)):
        return (px, py)

    return None

def segment_square_intersection(segment, square):
    (x1, y1), (x2, y2) = segment
    (x_min, y_min), (x_max, y_max) = square

    square_edges = [
        ((x_min, y_min), (x_max, y_min)),
        ((x_max, y_min), (x_max, y_max)),
        ((x_max, y_max), (x_min, y_max)),
        ((x_min, y_max), (x_min, y_min)) 
    ]

    intersections = []

    for edge in square_edges:
        intersection = line_intersection((x1, y1), (x2, y2), edge[0], edge[1])
        if intersection:
            intersections.append(intersection)

    unique_intersections = list(set(intersections))
    return unique_intersections


def rotate_points(points, angle):
    rotated_points = []
    for px, py in points:
        new_x = px * math.cos(angle) - py * math.sin(angle)
        new_y = px * math.sin(angle) + py * math.cos(angle)

        rotated_points.append(new_x)
        rotated_points.append(new_y)

    return rotated_points
