import bpy
from mathutils import *
from math import *

import fiona
import os

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

        for part in coordinates:
            if len(part) == 2:
                x = part[0]
                y = part[1]
                vertices.append(sph2euc(100.0, rad(x), rad(y-90)))
            else:
                for x,y in part:
                    vertices.append(sph2euc(100.0, rad(x), rad(y-90)))

        faces.append(list(range(face_start,len(vertices))))

    mesh.from_pydata(vertices, edges, faces)

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.flip_normals()
    bpy.ops.mesh.extrude_region_shrink_fatten(
        MESH_OT_extrude_region={
            "use_normal_flip":False,
            "use_dissolve_ortho_edges":False,
            "mirror":False},
        TRANSFORM_OT_shrink_fatten={
            "value":5.0,
            "use_even_offset":False,
            "mirror":False,
            "use_proportional_edit":False,
            "proportional_edit_falloff":'SMOOTH',
            "proportional_size":1,
            "use_proportional_connected":False,
            "use_proportional_projected":False,
            "snap":False,
            "snap_target":'CLOSEST',
            "snap_point":(0, 0, 0),
            "snap_align":False,
            "snap_normal":(0, 0, 0),
            "release_confirm":True,
            "use_accurate":False}
        )

    bpy.ops.object.editmode_toggle()


shape = fiona.open(os.path.join(os.getcwd(), "TM_WORLD_BORDERS-0.3.shp"))

for country in shape:
    creata_country(country)
