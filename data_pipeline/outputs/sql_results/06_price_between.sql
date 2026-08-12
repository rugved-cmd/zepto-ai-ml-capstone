SELECT
            b.title,
            c.category_name AS category,
            b.price_inr
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id
        WHERE b.price_inr BETWEEN 2000 AND 5000
        ORDER BY
            b.price_inr DESC
        LIMIT 10;
