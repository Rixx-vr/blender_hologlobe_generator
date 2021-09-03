import bpy
from mathutils import *
from math import *

import fiona

C = bpy.context
D = bpy.data

def sph2euc(r, phi, theta):
    x = r * cos(phi) * sin(theta)
    y = r * sin(phi) * sin(theta)
    z = r * cos(theta)

    return (x, y, z)


def rad(deg):
    return deg * pi / 180.0


def creata_country(country):
    data = country['geometry']['coordinates']
    name = country['properties']['NAME']

    mesh = D.meshes.new(name)
    object = D.objects.new(mesh.name, mesh)

    collection = D.collections.get("Collection")
    collection.objects.link(object)
    C.view_layer.objects.active = object

    vertices = list()
    edges = []
    faces = list()

    for section in data:
        if len(section) > 1:
            coordinates = section
        else:
            coordinates = section[0]
        face_start = len(vertices)

        for x, y in coordinates:
            vertices.append(sph2euc(100.0, rad(x), rad(y-90)))

        faces.append(list(range(face_start,len(vertices))))

    mesh.from_pydata(vertices, edges, faces)
