"""Thick, curved five-needle brush foliage for the stage-3 resin tree.

The input twig centerlines are in the parent's local coordinates.  Each twig
becomes one mesh object; the helper never changes the scene or uses operators.
"""

import math
import random

import bpy
from mathutils import Vector


_UP = Vector((0.0, 0.0, 1.0))


def _arc_path(points):
    clean = []
    for point in points:
        point = Vector(point)
        if not clean or (point - clean[-1]).length > 1.0e-7:
            clean.append(point)
    lengths = [0.0]
    for left, right in zip(clean, clean[1:]):
        lengths.append(lengths[-1] + (right - left).length)
    return clean, lengths


def _path_point(points, lengths, fraction):
    distance = lengths[-1] * max(0.0, min(1.0, fraction))
    for index in range(len(points) - 1):
        if distance <= lengths[index + 1]:
            tangent = (points[index + 1] - points[index]).normalized()
            part = (distance - lengths[index]) / (
                lengths[index + 1] - lengths[index]
            )
            return points[index].lerp(points[index + 1], part), tangent
    return points[-1].copy(), (points[-1] - points[-2]).normalized()


def _append_needle(vertices, faces, face_materials, base, direction,
                   width, length, droop, sway, material_index):
    """A pointed, diamond-section curved blade with actual side thickness."""
    direction = direction.normalized()
    cross = _UP.cross(direction)
    if cross.length < 1.0e-5:
        cross = Vector((1.0, 0.0, 0.0))
    cross.normalize()
    rings = []
    for fraction, envelope in (
        (0.0, 0.22), (0.18, 0.82), (0.42, 1.0),
        (0.66, 0.78), (0.86, 0.42),
    ):
        center = (base + direction * (length * fraction)
                  - _UP * (droop * fraction * fraction)
                  + cross * (sway * math.sin(math.pi * fraction)))
        tangent = (direction * length - _UP * (2.0 * droop * fraction)
                   + cross * (sway * math.pi * math.cos(math.pi * fraction)))
        tangent.normalize()
        normal = tangent.cross(cross).normalized()
        side = normal.cross(tangent).normalized()
        half_width = width * 0.5 * envelope
        half_thickness = width * 0.19 * envelope
        ring = []
        for offset in (
            side * half_width, normal * half_thickness,
            -side * half_width, -normal * half_thickness,
        ):
            ring.append(len(vertices))
            vertices.append(tuple(center + offset))
        rings.append(ring)

    faces.append(tuple(reversed(rings[0])))
    face_materials.append(material_index)
    for lower, upper in zip(rings, rings[1:]):
        for side_index in range(4):
            next_index = (side_index + 1) % 4
            faces.append((lower[side_index], lower[next_index],
                          upper[next_index], upper[side_index]))
            face_materials.append(material_index)
    tip_index = len(vertices)
    vertices.append(tuple(base + direction * length - _UP * droop))
    for side_index in range(4):
        faces.append((rings[-1][side_index],
                      rings[-1][(side_index + 1) % 4], tip_index))
        face_materials.append(material_index)


def make_brush_crown(coll, parent, twig_specs, materials, seed=20261014,
                     needle_scale=1.0, stage_index=3, name_prefix="RT_"):
    """Return merged needle meshes for flattened, full brush crowns.

    ``twig_specs`` is a sequence of centerline point sequences. ``materials``
    must contain three Blender materials (body, shadow and young-tip colors).
    Each twig's outer half carries close, alternating five-needle fascicles.
    Radial fans are compressed vertically so twigs read as horizontal brushes,
    while individually tapered blades remain visible around the silhouette.
    """
    materials = tuple(materials)
    if len(materials) != 3:
        raise ValueError("make_brush_crown requires exactly three materials")
    rng = random.Random(seed)
    objects = []
    for twig_index, spec in enumerate(twig_specs):
        points, lengths = _arc_path(spec)
        if len(points) < 2 or lengths[-1] < 1.0e-5:
            continue
        vertices, faces, face_materials = [], [], []
        # Close roots fill the inner silhouette; blades open into a comb edge.
        count = max(6, min(16, int(lengths[-1] * 0.52 / 0.042) + 1))
        phase = rng.uniform(-0.22, 0.22)
        for station in range(count):
            fraction = 0.46 + 0.51 * station / max(1, count - 1)
            base, tangent = _path_point(points, lengths, fraction)
            horizontal_side = _UP.cross(tangent)
            if horizontal_side.length < 1.0e-5:
                horizontal_side = Vector((1.0, 0.0, 0.0))
            horizontal_side.normalize()
            radial_up = tangent.cross(horizontal_side).normalized()
            rotation = phase + (station % 2) * 0.22
            for needle_index in range(5):
                angle = rotation + math.tau * needle_index / 5.0
                radial = (horizontal_side * math.cos(angle)
                          + radial_up * (0.31 * math.sin(angle)))
                direction = (tangent * rng.uniform(0.52, 0.63)
                             + radial * rng.uniform(0.79, 0.91)
                             - _UP * rng.uniform(0.02, 0.08)).normalized()
                # A tiny outward spread prevents all five roots sharing a dot.
                root = base + radial * rng.uniform(0.001, 0.006)
                if fraction > 0.83 and rng.random() < 0.52:
                    material_index = 2
                elif math.sin(angle) < -0.2 and rng.random() < 0.70:
                    material_index = 1
                else:
                    material_index = 0 if rng.random() < 0.79 else 1
                _append_needle(
                    vertices, faces, face_materials, root, direction,
                    width=rng.uniform(0.019, 0.027) * needle_scale,
                    length=rng.uniform(0.14, 0.205) * needle_scale,
                    droop=rng.uniform(0.006, 0.018) * needle_scale,
                    sway=rng.uniform(-0.008, 0.008) * needle_scale,
                    material_index=material_index,
                )

        mesh = bpy.data.meshes.new(f"{name_prefix}Needles_{twig_index:02d}_Mesh")
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        for material in materials:
            mesh.materials.append(material)
        for polygon, material_index in zip(mesh.polygons, face_materials):
            polygon.material_index = material_index
            polygon.use_smooth = True
        obj = bpy.data.objects.new(f"{name_prefix}NeedleBrush_{twig_index:02d}", mesh)
        coll.objects.link(obj)
        obj.parent = parent
        obj["organ"] = "five_needle_brush"
        obj["growth_stage"] = stage_index
        obj["twig_index"] = twig_index
        objects.append(obj)
    return objects
