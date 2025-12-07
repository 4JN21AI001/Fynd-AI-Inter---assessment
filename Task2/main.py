import os
import json
from datetime import datetime
from typing import List

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient

from dotenv import load_dotenv
load_dotenv()

# ------------------------------
# MongoDB SETUP
# ------------------------------
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("❌ MONGO_URI missing in Render environment variables")

client = AsyncIOMotorClient(MONGO_URI)
db = client["fynd_reviews"]  # <<✔ Correct database
reviews_collection = db["reviews"]  # collection for storing reviews


# ------------------------------
# OpenRouter API
# ------------------------------
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("⚠️ Warning: OPENROUTER_API_KEY not set")

app = FastAPI()

# Allow Frontends (Netlify apps)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Pydantic Models
# ------------------------------
class ReviewIn(BaseModel):
    rating: int
    review_text: str

class ReviewOut(BaseModel):
    id: str
    timestamp: str
    rating: int
    review_text: str
    ai_summary: str
    ai_actions: List[str]
    ai_user_response: str


# ------------------------------
# LLM AI Analysis
# ------------------------------
async def call_llm_for_feedback(rating: int, review_text: str) -> dict:
    system_prompt = """
    You are an AI assistant analyzing customer reviews.
    Generate:
    - Short summary
    - 2-4 recommended actions
    - Friendly user response
    """

    user_prompt = f"Rating: {rating}\nReview: {review_text}"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        data = response.json()

    try:
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except:
        return {
            "summary": "Feedback received.",
            "actions": ["Team will review internally."],
            "user_response": "Thanks for your feedback!"
        }


# ------------------------------
# API ROUTES
# ------------------------------
@app.post("/api/reviews", response_model=ReviewOut)
async def create_review(review: ReviewIn):
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")

    feedback = await call_llm_for_feedback(review.rating, review.review_text)

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "rating": review.rating,
        "review_text": review.review_text,
        "ai_summary": feedback["summary"],
        "ai_actions": feedback["actions"],
        "ai_user_response": feedback["user_response"],
    }

    result = await reviews_collection.insert_one(entry)
    entry["id"] = str(result.inserted_id)
    return entry


@app.get("/api/reviews", response_model=List[ReviewOut])
async def get_reviews():
    cursor = reviews_collection.find({})
    reviews = await cursor.to_list(length=None)

    for r in reviews:
        r["id"] = str(r["_id"])
        del r["_id"]
    return reviews


@app.get("/api/analytics")
async def analytics():
    reviews = await reviews_collection.find({}).to_list(None)

    if not reviews:
        return {"total": 0, "average_rating": 0, "rating_counts": {}}

    total = len(reviews)
    avg = round(sum(r["rating"] for r in reviews) / total, 2)

    counts = {}
    for r in reviews:
        counts[r["rating"]] = counts.get(r["rating"], 0) + 1

    return {
        "total": total,
        "average_rating": avg,
        "rating_counts": counts
    }


@app.get("/")
def root():
    return {"msg": "Backend Running with MongoDB ✔"}
