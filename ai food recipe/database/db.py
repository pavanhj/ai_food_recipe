import os
import sqlite3
import json
import pymysql
import pymysql.cursors
from flask import g, has_app_context
from werkzeug.security import generate_password_hash
from config import Config

# Path to SQLite fallback database file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_DB_PATH = os.path.join(BASE_DIR, 'database', 'recipe_db.sqlite')
SCHEMA_SQL_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')
SEED_SQL_PATH = os.path.join(BASE_DIR, 'database', 'seed.sql')

# Global database status tracker
DB_STATUS = {
    "engine": "unknown",
    "connected": False,
    "message": ""
}

def can_connect_mysql():
    """Test if MySQL server is reachable with configured credentials."""
    try:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT,
            connect_timeout=2
        )
        conn.close()
        return True
    except Exception as e:
        return False

def init_mysql_database():
    """Initialize MySQL database, tables, and seed data if not already existing."""
    try:
        # Step 1: Connect to server without database to ensure database exists
        server_conn = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT,
            autocommit=True
        )
        with server_conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        server_conn.close()

        # Step 2: Connect to the specific database
        db_conn = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT,
            autocommit=True
        )
        with db_conn.cursor() as cur:
            # Check if tables exist
            cur.execute("SHOW TABLES LIKE 'recipes';")
            table_exists = cur.fetchone()
            if not table_exists:
                # Read and execute schema.sql
                if os.path.exists(SCHEMA_SQL_PATH):
                    with open(SCHEMA_SQL_PATH, 'r', encoding='utf-8') as f:
                        sql_script = f.read()
                    # Execute statements individually
                    statements = [s.strip() for s in sql_script.split(';') if s.strip()]
                    for stmt in statements:
                        if stmt.upper().startswith("USE "):
                            continue
                        cur.execute(stmt)

                # Read and execute seed.sql
                if os.path.exists(SEED_SQL_PATH):
                    with open(SEED_SQL_PATH, 'r', encoding='utf-8') as f:
                        seed_script = f.read()
                    statements = [s.strip() for s in seed_script.split(';') if s.strip()]
                    for stmt in statements:
                        if stmt.upper().startswith("USE "):
                            continue
                        try:
                            cur.execute(stmt)
                        except Exception:
                            pass
        db_conn.close()
        DB_STATUS["engine"] = "MySQL"
        DB_STATUS["connected"] = True
        DB_STATUS["message"] = f"Connected to MySQL on {Config.DB_HOST}:{Config.DB_PORT} (DB: {Config.DB_NAME})"
        print(f"[DB SUCCESS] {DB_STATUS['message']}")
        return True
    except Exception as e:
        DB_STATUS["engine"] = "SQLite (Fallback)"
        DB_STATUS["connected"] = False
        DB_STATUS["message"] = f"MySQL connection failed ({e}). Fallback to SQLite active."
        print(f"[DB NOTICE] {DB_STATUS['message']}")
        return False

def init_sqlite_database():
    """Initialize local SQLite database for instant out-of-the-box readiness."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cur = conn.cursor()
    
    # 1. Users Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Recipes Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT NOT NULL DEFAULT 'Main Course',
        diet_type TEXT NOT NULL DEFAULT 'Veg',
        prep_time INTEGER NOT NULL DEFAULT 15,
        cook_time INTEGER NOT NULL DEFAULT 20,
        total_time INTEGER NOT NULL DEFAULT 35,
        servings INTEGER NOT NULL DEFAULT 4,
        difficulty TEXT NOT NULL DEFAULT 'Medium',
        ingredients TEXT NOT NULL,
        instructions TEXT NOT NULL,
        nutrition TEXT,
        image_url TEXT,
        chef_tips TEXT,
        source TEXT DEFAULT 'gemini_ai',
        views INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Favourites Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS favourites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        recipe_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, recipe_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
    );
    """)

    # 4. Search History Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        query TEXT NOT NULL,
        category_filter TEXT,
        diet_filter TEXT,
        time_filter TEXT,
        searched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # Check if demo user exists
    cur.execute("SELECT id FROM users WHERE email = 'demo@recipeai.com'")
    demo_user = cur.fetchone()
    demo_pwd_hash = generate_password_hash('password123')
    if not demo_user:
        cur.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", 
                    ('BCA Demo Student', 'demo@recipeai.com', demo_pwd_hash))
    else:
        # Keep hash fresh and compatible with current runtime
        cur.execute("UPDATE users SET password_hash = ? WHERE email = 'demo@recipeai.com'", (demo_pwd_hash,))

    # Check if sample recipes exist
    cur.execute("SELECT count(*) FROM recipes")
    count = cur.fetchone()[0]
    if count == 0:
        # Seed default recipes
        seed_recipes = [
            (
                'Royal Hyderabadi Chicken Biryani',
                'A world-renowned aromatic rice and chicken dish infused with exotic saffron, fried onions, and whole spices cooked in the traditional dum style.',
                'Dinner', 'Non-Veg', 30, 45, 75, 4, 'Medium',
                json.dumps([
                    "500g Chicken cut into pieces", "2 cups aged Basmati Rice", "1 cup thick Yogurt (Dahi)",
                    "2 large Onions, fried golden (Birista)", "2 tbsp Ginger-Garlic paste", "1 tsp Red Chili powder",
                    "1/2 tsp Turmeric powder", "1 tsp Garam Masala", "A pinch of Saffron soaked in 4 tbsp warm milk",
                    "1/4 cup fresh Mint leaves", "1/4 cup fresh Coriander leaves", "3 tbsp Pure Ghee",
                    "Whole spices (Bay leaf, cardamom, cloves, cinnamon)", "Salt to taste"
                ]),
                json.dumps([
                    "Marinate chicken with yogurt, ginger-garlic paste, red chili powder, turmeric, garam masala, salt, and mint-coriander for 30 minutes.",
                    "Parboil soaked basmati rice in whole-spiced salted water until 70% done, then drain.",
                    "In a heavy pot, sear marinated chicken in ghee for 5 minutes.",
                    "Layer parboiled rice on top. Sprinkle fried golden onions, chopped herbs, saffron milk, and ghee.",
                    "Cover with tight foil and heavy lid. Cook on low heat (dum) for 25 minutes.",
                    "Fluff gently and serve steaming hot with cooling cucumber raita and mirchi ka salan."
                ]),
                json.dumps({"calories": 580, "protein": "34g", "carbs": "65g", "fats": "19g", "fiber": "3.5g"}),
                'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80',
                'Never stir aggressively; gently lift from the rim with a flat spatula to keep long rice grains intact.',
                'system', 42
            ),
            (
                'South Indian Masala Dosa',
                'Crispy golden fermented rice and lentil crepe stuffed with fragrant spiced potato masala, served alongside fresh coconut chutney and piping hot sambar.',
                'Breakfast', 'Veg', 20, 15, 35, 4, 'Medium',
                json.dumps([
                    "3 cups Parboiled Rice", "1 cup Urad Dal", "1/2 tsp Fenugreek seeds",
                    "4 large Potatoes, boiled & mashed", "1 large Onion, sliced", "2 Green chilies, slit",
                    "1 tsp Mustard seeds", "1 tsp Cumin seeds", "1 sprig Curry leaves",
                    "1/2 tsp Turmeric powder", "2 tbsp Oil or Butter", "Salt to taste"
                ]),
                json.dumps([
                    "Soak rice, fenugreek seeds, and urad dal for 6 hours. Grind into silky smooth batter and ferment for 8-10 hours.",
                    "Prepare potato filling: crackle mustard, cumin, curry leaves, and green chilies in oil. Sauté onions, add turmeric, mashed potatoes, and salt.",
                    "Heat cast-iron dosa tawa on medium heat. Pour a ladle of batter in center and swirl outwards into a thin circle.",
                    "Drizzle oil or butter around edges until crispy and golden brown.",
                    "Place potato filling in center, fold crepe, and serve immediately with fresh coconut chutney and sambar."
                ]),
                json.dumps({"calories": 320, "protein": "7g", "carbs": "54g", "fats": "9g", "fiber": "4g"}),
                'https://images.unsplash.com/photo-1668236543090-82eba5ee5976?auto=format&fit=crop&w=800&q=80',
                'Sprinkle droplets of water on the tawa and wipe down before spreading batter to ensure even heat distribution.',
                'system', 55
            ),
            (
                'Restaurant Style Paneer Butter Masala',
                'Tender soft paneer cubes simmered in a velvety, buttery tomato-cashew gravy scented with dried fenugreek leaves (kasuri methi).',
                'Dinner', 'Veg', 15, 25, 40, 4, 'Easy',
                json.dumps([
                    "250g Paneer cubes", "4 large ripe Tomatoes, pureed", "2 medium Onions, chopped",
                    "15 Cashew nuts, soaked", "2 tbsp Butter", "1 tbsp Cooking Oil",
                    "1 tbsp Ginger-Garlic paste", "1 tsp Kashmiri Red Chili powder", "1/2 tsp Garam Masala",
                    "1 tsp Coriander powder", "1 tbsp crushed Kasuri Methi", "3 tbsp Fresh Cream", "Salt to taste"
                ]),
                json.dumps([
                    "Boil onions and soaked cashews for 10 minutes; cool and blend to a silky paste.",
                    "Heat oil and butter in a pan, cook ginger-garlic paste and onion-cashew paste until golden.",
                    "Add pureed tomatoes, chili powder, coriander powder, and salt. Cook covered until oil separates.",
                    "Add warm water to adjust gravy consistency, bring to a gentle simmer.",
                    "Gently add soft paneer cubes and simmer for 4 minutes.",
                    "Finish with crushed kasuri methi, garam masala, extra butter, and rich fresh cream. Serve with hot butter naan."
                ]),
                json.dumps({"calories": 410, "protein": "16g", "carbs": "18g", "fats": "32g", "fiber": "3g"}),
                'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=800&q=80',
                'Soak store-bought paneer in warm water for 15 minutes before cooking for a melt-in-mouth texture.',
                'system', 38
            ),
            (
                'Fragrant Vegetable Pulao',
                'A wholesome one-pot meal made with fragrant basmati rice, colorful mixed garden vegetables, and warm whole spices.',
                'Lunch', 'Veg', 15, 20, 35, 4, 'Easy',
                json.dumps([
                    "1.5 cups Basmati Rice", "1/2 cup diced Carrots", "1/2 cup Green Peas",
                    "1/2 cup French Beans", "1 medium Potato, cubed", "1 large Onion, sliced",
                    "1 tbsp Ginger-Garlic paste", "2 tbsp Ghee or Oil",
                    "Whole spices (Bay leaf, star anise, cardamoms, cinnamon)", "3 cups Water or Broth", "Fresh herbs"
                ]),
                json.dumps([
                    "Heat ghee in a pot, add whole spices and sauté until fragrant.",
                    "Add sliced onions and green chilies, frying until translucent.",
                    "Stir in ginger-garlic paste and chopped colorful vegetables, sautéing for 3 minutes.",
                    "Add soaked, drained basmati rice and gently stir to coat grains.",
                    "Pour 3 cups of water and salt; bring to a rolling boil.",
                    "Cover tightly and cook on low heat for 15 minutes until liquid is fully absorbed.",
                    "Fluff with a fork and serve with cucumber raita and papad."
                ]),
                json.dumps({"calories": 290, "protein": "6g", "carbs": "56g", "fats": "6g", "fiber": "4.5g"}),
                'https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=800&q=80',
                'Maintain a strict 1:2 ratio of basmati rice to water for distinct, fluffy grains.',
                'system', 29
            ),
            (
                'Creamy Italian Fettuccine Alfredo',
                'Silky ribbons of fettuccine pasta coated in an opulent homemade parmesan cream sauce and freshly cracked black pepper.',
                'Dinner', 'Veg', 10, 15, 25, 2, 'Easy',
                json.dumps([
                    "250g Fettuccine pasta", "3 tbsp Unsalted Butter", "3 cloves Garlic, minced",
                    "1 cup Heavy Cream", "1 cup freshly grated Parmigiano-Reggiano cheese",
                    "Freshly cracked black pepper", "A pinch of Nutmeg", "Fresh flat-leaf Parsley"
                ]),
                json.dumps([
                    "Boil fettuccine pasta in salted water until al dente; reserve 1/2 cup cooking water.",
                    "Melt butter in a skillet over medium heat, add minced garlic and sauté for 1 minute.",
                    "Pour in heavy cream and simmer for 3 minutes until slightly reduced.",
                    "Lower heat, whisk in freshly grated parmesan until silky and smooth.",
                    "Toss hot pasta in the sauce, adding pasta water if needed to loosen.",
                    "Garnish with freshly ground black pepper and chopped parsley. Serve immediately."
                ]),
                json.dumps({"calories": 520, "protein": "14g", "carbs": "48g", "fats": "31g", "fiber": "2g"}),
                'https://images.unsplash.com/photo-1645112411341-6c4fd023714a?auto=format&fit=crop&w=800&q=80',
                'Avoid pre-shredded cheese from bags as starch additives prevent the sauce from becoming velvety.',
                'system', 18
            ),
            (
                'Authentic Mango Lassi',
                'Thick, creamy and refreshingly sweet yogurt smoothie blended with ripe Alphonso mangoes and a touch of fragrant cardamom.',
                'Beverages', 'Veg', 10, 0, 10, 2, 'Easy',
                json.dumps([
                    "1.5 cups ripe Mango pulp (Alphonso or Kesar)", "1.5 cups chilled Greek yogurt",
                    "1/2 cup chilled Milk", "2 tbsp Sugar or Honey",
                    "1/4 tsp Cardamom powder", "Crushed Ice cubes", "Pistachio slivers & saffron for garnish"
                ]),
                json.dumps([
                    "Add mango pulp, thick chilled yogurt, milk, sugar, and cardamom powder into a blender.",
                    "Blend on high speed for 1 minute until completely velvety and frothy.",
                    "Pulse with crushed ice cubes for extra chill.",
                    "Pour into tall glasses and garnish with slivered pistachios and saffron strands."
                ]),
                json.dumps({"calories": 210, "protein": "7g", "carbs": "38g", "fats": "4g", "fiber": "2g"}),
                'https://images.unsplash.com/photo-1546173159-315724a31696?auto=format&fit=crop&w=800&q=80',
                'Use Greek yogurt or hung curd for thick café-style consistency.',
                'system', 60
            ),
            (
                'Decadent Warm Chocolate Lava Cake',
                'Individual chocolate sponge cake with a warm molten chocolate center that flows effortlessly upon first spoonful.',
                'Desserts', 'Veg', 15, 12, 27, 2, 'Medium',
                json.dumps([
                    "100g Dark chocolate (70% cocoa)", "50g Unsalted Butter", "2 large Eggs",
                    "3 tbsp Caster Sugar", "2 tbsp All-purpose Flour", "1 tsp Vanilla extract",
                    "Cocoa powder for ramekins", "Powdered sugar and fresh berries for serving"
                ]),
                json.dumps([
                    "Preheat oven to 200°C (400°F). Butter two ramekins and coat with cocoa powder.",
                    "Melt chocolate and butter over a double boiler until smooth; let cool slightly.",
                    "Whisk eggs, sugar, and vanilla until pale and doubled in volume (3 mins).",
                    "Fold melted chocolate into eggs, then gently fold in sifted flour.",
                    "Divide into ramekins and bake 11-12 minutes until edges are set but center remains soft.",
                    "Invert onto plates, dust with powdered sugar, and serve warm with vanilla ice cream."
                ]),
                json.dumps({"calories": 440, "protein": "7g", "carbs": "42g", "fats": "28g", "fiber": "3.8g"}),
                'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=800&q=80',
                'Do not overbake! At 11 minutes the core remains a delicious liquid river.',
                'system', 49
            ),
            (
                'Crispy Vegetable Spring Rolls',
                'Crunchy golden wrappers loaded with savory shredded cabbage, carrots, bell peppers, and scallions tossed with soy sauce and sesame oil.',
                'Snacks', 'Veg', 20, 15, 35, 4, 'Medium',
                json.dumps([
                    "10 Spring roll sheets", "2 cups shredded Cabbage", "1 cup julienned Carrots",
                    "1/2 cup sliced Bell Peppers", "3 Spring onions", "3 cloves Garlic, minced",
                    "1 tbsp Soy Sauce", "1 tbsp Sweet chili sauce", "1 tsp Sesame oil",
                    "1/2 tsp White pepper", "Flour paste for sealing", "Oil for frying"
                ]),
                json.dumps([
                    "Stir-fry minced garlic, spring onions, cabbage, carrots, and peppers on high heat for 3 minutes.",
                    "Toss with soy sauce, sweet chili sauce, white pepper, and sesame oil. Cool completely.",
                    "Place wrapper diamond-style, spoon 2 tbsp filling near bottom, fold over, fold sides in, and roll tightly.",
                    "Seal edge with flour-water paste.",
                    "Deep fry in hot oil (180°C) for 4-5 minutes until golden and delightfully crispy. Serve with chili dip."
                ]),
                json.dumps({"calories": 260, "protein": "5g", "carbs": "34g", "fats": "12g", "fiber": "3g"}),
                'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80',
                'Ensure vegetable stuffing is cool and dry before wrapping to prevent tearing.',
                'system', 31
            )
        ]
        cur.executemany("""
        INSERT INTO recipes (title, description, category, diet_type, prep_time, cook_time, total_time, servings, difficulty, ingredients, instructions, nutrition, image_url, chef_tips, source, views)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_recipes)

    conn.commit()
    conn.close()
    if DB_STATUS["engine"] == "unknown":
        DB_STATUS["engine"] = "SQLite"
        DB_STATUS["connected"] = True
        DB_STATUS["message"] = f"Using SQLite database ({SQLITE_DB_PATH})"
        print(f"[DB SUCCESS] {DB_STATUS['message']}")

def init_db():
    """Initializes the database connection (MySQL primary, SQLite fallback)."""
    if can_connect_mysql():
        if init_mysql_database():
            return
    # Fallback to SQLite
    init_sqlite_database()

def get_db():
    """Returns database connection stored in Flask application context (or standalone if outside context)."""
    if has_app_context():
        if 'db_conn' not in g:
            if DB_STATUS["engine"] == "MySQL":
                try:
                    g.db_conn = pymysql.connect(
                        host=Config.DB_HOST,
                        user=Config.DB_USER,
                        password=Config.DB_PASSWORD,
                        database=Config.DB_NAME,
                        port=Config.DB_PORT,
                        cursorclass=pymysql.cursors.DictCursor,
                        autocommit=True
                    )
                    g.db_type = 'mysql'
                except Exception:
                    g.db_conn = sqlite3.connect(SQLITE_DB_PATH)
                    g.db_conn.row_factory = sqlite3.Row
                    g.db_type = 'sqlite'
            else:
                g.db_conn = sqlite3.connect(SQLITE_DB_PATH)
                g.db_conn.row_factory = sqlite3.Row
                g.db_type = 'sqlite'
        return g.db_conn
    else:
        # Standalone connection when called from tests or scripts outside request context
        if DB_STATUS["engine"] == "MySQL":
            try:
                conn = pymysql.connect(
                    host=Config.DB_HOST,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    database=Config.DB_NAME,
                    port=Config.DB_PORT,
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=True
                )
                return conn
            except Exception:
                pass
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def close_db(e=None):
    """Closes database connection at the end of the request."""
    if has_app_context():
        db_conn = g.pop('db_conn', None)
        if db_conn is not None:
            db_conn.close()

def query_db(query, args=(), one=False):
    """
    Executes a SELECT query safely with parameterization.
    Automatically translates parameter placeholders between MySQL (%s) and SQLite (?).
    Returns a list of dicts (or a single dict if one=True).
    """
    conn = get_db()
    is_sqlite = isinstance(conn, sqlite3.Connection)
    
    if is_sqlite:
        sqlite_query = query.replace('%s', '?')
        cur = conn.cursor()
        cur.execute(sqlite_query, args)
        rows = cur.fetchall()
        cur.close()
        result = [dict(row) for row in rows]
        if not has_app_context():
            conn.close()
    else:
        mysql_query = query
        with conn.cursor() as cur:
            cur.execute(mysql_query, args)
            rows = cur.fetchall()
            result = list(rows) if rows else []
        if not has_app_context():
            conn.close()

    if one:
        return result[0] if result else None
    return result

def execute_db(query, args=(), commit=True):
    """
    Executes an INSERT, UPDATE, or DELETE query safely.
    Returns the lastrowid or affected rows.
    """
    conn = get_db()
    is_sqlite = isinstance(conn, sqlite3.Connection)
    
    if is_sqlite:
        sqlite_query = query.replace('%s', '?')
        cur = conn.cursor()
        cur.execute(sqlite_query, args)
        last_id = cur.lastrowid
        if commit:
            conn.commit()
        cur.close()
        if not has_app_context():
            conn.close()
        return last_id
    else:
        mysql_query = query
        with conn.cursor() as cur:
            cur.execute(mysql_query, args)
            last_id = cur.lastrowid
            if commit:
                conn.commit()
            if not has_app_context():
                conn.close()
            return last_id
