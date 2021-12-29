import math
import pygame


def project(vector, w, h, fov, distance):
    factor = math.atan(fov / 2 * math.pi / 180) / (distance + vector.z)
    x = vector.x * factor * w + w / 2 + 450
    y = -vector.y * factor * w + h / 2 + 50
    return pygame.math.Vector3(x, y, vector.z)


def rotate_vertices(vertices, angle, axis):
    return [v.rotate(angle, axis) for v in vertices]


def scale_vertices(vertices, s):
    return [pygame.math.Vector3(v[0] * s[0], v[1] * s[1], v[2] * s[2]) for v in vertices]


def translate_vertices(vertices, t):
    return [v + pygame.math.Vector3(t) for v in vertices]


def project_vertices(vertices, w, h, fov, distance):
    return [project(v, w, h, fov, distance) for v in vertices]


class Mesh:
    def __init__(self, vertices, faces):
        self.__vertices = [pygame.math.Vector3(v) for v in vertices]
        self.__faces = faces

    def rotate(self, angle, axis):
        self.__vertices = rotate_vertices(self.__vertices, angle, axis)

    def scale(self, s):
        self.__vertices = scale_vertices(self.__vertices, s)

    def translate(self, t):
        self.__vertices = translate_vertices(self.__vertices, t)

    def calculate_average_z(self, vertices):
        return [(i, sum([vertices[j].z for j in f]) / len(f)) for i, f in enumerate(self.__faces)]

    def get_face(self, index):
        return self.__faces[index]

    def get_vertices(self):
        return self.__vertices

    def create_polygon(self, face, vertices):
        return [(vertices[i].x, vertices[i].y) for i in [*face, face[0]]]


class Scene:
    def __init__(self, mehses, fov, distance):
        self.meshes = mehses
        self.fov = fov
        self.distance = distance
        self.euler_angles = [45, 45, 0]

    def transform_vertices(self, vertices, width, height):
        transformed_vertices = vertices
        axis_list = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
        for angle, axis in reversed(list(zip(list(self.euler_angles), axis_list))):
            transformed_vertices = rotate_vertices(transformed_vertices, angle, axis)
        transformed_vertices = project_vertices(transformed_vertices, width, height, self.fov, self.distance)
        return transformed_vertices

    def draw(self, surface):
        polygons = []
        for mesh in self.meshes:
            transformed_vertices = self.transform_vertices(mesh.get_vertices(), 1000, 1000)
            avg_z = mesh.calculate_average_z(transformed_vertices)
            for z in avg_z:
                pointlist = mesh.create_polygon(mesh.get_face(z[0]), transformed_vertices)
                polygons.append((pointlist, z[1]))

        for poly in sorted(polygons, key=lambda x: x[1], reverse=True):
            xs = sum(list(map(lambda x: x[0], poly[0]))) / len(poly[0])
            ys = sum(list(map(lambda x: x[1], poly[0]))) / len(poly[0])
            pygame.draw.polygon(surface, (255 * (xs / 1500), 255 * (ys / 1000), 130 + 30 * poly[1]), poly[0])
            pygame.draw.polygon(surface, (0, 0, 0), poly[0], 1)


# base cube properties
vertices = [(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1), (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1)]
faces = [(0, 1, 2, 3), (1, 5, 6, 2), (5, 4, 7, 6), (4, 0, 3, 7), (3, 2, 6, 7), (1, 0, 4, 5)]

# cube matrix
cube_origins = [
    (-1, -1, 0), (0, -1, 0), (1, -1, 0),
    (-1, 0, 0), (0, 0, 0), (1, 0, 0),
    (-1, 1, 0), (0, 1, 0), (1, 1, 0),

    (-1, -1, 1), (0, -1, 1), (1, -1, 1),
    (-1, 0, 1), (0, 0, 1), (1, 0, 1),
    (-1, 1, 1), (0, 1, 1), (1, 1, 1),

    (-1, -1, -1), (0, -1, -1), (1, -1, -1),
    (-1, 0, -1), (0, 0, -1), (1, 0, -1),
    (-1, 1, -1), (0, 1, -1), (1, 1, -1)
]

meshes = []
for origin in cube_origins:
    cube = Mesh(vertices, faces)
    cube.scale((0.3, 0.3, 0.3))
    cube.translate(origin)
    meshes.append(cube)

scene = Scene(meshes, 90, 5)

pygame.init()
window = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()

run = True
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == 27:
                    run = False
                else:
                    if event.key == 119:
                        scene.euler_angles[0] += 15
                    elif event.key == 115:
                        scene.euler_angles[0] -= 15
                    elif event.key == 113:
                        scene.euler_angles[1] += 15
                    elif event.key == 101:
                        scene.euler_angles[1] -= 15
                    elif event.key == 97:
                        scene.euler_angles[2] += 15
                    elif event.key == 100:
                        scene.euler_angles[2] -= 15

    window.fill((255, 255, 255))
    scene.draw(window)
    #scene.euler_angles[1] += 1
    pygame.display.flip()

    pygame.display.set_caption(str(clock.get_fps()))

pygame.quit()
