import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext
import os
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

DATABASE_URL = "postgresql://postgres:password123@postgres:5432/dayfold"

def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def seed():
    print("🚀 Lancement du seed 'Grand Format' (30 pins)...")
    conn = get_connection()
    cur = conn.cursor()

    try:
        print("Nettoyage de la base...")
        cur.execute("TRUNCATE users, boards, pins, follows RESTART IDENTITY CASCADE;")

        users_data = [
            ("Alice_Design", "alice@test.com", "password123"),
            ("Bob_Tech", "bob@test.com", "password123"),
            ("Charlie_Travel", "charlie@test.com", "password123"),
            ("David_Art", "david@test.com", "password123"),
            ("Eve_Nature", "eve@test.com", "password123")
        ]
        user_ids = {}
        for name, email, pwd in users_data:
            cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
                        (name, email, hash_password(pwd)))
            user_ids[name] = cur.fetchone()['id']

        follows = [
            (user_ids["Alice_Design"], user_ids["Bob_Tech"]),
            (user_ids["Alice_Design"], user_ids["Charlie_Travel"]),
            (user_ids["Bob_Tech"], user_ids["Eve_Nature"]),
            (user_ids["Charlie_Travel"], user_ids["David_Art"]),
            (user_ids["David_Art"], user_ids["Alice_Design"]),
            (user_ids["Eve_Nature"], user_ids["Alice_Design"])
        ]
        for f, t in follows:
            cur.execute("INSERT INTO follows (follower_id, following_id) VALUES (%s, %s)", (f, t))

        content_map = [
            {
                "user": "Alice_Design", "board": "Architecture Moderne", "cat": "Design",
                "pins": [
                    ("Villa Minimaliste", "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=500"),
                    ("Escalier en béton", "https://images.unsplash.com/photo-1511818333244-f25694d67c9f?w=500"),
                    ("Baie Vitrée", "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=500"),
                    ("Piscine à débordement", "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=500"),
                    ("Maison A-Frame", "https://images.unsplash.com/photo-1510076857177-7470076d4098?w=500")
                ]
            },
            {
                "user": "Bob_Tech", "board": "Hardware & Neon", "cat": "Tech",
                "pins": [
                    ("Setup Gaming", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=500"),
                    ("Circuit Imprimé", "https://images.unsplash.com/photo-1518770660439-4636190af475?w=500"),
                    ("Néon Tokyo", "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=500"),
                    ("Clavier Custom", "https://images.unsplash.com/photo-1595044426077-d36d9236d54a?w=500"),
                    ("Écran incurvé", "https://images.unsplash.com/photo-1547082299-de196ea013d6?w=500"),
                    ("Serveur Data", "https://images.unsplash.com/photo-1558494949-ef010cbdcc51?w=500")
                ]
            },
            {
                "user": "Charlie_Travel", "board": "Vues d'Asie", "cat": "Voyage",
                "pins": [
                    ("Temple Kyoto", "https://images.unsplash.com/photo-1493780474015-ba834ff0ce2f?w=500"),
                    ("Rue d'Osaka", "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"),
                    ("Forêt de Bambous", "https://images.unsplash.com/photo-1503614472-8c93d56e92ce?w=500"),
                    ("Marché de nuit", "https://images.unsplash.com/photo-1513415277900-a62401e19be4?w=500"),
                    ("Street Food", "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500")
                ]
            },
            {
                "user": "David_Art", "board": "Sculptures & Musées", "cat": "Art",
                "pins": [
                    ("Statue Grecque", "https://images.unsplash.com/photo-1549490349-8643362247b5?w=500"),
                    ("Pyramide du Louvre", "https://images.unsplash.com/photo-1505691938895-1758d7eaa511?w=500"),
                    ("Peinture Huile", "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=500"),
                    ("Atelier d'artiste", "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=500"),
                    ("Art Moderne", "https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=500")
                ]
            },
            {
                "user": "Eve_Nature", "board": "Wild Photography", "cat": "Nature",
                "pins": [
                    ("Cerf en forêt", "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?w=500"),
                    ("Montagnes enneigées", "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=500"),
                    ("Cascade Islande", "https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=500"),
                    ("Plage tropicale", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=500"),
                    ("Aurore Boréale", "https://images.unsplash.com/photo-1531366930477-0f430a78f36c?w=500"),
                    ("Désert Sahara", "https://images.unsplash.com/photo-1473580044384-7ba9967e16a0?w=500"),
                    ("Vagues géantes", "https://images.unsplash.com/photo-1505118380757-91f5f5832de0?w=500")
                ]
            }
        ]

        for item in content_map:
            cur.execute("INSERT INTO boards (title, category, user_id) VALUES (%s, %s, %s) RETURNING id",
                        (item["board"], item["cat"], user_ids[item["user"]]))
            b_id = cur.fetchone()['id']
            for title, url in item["pins"]:
                cur.execute("INSERT INTO pins (title, image_url, board_id, likes) VALUES (%s, %s, %s, %s)",
                            (title, url, b_id, 0))
        
        conn.commit()
        print(f"Terminé ! 5 utilisateurs et {sum(len(i['pins']) for i in content_map)} pins créés.")

    except Exception as e:
        print(f"Erreur: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed()