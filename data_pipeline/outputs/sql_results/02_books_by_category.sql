SELECT
            c.category_name AS category,
            COUNT(b.book_id) AS book_count
        FROM categories AS c
        JOIN books AS b
            ON c.category_id = b.category_id
        GROUP BY
            c.category_id,
            c.category_name
        ORDER BY
            book_count DESC;
