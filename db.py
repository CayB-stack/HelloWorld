import pyodbc
import json
import pycountry
import os
 
# ──────────────────────────────────────────────────────────────────────────────
def connect_to_db():
    """Connect to the SQL Server database."""
    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=localhost,1433;"
        "Database=CayTestRequests;"
        "UID=sa;"
        "PWD=Cheese89!@;"
    )
    try:
        conn = pyodbc.connect(conn_str)
        print("✅  Connected to database")
        return conn
    except pyodbc.Error as e:
        print("❌  DB connection error:", e)
        return None
 
def ensure_iso3_column(conn):
    """Add iso3 CHAR(3) column if it doesn't exist."""
    ddl = """
    IF NOT EXISTS (
      SELECT * FROM sys.columns
       WHERE Name = N'iso3'
         AND Object_ID = Object_ID(N'dbo.countries')
    )
    BEGIN
      ALTER TABLE dbo.countries ADD iso3 CHAR(3) NULL;
    END
    """
    cursor = conn.cursor()
    cursor.execute(ddl)
    conn.commit()
    cursor.close()
    print("🔧  Ensured iso3 column exists")
 
def get_iso3(name: str) -> str:
    """
    Lookup ISO‑3 code from country name.
    Returns None (and logs) on failure.
    """
    try:
        return pycountry.countries.lookup(name).alpha_3
    except LookupError:
        print(f"⚠️  ISO3 not found for '{name}'")
        return None
 
def fetch_all_countries(conn):
    """Fetch all rows from countries, return list of dicts."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, iso3 FROM dbo.countries")
    cols = [c[0] for c in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    return [dict(zip(cols, row)) for row in rows]
 
def insert_country_data(conn, country):
    """Insert a new country row (with iso3)."""
    iso3 = get_iso3(country['Name'])
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO dbo.countries
              (name, iso3, capital, population, area, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            country['Name'],
            iso3,
            country.get('Capital'),
            int(country.get('Population', 0)),
            float(country.get('Area', 0)),
            json.dumps(country)
        )
        conn.commit()
        print(f"➕  Inserted {country['Name']} ({iso3})")
    except pyodbc.Error as e:
        print(f"❌  Insert failed for {country['Name']}: {e}")
    finally:
        cursor.close()
 
def update_country_iso(conn, country_name):
    """Back‑fill ISO3 on an existing row."""
    iso3 = get_iso3(country_name)
    if not iso3:
        return
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE dbo.countries SET iso3 = ? WHERE name = ?",
            iso3, country_name
        )
        conn.commit()
        print(f"🔄  Updated ISO3 for {country_name} → {iso3}")
    except pyodbc.Error as e:
        print(f"❌  Update failed for {country_name}: {e}")
    finally:
        cursor.close()
 
# ──────────────────────────────────────────────────────────────────────────────
def main():
    conn = connect_to_db()
    if not conn:
        return
 
    ensure_iso3_column(conn)
 
    # load JSON
    json_path = os.path.join(os.path.dirname(__file__), "countries_data.json")
    with open(json_path, "r", encoding="utf-8") as f:
        countries = json.load(f)
 
    existing = fetch_all_countries(conn)
    existing_names = {r['name']: r for r in existing}
 
    for c in countries:
        name = c['Name']
        if name not in existing_names:
            insert_country_data(conn, c)
        else:
            # back‑fill iso3 if missing
            if not existing_names[name].get('iso3'):
                update_country_iso(conn, name)
            else:
                print(f"✔️  {name} already exists with ISO3={existing_names[name]['iso3']}")
 
    conn.close()
    print("🏁  All done.")
 
if __name__ == "__main__":
    main()