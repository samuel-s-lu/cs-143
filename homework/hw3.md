### Part 1
**(a)**
```SQL
SELECT
    name
FROM
    ta_restaurant
WHERE
    name LIKE '%Lotus%';
```

**(b)**
```SQL
SELECT
    rating,
    COUNT(id) AS total
FROM
    ta_restaurant
GROUP BY
    rating
ORDER BY
    rating;
```

**(c)**
```SQL
SELECT
    city,
    AVG(rating)::DECIMAL(4,3) AS average_rating,
    COUNT(id) AS num_rest
FROM
    ta_restaurant
GROUP BY
    city
ORDER BY
    average_rating DESC;
```

**(d)**
```SQL
SELECT
    city
FROM
    ta_restaurant r
JOIN
    ta_cuisine c
ON
    r.id = c.id
WHERE
    cuisine = 'Indian'
GROUP BY
    city
HAVING
    AVG(rating) > 4.2
ORDER BY
    AVG(rating) DESC;
```

### Part 2
**(a)**
```SQL
SELECT
    s.id AS trip_id,
    (EXTRACT(EPOCH FROM (e.time - s.time))/60)::int AS trip_length
FROM
    sf_trip_start s
LEFT JOIN
    sf_trip_end e
ON
    s.id = e.id
ORDER BY
    trip_id ASC;
```

**(b)**
```SQL
SELECT
    SUM(CASE
        WHEN e.time IS NULL THEN 1
        ELSE 0
        END) AS stolen_bikes
FROM
    sf_trip_start s
LEFT JOIN
    sf_trip_end e
ON
    s.id = e.id;
```

**(c)**
```SQL
SELECT
    s.id AS trip_id,
    CASE
        WHEN e.time IS NOT NULL THEN (3.49+(EXTRACT(EPOCH FROM (e.time - s.time))/60) * 0.3)::DECIMAL(8,2)
        ELSE 1000::DECIMAL(6,2)
    END AS trip_charge
FROM
    sf_trip_start s
LEFT JOIN
    sf_trip_end e
ON
    s.id = e.id
ORDER BY
    trip_id ASC;
```

**(d)**
```SQL
SELECT
    s.id AS trip_id,
    user_type,
    CASE
        WHEN user_type = 'Subscriber' THEN TRUNC(COALESCE((EXTRACT(EPOCH FROM (e.time - s.time))/60) * 0.2, 1000), 2)
        WHEN user_type = 'Customer' THEN TRUNC(COALESCE(3.49+(EXTRACT(EPOCH FROM (e.time - s.time))/60) * 0.3, 1000), 2)
    END AS trip_cost
FROM
    sf_trip_start s
LEFT JOIN
    sf_trip_end e
ON
    s.id = e.id
JOIN
    sf_trip_user u
ON
    s.id = u.trip_id
ORDER BY
    trip_id ASC;
```

**(e)**
The query would return a charge of 1000 for any trip that did not start in March 2022.

This is because the LEFT JOIN will always return all rows in the left table (trip start in this case) regardless if the join condition is fulfilled or not. But in the rows where the join condition fails, the columns from the right table (trip end) become all NULL, resulting the query treating them like lost bikes without an end time.

This tells me that I should only filter rows in the WHERE clause, and never in the ON clause, or else it leads to join anomalies.

```SQL
SELECT
    s.id AS trip_id,
    CASE
        WHEN e.time IS NOT NULL THEN (3.49+(EXTRACT(EPOCH FROM (e.time - s.time))/60) * 0.3)::DECIMAL(8,2)
        ELSE 1000::DECIMAL(6,2)
    END AS trip_charge
FROM
    sf_trip_start s
LEFT JOIN
    sf_trip_end e
ON
    s.id = e.id AND EXTRACT(YEAR FROM s.time) = 2022 AND EXTRACT(MONTH FROM s.time) = 3
ORDER BY
    trip_id ASC;
```