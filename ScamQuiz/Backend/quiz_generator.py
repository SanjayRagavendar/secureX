import os
import warnings
import json
import re
import random
from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import google.generativeai as genai
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = "AIzaSyBKV6w3wgRPMKmuXdxrDYkAhNkqgFA79lU"

# Flask App and SQLite Configuration
app = Flask(_name_)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fintech_quiz.db'
db = SQLAlchemy(app)

# Suppress future warnings
warnings.simplefilter("ignore", FutureWarning)

# Define the database models
class KnowledgeBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    embedding = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenario.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Scenario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    embedding = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Pattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    red_flags = db.Column(db.Text, nullable=False)  # Store as JSON string
    avoidance_tips = db.Column(db.Text, nullable=False)  # Store as JSON string
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

class FintechRAGQuizGenerator:
    def _init_(self, embedding_model="sentence-transformers/all-MiniLM-L6-v2"):
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        
        # Initialize the Google Gemini model
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            print("Successfully initialized Google Gemini API")
        except Exception as e:
            print(f"Error initializing Google Gemini API: {e}")
            raise RuntimeError("Unable to initialize Google Gemini model")

        # Load patterns from the database
        self.patterns = self._load_patterns_from_db()

        # Schedule daily updates at midnight
        scheduler.add_job(self._daily_update, 'cron', hour=0, minute=0)

    def _load_patterns_from_db(self) -> List[Dict[str, Any]]:
        """Load patterns from the database."""
        patterns = []
        with app.app_context():  # Ensure database access within application context
            for pattern in Pattern.query.all():
                patterns.append({
                    "title": pattern.title,
                    "description": pattern.description,
                    "red_flags": json.loads(pattern.red_flags),
                    "avoidance_tips": json.loads(pattern.avoidance_tips)
                })
        return patterns

    def _daily_update(self):
        """Update patterns daily at midnight."""
        print("Running daily update at midnight...")
        
        # Reload patterns from the database
        self.patterns = self._load_patterns_from_db()
        print(f"Loaded {len(self.patterns)} patterns from the database.")

    def load_sample_knowledge(self, sample_texts: Dict[str, str]):
        with app.app_context():  # Ensure database access within application context
            for category, text in sample_texts.items():
                texts = self.text_splitter.split_text(text)
                for chunk in texts:
                    embedding = self.embeddings.embed_query(chunk)
                    existing = KnowledgeBase.query.filter_by(content=chunk).first()
                    if not existing:
                        new_entry = KnowledgeBase(category=category, content=chunk, embedding=json.dumps(embedding))
                        db.session.add(new_entry)
            db.session.commit()
            print(f"Loaded knowledge from {len(sample_texts)} documents into the database.")

    def add_user_scenario(self, title: str, content: str) -> int:
        with app.app_context():  # Ensure database access within application context
            embedding = self.embeddings.embed_query(content)
            new_scenario = Scenario(title=title, content=content, embedding=json.dumps(embedding))
            db.session.add(new_scenario)
            db.session.commit()
            return new_scenario.id

    def _find_relevant_context(self, query_text: str, k: int = 3) -> str:
        with app.app_context():  # Ensure database access within application context
            query_embedding = self.embeddings.embed_query(query_text)
            relevant_docs = KnowledgeBase.query.limit(k).all()
            return "\n\n".join([doc.content for doc in relevant_docs])

    def _call_llm_with_google(self, prompt: str) -> str:
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]

        try:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt, safety_settings=safety_settings)
            return response.text if hasattr(response, 'text') else "Error: No valid response received."
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return "Error: Failed to call Gemini API."

    def generate_quiz_questions_from_scenarios(self, num_questions: int = 10) -> List[Dict[str, Any]]:
        all_questions = []
        with app.app_context():  # Ensure database access within application context
            scenarios = Scenario.query.all()
            for scenario in scenarios:
                relevant_context = self._find_relevant_context(scenario.content, k=random.randint(3, 5))
                relevant_context += f"\n\nUser scenario: {scenario.content}"

                prompt = f"""
                You are a financial literacy expert creating educational content about financial scams and fraud.
                
                Based on the following scenario, generate {num_questions} multiple-choice quiz questions.
                
                SCENARIO:
                {scenario.content}
                
                INSTRUCTIONS:
                Generate exactly {num_questions} quiz questions in JSON format.
                """

                try:
                    raw_response = self._call_llm_with_google(prompt)
                    questions = self._parse_questions(raw_response)
                    for question in questions:
                        question['scenario_id'] = scenario.id
                    all_questions.extend(questions)
                except Exception as e:
                    print(f"Failed to generate questions for scenario: {e}")
                    all_questions.extend(self._generate_fallback_questions())
        return all_questions

    def _parse_questions(self, raw_response: str) -> List[Dict[str, Any]]:
        try:
            json_match = re.search(r'\[.*\]', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"Error parsing questions JSON: {e}")
        return []

    def _generate_fallback_questions(self) -> List[Dict[str, Any]]:
        return [{
            "question": "What is a common red flag of a phishing attempt?",
            "options": [
                "A) Requests for personal information",
                "B) Professional email address",
                "C) Proper spelling and grammar",
                "D) Clear company logo"
            ],
            "correct_answer": "A",
            "explanation": "Legitimate organizations typically don't ask for personal information via email."
        }]

    def generate_scenarios_for_pattern(self, pattern_id: int) -> List[Dict[str, Any]]:
        """Generate multiple unique scenarios for a specific pattern ID."""
        with app.app_context():
            pattern = Pattern.query.get(pattern_id)
            if not pattern:
                raise ValueError(f"Pattern with ID {pattern_id} not found")
            
            pattern_data = {
                "title": pattern.title,
                "description": pattern.description,
                "red_flags": json.loads(pattern.red_flags),
                "avoidance_tips": json.loads(pattern.avoidance_tips)
            }
            
            num_scenarios = random.randint(3, 5)
            scenarios = []
            previous_scenarios = []  # Track previous scenarios to ensure uniqueness
            
            variations = [
                "social media-based variation",
                "email-based variation",
                "phone call-based variation",
                "in-person variation",
                "messaging app-based variation"
            ]
            
            for i in range(num_scenarios):
                variation = variations[i % len(variations)]
                previous_content = "\n\nPrevious scenarios (DO NOT REPEAT THESE):\n" + \
                                 "\n".join([f"- {s['content']}" for s in previous_scenarios]) if previous_scenarios else ""
                
                prompt = f"""
                You are a financial literacy expert creating educational content to help people recognize and avoid financial scams and fraud.

                Create a {variation} of this scam pattern that is COMPLETELY DIFFERENT from any previous scenarios.

                PATTERN:
                Title: {pattern_data["title"]}
                Description: {pattern_data["description"]}
                Red Flags: {", ".join(pattern_data["red_flags"])}
                Avoidance Tips: {", ".join(pattern_data["avoidance_tips"])}
                {previous_content}

                INSTRUCTIONS:
                - Create a detailed scenario focusing on {variation}
                - Include specific red flags and avoidance tips relevant to this variation
                - Make sure the scenario is completely different from the previous ones
                - Return ONLY the scenario in this JSON format (no explanations):
                {{
                    "title": "Specific and unique title for this variation",
                    "content": "Detailed unique scenario description",
                    "example_red_flag": "An example conversation or note that imitates the specific red flag",
                }}
                """
                
                max_attempts = 3
                for attempt in range(max_attempts):
                    try:
                        raw_response = self._call_llm_with_google(prompt)
                        scenario = json.loads(raw_response)
                        
                        # Check if this scenario is too similar to previous ones
                        if previous_scenarios:
                            similarity_scores = [
                                self._calculate_similarity(scenario['content'], prev['content'])
                                for prev in previous_scenarios
                            ]
                            if max(similarity_scores) > 0.8:  # Threshold for similarity
                                if attempt == max_attempts - 1:
                                    raise ValueError("Failed to generate unique scenario")
                                continue
                        
                        scenario_id = self.add_user_scenario(scenario["title"], scenario["content"])
                        scenario_with_metadata = {**scenario, "id": scenario_id, "pattern_id": pattern_id}
                        scenarios.append(scenario_with_metadata)
                        previous_scenarios.append(scenario)
                        break
                    except Exception as e:
                        if attempt == max_attempts - 1:
                            print(f"Failed all attempts to generate unique scenario {i+1}: {e}")
                            fallback_scenario = {
                                "title": f"{pattern_data['title']} - {variation}",
                                "content": f"A unique {variation} of {pattern_data['title']}. "
                                         f"This variant specifically focuses on {random.choice(pattern_data['red_flags'])}. "
                                         f"Key prevention: {random.choice(pattern_data['avoidance_tips'])}",
                                "pattern_id": pattern_id
                            }
                            scenario_id = self.add_user_scenario(fallback_scenario["title"], fallback_scenario["content"])
                            scenarios.append({**fallback_scenario, "id": scenario_id})
            
            return scenarios

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using their embeddings."""
        try:
            embedding1 = self.embeddings.embed_query(text1)
            embedding2 = self.embeddings.embed_query(text2)
            
            # Calculate cosine similarity
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            norm1 = sum(a * a for a in embedding1) ** 0.5
            norm2 = sum(b * b for b in embedding2) ** 0.5
            return dot_product / (norm1 * norm2)
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0

# Initialize the FintechRAGQuizGenerator within the application context
with app.app_context():
    db.create_all()  # Ensure all tables are created
    fintech_quiz_generator = FintechRAGQuizGenerator()

@app.route("/load_knowledge", methods=["POST"])
def load_knowledge():
    sample_texts = request.get_json()
    fintech_quiz_generator.load_sample_knowledge(sample_texts)
    return {"message": "Knowledge loaded successfully."}, 200

@app.route("/generate_quiz_questions", methods=["GET"])
def generate_quiz_questions():
    num_questions = request.args.get("num_questions", 10, type=int)
    quiz_questions = fintech_quiz_generator.generate_quiz_questions_from_scenarios(num_questions)
    return {"quiz_questions": quiz_questions}, 200

@app.route("/generate_scenarios/<int:pattern_id>", methods=["GET"])
def generate_scenarios_for_pattern(pattern_id):
    try:
        scenarios = fintech_quiz_generator.generate_scenarios_for_pattern(pattern_id)
        return jsonify({"scenarios": scenarios}), 200
    except ValueError as e:
        return {"error": str(e)}, 404
    except Exception as e:
        return {"error": f"Failed to generate scenarios: {str(e)}"}, 500

@app.route("/generate_quiz_job", methods=["GET"])
def generate_quiz_job():
    all_questions = []
    num_questions = 2

    with app.app_context():
        scenarios = Scenario.query.all()
        print(scenarios)
        max_loop = 5
        for scenario in scenarios:
            if max_loop >= 0:
                max_loop -= 1
            elif max_loop <= 0:
                break
            relevant_context = fintech_quiz_generator._find_relevant_context(scenario.content, k=random.randint(3, 5))
            relevant_context += f"\n\nUser scenario: {scenario.content}"

            prompt = f"""
            You are a financial literacy expert creating educational content about financial scams and fraud.
            
            Based on the following scenario, generate {num_questions} multiple-choice quiz questions.
            Each question MUST have these fields: question, options (array), correct_answer (A, B, C, or D), and explanation.
            
            SCENARIO:
            {scenario.content}
            
            INSTRUCTIONS:
            Generate exactly {num_questions} quiz questions in this JSON format:
            [
                {{
                    "question": "Question text here",
                    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                    "correct_answer": "A",
                    "explanation": "Explanation here"
                }}
            ]
            """

            try:
                raw_response = fintech_quiz_generator._call_llm_with_google(prompt)
                #print(raw_response)
                questions = fintech_quiz_generator._parse_questions(raw_response)
                for question in questions:
                    # Validate question structure
                    print("Hello")
                    if not all(key in question for key in ["question", "options", "correct_answer", "explanation"]):
                        continue
                    
                    # Ensure correct_answer is valid
                    if question["correct_answer"] not in ["A", "B", "C", "D"]:
                        continue
                    
                    question['scenario_id'] = scenario.id
                    
                    # Add validated question to database
                    new_question = QuizQuestion(
                        question=question["question"],
                        options=json.dumps(question.get("options", [])),
                        correct_answer=question["correct_answer"],
                        explanation=question.get("explanation", ""),
                        scenario_id=question["scenario_id"]
                    )
                    db.session.add(new_question)
                    all_questions.append(question)
                    
            except Exception as e:
                print(f"Failed to generate questions for scenario: {e}")
                all_questions.extend(fintech_quiz_generator._generate_fallback_questions())

        try:
            db.session.commit()
            print("committed to db successfuly")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to database: {e}")
            return jsonify({"error": "Failed to save questions"}), 500

    return jsonify({"quiz_questions": all_questions}), 200

if _name_ == "_main_":
    with app.app_context():
        db.create_all()
        # Check if patterns exist, if not initialize them
        if Pattern.query.count() == 0:
            from initial_patterns import initialize_patterns
            initialize_patterns()
        #print("Running quiz job")
        #generate_quiz_job()
    app.run(debug=True)