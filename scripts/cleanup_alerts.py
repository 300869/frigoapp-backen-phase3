import psycopg

conn = psycopg.connect(
    host="localhost", port=5432, dbname="frigoapp", user="frigo_user"
)
with conn, conn.cursor() as cur:
    cur.execute(
        """
        DELETE FROM alerts a
        USING (
          SELECT id, ROW_NUMBER() OVER (
              PARTITION BY product_id, kind, due_date
              ORDER BY id
          ) AS rn
          FROM alerts
        ) d
        WHERE a.id = d.id AND d.rn > 1;
    """
    )
print("Doublons supprimés.")
