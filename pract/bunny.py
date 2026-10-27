import bpy
import math
import os
from mathutils import Vector


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


def material(name, color, roughness=0.65, metallic=0.0, emission=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True

    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic

    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1)
        bsdf.inputs["Emission Strength"].default_value = 2.0

    return mat


def sphere(name, loc, scale, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=40,
        ring_count=24,
        location=loc
    )

    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.rotation_euler = rotation
    obj.data.materials.append(mat)

    bpy.ops.object.shade_smooth()

    return obj


def look_at(obj, point):
    direction = Vector(point) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def make_scene():
    # Материалы
    white = material("Мягкий белый мех", (0.92, 0.94, 0.97), 0.82)
    pink = material("Розовый", (0.95, 0.42, 0.55), 0.55)
    black = material("Глаза", (0.012, 0.018, 0.028), 0.18)
    nose_mat = material("Носик", (0.95, 0.58, 0.68), 0.35)
    floor_mat = material("Матовый пол", (0.68, 0.73, 0.75), 0.9)

    # Тело и голова (увеличен масштаб по X и Y для придания толщины)
    sphere(
        "Тело",
        (0, 0, 1.15),
        (0.85, 0.72, 0.92),  # Было: (0.67, 0.53, 0.88)
        white
    )

    sphere(
        "Голова",
        (0, -0.03, 2.25),
        (0.86, 0.76, 0.74),  # Было: (0.72, 0.61, 0.67)
        white
    )

    # Уши
    sphere(
        "Левое ухо",
        (-0.42, 0.02, 3.05),
        (0.21, 0.18, 0.62),
        white,
        (0, math.radians(-10), math.radians(-5))
    )

    sphere(
        "Правое ухо",
        (0.42, 0.02, 3.07),
        (0.21, 0.18, 0.62),
        white,
        (0, math.radians(10), math.radians(5))
    )

    # Розовая внутренняя часть ушей
    sphere(
        "Внутри левого уха",
        (-0.42, -0.125, 3.08),
        (0.12, 0.065, 0.46),
        pink,
        (0, math.radians(-10), math.radians(-5))
    )

    sphere(
        "Внутри правого уха",
        (0.42, -0.125, 3.10),
        (0.12, 0.065, 0.46),
        pink,
        (0, math.radians(10), math.radians(5))
    )

    # Глаза (немного раздвинуты под новую ширину головы)
    sphere(
        "Левый глаз",
        (-0.32, -0.72, 2.37),
        (0.11, 0.06, 0.15),
        black
    )

    sphere(
        "Правый глаз",
        (0.32, -0.72, 2.37),
        (0.11, 0.06, 0.15),
        black
    )

    # Блики в глазах
    sphere(
        "Блик левого глаза",
        (-0.345, -0.77, 2.415),
        (0.027, 0.018, 0.035),
        white
    )

    sphere(
        "Блик правого глаза",
        (0.295, -0.77, 2.415),
        (0.027, 0.018, 0.035),
        white
    )

    # Нос и пухлые щёчки
    sphere(
        "Нос",
        (0, -0.81, 2.19),
        (0.095, 0.05, 0.055),
        nose_mat
    )

    sphere(
        "Левая щёчка",
        (-0.25, -0.71, 2.12),
        (0.18, 0.07, 0.13),  # Было: (0.15, 0.055, 0.105)
        white
    )

    sphere(
        "Правая щёчка",
        (0.25, -0.71, 2.12),
        (0.18, 0.07, 0.13),  # Было: (0.15, 0.055, 0.105)
        white
    )

    # Руки
    sphere(
        "Левая рука",
        (-0.68, -0.02, 1.27),
        (0.22, 0.22, 0.36),
        white,
        (0, 0, math.radians(-25))
    )

    sphere(
        "Правая рука",
        (0.58, -0.02, 1.27),
        (0.22, 0.22, 0.36),
        white,
        (0, 0, math.radians(25))
    )

    # Упитанные лапки
    sphere(
        "Левая лапка",
        (-0.38, -0.08, 0.38),
        (0.26, 0.30, 0.25),  # Было: (0.22, 0.25, 0.25)
        white
    )

    sphere(
        "Правая лапка",
        (0.38, -0.08, 0.38),
        (0.26, 0.30, 0.25),  # Было: (0.22, 0.25, 0.25)
        white
    )

    # Хвост
    sphere(
        "Пушистый хвост",
        (0, 0.65, 0.78),
        (0.26, 0.26, 0.26),
        white
    )

    # Пол
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0.08))
    bpy.context.object.name = "Пол"
    bpy.context.object.data.materials.append(floor_mat)

    # Основной источник света
    bpy.ops.object.light_add(type='AREA', location=(4, -4, 6))
    key = bpy.context.object
    key.name = "Мягкий основной свет"
    key.data.energy = 650
    key.data.shape = 'DISK'
    key.data.size = 5
    look_at(key, (0, 0, 1.8))

    # Дополнительный свет
    bpy.ops.object.light_add(type='AREA', location=(-4, -1, 3.5))
    fill = bpy.context.object
    fill.name = "Заполняющий свет"
    fill.data.energy = 300
    fill.data.size = 4
    look_at(fill, (0, 0, 1.8))

    # Камера (немного отодвинута назад по Y под новые пропорции)
    bpy.ops.object.camera_add(location=(4.7, -9.2, 4.0))
    cam = bpy.context.object
    cam.name = "Камера"
    cam.data.lens = 55
    look_at(cam, (0, 0, 1.75))
    bpy.context.scene.camera = cam

    # Настройки рендера
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(os.path.expanduser("~"), "bunny_render.png")

    # Фон
    scene.world.color = (0.45, 0.48, 0.52)
    scene.view_settings.view_transform = 'AgX'
    scene.camera.data.dof.use_dof = False
    scene.render.film_transparent = False

    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.32, 0.36, 0.42, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35

    # Выполнение рендера
    bpy.ops.render.render(write_still=True)

    print("Готово! Рендер сохранён:", scene.render.filepath)
    print("Количество объектов в сцене:", len(bpy.context.scene.objects))


clear_scene()
make_scene()
