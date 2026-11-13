import os
import json
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, 
    flash, session, jsonify, g
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from database.db import (
    init_db, close_db, query_db, execute_db, DB_STATUS
)
from gemini_service import generate_recipe_with_gemini

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Register teardown function to close database connections
app.teardown_appcontext(close_db)

# Initialize database tables and seeds on application startup
with app.app_context():
    init_db()

# ========================================================
# Helper Functions & Decorators
# ========================================================

def login_required(f):
    """Decorator to protect routes requiring authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def parse_recipe_json_fields(recipe):
    """Helper to deserialize ingredients, instructions, and nutrition JSON strings."""
    if not recipe:
        return None
    r = dict(recipe)
    
    # Parse ingredients
    if isinstance(r.get('ingredients'), str):
        try:
            r['ingredients_list'] = json.loads(r['ingredients'])
        except Exception:
            r['ingredients_list'] = [line.strip() for line in r['ingredients'].split('\n') if line.strip()]
    elif isinstance(r.get('ingredients'), list):
        r['ingredients_list'] = r['ingredients']
    else:
        r['ingredients_list'] = []

    # Parse instructions
    if isinstance(r.get('instructions'), str):
        try:
            r['instructions_list'] = json.loads(r['instructions'])
        except Exception:
            r['instructions_list'] = [line.strip() for line in r['instructions'].split('\n') if line.strip()]
    elif isinstance(r.get('instructions'), list):
        r['instructions_list'] = r['instructions']
    else:
        r['instructions_list'] = []

    # Parse nutrition
    if isinstance(r.get('nutrition'), str):
        try:
            r['nutrition_dict'] = json.loads(r['nutrition'])
        except Exception:
            r['nutrition_dict'] = {"calories": "N/A", "protein": "N/A", "carbs": "N/A", "fats": "N/A", "fiber": "N/A"}
    elif isinstance(r.get('nutrition'), dict):
        r['nutrition_dict'] = r['nutrition']
    else:
        r['nutrition_dict'] = {"calories": "N/A", "protein": "N/A", "carbs": "N/A", "fats": "N/A", "fiber": "N/A"}

    return r

@app.context_processor
def inject_global_vars():
    """Make common variables available across all Jinja templates."""
    user_fav_ids = set()
    if 'user_id' in session:
        favs = query_db("SELECT recipe_id FROM favourites WHERE user_id = %s", (session['user_id'],))
        user_fav_ids = {f['recipe_id'] for f in favs}
    
    return {
        'logged_in': 'user_id' in session,
        'current_user': {
            'id': session.get('user_id'),
            'name': session.get('user_name'),
            'email': session.get('user_email')
        },
        'user_fav_ids': user_fav_ids,
        'db_status': DB_STATUS,
        'gemini_configured': bool(Config.GEMINI_API_KEY and not Config.GEMINI_API_KEY.startswith("YOUR_GEMINI"))
    }

# ========================================================
# Authentication Routes
# ========================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User Registration Route."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template('register.html', name=name, email=email)
        
        if len(name) < 2:
            flash("Name must be at least 2 characters long.", "danger")
            return render_template('register.html', name=name, email=email)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('register.html', name=name, email=email)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html', name=name, email=email)

        # Check existing email
        existing_user = query_db("SELECT id FROM users WHERE email = %s", (email,), one=True)
        if existing_user:
            flash("Email address is already registered. Please log in.", "warning")
            return redirect(url_for('login'))

        # Secure password hash
        password_hash = generate_password_hash(password)
        try:
            user_id = execute_db(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, password_hash)
            )
            # Auto login on registration
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email
            flash(f"Welcome, {name}! Your account has been created successfully.", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f"Registration failed: {str(e)}", "danger")

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User Login Route."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    next_url = request.args.get('next')

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template('login.html', email=email)

        user = query_db("SELECT * FROM users WHERE email = %s", (email,), one=True)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash(f"Welcome back, {user['name']}!", "success")
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    """User Logout Route."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('login'))

# ========================================================
# Main Pages & Navigation Routes
# ========================================================

@app.route('/')
def index():
    """Public Landing Page / Home Page."""
    # Fetch Popular Recipes (highest views)
    popular_recipes = query_db("SELECT * FROM recipes ORDER BY views DESC LIMIT 6")
    parsed_popular = [parse_recipe_json_fields(r) for r in popular_recipes]

    # Fetch Recommended Recipes
    recommended_recipes = query_db("SELECT * FROM recipes ORDER BY id DESC LIMIT 4")
    parsed_recommended = [parse_recipe_json_fields(r) for r in recommended_recipes]

    # Fetch Recent Searches (across system or user)
    if 'user_id' in session:
        recent_searches = query_db(
            "SELECT DISTINCT query FROM search_history WHERE user_id = %s ORDER BY id DESC LIMIT 5",
            (session['user_id'],)
        )
    else:
        recent_searches = query_db(
            "SELECT DISTINCT query FROM search_history ORDER BY id DESC LIMIT 5"
        )
    recent_query_list = [s['query'] for s in recent_searches] if recent_searches else ["Biryani", "Dosa", "Paneer", "Pulao"]

    # Categories list with icons and counts
    categories_data = [
        {"name": "Breakfast", "icon": "fa-sun", "desc": "Energizing morning meals & crepes", "image": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?auto=format&fit=crop&w=400&q=80"},
        {"name": "Lunch", "icon": "fa-utensils", "desc": "Nutritious bowls, curries & rice", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=400&q=80"},
        {"name": "Dinner", "icon": "fa-moon", "desc": "Royal biryanis & creamy platters", "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=400&q=80"},
        {"name": "Snacks", "icon": "fa-cookie-bite", "desc": "Crispy rolls, chaat & appetizers", "image": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
        {"name": "Desserts", "icon": "fa-ice-cream", "desc": "Decadent cakes, puddings & sweets", "image": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=400&q=80"},
        {"name": "Beverages", "icon": "fa-glass-water", "desc": "Refreshing smoothies, lassi & teas", "image": "https://images.unsplash.com/photo-1546173159-315724a31696?auto=format&fit=crop&w=400&q=80"}
    ]

    return render_template(
        'index.html',
        popular_recipes=parsed_popular,
        recommended_recipes=parsed_recommended,
        recent_searches=recent_query_list,
        categories=categories_data
    )

@app.route('/dashboard')
@login_required
def dashboard():
    """User Dashboard with personalized analytics and quick actions."""
    user_id = session['user_id']
    
    # Counts
    fav_count_res = query_db("SELECT count(*) as count FROM favourites WHERE user_id = %s", (user_id,), one=True)
    fav_count = fav_count_res['count'] if fav_count_res else 0

    search_count_res = query_db("SELECT count(*) as count FROM search_history WHERE user_id = %s", (user_id,), one=True)
    search_count = search_count_res['count'] if search_count_res else 0

    total_recipes_res = query_db("SELECT count(*) as count FROM recipes", one=True)
    total_recipes = total_recipes_res['count'] if total_recipes_res else 0

    # User's recent search queries
    user_searches = query_db(
        "SELECT * FROM search_history WHERE user_id = %s ORDER BY searched_at DESC LIMIT 6",
        (user_id,)
    )

    # User's favorite recipes preview
    favorite_recipes = query_db("""
        SELECT r.* FROM recipes r
        INNER JOIN favourites f ON r.id = f.recipe_id
        WHERE f.user_id = %s
        ORDER BY f.created_at DESC LIMIT 4
    """, (user_id,))
    parsed_favs = [parse_recipe_json_fields(r) for r in favorite_recipes]

    # Recommended for user
    recommended = query_db("SELECT * FROM recipes ORDER BY views DESC LIMIT 4")
    parsed_rec = [parse_recipe_json_fields(r) for r in recommended]

    return render_template(
        'dashboard.html',
        fav_count=fav_count,
        search_count=search_count,
        total_recipes=total_recipes,
        user_searches=user_searches,
        favorite_recipes=parsed_favs,
        recommended_recipes=parsed_rec
    )

# ========================================================
# AI Recipe Search & Generation
# ========================================================

@app.route('/search', methods=['GET', 'POST'])
def search_recipe():
    """
    Search route:
    1. Reads query and filters (category, diet_type, max_time).
    2. Logs search to search_history.
    3. Checks if existing matching recipe is in database.
    4. If not found or if user clicks 'AI Generate', invokes Gemini AI API.
    5. Saves generated recipe to MySQL recipes table and redirects to recipe view.
    """
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        category_filter = request.form.get('category', '').strip() or None
        diet_filter = request.form.get('diet_type', '').strip() or None
        time_filter = request.form.get('time_filter', '').strip() or None
        force_ai = request.form.get('force_ai') == '1'
    else:
        query = request.args.get('q', '').strip()
        category_filter = request.args.get('category', '').strip() or None
        diet_filter = request.args.get('diet_type', '').strip() or None
        time_filter = request.args.get('time_filter', '').strip() or None
        force_ai = request.args.get('force_ai') == '1'

    if not query:
        flash("Please enter a dish name or ingredient to search.", "warning")
        return redirect(url_for('index'))

    # Record search history
    user_id = session.get('user_id')
    try:
        execute_db(
            "INSERT INTO search_history (user_id, query, category_filter, diet_filter, time_filter) VALUES (%s, %s, %s, %s, %s)",
            (user_id, query, category_filter, diet_filter, time_filter)
        )
    except Exception:
        pass

    # Step 1: Check existing recipes in DB if not forced AI
    if not force_ai:
        existing = query_db(
            "SELECT * FROM recipes WHERE LOWER(title) LIKE %s LIMIT 1",
            (f"%{query.lower()}%",),
            one=True
        )
        if existing:
            # Increment view counter
            try:
                execute_db("UPDATE recipes SET views = views + 1 WHERE id = %s", (existing['id'],))
            except Exception:
                pass
            flash(f"Loaded '{existing['title']}' from recipe library.", "info")
            return redirect(url_for('view_recipe', recipe_id=existing['id']))

    # Step 2: Generate via Google Gemini AI
    recipe_data, is_live_gemini, status_msg = generate_recipe_with_gemini(
        query, category_filter, diet_filter, time_filter
    )

    # Step 3: Save newly generated recipe into MySQL database
    try:
        new_recipe_id = execute_db("""
            INSERT INTO recipes (
                title, description, category, diet_type, 
                prep_time, cook_time, total_time, servings, 
                difficulty, ingredients, instructions, nutrition, 
                image_url, chef_tips, source, views
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
        """, (
            recipe_data['title'],
            recipe_data['description'],
            recipe_data['category'],
            recipe_data['diet_type'],
            recipe_data['prep_time'],
            recipe_data['cook_time'],
            recipe_data['total_time'],
            recipe_data['servings'],
            recipe_data['difficulty'],
            recipe_data['ingredients'],
            recipe_data['instructions'],
            recipe_data['nutrition'],
            recipe_data['image_url'],
            recipe_data['chef_tips'],
            recipe_data['source']
        ))

        flash(status_msg, "success" if is_live_gemini else "info")
        return redirect(url_for('view_recipe', recipe_id=new_recipe_id))
    except Exception as e:
        flash(f"Error saving recipe to database: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    """Recipe Details Page with interactive checkboxes, cooking timer, nutrition facts, and print."""
    recipe = query_db("SELECT * FROM recipes WHERE id = %s", (recipe_id,), one=True)
    if not recipe:
        flash("Recipe not found.", "warning")
        return redirect(url_for('index'))

    # Increment view count
    try:
        execute_db("UPDATE recipes SET views = views + 1 WHERE id = %s", (recipe_id,))
    except Exception:
        pass

    parsed_recipe = parse_recipe_json_fields(recipe)

    # Check if favourite for user
    is_favourite = False
    if 'user_id' in session:
        fav = query_db(
            "SELECT id FROM favourites WHERE user_id = %s AND recipe_id = %s",
            (session['user_id'], recipe_id),
            one=True
        )
        is_favourite = bool(fav)

    # Fetch similar recipes in same category
    similar_recipes = query_db(
        "SELECT * FROM recipes WHERE category = %s AND id != %s ORDER BY views DESC LIMIT 3",
        (recipe['category'], recipe_id)
    )
    parsed_similar = [parse_recipe_json_fields(r) for r in similar_recipes]

    return render_template(
        'recipe.html',
        recipe=parsed_recipe,
        is_favourite=is_favourite,
        similar_recipes=parsed_similar
    )

# ========================================================
# Favourites Management
# ========================================================

@app.route('/favourites')
@login_required
def favourites():
    """User's saved favourite recipes page."""
    user_id = session['user_id']
    favorite_recipes = query_db("""
        SELECT r.*, f.created_at as saved_at 
        FROM recipes r
        INNER JOIN favourites f ON r.id = f.recipe_id
        WHERE f.user_id = %s
        ORDER BY f.created_at DESC
    """, (user_id,))
    
    parsed_favs = [parse_recipe_json_fields(r) for r in favorite_recipes]
    return render_template('favourites.html', recipes=parsed_favs)

@app.route('/favourite/toggle/<int:recipe_id>', methods=['POST'])
@login_required
def toggle_favourite(recipe_id):
    """Toggle favourite status via AJAX or standard form submission."""
    user_id = session['user_id']
    
    existing = query_db(
        "SELECT id FROM favourites WHERE user_id = %s AND recipe_id = %s",
        (user_id, recipe_id),
        one=True
    )
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json

    if existing:
        execute_db("DELETE FROM favourites WHERE id = %s", (existing['id'],))
        is_fav = False
        message = "Removed from favourites."
    else:
        execute_db("INSERT INTO favourites (user_id, recipe_id) VALUES (%s, %s)", (user_id, recipe_id))
        is_fav = True
        message = "Added to favourites!"

    if is_ajax:
        return jsonify({
            "success": True,
            "is_favourite": is_fav,
            "message": message
        })

    flash(message, "success")
    return redirect(request.referrer or url_for('view_recipe', recipe_id=recipe_id))

# ========================================================
# Search History Management
# ========================================================

@app.route('/history')
@login_required
def history():
    """Search History Page."""
    user_id = session['user_id']
    history_items = query_db(
        "SELECT * FROM search_history WHERE user_id = %s ORDER BY searched_at DESC",
        (user_id,)
    )
    return render_template('history.html', history_items=history_items)

@app.route('/history/delete/<int:history_id>', methods=['POST'])
@login_required
def delete_history_item(history_id):
    """Delete a single search history item."""
    user_id = session['user_id']
    execute_db("DELETE FROM search_history WHERE id = %s AND user_id = %s", (history_id, user_id))
    flash("History item removed.", "info")
    return redirect(url_for('history'))

@app.route('/history/clear', methods=['POST'])
@login_required
def clear_all_history():
    """Clear all search history for current user."""
    user_id = session['user_id']
    execute_db("DELETE FROM search_history WHERE user_id = %s", (user_id,))
    flash("Search history cleared successfully.", "success")
    return redirect(url_for('history'))

# ========================================================
# Categories & Filter Pages
# ========================================================

@app.route('/categories')
def categories_list():
    """Browse all food categories."""
    categories = [
        {"name": "Breakfast", "icon": "fa-sun", "color": "#f59e0b", "desc": "Morning dishes, crepes, oats & toasts", "image": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?auto=format&fit=crop&w=600&q=80"},
        {"name": "Lunch", "icon": "fa-bowl-rice", "color": "#10b981", "desc": "Wholesome bowls, pulao, curries & salads", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80"},
        {"name": "Dinner", "icon": "fa-moon", "color": "#6366f1", "desc": "Gourmet platters, pasta, biryani & gravies", "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=600&q=80"},
        {"name": "Snacks", "icon": "fa-cookie-bite", "color": "#ec4899", "desc": "Crispy spring rolls, pakoras & finger foods", "image": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=600&q=80"},
        {"name": "Desserts", "icon": "fa-ice-cream", "color": "#f43f5e", "desc": "Decadent cakes, puddings & chocolate treats", "image": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=600&q=80"},
        {"name": "Beverages", "icon": "fa-glass-water", "color": "#06b6d4", "desc": "Creamy lassis, smoothies, mocktails & teas", "image": "https://images.unsplash.com/photo-1546173159-315724a31696?auto=format&fit=crop&w=600&q=80"}
    ]
    return render_template('categories.html', categories=categories)

@app.route('/category/<string:cat_name>')
def view_category(cat_name):
    """View recipes filtered by a specific category with diet and time filters."""
    diet_filter = request.args.get('diet', '')
    max_time = request.args.get('max_time', type=int)

    query = "SELECT * FROM recipes WHERE LOWER(category) = LOWER(%s)"
    params = [cat_name]

    if diet_filter in ('Veg', 'Non-Veg', 'Vegan'):
        query += " AND diet_type = %s"
        params.append(diet_filter)

    if max_time and max_time > 0:
        query += " AND total_time <= %s"
        params.append(max_time)

    query += " ORDER BY id DESC"
    recipes = query_db(query, tuple(params))
    parsed_recipes = [parse_recipe_json_fields(r) for r in recipes]

    return render_template(
        'search_results.html',
        recipes=parsed_recipes,
        category_name=cat_name,
        selected_diet=diet_filter,
        selected_time=max_time
    )

# ========================================================
# Error Handlers
# ========================================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('404.html', error="500 - Internal Server Error"), 500

# ========================================================
# Application Entry Point
# ========================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print("  AI FOOD RECIPE PREPARATION & RECOMMENDATION SYSTEM")
    print("  BCA FINAL YEAR PROJECT")
    print(f"  Database Status: {DB_STATUS['message']}")
    print(f"  Gemini API Status: {'Active' if Config.GEMINI_API_KEY else 'Demo / Smart Fallback Mode'}")
    print(f"  Running on: http://127.0.0.1:{port}")
    print("=" * 60)
    app.run(host='127.0.0.1', port=port, debug=Config.DEBUG)
