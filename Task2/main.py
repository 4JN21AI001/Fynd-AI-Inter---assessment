import os
import json
from datetime import datetime
from typing import List

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()


# --------------------------------
# Load API Key (Add to Render Env Variables)
# --------------------------------
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("⚠️ Warning: OPENROUTER_API_KEY not set")

DATA_FILE = "reviews.json"

app = FastAPI()

# Allow access from User & Admin dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------
# Models
# --------------------------------
class ReviewIn(BaseModel):
    rating: int
    review_text: str

class ReviewOut(BaseModel):
    id: int
    timestamp: str
    rating: int
    review_text: str
    ai_summary: str
    ai_actions: List[str]
    ai_user_response: str

# --------------------------------
# Helpers: Save + Load
# --------------------------------
def load_reviews():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_reviews(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --------------------------------
# LLM AI Function (Summarization + Actions + Response)
# --------------------------------
async def call_llm_for_feedback(rating: int, review_text: str) -> dict:
    system_prompt = """
You are an AI assistant helping a business analyze customer reviews.

Given a star rating (1-5) and review text:

1️⃣ Create a neutral summary of the review
2️⃣ Suggest 2-4 recommended business actions
3️⃣ Write a friendly user response

Return STRICT JSON ONLY:
{
 "summary": "...",
 "actions": ["...", "..."],
 "user_response": "..."
}
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
    except Exception as e:
        print("⚠️ JSON parsing failed:", content)
        return {
            "summary": "We received your review.",
            "actions": ["The team will manually review this feedback."],
            "user_response": "Thanks for sharing! We will improve based on your feedback."
        }

# --------------------------------
# API Routes
# --------------------------------

@app.post("/api/reviews", response_model=ReviewOut)
async def create_review(review: ReviewIn):
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    feedback = await call_llm_for_feedback(review.rating, review.review_text)

    reviews = load_reviews()
    new_id = reviews[-1]["id"] + 1 if reviews else 1

    entry = {
        "id": new_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "rating": review.rating,
        "review_text": review.review_text,
        "ai_summary": feedback["summary"],
        "ai_actions": feedback["actions"],
        "ai_user_response": feedback["user_response"],
    }

    reviews.append(entry)
    save_reviews(reviews)

    return entry


@app.get("/api/reviews", response_model=List[ReviewOut])
def get_reviews():
    return load_reviews()


@app.get("/api/analytics")
def analytics():
    reviews = load_reviews()
    if not reviews:
        return {"total": 0, "average_rating": 0, "rating_counts": {}}

    total = len(reviews)
    avg_rating = round(sum(r["rating"] for r in reviews) / total, 2)

    rating_counts = {}
    for r in reviews:
        rating_counts[r["rating"]] = rating_counts.get(r["rating"], 0) + 1

    return {
        "total": total,
        "average_rating": avg_rating,
        "rating_counts": rating_counts
    }

# --------------------------------
# Local Testing Command
# --------------------------------
# uvicorn main:app --reload --port 8000
