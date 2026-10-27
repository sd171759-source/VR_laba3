import math
import numpy as np




# Стереокамеры: расчёт позиций левого и правого глаза
# ==========================================
print("=== Стереокамеры: расчёт позиций левого и правого глаза ===")
head_pos = np.array([0.0, -2.0, 1.6])
ipd = 0.065  # 65 мм в метрах

# Смещение по оси X (влево и вправо от центра головы)
left_eye = head_pos + np.array([-ipd / 2, 0.0, 0.0])
right_eye = head_pos + np.array([ipd / 2, 0.0, 0.0])
dist = np.linalg.norm(right_eye - left_eye)

print(f"Левый глаз:  {left_eye}")
print(f"Правый глаз: {right_eye}")
print(f"Расстояние между камерами: {dist:.3f} м\n")



# Поле зрения (FOV) и размер объекта в кадре
# ==========================================
print("=== Поле зрения (FOV) и размер объекта в кадре ===")
fov_deg = 100.0
distance = 5.0
object_width = 2.0

# Расчет ширины видимой области на расстоянии distance
visible_width = 2 * distance * math.tan(math.radians(fov_deg / 2))
frame_share = (object_width / visible_width) * 100

print(f"FOV = {fov_deg} град, расстояние = {distance} м")
print(f"Ширина видимой области: {visible_width:.2f} м")
print(f"Объект шириной {object_width} м занимает {frame_share:.1f}% ширины кадра\n")



# Кватернионы: поворот вектора взгляда
# ==========================================
print("=== Кватернионы: поворот вектора взгляда ===")
angle = math.radians(90)
# Поворот вокруг оси Z: [w, x, y, z]
w = math.cos(angle / 2)
z = math.sin(angle / 2)
q = np.array([w, 0.0, 0.0, z])

# Исходный вектор взгляда "вперед"
v = np.array([0.0, 1.0, 0.0])

# Формируем матрицу поворота из кватерниона
r_mat = np.array([
    [1 - 2*(q[3]**2), -2*q[0]*q[3], 0.0],
    [2*q[0]*q[3], 1 - 2*(q[3]**2), 0.0],
    [0.0, 0.0, 1.0]
])

v_rotated = r_mat.dot(v)

print(f"Кватернион (w,x,y,z): {np.round(q, 3)}")
print(f"Вектор взгляда до поворота: {v}")
print(f"После поворота на 90 по Z: {np.round(v_rotated, 1)}\n")



# Бюджет кадра для частоты VR-дисплея
# ==========================================
print("=== Бюджет кадра для частоты VR-дисплея ===")
frequencies = [72, 90, 120]
render_time = 9.5

for hz in frequencies:
    budget = 1000 / hz
    print(f"{hz} Гц -> бюджет кадра {budget:.2f} мс")
    if hz == 90:
        status = "успеваем" if render_time <= budget else "НЕ успеваем"
        print(f"Рендер {render_time} мс при 90 Гц ({budget:.2f} мс): {status}")
print()



# Выбор уровня детализации (LOD) по расстоянию
# ==========================================
print("=== Выбор уровня детализации (LOD) по расстоянию ===")
distances = [2, 10, 35, 80]

for d in distances:
    if d < 5:
        lod = "LOD0 (высокая детализация)"
    elif d < 20:
        lod = "LOD1 (средняя)"
    elif d < 50:
        lod = "LOD2 (низкая)"
    else:
        lod = "culled (не рендерится)"
    print(f" {d:2d} м -> {lod}")
print()



# Полигональный бюджет VR-сцены
# ==========================================
print("=== Полигональный бюджет VR-сцены ===")
total_budget = 1000000
poly_per_object = 8000
test_objects = 150

max_objects = total_budget // poly_per_object
current_load = test_objects * poly_per_object
exceeded = current_load > total_budget

print(f"Бюджет сцены: {total_budget:,} тр., на объект: {poly_per_object:,} тр.")
print(f"Максимум объектов в бюджете: {max_objects}")
status = "ПРЕВЫШЕН бюджет" if exceeded else "в рамках бюджета"
print(f"Сцена из {test_objects} объектов = {current_load:,} тр. -> {status}\n")



# Задержка motion-to-photon
# ==========================================
print("=== Задержка motion-to-photon ===")
tracking = 2.0
processing = 3.0
render = 11.0
display = 4.0
threshold = 20.0

total_latency = tracking + processing + render + display
is_comfortable = total_latency < threshold

print(f"Датчик (трекинг): {tracking} мс")
print(f"Обработка: {processing} мс")
print(f"Рендер: {render} мс")
print(f"Вывод на дисплей: {display} мс")
print(f"Суммарная задержка motion-to-photon: {total_latency} мс")
print(f"Комфортно (< 20 мс)? {is_comfortable}\n")


