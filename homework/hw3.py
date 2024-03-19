import psycopg2

configs = dict(user='cs143', password='cs143', host='localhost', port='5432', database='cs143')

with psycopg2.connect(**configs) as connection:
    connection.autocommit = True
    with connection.cursor() as cur:
        cur.execute("""
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
                        trip_id ASC
                    LIMIT 5;
                    """)
        print('SAN FRANCISCO BIKE SHARE\nRoster of Charges\n')
        print('Trip ID     Charge')
        print('--------    ---------')
        rows = cur.fetchall()
        for trip_id, _, trip_cost in rows:
            print(f'{trip_id}         $ {trip_cost}')