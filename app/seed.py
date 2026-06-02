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
    print("🚀 Launching 'Grand Format' seed (100 pins)...")
    conn = get_connection()
    cur = conn.cursor()

    try:
        print("Cleaning up the database...")
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
                "user": "Alice_Design", "board": "Modern Architecture", "cat": "Design",
                "pins": [
                    ("Minimalist Villa", "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=500"),
                    ("Concrete Staircase", "https://images.unsplash.com/photo-1511818333244-f25694d67c9f?w=500"),
                    ("Large Glass Window", "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=500"),
                    ("Infinity Pool", "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=500"),
                    ("A-Frame House", "https://images.unsplash.com/photo-1510076857177-7470076d4098?w=500"),
                    ("Japandi Interior", "https://images.unsplash.com/photo-1585412727339-54e4bae3bbf9?w=500"),
                    ("Haussmann Façade", "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=500"),
                    ("Industrial Loft", "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=500"),
                    ("Scandinavian Kitchen", "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=500"),
                    ("Rooftop Terrace", "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=500"),
                    ("Minimalist Office", "https://images.unsplash.com/photo-1497366216548-37526070297c?w=500"),
                    ("Marble Bathroom", "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=500"),
                    ("Wall Library", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500"),
                    ("Mountain Cabin", "https://images.unsplash.com/photo-1519974719765-e6559eac2575?w=500"),
                    ("Stone Archway", "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500"),
                    ("Suspension Bridge", "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=500"),
                    ("Glass Tower", "https://images.unsplash.com/photo-1486325212027-8081e485255e?w=500"),
                    ("Vaulted Corridor", "https://images.unsplash.com/photo-1555448248-2571daf6344b?w=500"),
                    ("Spiral Staircase", "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=500"),
                    ("Geodesic Dome", "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=500"),
                ]
            },
            {
                "user": "Bob_Tech", "board": "Hardware & Neon", "cat": "Tech",
                "pins": [
                    ("Gaming Setup", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=500"),
                    ("Circuit Board", "https://images.unsplash.com/photo-1518770660439-4636190af475?w=500"),
                    ("Tokyo Neon", "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=500"),
                    ("Custom Keyboard", "https://images.unsplash.com/photo-1595044426077-d36d9236d54a?w=500"),
                    ("Curved Screen", "https://images.unsplash.com/photo-1547082299-de196ea013d6?w=500"),
                    ("Data Server", "https://images.unsplash.com/photo-1558494949-ef010cbdcc51?w=500"),
                    ("FPV Drone", "https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=500"),
                    ("3D Printer", "https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?w=500"),
                    ("Industrial Robot", "https://images.unsplash.com/photo-1555255707-c07966088b7b?w=500"),
                    ("VR Headset", "https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac?w=500"),
                    ("Fiber Optics", "https://images.unsplash.com/photo-1558494949-ef010cbdcc51?w=500"),
                    ("Processor Chip", "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=500"),
                    ("Smartwatch", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"),
                    ("LED Strip", "https://images.unsplash.com/photo-1608502985333-7b1c4c4b5295?w=500"),
                    ("Retro Console", "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=500"),
                    ("Oscilloscope", "https://images.unsplash.com/photo-1581093588401-fbb62a02f120?w=500"),
                    ("Raspberry Pi", "https://images.unsplash.com/photo-1629654291663-b91ad427698f?w=500"),
                    ("Ethernet Cables", "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=500"),
                    ("Sound Studio", "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=500"),
                    ("Satellite Dish", "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=500"),
                ]
            },
            {
                "user": "Charlie_Travel", "board": "Asian Views", "cat": "Travel",
                "pins": [
                    ("Kyoto Temple", "https://images.unsplash.com/photo-1493780474015-ba834ff0ce2f?w=500"),
                    ("Osaka Street", "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"),
                    ("Bamboo Forest", "https://images.unsplash.com/photo-1503614472-8c93d56e92ce?w=500"),
                    ("Night Market", "https://images.unsplash.com/photo-1513415277900-a62401e19be4?w=500"),
                    ("Street Food", "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500"),
                    ("Red Torii", "https://images.unsplash.com/photo-1478436127897-769e1b3f0f36?w=500"),
                    ("Mount Fuji", "https://images.unsplash.com/photo-1542315204-8f40f90d7e93?w=500"),
                    ("Bali Rice Fields", "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=500"),
                    ("Angkor Wat", "https://images.unsplash.com/photo-1548366086-7f1b76106622?w=500"),
                    ("Vietnam Sampan", "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=500"),
                    ("Chinese Lantern", "https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?w=500"),
                    ("Bangkok Tuk-tuk", "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=500"),
                    ("Great Wall", "https://images.unsplash.com/photo-1508193638397-1c4234db14d8?w=500"),
                    ("Thailand Beach", "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=500"),
                    ("India Monsoon", "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=500"),
                    ("Floating Market", "https://images.unsplash.com/photo-1555217851-6141535bd771?w=500"),
                    ("Mumbai Yellow Taxi", "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=500"),
                    ("Burma Monks", "https://images.unsplash.com/photo-1528181304800-259b08848526?w=500"),
                    ("Halong Bay Junk", "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=500"),
                    ("Japan Cherry Blossoms", "https://images.unsplash.com/photo-1522383225653-ed111181a951?w=500"),
                ]
            },
            {
                "user": "David_Art", "board": "Sculptures & Museums", "cat": "Art",
                "pins": [
                    ("Greek Statue", "https://images.unsplash.com/photo-1549490349-8643362247b5?w=500"),
                    ("Louvre Pyramid", "https://images.unsplash.com/photo-1505691938895-1758d7eaa511?w=500"),
                    ("Oil Painting", "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=500"),
                    ("Artist Studio", "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=500"),
                    ("Modern Art", "https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=500"),
                    ("Urban Graffiti", "https://images.unsplash.com/photo-1499781350541-7783f6c6a0c8?w=500"),
                    ("Floral Watercolor", "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=500"),
                    ("Japanese Ceramics", "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=500"),
                    ("African Bronze", "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=500"),
                    ("Gothic Stained Glass", "https://images.unsplash.com/photo-1548625361-58a9d386c2fe?w=500"),
                    ("Arabic Calligraphy", "https://images.unsplash.com/photo-1496715976403-7e36dc43f17b?w=500"),
                    ("Roman Fresco", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500"),
                    ("Lithography", "https://images.unsplash.com/photo-1455734729978-db1ae4f687fc?w=500"),
                    ("Digital Art", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=500"),
                    ("Byzantine Mosaic", "https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?w=500"),
                    ("Charcoal Drawing", "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=500"),
                    ("Medieval Tapestry", "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?w=500"),
                    ("Baroque Portrait", "https://images.unsplash.com/photo-1578926288207-a90a5366b2e0?w=500"),
                    ("Complex Origami", "https://images.unsplash.com/photo-1569017388730-020b5f80a004?w=500"),
                    ("Light Installation", "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=500"),
                ]
            },
            {
                "user": "Eve_Nature", "board": "Wild Photography", "cat": "Nature",
                "pins": [
                    ("Deer in Forest", "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?w=500"),
                    ("Snowy Mountains", "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=500"),
                    ("Iceland Waterfall", "https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=500"),
                    ("Tropical Beach", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=500"),
                    ("Northern Lights", "https://images.unsplash.com/photo-1531366930477-0f430a78f36c?w=500"),
                    ("Sahara Desert", "https://images.unsplash.com/photo-1473580044384-7ba9967e16a0?w=500"),
                    ("Giant Waves", "https://images.unsplash.com/photo-1505118380757-91f5f5832de0?w=500"),
                    ("Savanna Leopard", "https://images.unsplash.com/photo-1456926631375-92c8ce872def?w=500"),
                    ("Blue Whale", "https://images.unsplash.com/photo-1568430462989-44163eb1752f?w=500"),
                    ("Active Volcano", "https://images.unsplash.com/photo-1504701954957-2010ec3bcec1?w=500"),
                    ("Amazon Rainforest", "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=500"),
                    ("Turquoise Lake", "https://images.unsplash.com/photo-1439853949212-36589f9d9b58?w=500"),
                    ("Hummingbird in Flight", "https://images.unsplash.com/photo-1444464666168-49d633b86797?w=500"),
                    ("Colorado Canyon", "https://images.unsplash.com/photo-1474044159687-1ee9f3a51722?w=500"),
                    ("Tropical Mangrove", "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=500"),
                    ("Arctic Fox", "https://images.unsplash.com/photo-1474511320723-9a56873867b5?w=500"),
                    ("Forest Mushrooms", "https://images.unsplash.com/photo-1518791841217-8f162f1912da?w=500"),
                    ("Sea Sunset", "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=500"),
                    ("Norwegian Fjord", "https://images.unsplash.com/photo-1531366930477-0f430a78f36c?w=500"),
                    ("Monarch Butterfly", "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500"),
                ]
            },
            {
                "user": "Bob_Tech", "board": "Digital Art", "cat": "Art",
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
        print(f"Done! 5 users and {total} pins created.")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed()