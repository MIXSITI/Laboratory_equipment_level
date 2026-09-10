from datetime import date

user_name = "Иванов Алексей"
user_role = "студент"
user_level_str = "2"
has_safety_briefing = True

equipment_name = "Спектрофотометр UV-1800"
is_operational = True
is_under_maintenance = False
required_access_level = 2
hourly_rate = 1200.0

booking_date = date(2026, 9, 15)
duration_hours_str = "3.0"

# Преобразование типов данных
user_access_level = int(user_level_str)
duration_hours = float(duration_hours_str)
is_student = (user_role.lower() == "студент")


# 1. Функция проверки готовности оборудования (условные конструкции)
def check_equipment_availability(operational, under_maintenance):
    if not operational:
        return "Оборудование неисправно"
    if under_maintenance:
        return "Оборудование на техническом обслуживании"
    return "Оборудование готово к работе"


# 2. Функция проверки допуска пользователя (операции сравнения, логические операции)
def check_user_access(user_level, min_level, briefing_passed):
    if not briefing_passed:
        return False
    if user_level >= min_level:
        return True
    return False


# 3. Функция расчета стоимости бронирования (арифметические операции, условия)
def calculate_booking_cost(rate, hours, student):
    base_cost = rate * hours
    if student:
        discount = 0.5  # Скидка 50% для студентов
        total_cost = base_cost - (base_cost * discount)
    else:
        total_cost = base_cost
    return round(total_cost, 2)


# Вывод информации о бронировании (начальный сценарий ПР1)
print(f"Пользователь: {user_name} ({user_role}, уровень допуска: {user_access_level})")
print(f"Оборудование: {equipment_name}")
print(f"Дата бронирования: {booking_date}")
print(f"Длительность: {duration_hours} ч.")

# Проверка оборудования
equipment_status = check_equipment_availability(is_operational, is_under_maintenance)
print(f"Статус оборудования: {equipment_status}")

# Проверка допуска
user_access_granted = check_user_access(user_access_level, required_access_level, has_safety_briefing)
if user_access_granted:
    print("Допуск пользователя: Разрешен")
else:
    print("Допуск пользователя: Отклонен")

# Расчет стоимости и итоговый статус заявки
if equipment_status == "Оборудование готово к работе" and user_access_granted:
    cost = calculate_booking_cost(hourly_rate, duration_hours, is_student)
    print(f"Стоимость бронирования: {cost} руб.")
    print("Статус заявки: Бронирование успешно подтверждено")
else:
    print("Статус заявки: Бронирование невозможно")





