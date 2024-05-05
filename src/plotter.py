import matplotlib.pyplot as plt
import random


def generate_point_coordinates_lists(points):
    x = []
    y = []
    for point in points:
        x.append(point.x)
        y.append(point.y)

    return x, y


def draw_plate(plate_x: int, plate_y: int) -> None:
    x = []
    y = []
    for i in range(0, plate_x + 1):
        for j in range(0, plate_y + 1):
            x.append(i)
            y.append(j)
    plt.figure()
    plt.plot(x, y, 'o', color='red')


def draw_path(genotype, plate_x: int, plate_y: int, start_points) -> None:
    draw_plate(plate_x, plate_y)
    color_i = '000000'
    for i in range(len(genotype)):
        visited = genotype[i].get_all_visited_points(start_points[i])
        for (start, end) in zip(visited, visited[1:]):
            plt.plot([start.x, end.x], [start.y, end.y], color='#' + color_i, linewidth=4)
        color_i = "%06x" % random.randint(0, 0xFFFFFF)
    plt.show()
