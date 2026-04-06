from database import connection

def create_users_table():
    try:
        cur = connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id SERIAL PRIMARY KEY,
                google_sub TEXT UNIQUE,
                email TEXT,
                name TEXT,
                profile_picture_url TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                last_login_at TIMESTAMPTZ DEFAULT NOW(),
                is_onboarded BOOLEAN DEFAULT FALSE)
        """)
        connection.commit()
        print("Table is created successfully!!")
    except Exception as e:
        connection.rollback()
        print(f"Error {e}")
    finally:
        cur.close()

def main():
    create_users_table()

if __name__ == "__main__":
    main()