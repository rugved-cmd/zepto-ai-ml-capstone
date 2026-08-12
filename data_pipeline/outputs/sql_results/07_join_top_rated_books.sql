SELECT
            b.title,
            c.category_name AS category,
            b.price_gbp,
            b.price_inr,
            b.rating,
            b.in_stock
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id
        ORDER BY
            b.rating DESC,
            b.price_inr DESC
        LIMIT 10;
