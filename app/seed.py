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
    print("🚀 Lancement du seed 'Grand Format' (100 pins)...")
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
                    ("Maison A-Frame", "https://images.unsplash.com/photo-1510076857177-7470076d4098?w=500"),
                    ("Intérieur Japandi", "https://images.unsplash.com/photo-1585412727339-54e4bae3bbf9?w=500"),
                    ("Façade Haussmannienne", "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=500"),
                    ("Loft Industriel", "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=500"),
                    ("Cuisine Scandinave", "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=500"),
                    ("Terrasse Rooftop", "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=500"),
                    ("Bureau Minimaliste", "https://images.unsplash.com/photo-1497366216548-37526070297c?w=500"),
                    ("Salle de Bain Marbre", "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=500"),
                    ("Bibliothèque Murale", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500"),
                    ("Chalet Montagne", "https://images.unsplash.com/photo-1519974719765-e6559eac2575?w=500"),
                    ("Arche en Pierre", "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500"),
                    ("Pont Suspendu", "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=500"),
                    ("Tour de Verre", "https://images.unsplash.com/photo-1486325212027-8081e485255e?w=500"),
                    ("Couloir Voûté", "https://images.unsplash.com/photo-1555448248-2571daf6344b?w=500"),
                    ("Escalier Hélicoïdal", "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=500"),
                    ("Dome Géodésique", "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=500"),
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
                    ("Serveur Data", "https://images.unsplash.com/photo-1558494949-ef010cbdcc51?w=500"),
                    ("Drone FPV", "https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=500"),
                    ("Imprimante 3D", "https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?w=500"),
                    ("Robot Industriel", "https://images.unsplash.com/photo-1555255707-c07966088b7b?w=500"),
                    ("VR Casque", "https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac?w=500"),
                    ("Fibre Optique", "https://images.unsplash.com/photo-1558494949-ef010cbdcc51?w=500"),
                    ("Puce Processeur", "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=500"),
                    ("Smartwatch", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"),
                    ("LED Strip", "https://images.unsplash.com/photo-1608502985333-7b1c4c4b5295?w=500"),
                    ("Console Rétro", "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=500"),
                    ("Oscilloscope", "https://images.unsplash.com/photo-1581093588401-fbb62a02f120?w=500"),
                    ("Raspberry Pi", "https://images.unsplash.com/photo-1629654291663-b91ad427698f?w=500"),
                    ("Câbles Ethernet", "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=500"),
                    ("Studio Son", "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=500"),
                    ("Satellite Dish", "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=500"),
                ]
            },
            {
                "user": "Charlie_Travel", "board": "Vues d'Asie", "cat": "Voyage",
                "pins": [
                    ("Temple Kyoto", "https://images.unsplash.com/photo-1493780474015-ba834ff0ce2f?w=500"),
                    ("Rue d'Osaka", "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"),
                    ("Forêt de Bambous", "https://images.unsplash.com/photo-1503614472-8c93d56e92ce?w=500"),
                    ("Marché de nuit", "https://images.unsplash.com/photo-1513415277900-a62401e19be4?w=500"),
                    ("Street Food", "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500"),
                    ("Torii Rouge", "https://images.unsplash.com/photo-1478436127897-769e1b3f0f36?w=500"),
                    ("Mont Fuji", "https://images.unsplash.com/photo-1542315204-8f40f90d7e93?w=500"),
                    ("Rizières Bali", "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=500"),
                    ("Angkor Vat", "https://images.unsplash.com/photo-1548366086-7f1b76106622?w=500"),
                    ("Sampan Vietnam", "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=500"),
                    ("Lanterne Chine", "https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?w=500"),
                    ("Tuk-tuk Bangkok", "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=500"),
                    ("Grande Muraille", "https://images.unsplash.com/photo-1508193638397-1c4234db14d8?w=500"),
                    ("Plage Thaïlande", "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=500"),
                    ("Monsoon Inde", "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=500"),
                    ("Marché Flottant", "https://images.unsplash.com/photo-1555217851-6141535bd771?w=500"),
                    ("Taxi Jaune Mumbai", "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=500"),
                    ("Moines Birmanie", "https://images.unsplash.com/photo-1528181304800-259b08848526?w=500"),
                    ("Junk Halong Bay", "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=500"),
                    ("Cerisiers Japon", "https://images.unsplash.com/photo-1522383225653-ed111181a951?w=500"),
                ]
            },
            {
                "user": "David_Art", "board": "Sculptures & Musées", "cat": "Art",
                "pins": [
                    ("Statue Grecque", "https://images.unsplash.com/photo-1549490349-8643362247b5?w=500"),
                    ("Pyramide du Louvre", "https://images.unsplash.com/photo-1505691938895-1758d7eaa511?w=500"),
                    ("Peinture Huile", "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=500"),
                    ("Atelier d'artiste", "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=500"),
                    ("Art Moderne", "https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=500"),
                    ("Graffiti Urbain", "https://images.unsplash.com/photo-1499781350541-7783f6c6a0c8?w=500"),
                    ("Aquarelle Florale", "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=500"),
                    ("Céramique Japonaise", "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=500"),
                    ("Bronze Africain", "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=500"),
                    ("Vitrail Gothique", "https://images.unsplash.com/photo-1548625361-58a9d386c2fe?w=500"),
                    ("Calligraphie Arabe", "https://images.unsplash.com/photo-1496715976403-7e36dc43f17b?w=500"),
                    ("Fresque Romaine", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500"),
                    ("Lithographie", "https://images.unsplash.com/photo-1455734729978-db1ae4f687fc?w=500"),
                    ("Art Numérique", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=500"),
                    ("Mosaïque Byzantine", "https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?w=500"),
                    ("Dessin Charbon", "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=500"),
                    ("Tapisserie Médiévale", "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?w=500"),
                    ("Portrait Baroque", "https://images.unsplash.com/photo-1578926288207-a90a5366b2e0?w=500"),
                    ("Origami Complexe", "https://images.unsplash.com/photo-1569017388730-020b5f80a004?w=500"),
                    ("Installation Lumière", "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=500"),
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
                    ("Vagues géantes", "https://images.unsplash.com/photo-1505118380757-91f5f5832de0?w=500"),
                    ("Léopard Savane", "https://images.unsplash.com/photo-1456926631375-92c8ce872def?w=500"),
                    ("Baleine Bleue", "https://images.unsplash.com/photo-1568430462989-44163eb1752f?w=500"),
                    ("Volcan Actif", "https://images.unsplash.com/photo-1504701954957-2010ec3bcec1?w=500"),
                    ("Forêt Amazonienne", "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=500"),
                    ("Lac Turquoise", "https://images.unsplash.com/photo-1439853949212-36589f9d9b58?w=500"),
                    ("Colibri en vol", "https://images.unsplash.com/photo-1444464666168-49d633b86797?w=500"),
                    ("Canyon Colorado", "https://images.unsplash.com/photo-1474044159687-1ee9f3a51722?w=500"),
                    ("Mangrove Tropicale", "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=500"),
                    ("Renard Arctique", "https://images.unsplash.com/photo-1474511320723-9a56873867b5?w=500"),
                    ("Champignons Forêt", "https://images.unsplash.com/photo-1518791841217-8f162f1912da?w=500"),
                    ("Coucher Soleil Mer", "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=500"),
                    ("Fjord Norvégien", "https://images.unsplash.com/photo-1531366930477-0f430a78f36c?w=500"),
                    ("Papillon Monarque", "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500"),
                ]
            },
            {
    "user": "Bob_Tech", "board": "Art Numérique", "cat": "Art",
    "pins": [
        ("Pixel Art", "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=500"),
        ("Glitch Art", "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500"),
        ("NFT Design", "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500"),
    ]
},
        ]

        for item in content_map:
            cur.execute("INSERT INTO boards (title, category, user_id) VALUES (%s, %s, %s) RETURNING id",
                        (item["board"], item["cat"], user_ids[item["user"]]))
            b_id = cur.fetchone()['id']
            for title, url in item["pins"]:
                cur.execute("INSERT INTO pins (title, image_url, board_id, likes) VALUES (%s, %s, %s, %s)",
                            (title, url, b_id, 0))

        conn.commit()
        total = sum(len(i['pins']) for i in content_map)
        print(f"Terminé ! 5 utilisateurs et {total} pins créés.")

    except Exception as e:
        print(f"Erreur: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed()