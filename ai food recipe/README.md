# AI Food Recipe Preparation & Recommendation System
### A BCA Final Year Academic Capstone Project

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1-black.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)
![AI](https://img.shields.io/badge/Google-Gemini%20AI-red.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)

---

## 📌 1. Project Overview & Objective

The **AI Food Recipe Preparation and Recommendation System** is a full-stack web application developed for the BCA final-year project. It enables users to search for any food recipe or dish and dynamically receive comprehensive culinary information generated via **Google Gemini AI**.

The system provides:
- **Exact Ingredient Proportions** (with quantities and interactive kitchen prep checklist).
- **Step-by-Step Cooking Instructions** (numbered and structured for effortless cooking).
- **Preparation, Cooking, and Total Times**.
- **Servings Count & Difficulty Ratings** (Easy, Medium, Hard).
- **Macro Nutritional Information** (Calories, Protein, Carbohydrates, Fats, Fiber).
- **Interactive Kitchen Cooking Timer** (with Web Audio countdown alerts).
- **Chef's Culinary Secrets & Tips**.
- **Clean Recipe Print Formatting** (optimized for physical printing).
- **Personalized Favourites & Search History Management**.
- **Secure Authentication & User Session Management**.

---

## 🏗️ 2. Technology Stack

- **Backend Framework**: Python Flask
- **Template Engine**: Jinja2
- **Frontend / UI**: HTML5, CSS3, Bootstrap 5.3, Font Awesome 6
- **Database**: MySQL (with automatic SQLite fallback for offline demonstrations)
- **AI Integration**: Google Gemini API (`gemini-1.5-flash`)
- **Environment Management**: `python-dotenv` (`.env`)
- **IDE**: Visual Studio Code (VS Code) on Windows 11

---

## 📁 3. Project Directory Structure

```text
ai-food-recipe/
├── app.py                      # Core Flask application, route controllers, session handling
├── config.py                   # Environment configuration loader
├── gemini_service.py           # Gemini AI API integration, prompt engineering & fallback engine
├── requirements.txt            # Python dependencies
├── test_app.py                 # Automated unit test suite (7/7 tests passed)
├── .env                        # Active environment variables (API keys, DB config)
├── .env.example                # Sample environment file template
├── README.md                   # Complete project documentation & viva guide
├── database/
│   ├── db.py                   # Universal database connector (MySQL + SQLite fallback)
│   ├── schema.sql              # MySQL DDL table schema script
│   ├── seed.sql                # Initial verified recipes & demo user account
│   └── recipe_db.sqlite        # Auto-generated SQLite fallback database
├── templates/
│   ├── base.html               # Master layout with navbar, footer, search modal & toasts
│   ├── index.html              # Home page (Hero AI search, categories, popular dishes)
│   ├── login.html              # Login page with 1-click viva demo credentials
│   ├── register.html           # User registration with password hashing
│   ├── dashboard.html          # Member dashboard with analytics & recent activity
│   ├── recipe.html             # Recipe details, cooking timer, checklist & print
│   ├── favourites.html         # User's saved recipes collection
│   ├── history.html            # Search history tracking & "Search Again" feature
│   ├── categories.html         # Category explorer (Breakfast, Lunch, Dinner, etc.)
│   ├── search_results.html     # Filtered search results (Diet & Cooking time filters)
│   └── 404.html                # Friendly 404/500 error page
└── static/
    ├── css/
    │   └── style.css           # Gourmet theme styling & @media print stylesheet
    ├── js/
    │   └── main.js             # AJAX favourites, Web Audio timer, checklist interactions
    └── images/
        └── logo.svg            # Custom vector brand logo
```

---

## 🚀 4. Step-by-Step Setup Guide (Windows 11 & VS Code)

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Click **File** &rarr; **Open Folder...** and select the `ai food recipe` directory.
3. Open the built-in terminal by pressing ``Ctrl + ` `` (Backtick) or selecting **Terminal** &rarr; **New Terminal**.

### Step 2: Set Up Python Virtual Environment
Run the following PowerShell commands in the terminal:
```powershell
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```
*(If PowerShell displays an ExecutionPolicy error, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and then run the activate command again).*

### Step 3: Install Required Python Packages
```powershell
pip install -r requirements.txt
```

### Step 4: Configure the Environment Variables (`.env`)
A default `.env` file is already created. Open `.env` in VS Code:
```env
SECRET_KEY=bca_final_year_secret_key_recipe_ai_2026

# Paste your free Gemini API Key below
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
GEMINI_MODEL=gemini-1.5-flash

# MySQL Database Configuration (XAMPP / WAMP / MySQL Server)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=recipe_db
DB_PORT=3306

FLASK_ENV=development
FLASK_DEBUG=True
```

> **How to get a Free Google Gemini API Key:**
> 1. Visit [Google AI Studio](https://aistudio.google.com/).
> 2. Sign in with any Google account.
> 3. Click **Get API key** &rarr; **Create API key**.
> 4. Copy and paste the key into `GEMINI_API_KEY=` in `.env`.

---

## 🗄️ 5. MySQL Database Setup

### Option A: Using XAMPP (Recommended for BCA Demonstrations)
1. Open the **XAMPP Control Panel**.
2. Click **Start** next to **MySQL** (and **Apache** if you wish to use phpMyAdmin).
3. Open your browser and navigate to `http://localhost/phpmyadmin/`.
4. Click **New** on the left sidebar, enter `recipe_db` as the database name, and click **Create**.
5. Click the **Import** tab, choose the file `database/schema.sql`, and click **Import**.
6. (Optional) Import `database/seed.sql` to preload authentic recipes and the demo account.

### Option B: Using MySQL Command Line Client
```sql
mysql -u root -p
```
Once logged in, execute:
```sql
SOURCE database/schema.sql;
SOURCE database/seed.sql;
```

### Option C: Seamless SQLite Auto-Fallback
If MySQL is not installed on the testing computer, the application's database layer (`database/db.py`) **automatically detects this and switches to SQLite (`database/recipe_db.sqlite`)**. All tables, relationships, password hashes, and pre-seeded recipes work seamlessly without any manual configuration!

---

## ▶️ 6. Running the Application

In the VS Code terminal (with `.venv` active):
```powershell
python app.py
```

You will see output similar to:
```text
============================================================
  AI FOOD RECIPE PREPARATION & RECOMMENDATION SYSTEM
  BCA FINAL YEAR PROJECT
  Database Status: Connected to MySQL (or SQLite Fallback)
  Gemini API Status: Active
  Running on: http://127.0.0.1:5000
============================================================
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🧪 7. Running the Automated Test Suite

An automated test suite is included to verify all routes, database transactions, authentication flows, and search logic:
```powershell
python test_app.py
```
**Result**: `Ran 7 tests ... OK`

---

## 🔑 8. Pre-Seeded Demo Credentials

For quick evaluation during project viva presentations:
- **Email**: `demo@recipeai.com`
- **Password**: `password123`
*(A convenient **"Autofill Demo Credentials"** button is also available directly on the login page).*

---

## 🌟 9. Key Features for Project Viva / Demonstration

1. **AI Recipe Generation**:
   Enter any dish (e.g. *Hyderabadi Biryani*, *Masala Dosa*, *Paneer Butter Masala*, *Vegetable Pulao*, *Pasta Carbonara*, *Matcha Latte*). The system sends a prompt to Gemini AI and parses clean JSON containing ingredients, instructions, cooking time, and nutrition.
2. **Interactive Kitchen Checklist**:
   Checkboxes allow users to strike through ingredients as they prepare them in their kitchen. Includes a **Copy Ingredients to Clipboard** button.
3. **Interactive Kitchen Timer**:
   Features a modal countdown timer with Start, Pause, Reset, +1 Min, and a Web Audio API chime that rings when cooking finishes.
4. **Print Optimization**:
   Clicking **Print Recipe** uses custom `@media print` CSS to render a clean, distraction-free physical recipe card.
5. **Dietary & Duration Filters**:
   Filter recipes by Category (Breakfast, Lunch, Dinner, Snacks, Desserts, Beverages), Dietary Type (Vegetarian, Non-Vegetarian, Vegan), and Cooking Duration (< 20m, < 40m, < 60m).
6. **AJAX Favourites Toggle**:
   Users can favorite and unfavorite dishes without full-page reloads.
7. **Full Search History**:
   Keeps track of all queries, timestamps, and active filters, with one-click **Search Again** and **Clear History** options.
8. **Enterprise-Grade Security**:
   Password hashing using `Werkzeug` (scrypt), strict session protection via `@login_required` decorators, environment variable isolation, and 100% parameterized SQL queries to prevent SQL Injection.

---

## 🎓 10. Sample Viva Questions & Answers

**Q1: Why did you choose Flask over Django or Node.js?**
> *Answer:* Flask is a lightweight WSGI micro-framework in Python. Unlike monolithic frameworks, Flask allows fine-grained architectural control over routing, session handling, and database integration while integrating with AI libraries and the Google Gemini API.

**Q2: How do you prevent SQL Injection in your database queries?**
> *Answer:* All queries in `database/db.py` use parameterized queries with placeholders (`%s` in MySQL and `?` in SQLite). Raw user input is never concatenated into SQL strings, neutralizing SQL injection vectors.

**Q3: How is password security managed?**
> *Answer:* Passwords are never stored in plaintext. They are salted and hashed using `werkzeug.security.generate_password_hash()` implementing cryptographic hashing (scrypt). On login, `check_password_hash()` verifies the hash in constant time to prevent timing attacks.

**Q4: How does the application handle Gemini API downtime or missing API keys?**
> *Answer:* The system implements a resilient fallback architecture in `gemini_service.py`. If the API key is missing or quota is exceeded, an intelligent local recipe knowledge engine procedurally synthesizes realistic ingredients, instructions, and nutritional data tailored to the dish so the application never crashes or displays a 500 error.

---

## 📄 License & Academic Attribution
Developed as a BCA Final Year Project. Free for educational and learning purposes.
#   a i - f o o d - r e c i p e  
 #   a i - f o o d - r e c i p e  
 