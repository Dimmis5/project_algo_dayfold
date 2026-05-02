# -*- coding: utf-8 -*-
import psycopg2
from neo4j import GraphDatabase

# --------------------
# CONFIG POSTGRESQL
# --------------------
pg_conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="dayfold",
    user="postgres",
    password="tureti123",
    client_encoding="UTF8"
)
# --------------------
# CONFIG NEO4J
# --------------------
neo4j_driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "testinglimit")
)


def create_user(username, email, password_hash):
    with pg_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            ON CONFLICT (email)
            DO UPDATE SET username = EXCLUDED.username
            RETURNING id;
        """, (username, email, password_hash))

        user_id = cur.fetchone()[0]
        pg_conn.commit()

    with neo4j_driver.session() as session:
        session.run("""
            MERGE (u:User {id: $id})
            SET u.username = $username,
                u.email = $email
        """, id=str(user_id), username=username, email=email)

    return user_id


def create_board(name, user_id):
    with pg_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO boards (name, user_id)
            VALUES (%s, %s)
            RETURNING id;
        """, (name, user_id))

        board_id = cur.fetchone()[0]
        pg_conn.commit()

    with neo4j_driver.session() as session:
        session.run("""
            MATCH (u:User {id: $user_id})
            MERGE (b:Board {id: $board_id})
            SET b.name = $name
            MERGE (u)-[:CREATED]->(b)
        """, user_id=str(user_id), board_id=str(board_id), name=name)

    return board_id


def create_pin(title, description, image_url, user_id, category):
    with pg_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO pins (title, description, image_url, user_id, category)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (title, description, image_url, user_id, category))

        pin_id = cur.fetchone()[0]
        pg_conn.commit()

    with neo4j_driver.session() as session:
        session.run("""
            MATCH (u:User {id: $user_id})
            MERGE (p:Pin {id: $pin_id})
            SET p.title = $title,
                p.description = $description,
                p.image_url = $image_url,
                p.category = $category
            MERGE (u)-[:CREATED]->(p)

            MERGE (c:Category {name: $category})
            MERGE (p)-[:IN_CATEGORY]->(c)
        """,
        user_id=str(user_id),
        pin_id=str(pin_id),
        title=title,
        description=description,
        image_url=image_url,
        category=category)

    return pin_id


def add_pin_to_board(board_id, pin_id):
    with pg_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO board_pins (board_id, pin_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (board_id, pin_id))
        pg_conn.commit()

    with neo4j_driver.session() as session:
        session.run("""
            MATCH (b:Board {id: $board_id})
            MATCH (p:Pin {id: $pin_id})
            MERGE (b)-[:CONTAINS]->(p)
        """, board_id=str(board_id), pin_id=str(pin_id))


def like_pin(user_id, pin_id):
    with pg_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO likes (user_id, pin_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (user_id, pin_id))
        pg_conn.commit()

    with neo4j_driver.session() as session:
        session.run("""
            MATCH (u:User {id: $user_id})
            MATCH (p:Pin {id: $pin_id})
            MERGE (u)-[:LIKED]->(p)
        """, user_id=str(user_id), pin_id=str(pin_id))


def save_pin(user_id, pin_id):
    with pg_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO saves (user_id, pin_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (user_id, pin_id))
        pg_conn.commit()

    with neo4j_driver.session() as session:
        session.run("""
            MATCH (u:User {id: $user_id})
            MATCH (p:Pin {id: $pin_id})
            MERGE (u)-[:SAVED]->(p)
        """, user_id=str(user_id), pin_id=str(pin_id))


def share(user_id, pin_id):
    with pg_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO shares (user_id, pin_id)
            VALUES (%s, %s)
            ON CONFLICT (user_id, pin_id) DO NOTHING;
        """, (user_id, pin_id))
        pg_conn.commit()

    with neo4j_driver.session() as session:
        session.run("""
            MATCH (u:User {id: $user_id})
            MATCH (p:Pin {id: $pin_id})
            MERGE (u)-[:SHARED]->(p)
        """, user_id=str(user_id), pin_id=str(pin_id))


def follow_user(follower_id, following_id):
    with pg_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO follows (follower_id, following_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (follower_id, following_id))
        pg_conn.commit()

    with neo4j_driver.session() as session:
        session.run("""
            MATCH (a:User {id: $follower_id})
            MATCH (b:User {id: $following_id})
            MERGE (a)-[:FOLLOWS]->(b)
        """, follower_id=str(follower_id), following_id=str(following_id))


if __name__ == "__main__":

    # USERS
    alice = create_user("alice", "alice@mail.com", "hash")
    bob = create_user("bob", "bob@mail.com", "hash")
    charlie = create_user("charlie", "charlie@mail.com", "hash")
    lea = create_user("lea", "lea@mail.com", "hash")

    emma = create_user("emma", "emma@mail.com", "hash")
    david = create_user("david", "david@mail.com", "hash")
    sophia = create_user("sophia", "sophia@mail.com", "hash")
    lucas = create_user("lucas", "lucas@mail.com", "hash")

    nina = create_user("nina", "nina@mail.com", "hash")
    hugo = create_user("hugo", "hugo@mail.com", "hash")
    jade = create_user("jade", "jade@mail.com", "hash")
    noah = create_user("noah", "noah@mail.com", "hash")

    # PINS
    street1 = create_pin("Streetwear Hoodie", "Urban outfit", "url1", alice, "streetwear")
    street2 = create_pin("Sneaker Style", "Sneaker inspiration", "url2", bob, "streetwear")
    street3 = create_pin("Cargo Pants", "Streetwear cargo", "url3", charlie, "streetwear")

    luxury1 = create_pin("Luxury Dress", "Elegant dress", "url4", emma, "luxury")
    luxury2 = create_pin("Minimalist Bag", "Luxury accessory", "url5", david, "luxury")
    luxury3 = create_pin("Runway Look", "Fashion week style", "url6", sophia, "luxury")

    sport1 = create_pin("Gym Outfit", "Fitness clothing", "url7", nina, "sport")
    sport2 = create_pin("Running Shoes", "Sport shoes", "url8", hugo, "sport")
    sport3 = create_pin("Yoga Set", "Yoga fashion", "url9", jade, "sport")

    bridge_pin = create_pin("Sporty Streetwear", "Mix sport and streetwear", "url10", lea, "streetwear_sport")

    # BOARDS
    street_board = create_board("Streetwear Ideas", alice)
    luxury_board = create_board("Luxury Inspiration", emma)
    sport_board = create_board("Sport Fitness", nina)

    add_pin_to_board(street_board, street1)
    add_pin_to_board(street_board, street2)
    add_pin_to_board(street_board, street3)
    add_pin_to_board(street_board, bridge_pin)

    add_pin_to_board(luxury_board, luxury1)
    add_pin_to_board(luxury_board, luxury2)
    add_pin_to_board(luxury_board, luxury3)

    add_pin_to_board(sport_board, sport1)
    add_pin_to_board(sport_board, sport2)
    add_pin_to_board(sport_board, sport3)
    add_pin_to_board(sport_board, bridge_pin)

    # COMMUNITY 1 : STREETWEAR
    like_pin(alice, street1)
    like_pin(bob, street1)
    like_pin(charlie, street1)
    save_pin(lea, street1)

    like_pin(alice, street2)
    save_pin(bob, street2)
    share(charlie, street2)
    like_pin(lea, street2)

    save_pin(alice, street3)
    like_pin(bob, street3)
    like_pin(charlie, street3)

    follow_user(alice, bob)
    follow_user(bob, charlie)
    follow_user(charlie, lea)
    follow_user(lea, alice)

    # COMMUNITY 2 : LUXURY
    like_pin(emma, luxury1)
    like_pin(david, luxury1)
    save_pin(sophia, luxury1)
    like_pin(lucas, luxury1)

    save_pin(emma, luxury2)
    like_pin(david, luxury2)
    share(sophia, luxury2)
    like_pin(lucas, luxury2)

    like_pin(emma, luxury3)
    save_pin(david, luxury3)
    like_pin(sophia, luxury3)

    follow_user(emma, david)
    follow_user(david, sophia)
    follow_user(sophia, lucas)
    follow_user(lucas, emma)

    # COMMUNITY 3 : SPORT
    like_pin(nina, sport1)
    like_pin(hugo, sport1)
    save_pin(jade, sport1)
    like_pin(noah, sport1)

    save_pin(nina, sport2)
    like_pin(hugo, sport2)
    share(jade, sport2)
    like_pin(noah, sport2)

    like_pin(nina, sport3)
    save_pin(hugo, sport3)
    like_pin(jade, sport3)

    follow_user(nina, hugo)
    follow_user(hugo, jade)
    follow_user(jade, noah)
    follow_user(noah, nina)

    # LIENS CROISÉS FAIBLES
    like_pin(bob, luxury1)
    save_pin(lea, luxury2)

    like_pin(lucas, street2)
    share(david, street3)

    like_pin(noah, street1)
    save_pin(charlie, sport2)

    # BRIDGE PIN
    like_pin(alice, bridge_pin)
    like_pin(lea, bridge_pin)
    like_pin(nina, bridge_pin)
    like_pin(hugo, bridge_pin)

    # FOLLOW PONTS ENTRE GROUPES
    follow_user(bob, emma)
    follow_user(lea, nina)
    follow_user(lucas, noah)

    print("Nouvelles données ajoutées dans PostgreSQL et Neo4j.")