from datetime import date


# 1. Функция проверки готовности оборудования
def check_equipment_availability(operational, under_maintenance):
    if not operational:
        return "Оборудование неисправно"
    if under_maintenance:
        return "Оборудование на техническом обслуживании"
    return "Оборудование готово к работе"


# 2. Функция проверки допуска пользователя
def check_user_access(user_level, min_level, briefing_passed):
    if not briefing_passed:
        return False
    if user_level >= min_level:
        return True
    return False


# 3. Функция расчета стоимости бронирования
def calculate_booking_cost(rate, hours, student):
    base_cost = rate * hours
    if student:
        discount = 0.5  # Скидка 50% для студентов
        total_cost = base_cost - (base_cost * discount)
    else:
        total_cost = base_cost
    return round(total_cost, 2)


print("=== Ввод данных для бронирования оборудования ===")

user_name = input("Введите ФИО пользователя: ")
user_role = input("Введите статус пользователя (студент / сотрудник): ")
user_level_str = input("Введите уровень допуска пользователя (число, например 2): ")
briefing_str = input("Пройден ли инструктаж по ТБ (да/нет): ")

equipment_name = input("Введите название оборудования: ")
operational_str = input("Оборудование исправно (да/нет): ")
maintenance_str = input("Оборудование сейчас на техобслуживании (да/нет): ")
required_level_str = input("Требуемый уровень допуска для оборудования (число, например 2): ")
hourly_rate_str = input("Почасовая ставка аренды (руб/час, например 1200): ")

booking_date_str = input("Введите дату бронирования (ГГГГ-ММ-ДД, например 2026-09-15): ")
duration_hours_str = input("Введите длительность бронирования в часах (например 3.0): ")

user_access_level = int(user_level_str)
has_safety_briefing = (briefing_str.strip().lower() == "да")

is_operational = (operational_str.strip().lower() == "да")
is_under_maintenance = (maintenance_str.strip().lower() == "да")
required_access_level = int(required_level_str)
hourly_rate = float(hourly_rate_str)

booking_date = date.fromisoformat(booking_date_str.strip())
duration_hours = float(duration_hours_str)
is_student = (user_role.strip().lower() == "студент")

print("\n=== Результат обработки заявки ===")
print(f"Пользователь: {user_name} ({user_role}, уровень допуска: {user_access_level})")
print(f"Оборудование: {equipment_name}")
print(f"Дата бронирования: {booking_date}")
print(f"Длительность: {duration_hours} ч.")

# 1. Проверка оборудования
equipment_status = check_equipment_availability(is_operational, is_under_maintenance)
print(f"Статус оборудования: {equipment_status}")

# 2. Проверка допуска
user_access_granted = check_user_access(user_access_level, required_access_level, has_safety_briefing)
if user_access_granted:
    print("Допуск пользователя: Разрешен")
else:
    print("Допуск пользователя: Отклонен")

# 3. Расчет стоимости и итоговый статус заявки
if equipment_status == "Оборудование готово к работе" and user_access_granted:
    cost = calculate_booking_cost(hourly_rate, duration_hours, is_student)
    print(f"Стоимость бронирования: {cost} руб.")
    print("Статус заявки: Бронирование успешно подтверждено")
else:
    print("Статус заявки: Бронирование невозможно")

