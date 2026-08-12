SELECT
            b.title,
            c.category_name AS category,
            b.rating,
            b.price_inr
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id
        WHERE b.rating >= 4
        ORDER BY
            b.rating DESC,
            b.price_inr DESC;
