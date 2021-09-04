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


def creata_country(country):
    data = country['geometry']['coordinates']
    name = country['properties']['NAME']

    mesh = D.meshes.new(name)
    object = D.objects.new(mesh.name, mesh)

    add_material(object, name, 0, 1, 0, 1)

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
                vertices.append(sph2euc(100.0, radians(x), radians(y-90)))
            else:
                for x,y in part:
                    vertices.append(sph2euc(100.0, radians(x), radians(y-90)))

        faces.append(list(range(face_start,len(vertices))))

    mesh.from_pydata(vertices, edges, faces)

    bpy.ops.object.modifier_add(type='TRIANGULATE')
    bpy.context.object.modifiers["Triangulate"].quad_method = 'BEAUTY'
    bpy.ops.object.modifier_apply(modifier="Triangulate")

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.flip_normals()
    bpy.ops.mesh.decimate(ratio=0.2)

    extrude()
    add_shapekeys()


def extrude():
    bpy.ops.mesh.extrude_region_shrink_fatten(
        MESH_OT_extrude_region={
            "use_normal_flip":False,
            "use_dissolve_ortho_edges":False,
            "mirror":False},
        TRANSFORM_OT_shrink_fatten={
            "value": 2.0,
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


def add_shapekeys():
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.shape_key_add(from_mix=False)
    bpy.ops.object.shape_key_add(from_mix=False)

    bpy.ops.object.editmode_toggle()
    bpy.ops.transform.translate(value=(0, 0, 25.0),
        orient_type='NORMAL',
        orient_matrix_type='NORMAL',
        constraint_axis=(False, False, True),
        mirror=True,
        use_proportional_edit=True,
        proportional_edit_falloff='SMOOTH',
        proportional_size=1,
        use_proportional_connected=False,
        use_proportional_projected=False)

    bpy.ops.object.editmode_toggle()


def add_material(object, name, r, g, b, a):
    material = D.materials.new(name)
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (r, g, b, a)
    object.data.materials.append(material)


def add_sphere():
    bpy.ops.mesh.primitive_uv_sphere_add(enter_editmode=False,
        align='WORLD',
        location=(0, 0, 0),
        scale=(100, 100, 100))

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.faces_shade_smooth()
    bpy.ops.object.editmode_toggle()
    add_material(C.selected_objects[0], "Globe", 0, 0, 1, 1)


shape = fiona.open(os.path.join(os.getcwd(), "TM_WORLD_BORDERS-0.3.shp"))

for country in shape:
    creata_country(country)

add_sphere()
