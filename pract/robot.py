import bpy
import math
from mathutils import Vector
import os


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights
    ):
        for item in list(datablocks):
            if item.users == 0:
                datablocks.remove(item)


def material(name, color, metallic=0.0, roughness=0.45, emission=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True

    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic

    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1)
        bsdf.inputs["Emission Strength"].default_value = 4.0

    return mat


def sphere(name, loc, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=20,
        location=loc
    )

    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)

    bpy.ops.object.shade_smooth()

    return obj


def cube(name, loc, scale, mat, bevel=0.08):
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=loc
    )

    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)

    mod = obj.modifiers.new(
        "Скругление граней",
        'BEVEL'
    )

    mod.width = bevel
    mod.segments = 3

    obj.modifiers.new(
        "Сглаживание поверхности",
        'WEIGHTED_NORMAL'
    )

    return obj


def cylinder_between(name, start, end, radius, mat, vertices=32):
    # Создание цилиндра между двумя точками
    a = Vector(start)
    b = Vector(end)

    direction = b - a
    midpoint = (a + b) / 2

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=direction.length,
        location=midpoint
    )

    obj = bpy.context.object
    obj.name = name

    # Поворот цилиндра в направлении второй точки
    obj.rotation_euler = direction.to_track_quat(
        'Z', 'Y'
    ).to_euler()

    obj.data.materials.append(mat)

    bpy.ops.object.shade_smooth()

    # Скругление цилиндра
    bevel = obj.modifiers.new(
        "Скругление цилиндра",
        'BEVEL'
    )

    bevel.width = min(radius * 0.25, 0.04)
    bevel.segments = 2

    return obj


def look_at(obj, point):
    obj.rotation_euler = (
        Vector(point) - obj.location
    ).to_track_quat('-Z', 'Y').to_euler()


def make_scene():
    # Материалы робота
    dark = material(
        "Тёмный графитовый металл",
        (0.055, 0.075, 0.105),
        metallic=0.82,
        roughness=0.28
    )

    gold = material(
        "Золотистые суставы",
        (0.72, 0.43, 0.13),
        metallic=0.78,
        roughness=0.25
    )

    glow = material(
        "Голубое свечение",
        (0.45, 0.9, 1.0),
        metallic=0.1,
        roughness=0.2,
        emission=(0.45, 0.9, 1.0)
    )

    black = material(
        "Тёмные подошвы",
        (0.018, 0.022, 0.03),
        metallic=0.45,
        roughness=0.35
    )

    floor_mat = material(
        "Серый пол",
        (0.19, 0.21, 0.25),
        roughness=0.82
    )

    # Голова
    cube(
        "Голова",
        (0, 0, 2.65),
        (1.05, 0.52, 0.68),
        dark,
        0.09
    )

    # Корпус
    cube(
        "Корпус",
        (0, 0, 1.55),
        (1.15, 0.62, 1.0),
        dark,
        0.10
    )

    # Антенна
    cylinder_between(
        "Стержень антенны",
        (0, 0, 3.00),
        (0, 0, 3.32),
        0.035,
        gold
    )

    sphere(
        "Шарик антенны",
        (0, 0, 3.38),
        (0.09, 0.09, 0.09),
        gold
    )

    # Светящиеся глаза
    sphere(
        "Левый глаз",
        (-0.23, -0.275, 2.72),
        (0.095, 0.045, 0.105),
        glow
    )

    sphere(
        "Правый глаз",
        (0.23, -0.275, 2.72),
        (0.095, 0.045, 0.105),
        glow
    )

    # Индикатор на груди
    sphere(
        "Окантовка индикатора",
        (0, -0.335, 1.62),
        (0.27, 0.055, 0.27),
        black
    )

    sphere(
        "Светящийся индикатор",
        (0, -0.385, 1.62),
        (0.17, 0.045, 0.17),
        glow
    )

    # Руки и суставы
    for side, label in [
        (-1, "Левая"),
        (1, "Правая")
    ]:
        shoulder = (side * 0.78, 0, 2.05)
        elbow = (side * 1.00, -0.01, 1.55)
        hand = (side * 1.08, -0.02, 1.18)

        sphere(
            label + " плечевой шарнир",
            shoulder,
            (0.16, 0.16, 0.16),
            gold
        )

        cylinder_between(
            label + " верхняя рука",
            shoulder,
            elbow,
            0.075,
            dark
        )

        sphere(
            label + " локтевой шарнир",
            elbow,
            (0.12, 0.12, 0.12),
            gold
        )

        cylinder_between(
            label + " предплечье",
            elbow,
            hand,
            0.07,
            dark
        )

        sphere(
            label + " кисть",
            hand,
            (0.12, 0.12, 0.12),
            gold
        )

    # Ноги и ступни
    for side, label in [
        (-1, "Левая"),
        (1, "Правая")
    ]:
        hip = (side * 0.30, 0, 1.02)
        ankle = (side * 0.32, 0, 0.38)

        cylinder_between(
            label + " нога",
            hip,
            ankle,
            0.105,
            dark
        )

        cube(
            label + " ступня",
            (side * 0.32, -0.08, 0.20),
            (0.38, 0.48, 0.18),
            black,
            0.035
        )

    # Пол
    bpy.ops.mesh.primitive_plane_add(
        size=200,
        location=(0, 0, 0.08)
    )

    bpy.context.object.name = "Пол"
    bpy.context.object.data.materials.append(floor_mat)

    # Основной источник света
    bpy.ops.object.light_add(
        type='AREA',
        location=(3.5, -4, 5.5)
    )

    key = bpy.context.object
    key.name = "Основной свет"
    key.data.energy = 750
    key.data.size = 4

    look_at(key, (0, 0, 1.7))

    # Заполняющий свет
    bpy.ops.object.light_add(
        type='AREA',
        location=(-4, -2, 3)
    )

    fill = bpy.context.object
    fill.name = "Заполняющий свет"
    fill.data.energy = 400
    fill.data.size = 4

    look_at(fill, (0, 0, 1.7))

    # Камера
    bpy.ops.object.camera_add(
        location=(4.2, -7.5, 3.1)
    )

    cam = bpy.context.object
    cam.name = "Камера"
    cam.data.lens = 55

    look_at(cam, (0, 0, 1.75))

    bpy.context.scene.camera = cam

    # Настройки рендера
    scene = bpy.context.scene

    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        scene.render.engine = 'BLENDER_EEVEE'

    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100

    scene.render.image_settings.file_format = 'PNG'

    scene.render.filepath = os.path.join(
        os.path.expanduser("~"),
        "robot_render.png"
    )

    # Цвет фона
    scene.world.use_nodes = True

    scene.world.node_tree.nodes["Background"].inputs[
        "Color"
    ].default_value = (0.035, 0.045, 0.065, 1)

    scene.world.node_tree.nodes["Background"].inputs[
        "Strength"
    ].default_value = 0.45

    scene.view_settings.view_transform = 'AgX'

    # Выполнение рендера
    bpy.ops.render.render(write_still=True)

    print("Готово! Рендер сохранён:", scene.render.filepath)
    print(
        "Количество объектов в сцене:",
        len(bpy.context.scene.objects)
    )


clear_scene()
make_scene()