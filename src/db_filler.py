import psycopg2
from psycopg2.extras import execute_values

from config import DB_CONFIG, TRACKED_COUNTRIES
from request_api import APIAdapter
from aeroplanes_info import Aeroplane


class DBFiller:
    """Создаёт таблицы и наполняет их данными 4 стран."""

    def __init__(self, config: dict = None) -> None:
        self._config = config or DB_CONFIG
        self._api = APIAdapter()

    def create_tables(self) -> None:
        ddl = """
            CREATE TABLE IF NOT EXISTS countries (
                country_id   SERIAL PRIMARY KEY,
                name         VARCHAR(100) NOT NULL UNIQUE,
                bounding_box VARCHAR(200)
            );

            CREATE TABLE IF NOT EXISTS aeroplanes (
                aeroplane_id  SERIAL PRIMARY KEY,
                country_id    INTEGER NOT NULL REFERENCES countries(country_id) ON DELETE CASCADE,
                callsign      VARCHAR(20)      NOT NULL DEFAULT 'Unknown',
                origin_country VARCHAR(100)    NOT NULL,
                velocity      DOUBLE PRECISION,
                baro_altitude DOUBLE PRECISION,
                fetched_at    TIMESTAMP        NOT NULL DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_aeroplanes_country
                ON aeroplanes(country_id);
            CREATE INDEX IF NOT EXISTS idx_aeroplanes_callsign
                ON aeroplanes(callsign);
        """
        with psycopg2.connect(**self._config) as conn, conn.cursor() as cur:
            cur.execute(ddl)

    def _upsert_country(self, cur, name: str, bbox: str) -> int:
        cur.execute(
            """
            INSERT INTO countries (name, bounding_box)
            VALUES (%s, %s)
            ON CONFLICT (name) DO UPDATE SET bounding_box = EXCLUDED.bounding_box
            RETURNING country_id;
            """,
            (name, bbox),
        )
        return cur.fetchone()[0]

    def fill_tracked_countries(self, countries=None) -> dict:
        """Заполняет БД данными по 4 странам. Возвращает статистику."""
        countries = countries or TRACKED_COUNTRIES
        stats = {}

        with psycopg2.connect(**self._config) as conn, conn.cursor() as cur:
            for country in countries:
                try:
                    bbox_list = self._api.get_geo_coordinates(country)
                    bbox_str = ",".join(bbox_list)
                    country_id = self._upsert_country(cur, country, bbox_str)

                    response = self._api.get_aeroplanes(country)
                    states = (response or {}).get("states") or []

                    rows = []
                    for state in states:
                        if len(state) < 10:
                            continue
                        try:
                            plane = Aeroplane(
                                callsign=state[1],
                                origin_country=state[2],
                                velocity=state[9],
                                baro_altitude=state[7],
                            )
                        except TypeError, ValueError:
                            continue
                        rows.append(
                            (
                                country_id,
                                plane.callsign,
                                plane.origin_country,
                                plane.velocity,
                                plane.baro_altitude,
                            )
                        )

                    if rows:
                        execute_values(
                            cur,
                            """
                            INSERT INTO aeroplanes
                                (country_id, callsign, origin_country, velocity, baro_altitude)
                            VALUES %s;
                            """,
                            rows,
                        )

                    stats[country] = len(rows)
                    print(f"[{country}] сохранено: {len(rows)}")

                except Exception as e:
                    stats[country] = 0
                    print(f"[{country}] ошибка: {e}")

        return stats
