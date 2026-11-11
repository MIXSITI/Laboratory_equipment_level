-- =========================================================================
-- Roomly / Система бронирования лабораторного оборудования (ПР7)
-- Набор из 11 проверенных SQL-запросов к базе данных data/roomly.sqlite
-- =========================================================================

-- 1. Выборка списка (SELECT + ORDER BY): каталог всех помещений и приборов
SELECT
    id,
    name,
    inventory_number,
    capacity,
    hourly_rate
FROM rooms
ORDER BY name ASC;

-- 2. Выборка списка (SELECT + ORDER BY по двум полям): пользователи лаборатории
SELECT
    id,
    name,
    email,
    role,
    access_level
FROM users
ORDER BY role DESC, name ASC;

-- 3. Фильтрация (WHERE): помещения вместимостью от 30 человек
SELECT
    id,
    name,
    capacity,
    hourly_rate
FROM rooms
WHERE capacity >= 30
ORDER BY capacity DESC;

-- 4. Фильтрация по состоянию (WHERE): только активные бронирования
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

-- 5. Фильтрация диапазона (WHERE + BETWEEN): ресурсы со ставкой 800..2000 руб/ч
SELECT
    id,
    name,
    inventory_number,
    hourly_rate
FROM rooms
WHERE hourly_rate BETWEEN 800.0 AND 2000.0
ORDER BY hourly_rate ASC;

-- 6. Соединение таблиц (INNER JOIN): полные сведения об активных заявках
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

-- 7. Соединение таблиц с фильтрацией (JOIN + WHERE): заявки пользователя ID=1
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

-- 8. Подзапрос (WHERE + NOT IN): свободные ресурсы на дату 2026-09-20
SELECT
    rooms.id,
    rooms.name,
    rooms.capacity,
    rooms.hourly_rate
FROM rooms
WHERE rooms.operational = 1
  AND rooms.under_maintenance = 0
  AND rooms.id NOT IN (
      SELECT bookings.room_id
      FROM bookings
      WHERE bookings.booking_date = '2026-09-20'
        AND bookings.is_cancelled = 0
  )
ORDER BY rooms.name ASC;

-- 9. Агрегатная функция (COUNT): количество активных бронирований
SELECT
    COUNT(*) AS active_bookings_count
FROM bookings
WHERE is_cancelled = 0;

-- 10. Агрегатные функции (COUNT, SUM, AVG, MIN, MAX): финансовая сводка
SELECT
    COUNT(*) AS total_active_bookings,
    SUM(cost) AS total_revenue,
    AVG(cost) AS average_booking_cost,
    MIN(cost) AS min_booking_cost,
    MAX(cost) AS max_booking_cost
FROM bookings
WHERE is_cancelled = 0;

-- 11. Группировка (LEFT JOIN + GROUP BY): число заявок по всем ресурсам (включая 0)
SELECT
    rooms.id AS room_id,
    rooms.name AS room_name,
    COUNT(bookings.id) AS bookings_count
FROM rooms
LEFT JOIN bookings ON rooms.id = bookings.room_id
                   AND bookings.is_cancelled = 0
GROUP BY rooms.id, rooms.name
ORDER BY bookings_count DESC, rooms.name ASC;

-- 12. Фильтрация групп (GROUP BY + HAVING): востребованные ресурсы (> 1 заявки)
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

-- 13. Группировка по ролям (JOIN + GROUP BY + SUM): расходы по категориям пользователей
SELECT
    users.role AS user_role,
    COUNT(bookings.id) AS bookings_count,
    SUM(bookings.cost) AS total_spent
FROM users
JOIN bookings ON users.id = bookings.user_id
WHERE bookings.is_cancelled = 0
GROUP BY users.role
ORDER BY total_spent DESC;
