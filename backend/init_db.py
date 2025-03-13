from app.database import SessionLocal
from app.initial_data import init_db

def main():
    db = SessionLocal()
    try:
        result = init_db(db)
        print(result["message"])
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 