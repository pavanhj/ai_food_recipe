-- ========================================================
-- AI Food Recipe Preparation & Recommendation System
-- Seed Data for Initial Recipes & Demo Account
-- ========================================================

USE `recipe_db`;

-- Demo User: email: demo@recipeai.com / password: password123
-- Password hash generated with Werkzeug generate_password_hash('password123')
INSERT INTO `users` (`id`, `name`, `email`, `password_hash`) 
VALUES (1, 'BCA Demo Student', 'demo@recipeai.com', 'scrypt:32768:8:1$hU9yF2W8kQ0oN0T0$7b61f93f1fa68b9ec44a33118cf23ad2e9ec21759faad5334cbe908cefb4b18efdcfc9feefbb31d2dafb4ebf519532822a904fa153fb50949392e205ae92d6e0')
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);

-- Insert Initial Popular & Recommended Recipes
INSERT INTO `recipes` 
(`id`, `title`, `description`, `category`, `diet_type`, `prep_time`, `cook_time`, `total_time`, `servings`, `difficulty`, `ingredients`, `instructions`, `nutrition`, `image_url`, `chef_tips`, `source`, `views`) 
VALUES
(
    1,
    'Royal Hyderabadi Chicken Biryani',
    'A world-renowned aromatic rice and chicken dish infused with exotic saffron, fried onions, and whole spices cooked in the traditional dum style.',
    'Dinner',
    'Non-Veg',
    30,
    45,
    75,
    4,
    'Medium',
    '["500g Chicken cut into pieces", "2 cups aged Basmati Rice", "1 cup thick Yogurt (Dahi)", "2 large Onions, thinly sliced & golden fried (Birista)", "2 tbsp Ginger-Garlic paste", "1 tsp Red Chili powder", "1/2 tsp Turmeric powder", "1 tsp Garam Masala", "A pinch of Saffron soaked in 4 tbsp warm milk", "1/4 cup fresh Mint leaves, chopped", "1/4 cup fresh Coriander leaves, chopped", "3 tbsp Pure Ghee", "Whole spices: 2 bay leaves, 4 green cardamoms, 1 black cardamom, 4 cloves, 1 cinnamon stick", "Salt to taste"]',
    '["Marinate chicken with yogurt, ginger-garlic paste, red chili powder, turmeric, garam masala, salt, and half the mint and coriander for at least 30 minutes.", "Wash and soak basmati rice for 30 minutes. In a large pot, boil water with whole spices and salt. Cook rice until 70% done, then drain.", "In a heavy-bottomed handi or pot, heat ghee and add the marinated chicken. Cook on high for 5 minutes.", "Layer the partially cooked basmati rice over the chicken. Top with fried golden onions, chopped mint, coriander, saffron milk, and a dollop of ghee.", "Seal the pot tightly with aluminum foil or dough and a heavy lid. Cook on high heat for 5 minutes, then place on a tawa (griddle) on low flame for 25 minutes for dum cooking.", "Rest for 10 minutes before opening. Gently fluff the rice from bottom to top and serve hot with cooling cucumber raita and salan."]',
    '{"calories": 580, "protein": "34g", "carbs": "65g", "fats": "19g", "fiber": "3.5g"}',
    'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80',
    'Never stir the biryani aggressively; use a flat flat spatula and lift gently from the edges so rice grains remain intact and fluffy.',
    'system',
    42
),
(
    2,
    'South Indian Masala Dosa',
    'Crispy golden fermented rice and lentil crepe stuffed with fragrant spiced potato masala, served alongside fresh coconut chutney and piping hot sambar.',
    'Breakfast',
    'Veg',
    20,
    15,
    35,
    4,
    'Medium',
    '["3 cups Parboiled Rice", "1 cup Urad Dal (skinless black gram)", "1/2 tsp Fenugreek (methi) seeds", "4 large Potatoes, boiled and mashed coarsely", "1 large Onion, finely sliced", "2 Green chilies, slit", "1 tsp Mustard seeds", "1 tsp Cumin seeds", "1 sprig Curry leaves", "1/2 tsp Turmeric powder", "2 tbsp Oil or Butter", "Salt to taste", "Cold water for batter consistency"]',
    '["Wash and soak rice and fenugreek seeds in one bowl, and urad dal in another for 6 hours. Grind separately to a fine silky batter.", "Mix both batters together with salt. Cover and ferment in a warm place for 8 to 10 hours until light and aerated.", "Prepare potato filling: Heat oil in a pan, crackle mustard seeds, cumin seeds, curry leaves, green chilies, and turmeric. Add sliced onions and sauté till translucent.", "Add boiled mashed potatoes and salt. Stir gently, cook for 3 minutes, sprinkle coriander leaves and keep warm.", "Heat a seasoned cast-iron dosa tawa on medium heat. Pour a ladleful of batter in the center and spread quickly in outward circular motion to form a thin crepe.", "Drizzle oil or butter around the edges. Cook until the bottom turns deep golden brown and crispy.", "Place 3 tablespoons of potato masala in the center, fold over, and serve hot immediately with coconut chutney and sambar."]',
    '{"calories": 320, "protein": "7g", "carbs": "54g", "fats": "9g", "fiber": "4g"}',
    'https://images.unsplash.com/photo-1668236543090-82eba5ee5976?auto=format&fit=crop&w=800&q=80',
    'Sprinkle a few drops of water on the hot tawa and wipe with a clean cloth before pouring batter to regulate surface temperature.',
    'system',
    55
),
(
    3,
    'Restaurant Style Paneer Butter Masala',
    'Tender soft paneer cubes simmered in a velvety, buttery tomato-cashew gravy scented with dried fenugreek leaves (kasuri methi).',
    'Dinner',
    'Veg',
    15,
    25,
    40,
    4,
    'Easy',
    '["250g Paneer cubes", "4 large ripe Tomatoes, pureed", "2 medium Onions, roughly chopped", "15 Cashew nuts, soaked in warm water", "2 tbsp Butter", "1 tbsp Cooking Oil", "1 tbsp Ginger-Garlic paste", "1 tsp Kashmiri Red Chili powder", "1/2 tsp Garam Masala", "1 tsp Coriander powder", "1 tbsp crushed Kasuri Methi", "3 tbsp Fresh Cream", "Salt to taste"]',
    '["Boil chopped onions and soaked cashews in 1 cup water for 10 minutes until soft. Cool and blend into a rich creamy paste.", "Heat oil and 1 tablespoon butter in a deep kadai. Add ginger-garlic paste and sauté for 1 minute until fragrant.", "Add the onion-cashew paste and cook on medium heat until light golden and oil begins to separate.", "Add tomato puree, red chili powder, coriander powder, and salt. Cook covered for 8 to 10 minutes until the gravy thickens.", "Pour 1/2 cup warm water to adjust gravy consistency. Bring to a gentle simmer.", "Gently slide in fresh paneer cubes and simmer on low flame for 4 minutes so the paneer absorbs flavors without getting rubbery.", "Crush kasuri methi between palms and sprinkle on top, add garam masala, remaining butter, and fresh cream. Mix gently and serve hot with garlic naan or basmati rice."]',
    '{"calories": 410, "protein": "16g", "carbs": "18g", "fats": "32g", "fiber": "3g"}',
    'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=800&q=80',
    'Soak store-bought paneer cubes in lukewarm salted water for 15 minutes before cooking to keep them exceptionally soft and melt-in-mouth.',
    'system',
    38
),
(
    4,
    'Fragrant Vegetable Pulao',
    'A wholesome one-pot meal made with fragrant basmati rice, colorful mixed garden vegetables, and warm whole spices.',
    'Lunch',
    'Veg',
    15,
    20,
    35,
    4,
    'Easy',
    '["1.5 cups Basmati Rice, washed and soaked 20 mins", "1/2 cup diced Carrots", "1/2 cup Green Peas (fresh or frozen)", "1/2 cup diced French Beans", "1 medium Potato, cubed", "1 large Onion, thinly sliced", "1 tbsp Ginger-Garlic paste", "2 Green chilies, slit", "2 tbsp Ghee or Vegetable Oil", "Whole spices: 1 Bay leaf, 1 star anise, 3 cardamoms, 1 inch cinnamon", "3 cups Water or Vegetable broth", "Fresh chopped mint and coriander"]',
    '["Heat ghee or oil in a pressure cooker or deep pot. Add whole spices and sauté until crackling and fragrant.", "Add sliced onions and green chilies. Fry until the onions turn translucent and light golden.", "Stir in ginger-garlic paste and sauté for 1 minute.", "Add all diced vegetables (carrots, peas, beans, potatoes) and sauté on medium heat for 3 minutes.", "Drain the soaked basmati rice and add to the pot. Gently mix for 1 minute ensuring rice grains coat with ghee.", "Add 3 cups of water and salt to taste. Bring to a rapid rolling boil.", "Cover with lid: If using pressure cooker, cook on medium heat for 2 whistles. If using a pot, cover tight and cook on low for 15 minutes.", "Turn off heat, let pressure release naturally. Fluff with a fork and garnish with fresh mint leaves."]',
    '{"calories": 290, "protein": "6g", "carbs": "56g", "fats": "6g", "fiber": "4.5g"}',
    'https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=800&q=80',
    'Always use a 1:2 ratio of basmati rice to water for fluffy, non-sticky rice grains.',
    'system',
    29
),
(
    5,
    'Creamy Italian Fettuccine Alfredo',
    'Silky ribbons of fettuccine pasta coated in an opulent homemade parmesan cream sauce and freshly cracked black pepper.',
    'Dinner',
    'Veg',
    10,
    15,
    25,
    2,
    'Easy',
    '["250g Fettuccine pasta", "3 tbsp Unsalted Butter", "3 cloves Garlic, minced", "1 cup Heavy Cream", "1 cup freshly grated Parmigiano-Reggiano cheese", "Freshly cracked black pepper", "A pinch of Nutmeg", "Fresh flat-leaf Parsley, finely chopped", "Salt for pasta water"]',
    '["Bring a large pot of generously salted water to a boil. Cook fettuccine pasta until al dente according to package instructions. Reserve 1/2 cup starchy pasta water.", "Meanwhile, melt butter in a large skillet over medium-low heat. Add minced garlic and cook for 1 minute until fragrant (do not brown).", "Pour in heavy cream and bring to a gentle simmer. Cook for 3 to 4 minutes until slightly thickened.", "Reduce heat to low and gradually stir in grated Parmesan cheese until completely melted and smooth.", "Transfer cooked fettuccine directly into the sauce. Toss vigorously to coat pasta ribbons.", "If sauce is too thick, ladle in a splash of reserved pasta water. Season with freshly cracked black pepper and a pinch of nutmeg.", "Serve immediately in warm pasta bowls, garnished with extra parmesan and fresh parsley."]',
    '{"calories": 520, "protein": "14g", "carbs": "48g", "fats": "31g", "fiber": "2g"}',
    'https://images.unsplash.com/photo-1645112411341-6c4fd023714a?auto=format&fit=crop&w=800&q=80',
    'Always use freshly grated block Parmesan cheese; pre-shredded cheese contains anti-caking starches that prevent a smooth sauce.',
    'system',
    18
),
(
    6,
    'Authentic Mango Lassi',
    'Thick, creamy and refreshingly sweet yogurt smoothie blended with ripe Alphonso mangoes and a touch of fragrant cardamom.',
    'Beverages',
    'Veg',
    10,
    0,
    10,
    2,
    'Easy',
    '["1.5 cups ripe Mango pulp (Alphonso or Kesar)", "1.5 cups chilled Greek yogurt or thick curd", "1/2 cup chilled whole Milk", "2 tbsp Sugar or Honey (adjust to mango sweetness)", "1/4 tsp Cardamom powder", "Crushed Ice cubes", "Slivered pistachios and saffron strands for garnish"]',
    '["Peel and dice fresh sweet mangoes, or use high quality Alphonso mango pulp.", "Add mango cubes, chilled thick yogurt, milk, sugar, and cardamom powder to a high-speed blender.", "Blend on high speed for 60 to 90 seconds until silky smooth, rich, and frothy.", "Add crushed ice cubes and pulse for 10 seconds to chill thoroughly.", "Pour into tall chilled serving glasses. Garnish with a sprinkle of cardamom powder, slivered pistachios, and saffron strands. Serve immediately."]',
    '{"calories": 210, "protein": "7g", "carbs": "38g", "fats": "4g", "fiber": "2g"}',
    'https://images.unsplash.com/photo-1546173159-315724a31696?auto=format&fit=crop&w=800&q=80',
    'For an authentic restaurant thickness, use hung yogurt or Greek yogurt and avoid adding excess water.',
    'system',
    60
),
(
    7,
    'Decadent Warm Chocolate Lava Cake',
    'Individual chocolate sponge cake with a warm molten chocolate center that flows effortlessly upon first spoonful.',
    'Desserts',
    'Veg',
    15,
    12,
    27,
    2,
    'Medium',
    '["100g Dark chocolate (70% cocoa), chopped", "50g Unsalted Butter", "2 large Eggs", "3 tbsp Caster Sugar", "2 tbsp All-purpose Flour", "1 tsp Vanilla extract", "Cocoa powder and butter for greasing ramekins", "Powdered sugar and fresh berries for serving"]',
    '["Preheat oven to 200°C (400°F). Grease two 6-oz ceramic ramekins with butter and dust thoroughly with cocoa powder.", "Melt dark chocolate and butter together in a heatproof bowl set over a pot of gently simmering water (bain-marie). Stir until smooth and glossy, then cool slightly.", "In another bowl, whisk eggs, sugar, and vanilla extract until pale, thick, and doubled in volume (about 3 minutes).", "Gently fold the melted chocolate mixture into the whipped eggs using a silicone spatula.", "Sift in the flour and fold gently just until no dry flour streaks remain. Do not overmix.", "Divide the batter evenly into the prepared ramekins. Place on a baking sheet and bake for 11 to 12 minutes until edges are firm but center is still soft and jiggly.", "Let rest for 1 minute. Run a thin knife around the rim and carefully invert onto dessert plates. Dust with powdered sugar and serve warm with vanilla ice cream."]',
    '{"calories": 440, "protein": "7g", "carbs": "42g", "fats": "28g", "fiber": "3.8g"}',
    'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=800&q=80',
    'Timing is critical for lava cakes: bake 11 minutes for a molten river center, or 12 minutes for a fudgy center.',
    'system',
    49
),
(
    8,
    'Crispy Vegetable Spring Rolls',
    'Crunchy golden wrappers loaded with savory shredded cabbage, carrots, bell peppers, and scallions tossed with soy sauce and sesame oil.',
    'Snacks',
    'Veg',
    20,
    15,
    35,
    4,
    'Medium',
    '["10 Spring roll pastry sheets", "2 cups shredded Green Cabbage", "1 cup julienned Carrots", "1/2 cup thinly sliced Bell Peppers", "3 Spring onions, chopped", "3 cloves Garlic, minced", "1 tbsp Soy Sauce", "1 tbsp Sweet chili sauce", "1 tsp Toasted sesame oil", "1/2 tsp White pepper powder", "2 tbsp Flour mixed with water into a paste (slurry)", "Vegetable oil for deep frying"]',
    '["Heat 1 tbsp sesame oil in a wok on high heat. Add minced garlic and whites of spring onions; sauté for 30 seconds.", "Add shredded cabbage, carrots, and bell peppers. Stir fry vigorously on high flame for 2 to 3 minutes so vegetables remain crunchy.", "Stir in soy sauce, sweet chili sauce, white pepper, and salt. Cook for 1 minute. Remove from heat, stir in green spring onions, and cool completely.", "Place a spring roll wrapper on a clean surface in a diamond shape. Spoon 2 tbsp filling near the bottom corner.", "Roll the corner over the filling, tuck tightly, fold left and right corners inward like an envelope, and continue rolling.", "Brush the top corner with the flour-water paste to seal securely.", "Heat vegetable oil to 180°C (350°F). Fry rolls in batches for 4 to 5 minutes until crispy and golden brown. Drain on paper towels and serve with sweet chili sauce."]',
    '{"calories": 260, "protein": "5g", "carbs": "34g", "fats": "12g", "fiber": "3g"}',
    'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80',
    'Ensure the vegetable filling has cooled completely before rolling, otherwise steam will make the delicate pastry sheets tear.',
    'system',
    31
);
