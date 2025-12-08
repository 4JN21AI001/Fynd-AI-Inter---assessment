⭐ AI Feedback System — Yelp Review Rating & Insights
🚀 Fynd AI Internship — Take Home Assessment
This project implements a two-part AI system:
✔ Task-1: LLM-based Yelp review star rating prediction
✔ Task-2: Full-stack web system for real-time customer feedback using AI insights

📂 Project/
│── Task1.ipynb        # Notebook for Rating Prediction
│── main.py / backend  # API to store & fetch data from MongoDB
│── frontend/          # User & Admin Dashboards (HTML/CSS/JS)
│── reviews.json       # Old storage (now replaced by MongoDB)
│── requirements.txt
│── README.md

🎯 Task-1: Rating Prediction via Prompting
Predicts star rating (1–5) from review text using an LLM
Uses multiple prompting strategies:
Direct Prompting
Reasoning Prompting
Few-shot Prompting (Best Results)
Output structured JSON:
{
 "predicted_stars": 4,
 "explanation": "Brief reasoning for the assigned rating"
}

📊 Results Summary
Method	Accuracy	JSON Validity
Direct Prompting	0.5641	0.975
Reasoning Prompting	0.4872	0.195
Few-shot Prompting	⭐ 0.63	🟢 1.00

🧠 Task-2: Two-Dashboard AI Feedback System

🟢 User Dashboard (Customer Facing)
Users can:
✔ Select rating
✔ Write review
✔ Submit feedback
Data stored in MongoDB → AI generates summary & suggestions.

🔗 Live Site: https://celadon-creponne-4c9baa.netlify.app

🔵 Admin Dashboard (Business Facing)
Admins can:
✔ View all reviews live
✔ See AI-generated summaries
✔ Read recommended actions
✔ Monitor analytics: total reviews, average rating
✔ See rating distribution
🔗 Live Site: https://spontaneous-gelato-df8f3a.netlify.app

🧩 AI Features
Review summarization
Actionable recommendations
Structured and automated sentiment analysis
Supports continuous feedback collection

☁️ Deployment
Component	Host
Frontend UI	Netlify
Database	MongoDB Atlas
Backend API	Render / Local Tunnel (based on your setup)

⚙️ Tech Stack
Area	Tools Used
LLM	Mistral-7B-Instruct (via OpenRouter)
Frontend	HTML, CSS, JavaScript
Backend	Python API
Database	MongoDB Atlas
Notebook	Jupyter + Python

🔧 Setup Instructions (Local)
# Clone the repository
git clone <repo-url>
cd <repo-folder>

# Create & activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Mac
.\.venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Add OpenRouter API key in .env file
OPENROUTER_API_KEY=your_key_here

# Run backend
python main.py

📌 Future Enhancements
Authentication for Admin Dashboard
Better UI styling + responsive layout
Chart visualizations using Chart.js
Automated alerts on negative reviews
🏁 Conclusion
This project fulfills all deliverables:
✔ Notebook + evaluation
✔ AI-powered feedback system
✔ Live deployed dashboards
✔ Proper storage & visualization

🙌 Author
👤 Abhishek Badiger
AI & ML Engineer
LinkedIn: https://www.linkedin.com/in/abhishek-badiger-460814339/
