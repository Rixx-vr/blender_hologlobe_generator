import bpy
from mathutils import *
from math import *

import bmesh

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

    add_material(object, name, 0, 0.6, 1, 0.25)

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

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.mesh.decimate(ratio=0.2)
    bpy.ops.transform.edge_crease(value=1)
    bpy.ops.object.editmode_toggle()

    bpy.ops.object.modifier_add(type='TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier="Triangulate")

    if get_size() > 2000:
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subdivision"].show_only_control_edges = False
        bpy.context.object.modifiers["Subdivision"].render_levels = 1
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].ratio = 0.4
        bpy.ops.object.modifier_apply(modifier="Subdivision")
        bpy.ops.object.modifier_apply(modifier="Decimate")
        normalize_verts()

    extrude()
    add_shapekeys()




def get_size():
    obj = bpy.context.active_object

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    area = sum(f.calc_area() for f in bm.faces)

    bm.free()

    return area


def extrude():
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
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
    bpy.ops.object.editmode_toggle()


#bpy.ops.mesh.faces_shade_smooth()
def add_shapekeys():

    bpy.ops.object.shape_key_add(from_mix=False)
    bpy.ops.object.shape_key_add(from_mix=False)

    bpy.ops.object.editmode_toggle()
    bpy.ops.transform.translate(
        value=(0, 0, 25.0),
        orient_type='NORMAL',
        orient_matrix_type='NORMAL',
        constraint_axis=(False, False, True),
        mirror=False,
        use_proportional_edit=False,
        use_accurate=True)


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


def normalize_verts():
    ref = 100.0

    for v in C.active_object.data.vertices:
        len = v.co.length
        v.co *= (ref/len)

shape = fiona.open(os.path.join(os.getcwd(), "TM_WORLD_BORDERS-0.3.shp"))

for country in shape:
    creata_country(country)

add_sphere()


