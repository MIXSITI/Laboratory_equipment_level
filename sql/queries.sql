-- ====================================================================
-- Практическая работа № 7. SQL-запросы проекта Roomly
-- Предметная область: Система бронирования лабораторного оборудования
-- ====================================================================

-- --------------------------------------------------------------------
-- Категория 1: Выборка списков объектов (SELECT, ORDER BY)
-- --------------------------------------------------------------------

-- Запрос 1. Список всех помещений/оборудования с сортировкой по названию
SELECT
    id,
    name,
    inventory_number,
    capacity,
    hourly_rate
FROM rooms
ORDER BY name ASC;

-- Запрос 2. Список пользователей лаборатории с сортировкой по роли и имени
SELECT
    id,
    name,
    email,
    role,
    access_level
FROM users
ORDER BY role DESC, name ASC;


-- --------------------------------------------------------------------
-- Категория 2: Фильтрация данных (WHERE, операторы сравнения и логические связки)
-- --------------------------------------------------------------------

-- Запрос 3. Поиск помещений с вместимостью не менее 30 человек
SELECT
    id,
    name,
    capacity,
    hourly_rate
FROM rooms
WHERE capacity >= 30
ORDER BY capacity DESC;

-- Запрос 4. Выборка действующих (не отмененных) бронирований
SELECT
    id,
    room_id,
    user_id,
    booking_date,
    duration_hours,
    cost
FROM bookings
WHERE is_cancelled = 0
ORDER BY booking_date ASC;

-- Запрос 5. Фильтрация оборудования по диапазону почасовой ставки аренды
SELECT
    id,
    name,
    inventory_number,
    hourly_rate
FROM rooms
WHERE hourly_rate BETWEEN 800.0 AND 2000.0
ORDER BY hourly_rate ASC;


-- --------------------------------------------------------------------
-- Категория 3: Соединение таблиц (JOIN, многотабличные выборки, подзапросы)
-- --------------------------------------------------------------------

-- Запрос 6. Полная сводка об активных бронированиях с именами пользователей и помещений
SELECT
    bookings.id,
    bookings.booking_date,
    bookings.duration_hours,
    bookings.cost,
    rooms.name AS room_name,
    rooms.capacity,
    users.name AS user_name,
    users.email AS user_email
FROM bookings
JOIN rooms ON bookings.room_id = rooms.id
JOIN users ON bookings.user_id = users.id
WHERE bookings.is_cancelled = 0
ORDER BY bookings.booking_date ASC;

-- Запрос 7. История всех бронирований конкретного пользователя (студента с id = 1)
SELECT
    bookings.id,
    bookings.booking_date,
    rooms.name AS room_name,
    bookings.duration_hours,
    bookings.cost,
    bookings.is_cancelled
FROM bookings
JOIN rooms ON bookings.room_id = rooms.id
WHERE bookings.user_id = 1
ORDER BY bookings.booking_date DESC;

-- Запрос 8. Поиск свободных помещений на выбранную дату с подзапросом NOT IN
SELECT
    rooms.id,
    rooms.name,
    rooms.capacity,
    rooms.hourly_rate
FROM rooms
WHERE rooms.id NOT IN (
    SELECT bookings.room_id
    FROM bookings
    WHERE bookings.booking_date = '2026-09-20'
      AND bookings.is_cancelled = 0
)
ORDER BY rooms.name ASC;


-- --------------------------------------------------------------------
-- Категория 4: Агрегирующие функции (COUNT, SUM, AVG, MIN, MAX)
-- --------------------------------------------------------------------

-- Запрос 9. Подсчет общего количества активных бронирований
SELECT
    COUNT(*) AS active_bookings_count
FROM bookings
WHERE is_cancelled = 0;

-- Запрос 10. Расчет суммарной стоимости, средней стоимости и диапазона цен активных бронирований
SELECT
    COUNT(*) AS total_active_bookings,
    SUM(cost) AS total_revenue,
    AVG(cost) AS average_booking_cost,
    MIN(cost) AS min_booking_cost,
    MAX(cost) AS max_booking_cost
FROM bookings
WHERE is_cancelled = 0;


-- --------------------------------------------------------------------
-- Категория 5: Группировка записей (GROUP BY) и фильтрация групп (HAVING)
-- --------------------------------------------------------------------

-- Запрос 11. Количество активных бронирований по каждому помещению (включая не забронированные)
SELECT
    rooms.id AS room_id,
    rooms.name AS room_name,
    COUNT(bookings.id) AS bookings_count
FROM rooms
LEFT JOIN bookings ON rooms.id = bookings.room_id
                   AND bookings.is_cancelled = 0
GROUP BY rooms.id, rooms.name
ORDER BY bookings_count DESC, rooms.name ASC;

-- Запрос 12. Помещения с высоким спросом (количество активных бронирований больше 1)
SELECT
    rooms.id AS room_id,
    rooms.name AS room_name,
    COUNT(bookings.id) AS bookings_count
FROM rooms
JOIN bookings ON rooms.id = bookings.room_id
WHERE bookings.is_cancelled = 0
GROUP BY rooms.id, rooms.name
HAVING COUNT(bookings.id) > 1
ORDER BY bookings_count DESC;

-- Запрос 13. Аналитика бронирований в разрезе ролей пользователей
SELECT
    users.role AS user_role,
    COUNT(bookings.id) AS bookings_count,
    SUM(bookings.cost) AS total_spent
FROM users
JOIN bookings ON users.id = bookings.user_id
WHERE bookings.is_cancelled = 0
GROUP BY users.role
ORDER BY total_spent DESC;
