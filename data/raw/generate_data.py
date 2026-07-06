"""
Synthetic Marketing Data Generator
Generates CSV files for all 10 source tables:
  customers, products, categories, suppliers, transactions,
  order_items, campaigns, campaign_responses, website_sessions, customer_behavior
"""
import pandas as pd
import numpy as np
from faker import Faker
from pathlib import Path
from datetime import datetime, timedelta
import random

fake = Faker()
random.seed(42)
np.random.seed(42)
Faker.seed(42)

OUTPUT_DIR = Path(__file__).parent
N_CUSTOMERS = 2000
N_PRODUCTS = 200
N_CATEGORIES = 20
N_SUPPLIERS = 30
N_TRANSACTIONS = 8000
N_CAMPAIGNS = 25
N_SESSIONS = 5000


def generate_categories():
    categories = [
        {"category_id": 1, "category_name": "Lips", "parent_category_id": None, "description": "Lipsticks, lip glosses, oils, and lip liners for the perfect pout."},
        {"category_id": 2, "category_name": "Face", "parent_category_id": None, "description": "Foundations, concealers, primers, blushes, highlighters, and setting powders."},
        {"category_id": 3, "category_name": "Eyes", "parent_category_id": None, "description": "Eyeshadow palettes, eyeliners, mascaras, and brow defining products."},
        {"category_id": 4, "category_name": "Skincare", "parent_category_id": None, "description": "Serums, moisturizers, cleansers, toners, and hydrating face masks."},
        {"category_id": 5, "category_name": "Brushes & Tools", "parent_category_id": None, "description": "Professional makeup brush sets, sponges, and cosmetic tools."},
    ]
    # Sub-categories
    sub_categories = [
        ("Lipsticks", 1), ("Lip Glosses", 1), ("Lip Liners", 1),
        ("Foundations", 2), ("Concealers", 2), ("Blushes & Bronzers", 2), ("Highlighters", 2),
        ("Eyeshadows", 3), ("Eyeliners", 3), ("Mascaras", 3), ("Brow Makeup", 3),
        ("Face Serums", 4), ("Moisturizers", 4), ("Cleansers", 4), ("Face Masks", 4),
    ]
    for idx, (sub_name, parent_id) in enumerate(sub_categories, 6):
        categories.append({
            "category_id": idx,
            "category_name": sub_name,
            "parent_category_id": parent_id,
            "description": f"Premium {sub_name.lower()} category."
        })
    # Fill remaining up to 20
    for i in range(len(categories) + 1, N_CATEGORIES + 1):
        categories.append({
            "category_id": i,
            "category_name": f"Limited Edition Collection {i}",
            "parent_category_id": random.choice([1, 2, 3, 4]),
            "description": "Special limited release cosmetic item collection."
        })
    return pd.DataFrame(categories)


def generate_suppliers():
    rows = []
    for i in range(1, N_SUPPLIERS + 1):
        rows.append({
            "supplier_id": i,
            "supplier_name": fake.company(),
            "contact_name": fake.name(),
            "email": fake.company_email(),
            "phone": fake.phone_number()[:20],
            "country": fake.country(),
            "city": fake.city(),
            "created_at": fake.date_time_between(start_date="-3y", end_date="-1y").isoformat()
        })
    return pd.DataFrame(rows)


def generate_products(categories_df, suppliers_df):
    rows = []
    
    # Base lists of actual best-selling products by parent category
    lips_base = [
        ("M.A.C Matte Lipstick", ["Ruby Woo", "Mehr", "Velvet Teddy", "Russian Red", "Chili", "Diva", "Kinda Sexy"]),
        ("M.A.C Retro Matte Liquid Lipcolour", ["Back In Vogue", "To Matte With Love", "Fashion Legacy"]),
        ("Maybelline Super Stay Matte Ink", ["Seductress", "Lover", "Pioneer", "Ruler", "Voyager", "Fighter"]),
        ("Maybelline Super Stay Vinyl Ink", ["Cheeky", "Coy", "Peachy", "Mischievous", "Red-Hot"]),
        ("Huda Beauty Liquid Matte Lipstick", ["Bombshell", "Venus", "Trophy Wife", "Icon", "Heartbreaker"]),
        ("Huda Beauty Lip Contour 2.0 Pencil", ["Pinky Brown", "Warm Brown", "Sandy Beige", "Honey Beige"]),
        ("L'Oreal Paris Infallible Matte Resistance", ["Le Rouge Paris", "French Touch", "Major Crush"]),
        ("L'Oreal Paris Color Riche Intense Volume Matte", ["Worth It", "Le Nude Admirable", "Le Wood Nonchalant"]),
        ("Nykaa Matte to Last Liquid Lipstick", ["Madras Kaapi", "Bombae", "Janhavi", "Guwahati", "Maharani"]),
        ("Nykaa So Creme Creamy Matte Lipstick", ["Wakeup Makeup", "Let it Glow", "Pretty in Pink", "Daily Doll"]),
        ("Charlotte Tilbury Matte Revolution", ["Pillow Talk", "Walk of No Shame", "Very Victoria", "Red Carpet Red"])
    ]
    
    face_base = [
        ("Maybelline Fit Me Matte+Poreless Foundation", ["115 Ivory", "128 Warm Nude", "220 Natural Beige", "310 Sun Beige", "330 Toffee"]),
        ("Maybelline Fit Me Concealer", ["10 Light", "15 Fair", "20 Sand", "25 Medium", "30 Honey"]),
        ("Maybelline Instant Age Rewind Eraser Concealer", ["110 Fair", "120 Light", "130 Medium", "140 Honey"]),
        ("M.A.C Studio Fix Fluid Foundation SPF 15", ["NC15", "NC25", "NC35", "NC40", "NC42", "NC45", "NW20"]),
        ("M.A.C Studio Fix Powder Plus Foundation", ["NC20", "NC30", "NC35", "NC42", "NC45"]),
        ("M.A.C Strobe Cream Hydrant", ["Pinklite", "Goldlite", "Peachlite"]),
        ("Huda Beauty Easy Bake Setting Powder", ["Banana Bread", "Pound Cake", "Cherry Blossom", "Cupcake"]),
        ("Huda Beauty FauxFilter Luminous Matte Concealer", ["Whipped Cream", "Coconut Flakes", "Nougat", "Granola"]),
        ("L'Oreal Paris Infallible 24H Fresh Wear Foundation", ["120 Vanilla", "140 Golden Beige", "220 Sand", "250 Radiant Sun"]),
        ("L'Oreal Paris Infallible Full Wear Concealer", ["320 Porcelain", "360 Cashmere", "380 Pecan"]),
        ("Nykaa All Day Matte Liquid Foundation", ["Olive", "Beige", "Warm Honey", "Caramel"]),
        ("Nykaa Get Cheeky Powder Blush", ["Peach Bliss", "Rose Meadow", "Bronze Glow"]),
        ("Charlotte Tilbury Hollywood Flawless Filter", ["1 Fair", "2 Light", "3 Light-Medium", "4 Medium", "5 Tan"]),
        ("Charlotte Tilbury Airbrush Flawless Finish Powder", ["1 Fair", "2 Medium", "3 Tan"]),
        ("Estee Lauder Double Wear Foundation", ["1W2 Sand", "2N1 Desert Beige", "3W1 Tawny", "4N1 Shell Beige"]),
        ("Nykaa Prep Me Up Face Primer", ["Clear Silk"]),
        ("M.A.C Mineralize Skinfinish Highlighter", ["Soft & Gentle", "Global Glow", "Cheeky Bronze"])
    ]
    
    eyes_base = [
        ("Maybelline Lash Sensational Sky High Mascara", ["Very Black", "Waterproof Very Black", "Brownish Black"]),
        ("Maybelline Colossal Waterproof Mascara", ["Glam Black"]),
        ("Maybelline Lasting Drama Gel Eyeliner", ["Blackest Black", "Charcoal"]),
        ("Maybelline Line Tattoo High Impact Eyeliner", ["Intense Black"]),
        ("M.A.C In Extreme Dimension 3D Mascara", ["Black 3D"]),
        ("M.A.C Eye Shadow Satin", ["Charcoal Brown", "Brun", "Omega", "Carbon", "Espresso"]),
        ("Huda Beauty Empowered Eyeshadow Palette", ["Full size 18 Shades"]),
        ("Huda Beauty Nude Obsessions Mini Palette", ["Light", "Medium", "Rich"]),
        ("Huda Beauty Rose Quartz Eyeshadow Palette", ["Full size 18 Shades"]),
        ("L'Oreal Paris Voluminous Lash Paradise Mascara", ["Blackest Black", "Washable Black"]),
        ("L'Oreal Paris Voluminous Panorama Mascara", ["Waterproof Black"]),
        ("L'Oreal Paris Super Liner Gel Intenza", ["Profundo Black"]),
        ("Nykaa Black Magic Liquid Eyeliner", ["Super Black"]),
        ("Nykaa Glamoreyes Liquid Eyeliner", ["01 Black", "02 Bronze", "03 Blue"]),
        ("Nykaa Brow Ontrend Eyebrow Pencil", ["Dark Brown", "Soft Black"]),
        ("Nykaa Eyes On Me 10-in-1 Eyeshadow Palette", ["Sunset Stroll", "Beachside Peach", "Smokey Dusk"]),
        ("Charlotte Tilbury Luxury Eyeshadow Palette", ["Pillow Talk", "Golden Hour", "Bella Sofia"]),
        ("Charlotte Tilbury Pillow Talk Push Up Lashes Mascara", ["Super Black"])
    ]
    
    skincare_base = [
        ("Clinique Moisture Surge 100H Hydrator", ["30ml", "50ml", "75ml"]),
        ("The Ordinary Niacinamide 10% + Zinc 1%", ["30ml", "60ml"]),
        ("The Ordinary Hyaluronic Acid 2% + B5", ["30ml", "60ml"]),
        ("The Ordinary Salicylic Acid 2% Solution", ["30ml"]),
        ("The Ordinary Squalane Cleanser", ["50ml", "150ml"]),
        ("The Ordinary Glycolic Acid 7% Toning Solution", ["240ml"]),
        ("Estee Lauder Advanced Night Repair Serum", ["30ml", "50ml", "75ml"]),
        ("Estee Lauder Revitalizing Supreme+ Cream", ["50ml"]),
        ("L'Oreal Paris Revitalift 1.5% Hyaluronic Acid Serum", ["15ml", "30ml", "50ml"]),
        ("L'Oreal Paris Glycolic Bright Skin Serum", ["15ml", "30ml"]),
        ("L'Oreal Paris Revitalift Crystal Micro-Essence", ["65ml", "130ml"]),
        ("Nykaa Skin Potion Facial Oil", ["Rosehip", "Marula", "Baobab"]),
        ("Nykaa Skin Genius Hydrating Moisturizer", ["50g"]),
        ("Clinique Take The Day Off Cleansing Balm", ["125ml"]),
        ("Clinique Clarifying Lotion 3 Toner", ["200ml", "400ml"]),
        ("Neutrogena Hydro Boost Water Gel Cream", ["50g"]),
        ("Neutrogena Deep Clean Facial Cleanser", ["200ml"])
    ]
    
    tools_base = [
        ("Nykaa BlendMaster Beauty Sponge", ["Classic Pink", "Teal Egg"]),
        ("Nykaa BlendMaster Oval Makeup Brush", ["Large Face", "Medium Blush"]),
        ("Nykaa Eyelash Curler", ["Rose Gold", "Classic Chrome"]),
        ("M.A.C 217S Blending Brush", ["Synthetic"]),
        ("M.A.C 170 Slanted Face Brush", ["Synthetic"]),
        ("M.A.C 187S Duo Fibre Face Brush", ["Synthetic"]),
        ("M.A.C 219S Pencil Brush", ["Synthetic"]),
        ("Real Techniques Miracle Complexion Sponge", ["Single Pack", "Two Pack"]),
        ("Real Techniques Everyday Essentials Brush Set", ["4 Brushes + Sponge"]),
        ("Real Techniques Powder Brush", ["Single"]),
        ("Sigma Beauty F80 Flat Kabuki Brush", ["Black Chrome", "Copper"]),
        ("Sigma Beauty E25 Blending Brush", ["Black Chrome"]),
        ("Sigma Beauty Clean Brush Cleaning Mat", ["Pink Silicone"])
    ]

    candidates = []
    
    # Lips (Parent=1)
    for prod_line, shades in lips_base:
        sub_cat = 6
        if "gloss" in prod_line.lower():
            sub_cat = 7
        elif "liner" in prod_line.lower() or "pencil" in prod_line.lower():
            sub_cat = 8
        price_base = 3200 if "M.A.C" in prod_line or "Charlotte" in prod_line else (2200 if "Huda" in prod_line else (850 if "L'Oreal" in prod_line or "Maybelline" in prod_line else 399))
        for shade in shades:
            price = round(price_base * random.uniform(0.95, 1.05), 2)
            candidates.append((f"{prod_line} - {shade}", sub_cat, price))
            
    # Face (Parent=2)
    for prod_line, shades in face_base:
        sub_cat = 9
        if "concealer" in prod_line.lower():
            sub_cat = 10
        elif "blush" in prod_line.lower() or "bronzer" in prod_line.lower():
            sub_cat = 11
        elif "highlighter" in prod_line.lower() or "strobe" in prod_line.lower() or "skinfinish" in prod_line.lower():
            sub_cat = 12
        price_base = 4500 if "M.A.C" in prod_line or "Charlotte" in prod_line or "Estee" in prod_line else (3200 if "Huda" in prod_line else (950 if "L'Oreal" in prod_line or "Maybelline" in prod_line else 599))
        for shade in shades:
            price = round(price_base * random.uniform(0.95, 1.05), 2)
            candidates.append((f"{prod_line} ({shade})", sub_cat, price))

    # Eyes (Parent=3)
    for prod_line, shades in eyes_base:
        sub_cat = 15
        if "palette" in prod_line.lower() or "shadow" in prod_line.lower():
            sub_cat = 13
        elif "liner" in prod_line.lower() or "eyeliner" in prod_line.lower():
            sub_cat = 14
        elif "brow" in prod_line.lower():
            sub_cat = 16
        price_base = 2800 if "M.A.C" in prod_line or "Charlotte" in prod_line else (4900 if "Huda" in prod_line and "palette" in prod_line.lower() else (1800 if "Huda" in prod_line else (850 if "L'Oreal" in prod_line or "Maybelline" in prod_line else 450)))
        for shade in shades:
            price = round(price_base * random.uniform(0.95, 1.05), 2)
            candidates.append((f"{prod_line} - {shade}", sub_cat, price))

    # Skincare (Parent=4)
    for prod_line, shades in skincare_base:
        sub_cat = 18
        if "serum" in prod_line.lower() or "potion" in prod_line.lower() or "night repair" in prod_line.lower():
            sub_cat = 17
        elif "cleanser" in prod_line.lower() or "balm" in prod_line.lower():
            sub_cat = 19
        elif "mask" in prod_line.lower():
            sub_cat = 20
        price_base = 5900 if "Estee" in prod_line else (3900 if "Clinique" in prod_line else (1200 if "The Ordinary" in prod_line or "L'Oreal" in prod_line else 690))
        for shade in shades:
            price = round(price_base * random.uniform(0.95, 1.05), 2)
            candidates.append((f"{prod_line} {shade}", sub_cat, price))

    # Tools (Parent=5)
    for prod_line, shades in tools_base:
        sub_cat = 5
        price_base = 2800 if "M.A.C" in prod_line else (2200 if "Sigma" in prod_line or "Real Techniques" in prod_line and "set" in prod_line.lower() else (800 if "Real Techniques" in prod_line else 499))
        for shade in shades:
            price = round(price_base * random.uniform(0.95, 1.05), 2)
            candidates.append((f"{prod_line} - {shade}", sub_cat, price))

    random.seed(42)
    random.shuffle(candidates)

    for i in range(1, N_PRODUCTS + 1):
        if i - 1 < len(candidates):
            name, category_id, unit_price = candidates[i - 1]
        else:
            name = f"Luxury Beauty Product {i}"
            category_id = random.choice(categories_df["category_id"].tolist())
            unit_price = round(random.uniform(500, 4500), 2)
            
        rows.append({
            "product_id": i,
            "product_name": name[:80],
            "category_id": category_id,
            "supplier_id": random.choice(suppliers_df["supplier_id"].tolist()),
            "unit_price": unit_price,
            "cost_price": round(unit_price * random.uniform(0.15, 0.25), 2),
            "stock_quantity": random.randint(50, 1000),
            "sku": f"SKU-{i:05d}",
            "is_active": random.random() > 0.05,
            "created_at": fake.date_time_between(start_date="-2y", end_date="-6m").isoformat()
        })
    return pd.DataFrame(rows)


def generate_customers():
    rows = []
    segments = ["Premium", "Regular", "Occasional", "At Risk", "New"]
    for i in range(1, N_CUSTOMERS + 1):
        rows.append({
            "customer_id": i,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": f"user{i}_{fake.user_name()}@{fake.free_email_domain()}",
            "phone": fake.phone_number()[:20],
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=75).isoformat(),
            "gender": random.choice(["M", "F", "Other"]),
            "country": random.choice(["US", "UK", "CA", "AU", "DE", "FR", "IN"]),
            "city": fake.city(),
            "registration_date": fake.date_time_between(start_date="-3y", end_date="-1m").isoformat(),
            "is_active": random.random() > 0.15,
            "customer_segment": random.choice(segments)
        })
    return pd.DataFrame(rows)


def generate_transactions(customers_df):
    rows = []
    customer_ids = customers_df["customer_id"].tolist()
    for i in range(1, N_TRANSACTIONS + 1):
        amount = round(random.expovariate(1 / 150), 2)
        discount = round(amount * random.uniform(0, 0.2), 2)
        rows.append({
            "transaction_id": i,
            "customer_id": random.choice(customer_ids),
            "transaction_date": fake.date_time_between(start_date="-2y", end_date="now").isoformat(),
            "total_amount": amount,
            "discount_amount": discount,
            "tax_amount": round(amount * 0.1, 2),
            "payment_method": random.choice(["credit_card", "debit_card", "paypal", "bank_transfer"]),
            "status": random.choices(["completed", "refunded", "cancelled"], weights=[90, 6, 4])[0],
            "channel": random.choice(["online", "mobile", "in_store", "phone"]),
            "created_at": datetime.utcnow().isoformat()
        })
    return pd.DataFrame(rows)


def generate_order_items(transactions_df, products_df):
    rows = []
    item_id = 1
    prod_ids = products_df["product_id"].tolist()
    prod_prices = dict(zip(products_df["product_id"], products_df["unit_price"]))
    for _, txn in transactions_df.head(N_TRANSACTIONS).iterrows():
        n_items = random.randint(1, 5)
        for _ in range(n_items):
            pid = random.choice(prod_ids)
            qty = random.randint(1, 5)
            price = float(prod_prices.get(pid, 50))
            rows.append({
                "order_item_id": item_id,
                "transaction_id": int(txn["transaction_id"]),
                "product_id": pid,
                "quantity": qty,
                "unit_price": price,
                "discount": round(price * random.uniform(0, 0.15), 2)
            })
            item_id += 1
    return pd.DataFrame(rows)


def generate_campaigns():
    rows = []
    types = ["email", "sms", "social_media", "display", "search"]
    channels = ["email", "facebook", "instagram", "google", "sms", "youtube"]
    
    campaign_themes = [
        "Summer Glow Up Campaign", "Velvet Matte Lipstick Launch", "Winter Hydration Rescue", 
        "Spring Skin Brightening Festival", "Holiday Glitz Eyeshadow Set", "Rose Gold Silk VIP", 
        "Luminous Foundation Launch", "Daily Skincare Rituals Promo", "Glow-Up Plumping Fest", 
        "Dewy Bronze Weekend Sale", "Flawless Primer Masterclass", "Anti-Aging Serum Pre-order", 
        "Vitamin C Serum Glow Boost", "Peach Lip Gloss Giveaway", "Velvet Blush Pop-up Event", 
        "Clear Skin Cleansing Challenge", "BFF Brush Set Discount", "Beauty Sponge Bundle", 
        "Matte Foundation Flash Sale", "Midnight Repair Face Mask Promo"
    ]
    
    for i in range(1, N_CAMPAIGNS + 1):
        start = fake.date_between(start_date="-1y", end_date="-1m")
        name = campaign_themes[i % len(campaign_themes)] if i <= len(campaign_themes) else f"{fake.color_name().title()} Collection Launch"
        rows.append({
            "campaign_id": i,
            "campaign_name": name[:80],
            "campaign_type": random.choice(types),
            "channel": random.choice(channels),
            "start_date": start.isoformat(),
            "end_date": (start + timedelta(days=random.randint(7, 60))).isoformat(),
            "budget": round(random.uniform(500, 50000), 2),
            "target_segment": random.choice(["All", "Premium", "Regular", "At Risk", "New"]),
            "status": random.choice(["active", "completed", "paused"]),
            "created_at": fake.date_time_between(start_date="-1y", end_date="-2m").isoformat()
        })
    return pd.DataFrame(rows)


def generate_campaign_responses(campaigns_df, customers_df):
    rows = []
    resp_id = 1
    customer_ids = customers_df["customer_id"].tolist()
    for _, camp in campaigns_df.iterrows():
        n_resp = random.randint(50, 300)
        for _ in range(n_resp):
            converted = random.random() < 0.12
            rows.append({
                "response_id": resp_id,
                "campaign_id": int(camp["campaign_id"]),
                "customer_id": random.choice(customer_ids),
                "response_type": random.choice(["click", "open", "purchase", "ignore"]),
                "response_date": fake.date_time_between(start_date="-1y", end_date="now").isoformat(),
                "converted": converted,
                "revenue_generated": round(random.uniform(20, 500), 2) if converted else 0
            })
            resp_id += 1
    return pd.DataFrame(rows)


def generate_website_sessions(customers_df):
    rows = []
    customer_ids = [None] * 200 + customers_df["customer_id"].tolist()
    for i in range(1, N_SESSIONS + 1):
        rows.append({
            "session_id": i,
            "customer_id": random.choice(customer_ids),
            "session_date": fake.date_time_between(start_date="-1y", end_date="now").isoformat(),
            "duration_seconds": random.randint(10, 3600),
            "pages_visited": random.randint(1, 20),
            "source": random.choice(["organic", "paid", "social", "email", "direct", "referral"]),
            "device_type": random.choice(["desktop", "mobile", "tablet"]),
            "bounce": random.random() < 0.35
        })
    return pd.DataFrame(rows)


def generate_customer_behavior(customers_df, products_df):
    rows = []
    customer_ids = customers_df["customer_id"].tolist()
    prod_ids = products_df["product_id"].tolist()
    behavior_types = ["view", "add_to_cart", "wishlist", "purchase", "review", "search"]
    for i in range(1, 5001):
        rows.append({
            "behavior_id": i,
            "customer_id": random.choice(customer_ids),
            "behavior_date": fake.date_time_between(start_date="-1y", end_date="now").isoformat(),
            "behavior_type": random.choice(behavior_types),
            "product_id": random.choice(prod_ids + [None]),
            "session_duration": random.randint(5, 900),
            "pages_viewed": random.randint(1, 15),
            "cart_value": round(random.uniform(0, 500), 2)
        })
    return pd.DataFrame(rows)


def main():
    print("Generating synthetic marketing data...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    categories = generate_categories()
    categories.to_csv(OUTPUT_DIR / "categories.csv", index=False)
    print(f"  categories: {len(categories)} rows")

    suppliers = generate_suppliers()
    suppliers.to_csv(OUTPUT_DIR / "suppliers.csv", index=False)
    print(f"  suppliers: {len(suppliers)} rows")

    products = generate_products(categories, suppliers)
    products.to_csv(OUTPUT_DIR / "products.csv", index=False)
    print(f"  products: {len(products)} rows")

    customers = generate_customers()
    customers.to_csv(OUTPUT_DIR / "customers.csv", index=False)
    print(f"  customers: {len(customers)} rows")

    transactions = generate_transactions(customers)
    transactions.to_csv(OUTPUT_DIR / "transactions.csv", index=False)
    print(f"  transactions: {len(transactions)} rows")

    order_items = generate_order_items(transactions, products)
    order_items.to_csv(OUTPUT_DIR / "order_items.csv", index=False)
    print(f"  order_items: {len(order_items)} rows")

    campaigns = generate_campaigns()
    campaigns.to_csv(OUTPUT_DIR / "campaigns.csv", index=False)
    print(f"  campaigns: {len(campaigns)} rows")

    responses = generate_campaign_responses(campaigns, customers)
    responses.to_csv(OUTPUT_DIR / "campaign_responses.csv", index=False)
    print(f"  campaign_responses: {len(responses)} rows")

    sessions = generate_website_sessions(customers)
    sessions.to_csv(OUTPUT_DIR / "website_sessions.csv", index=False)
    print(f"  website_sessions: {len(sessions)} rows")

    behavior = generate_customer_behavior(customers, products)
    behavior.to_csv(OUTPUT_DIR / "customer_behavior.csv", index=False)
    print(f"  customer_behavior: {len(behavior)} rows")

    print("\nAll data files generated successfully!")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
