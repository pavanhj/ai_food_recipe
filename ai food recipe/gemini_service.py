import json
import re
import requests
from config import Config

# Curated high-resolution food photography URLs mapped to food categories and common items
IMAGE_MAP = {
    "biryani": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80",
    "dosa": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?auto=format&fit=crop&w=800&q=80",
    "paneer": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=800&q=80",
    "pulao": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=800&q=80",
    "rice": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=800&q=80",
    "pasta": "https://images.unsplash.com/photo-1645112411341-6c4fd023714a?auto=format&fit=crop&w=800&q=80",
    "pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80",
    "burger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80",
    "salad": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80",
    "soup": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80",
    "dessert": "https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=800&q=80",
    "cake": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80",
    "chocolate": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=800&q=80",
    "chicken": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?auto=format&fit=crop&w=800&q=80",
    "fish": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80",
    "sandwich": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=800&q=80",
    "curry": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80",
    "noodles": "https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=800&q=80",
    "samosa": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80",
    "tea": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=800&q=80",
    "coffee": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=800&q=80",
    "smoothie": "https://images.unsplash.com/photo-1553530666-ba11a7da3888?auto=format&fit=crop&w=800&q=80",
    "lassi": "https://images.unsplash.com/photo-1546173159-315724a31696?auto=format&fit=crop&w=800&q=80",
    "breakfast": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?auto=format&fit=crop&w=800&q=80",
    "default": "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=800&q=80"
}

def resolve_recipe_image(food_name, category=""):
    """Finds the most suitable appetizing food photo for a given dish name."""
    name_lower = (food_name + " " + category).lower()
    for key, url in IMAGE_MAP.items():
        if key in name_lower:
            return url
    # High-quality dynamic fallback via Unsplash source
    clean_keyword = re.sub(r'[^a-zA-Z0-9]', '', food_name.split()[0].lower())
    if clean_keyword:
        return f"https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80"
    return IMAGE_MAP["default"]

def clean_json_text(text):
    """Strips markdown code blocks and returns clean JSON string."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def generate_recipe_with_gemini(food_name, category_filter=None, diet_filter=None, time_filter=None):
    """
    Sends food recipe request to Google Gemini API.
    Returns: (recipe_dict, is_live_gemini, status_message)
    """
    api_key = Config.GEMINI_API_KEY
    model = Config.GEMINI_MODEL or "gemini-1.5-flash"
    
    # Check if API key is provided
    if not api_key or api_key.startswith("YOUR_GEMINI"):
        fallback_data = generate_intelligent_fallback(food_name, category_filter, diet_filter, time_filter)
        return (fallback_data, False, "Demo Mode: Add your free Google Gemini API key to .env for live AI queries.")

    # Craft structured prompt
    prompt = f"""
You are an expert master chef and nutritionist.
The user wants an authentic, detailed, delicious recipe for: "{food_name}".

Additional User Preferences:
- Preferred Category: {category_filter if category_filter else 'Auto-detect'}
- Dietary Requirement: {diet_filter if diet_filter else 'Auto-detect (Veg/Non-Veg/Vegan)'}
- Time Preference: {time_filter if time_filter else 'Standard'}

Respond ONLY with a valid JSON object matching the exact structure below. Do not wrap in markdown quotes if possible, output pure JSON.

{{
  "title": "{food_name}",
  "description": "A 1-2 sentence appetizing description of the dish and its flavor profile.",
  "category": "Breakfast | Lunch | Dinner | Snacks | Desserts | Beverages",
  "diet_type": "Veg | Non-Veg | Vegan",
  "prep_time": 15,
  "cook_time": 25,
  "servings": 4,
  "difficulty": "Easy | Medium | Hard",
  "ingredients": [
    "Quantity and ingredient name with unit (e.g., 2 cups Basmati Rice)",
    "..."
  ],
  "instructions": [
    "Step 1: Clear, actionable cooking instruction",
    "Step 2: Clear, actionable cooking instruction",
    "..."
  ],
  "nutrition": {{
    "calories": 350,
    "protein": "12g",
    "carbs": "45g",
    "fats": "14g",
    "fiber": "3g"
  }},
  "chef_tips": "A professional chef secret or culinary tip for making this dish taste extraordinary."
}}
"""

    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 2048,
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=18)
        if response.status_code == 200:
            res_data = response.json()
            candidates = res_data.get("candidates", [])
            if candidates:
                raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                cleaned = clean_json_text(raw_text)
                recipe_json = json.loads(cleaned)
                
                # Sanitize and ensure required fields
                prep_time = int(recipe_json.get("prep_time", 15))
                cook_time = int(recipe_json.get("cook_time", 20))
                total_time = prep_time + cook_time
                
                recipe_data = {
                    "title": recipe_json.get("title", food_name.title()),
                    "description": recipe_json.get("description", f"Delicious homemade {food_name} prepared with aromatic herbs and fresh ingredients."),
                    "category": recipe_json.get("category", "Main Course"),
                    "diet_type": recipe_json.get("diet_type", "Veg"),
                    "prep_time": prep_time,
                    "cook_time": cook_time,
                    "total_time": total_time,
                    "servings": int(recipe_json.get("servings", 4)),
                    "difficulty": recipe_json.get("difficulty", "Medium"),
                    "ingredients": json.dumps(recipe_json.get("ingredients", [])),
                    "instructions": json.dumps(recipe_json.get("instructions", [])),
                    "nutrition": json.dumps(recipe_json.get("nutrition", {"calories": 350, "protein": "10g", "carbs": "40g", "fats": "12g", "fiber": "3g"})),
                    "image_url": resolve_recipe_image(food_name, recipe_json.get("category", "")),
                    "chef_tips": recipe_json.get("chef_tips", "Use freshly grounded spices for maximum aroma and authentic flavor."),
                    "source": "gemini_ai"
                }
                return (recipe_data, True, "Recipe successfully generated in real-time by Google Gemini AI!")
            else:
                fallback_data = generate_intelligent_fallback(food_name, category_filter, diet_filter, time_filter)
                return (fallback_data, False, "Gemini returned an empty candidate list. Fallback recipe provided.")
        else:
            err_msg = f"Gemini API returned status code {response.status_code}"
            try:
                err_json = response.json()
                err_msg += f": {err_json.get('error', {}).get('message', '')}"
            except Exception:
                pass
            fallback_data = generate_intelligent_fallback(food_name, category_filter, diet_filter, time_filter)
            return (fallback_data, False, f"{err_msg}. Generated using Recipe Knowledge Engine.")
    except Exception as e:
        fallback_data = generate_intelligent_fallback(food_name, category_filter, diet_filter, time_filter)
        return (fallback_data, False, f"Gemini connection error ({e}). Generated using Recipe Knowledge Engine.")

def generate_intelligent_fallback(food_name, category_filter=None, diet_filter=None, time_filter=None):
    """
    Intelligent culinary fallback engine for offline testing or missing API keys.
    Generates delicious, realistic recipe details so the application NEVER crashes or looks empty.
    """
    food_clean = food_name.strip().title()
    name_lower = food_clean.lower()
    
    # Determine category
    category = category_filter or "Lunch"
    if any(k in name_lower for k in ["toast", "pancake", "dosa", "idli", "oats", "egg", "cereal", "paratha", "poha", "upma"]):
        category = "Breakfast"
    elif any(k in name_lower for k in ["cake", "cookie", "halwa", "ice cream", "pudding", "sweet", "brownie", "pastry"]):
        category = "Desserts"
    elif any(k in name_lower for k in ["juice", "shake", "tea", "coffee", "lassi", "smoothie", "mocktail", "cooler"]):
        category = "Beverages"
    elif any(k in name_lower for k in ["samosa", "pakora", "fries", "roll", "nachos", "snack", "tikki", "chaat"]):
        category = "Snacks"
    elif any(k in name_lower for k in ["biryani", "steak", "curry", "pasta", "roast", "pulao", "dal", "paneer"]):
        category = "Dinner"

    # Determine diet type
    diet = diet_filter or "Veg"
    if any(k in name_lower for k in ["chicken", "mutton", "beef", "fish", "prawn", "egg", "pork", "meat", "salmon"]):
        diet = "Non-Veg"
    elif any(k in name_lower for k in ["vegan", "tofu", "almond milk", "oat milk"]):
        diet = "Vegan"

    # Cooking times
    prep_time = 15
    cook_time = 20
    if category == "Beverages":
        prep_time, cook_time = 5, 5
    elif category == "Desserts":
        prep_time, cook_time = 20, 30
    elif diet == "Non-Veg":
        prep_time, cook_time = 20, 35

    # Ingredients tailored to dish name
    if "chicken" in name_lower:
        ingredients = [
            "500g Chicken (cleaned and cut into bite-sized pieces)",
            "2 large Onions, finely sliced",
            "2 ripe Tomatoes, finely pureed",
            "1.5 tbsp Ginger-Garlic paste",
            "1 tsp Kashmiri Red Chili powder",
            "1/2 tsp Turmeric powder",
            "1 tsp Garam Masala powder",
            "1/2 cup fresh Curd/Yogurt",
            "3 tbsp Cooking Oil or Ghee",
            "Whole spices (Bay leaf, cloves, cardamom)",
            "Fresh chopped coriander leaves for garnish",
            "Salt to taste"
        ]
    elif "paneer" in name_lower:
        ingredients = [
            "250g Fresh Paneer cubes",
            "2 medium Onions, finely chopped",
            "3 ripe Tomatoes, pureed",
            "1 tbsp Ginger-Garlic paste",
            "1/2 cup soaked Cashew nuts (blended to paste)",
            "2 tbsp Butter and 1 tbsp Oil",
            "1 tsp Red Chili powder",
            "1/2 tsp Turmeric and 1 tsp Garam Masala",
            "1 tbsp crushed Kasuri Methi",
            "2 tbsp Fresh cream",
            "Salt to taste"
        ]
    elif "dosa" in name_lower or "idli" in name_lower:
        ingredients = [
            "3 cups Idli/Dosa Rice",
            "1 cup whole Urad Dal (black gram)",
            "1/2 tsp Fenugreek (methi) seeds",
            "Water for grinding to smooth batter",
            "1.5 tsp Rock salt",
            "Oil or Ghee for crisping on the griddle"
        ]
    elif "pasta" in name_lower or "spaghetti" in name_lower:
        ingredients = [
            "250g Durum Wheat Pasta",
            "3 tbsp Extra Virgin Olive Oil",
            "4 cloves Garlic, thinly sliced",
            "1 can Italian crushed tomatoes (or 1 cup heavy cream)",
            "1/2 cup freshly grated Parmesan cheese",
            "Fresh basil leaves",
            "Crushed red pepper flakes",
            "Salt and freshly ground black pepper"
        ]
    elif "cake" in name_lower or "dessert" in name_lower:
        ingredients = [
            "1.5 cups All-purpose Flour",
            "3/4 cup Caster Sugar",
            "1/2 cup Unsalted Butter, softened",
            "2 large Eggs (or 1/2 cup condensed milk for eggless)",
            "1 tsp Baking powder & 1/2 tsp Baking soda",
            "1 tsp Pure Vanilla Extract",
            "1/2 cup Whole Milk"
        ]
    else:
        ingredients = [
            f"500g primary fresh ingredient for {food_clean}",
            "2 medium Onions, diced",
            "2 cloves Garlic and 1 inch Ginger, minced",
            "2 tbsp Extra virgin cooking oil or ghee",
            "1 tsp aromatic ground spice blend",
            "1 cup fresh vegetable or herb broth",
            "Fresh garden herbs for garnish",
            "Salt and fresh black pepper to taste"
        ]

    # Cooking steps tailored to dish
    instructions = [
        f"Step 1: Prep and thoroughly clean all ingredients for {food_clean}. Chop herbs and vegetables evenly to ensure uniform cooking.",
        f"Step 2: Heat cooking fat (oil, butter, or ghee) in a heavy-bottomed skillet or pot over medium heat. Sauté aromatics (onions, ginger, garlic) until golden and fragrant.",
        f"Step 3: Add core spices and seasonings, cooking on low heat for 1 to 2 minutes until the essential oils are released.",
        f"Step 4: Incorporate the main ingredients into the fragrant base, tossing gently to coat every morsel evenly with flavor.",
        f"Step 5: Pour in liquid/broth as required, cover with a tight lid, and simmer on gentle heat until tender, aromatic, and cooked to perfection.",
        f"Step 6: Remove lid, test seasoning for salt and acid balance, and garnish generously with freshly chopped herbs.",
        f"Step 7: Rest for 3 to 5 minutes before serving hot alongside your favorite bread, rice, or side salad."
    ]

    nutrition = {
        "calories": 340 if diet == "Veg" else 480,
        "protein": "14g" if diet == "Veg" else "28g",
        "carbs": "46g",
        "fats": "12g",
        "fiber": "4g"
    }

    return {
        "title": food_clean,
        "description": f"An authentic, mouth-watering preparation of {food_clean} bursting with rich flavors, balanced spices, and enticing aroma.",
        "category": category,
        "diet_type": diet,
        "prep_time": prep_time,
        "cook_time": cook_time,
        "total_time": prep_time + cook_time,
        "servings": 4,
        "difficulty": "Medium",
        "ingredients": json.dumps(ingredients),
        "instructions": json.dumps(instructions),
        "nutrition": json.dumps(nutrition),
        "image_url": resolve_recipe_image(food_clean, category),
        "chef_tips": f"For the best tasting {food_clean}, let the dish rest for 5 minutes after cooking so the flavors marry together before serving.",
        "source": "knowledge_engine"
    }
