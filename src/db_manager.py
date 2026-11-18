import psycopg2
from psycopg2.extras import RealDictCursor

from config import DB_CONFIG


class DBManager:
    """Работа с данными о странах и самолётах в PostgreSQL."""

    def __init__(self, config: dict = None) -> None:
        self._config = config or DB_CONFIG

    def _connect(self):
        return psycopg2.connect(**self._config)

    # ---------- Методы из задания ----------

    def get_countries_and_aeroplanes_count(self) -> list:
        """Список стран и количество самолётов в их воздушном пространстве."""
        query = """
            SELECT c.name              AS country,
                   COUNT(a.aeroplane_id) AS aeroplanes_count
            FROM countries c
            LEFT JOIN aeroplanes a ON a.country_id = c.country_id
            GROUP BY c.name
            ORDER BY aeroplanes_count DESC, c.name;
        """
        with self._connect() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

    def get_all_aeroplanes(self) -> list:
        """Все воздушные суда."""
        query = """
            SELECT a.aeroplane_id, a.callsign, a.origin_country,
                   a.velocity, a.baro_altitude, c.name AS country
            FROM aeroplanes a
            JOIN countries c ON c.country_id = a.country_id
            ORDER BY a.aeroplane_id;
        """
        with self._connect() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

    def get_avg_speed(self):
        """Средняя скорость по всем самолётам (None, если данных нет)."""
        query = "SELECT AVG(velocity) AS avg_speed FROM aeroplanes WHERE velocity IS NOT NULL;"
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(query)
            row = cur.fetchone()
            return float(row[0]) if row and row[0] is not None else None

    def get_aeroplanes_with_higher_speed(self) -> list:
        """Самолёты со скоростью выше средней."""
        query = """
            SELECT a.aeroplane_id, a.callsign, a.origin_country,
                   a.velocity, a.baro_altitude, c.name AS country
            FROM aeroplanes a
            JOIN countries c ON c.country_id = a.country_id
            WHERE a.velocity IS NOT NULL
              AND a.velocity > (SELECT AVG(velocity) FROM aeroplanes WHERE velocity IS NOT NULL)
            ORDER BY a.velocity DESC;
        """
        with self._connect() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

    def get_aeroplanes_with_keyword(self, keyword: str) -> list:
        """Самолёты, в позывном которых содержится keyword (регистронезависимо)."""
        if not keyword:
            return []
        query = """
            SELECT a.aeroplane_id, a.callsign, a.origin_country,
                   a.velocity, a.baro_altitude, c.name AS country
            FROM aeroplanes a
            JOIN countries c ON c.country_id = a.country_id
            WHERE a.callsign ILIKE %s
            ORDER BY a.callsign;
        """
        with self._connect() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (f"%{keyword}%",))
            return cur.fetchall()
