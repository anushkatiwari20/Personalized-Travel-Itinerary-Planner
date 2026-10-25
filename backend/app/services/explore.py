"""Destination recommendation engine (Explore page data)."""

from typing import Optional

DESTINATIONS = [
    {"slug": "goa", "name": "Goa", "country": "India", "vibes": ["beach", "nightlife", "food"], "rating": 4.8, "reviews": 128000, "budget_level": 2, "avg_budget_per_day": 3000, "best_time": "November to February", "overview": "Sun-soaked beaches, Portuguese heritage, seafood shacks and a legendary nightlife scene.", "highlights": ["Baga Beach", "Fontainhas", "Dudhsagar Falls", "Anjuna Flea Market"]},
    {"slug": "jaipur", "name": "Jaipur", "country": "India", "vibes": ["city", "cultural", "food"], "rating": 4.7, "reviews": 96000, "budget_level": 2, "avg_budget_per_day": 2500, "best_time": "October to March", "overview": "The Pink City — forts, palaces, bazaars and royal Rajasthani cuisine.", "highlights": ["Amber Fort", "Hawa Mahal", "City Palace", "Johari Bazaar"]},
    {"slug": "leh-ladakh", "name": "Leh Ladakh", "country": "India", "vibes": ["mountain", "adventure"], "rating": 4.9, "reviews": 54000, "budget_level": 3, "avg_budget_per_day": 4500, "best_time": "June to September", "overview": "High-altitude desert with turquoise lakes, monasteries and epic road trips.", "highlights": ["Pangong Lake", "Nubra Valley", "Khardung La", "Thiksey Monastery"]},
    {"slug": "manali", "name": "Manali", "country": "India", "vibes": ["mountain", "adventure", "relaxed"], "rating": 4.7, "reviews": 150000, "budget_level": 2, "avg_budget_per_day": 3500, "best_time": "March to June", "overview": "A popular hill station in the Himalayas, offering snow-capped peaks, apple orchards, and a gateway to adventure sports.", "highlights": ["Rohtang Pass", "Solang Valley Ski", "Old Manali Cafes", "Hadimba Temple"]},
    {"slug": "mumbai", "name": "Mumbai", "country": "India", "vibes": ["city", "food", "nightlife"], "rating": 4.6, "reviews": 210000, "budget_level": 3, "avg_budget_per_day": 4000, "best_time": "November to February", "overview": "The city that never sleeps — colonial architecture, street food, Bollywood and the sea.", "highlights": ["Gateway of India", "Marine Drive", "Elephanta Caves", "Colaba Causeway"]},
    {"slug": "varanasi", "name": "Varanasi", "country": "India", "vibes": ["cultural", "relaxed"], "rating": 4.8, "reviews": 88000, "budget_level": 1, "avg_budget_per_day": 1800, "best_time": "October to March", "overview": "One of the oldest living cities — ghats, Ganga aarti, silk and spiritual energy.", "highlights": ["Dashashwamedh Ghat", "Kashi Vishwanath", "Sarnath", "Sunrise boat ride"]},
    {"slug": "udaipur", "name": "Udaipur", "country": "India", "vibes": ["cultural", "relaxed", "city"], "rating": 4.8, "reviews": 72000, "budget_level": 3, "avg_budget_per_day": 3800, "best_time": "September to March", "overview": "City of Lakes — palaces reflected in water, rooftop dinners and romantic sunsets.", "highlights": ["City Palace", "Lake Pichola", "Jag Mandir", "Sajjangarh"]},
    {"slug": "delhi", "name": "Delhi", "country": "India", "vibes": ["city", "cultural", "food"], "rating": 4.5, "reviews": 190000, "budget_level": 2, "avg_budget_per_day": 2800, "best_time": "October to March", "overview": "Layers of empires — Mughal monuments, Lutyens' avenues and Old Delhi street food.", "highlights": ["Red Fort", "Qutub Minar", "Humayun's Tomb", "Chandni Chowk"]},
    {"slug": "kuala-lumpur", "name": "Kuala Lumpur", "country": "Malaysia", "vibes": ["city", "food", "nightlife"], "rating": 4.6, "reviews": 160000, "budget_level": 2, "avg_budget_per_day": 5000, "best_time": "May to July", "overview": "Skyline icons, hawker food and a vibrant mix of Malay, Chinese and Indian culture.", "highlights": ["Petronas Towers", "Batu Caves", "Jalan Alor", "KLCC Park"]},
    {"slug": "kerala", "name": "Kerala Backwaters", "country": "India", "vibes": ["relaxed", "beach", "food"], "rating": 4.8, "reviews": 110000, "budget_level": 2, "avg_budget_per_day": 3200, "best_time": "September to March", "overview": "Houseboats drifting through palm-lined canals, Ayurveda and coastal cuisine.", "highlights": ["Alleppey Houseboat", "Kumarakom", "Munnar Tea Gardens", "Fort Kochi"]},
    {"slug": "gulmarg", "name": "Gulmarg", "country": "India", "vibes": ["mountain", "adventure"], "rating": 4.7, "reviews": 42000, "budget_level": 3, "avg_budget_per_day": 4200, "best_time": "December to March", "overview": "Asia's premier ski destination with one of the world's highest gondolas.", "highlights": ["Gulmarg Gondola", "Apharwat Peak", "Strawberry Valley", "Khilanmarg"]},
    {"slug": "hyderabad", "name": "Hyderabad", "country": "India", "vibes": ["city", "food", "cultural"], "rating": 4.6, "reviews": 98000, "budget_level": 2, "avg_budget_per_day": 2500, "best_time": "October to February", "overview": "Nizami heritage, biryani capital and a booming tech skyline.", "highlights": ["Charminar", "Golconda Fort", "Salar Jung Museum", "Chowmahalla Palace"]},
    {"slug": "rishikesh", "name": "Rishikesh", "country": "India", "vibes": ["adventure", "relaxed", "mountain"], "rating": 4.7, "reviews": 76000, "budget_level": 1, "avg_budget_per_day": 1800, "best_time": "September to April", "overview": "Yoga capital on the Ganga — rafting, cafes and evening aarti.", "highlights": ["Laxman Jhula", "River Rafting", "Beatles Ashram", "Triveni Ghat"]},
    {"slug": "bali", "name": "Bali", "country": "Indonesia", "vibes": ["beach", "relaxed", "cultural"], "rating": 4.8, "reviews": 240000, "budget_level": 2, "avg_budget_per_day": 4500, "best_time": "April to October", "overview": "Temples, rice terraces, surf beaches and wellness retreats.", "highlights": ["Ubud", "Uluwatu Temple", "Tegallalang", "Seminyak"]},
]

VIBES = ["all", "beach", "mountain", "city", "cultural", "food", "nightlife", "adventure", "relaxed"]


def _image(slug: str) -> str:
    return f"https://picsum.photos/seed/{slug}/640/420"


def list_destinations(vibe: Optional[str] = None, q: Optional[str] = None) -> list[dict]:
    rows = DESTINATIONS
    if vibe and vibe != "all":
        rows = [d for d in rows if vibe in d["vibes"]]
    if q:
        ql = q.lower()
        rows = [d for d in rows if ql in d["name"].lower() or ql in d["country"].lower()]
    return [{**d, "image_url": _image(d["slug"])} for d in rows]


def get_destination(slug: str) -> Optional[dict]:
    for d in DESTINATIONS:
        if d["slug"] == slug:
            return {**d, "image_url": _image(d["slug"])}
    return None
