from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
from werkzeug.utils import secure_filename
from datetime import datetime
import csv
import random
import logging
import sys
import argparse

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    },
    r"/trivia/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

class MyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.print_help(sys.stderr)
        self.exit(2, f'{self.prog}: error: {message}\n')

class ChatBot:
    def __init__(self):
        self.questions = {}
        self.trivia_questions = []
        self.trivia_active = False
        self.trivia_score = 0
        self.trivia_total = 0
        self.current_trivia_question = None
        self.trivia_questions_remaining = []
        self.DEBUG = False
        
        # Load existing data
        self.load_questions_from_csv("questions.csv")
        self.load_trivia_from_csv("trivia.csv")
        
        # Create default trivia if none exists
        if not self.trivia_questions:
            self.create_default_trivia()
            self.save_trivia_to_csv("trivia.csv")
    
    def setup_logging(self, enable_logging, log_level):
        if enable_logging:
            logging.basicConfig(
                filename='app.log',
                level=getattr(logging, log_level),
                format='%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                encoding='utf-8',
                force=True
            )
    
    def get_current_time(self):
        return datetime.now().strftime("%H:%M:%S")
    
    def get_current_date(self):
        return datetime.now().strftime("%Y-%m-%d")
    
    def save_questions_to_csv(self, filename="questions.csv"):
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['question', 'answer1', 'answer2', 'answer3', 'answer4'])
                for question, answers in self.questions.items():
                    row = [question] + list(answers)[:4] + [''] * (4 - len(answers))
                    writer.writerow(row)
            if self.DEBUG:
                print(f"DEBUG: Saved {len(self.questions)} questions to '{filename}'")
            return True
        except Exception as e:
            logging.error(f"Failed to save questions to '{filename}': {str(e)}")
            if self.DEBUG:
                print(f"Error: Failed to save questions to '{filename}': {str(e)}")
            return False
    
    def save_trivia_to_csv(self, filename="trivia.csv"):
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer'])
                for trivia in self.trivia_questions:
                    row = [
                        trivia['question'],
                        trivia['options'][0],
                        trivia['options'][1],
                        trivia['options'][2],
                        trivia['options'][3],
                        trivia['correct_answer']
                    ]
                    writer.writerow(row)
            if self.DEBUG:
                print(f"DEBUG: Saved {len(self.trivia_questions)} trivia questions to '{filename}'")
            return True
        except Exception as e:
            logging.error(f"Failed to save trivia questions to '{filename}': {str(e)}")
            if self.DEBUG:
                print(f"Error: Failed to save trivia questions to '{filename}': {str(e)}")
            return False
    
    def create_default_trivia(self):
        default_trivia = [
            {
                'question': 'What is typically the main purpose of a university library?',
                'options': ['Cafeteria services', 'Academic research and study', 'Sports activities',
                            'Administrative meetings'],
                'correct_answer': 'Academic research and study'
            },
            {
                'question': 'Which university service helps students with career planning?',
                'options': ['IT Help Desk', 'Career Services Center', 'Maintenance Department', 'Security Office'],
                'correct_answer': 'Career Services Center'
            },
            {
                'question': 'What does a university registrar typically handle?',
                'options': ['Food services', 'Student records and enrollment', 'Campus security', 'Library books'],
                'correct_answer': 'Student records and enrollment'
            },
            {
                'question': 'Which service usually provides mental health support for students?',
                'options': ['Counseling Center', 'Finance Office', 'Alumni Relations', 'Parking Services'],
                'correct_answer': 'Counseling Center'
            },
            {
                'question': 'What is the primary function of a university admissions office?',
                'options': ['Managing student housing', 'Processing applications and enrollment',
                            'Organizing sports events', 'Maintaining buildings'],
                'correct_answer': 'Processing applications and enrollment'
            },
            {
                'question': 'Which university service typically handles student financial aid?',
                'options': ['Academic Advising', 'Financial Aid Office', 'Campus Store', 'Transportation Services'],
                'correct_answer': 'Financial Aid Office'
            },
            {
                'question': 'What does IT Services at a university usually provide?',
                'options': ['Food delivery', 'Technology support and resources', 'Athletic training', 'Legal advice'],
                'correct_answer': 'Technology support and resources'
            },
            {
                'question': 'Which office typically coordinates student organizations and activities?',
                'options': ['Student Life Office', 'Accounting Department', 'Facilities Management', 'Research Office'],
                'correct_answer': 'Student Life Office'
            },
            {
                'question': 'What service helps international students with visa and cultural adaptation?',
                'options': ['Campus Safety', 'International Student Services', 'Dining Services', 'Bookstore'],
                'correct_answer': 'International Student Services'
            },
            {
                'question': 'Which university service typically manages dormitories and residence halls?',
                'options': ['Academic Affairs', 'Housing and Residential Life', 'Public Relations', 'Alumni Office'],
                'correct_answer': 'Housing and Residential Life'
            },
            {
                'question': 'What does a university health center primarily provide?',
                'options': ['Academic tutoring', 'Medical care for students', 'Career counseling', 'Sports equipment'],
                'correct_answer': 'Medical care for students'
            },
            {
                'question': 'Which service helps students choose courses and plan their academic path?',
                'options': ['Campus Security', 'Academic Advising', 'Food Services', 'Transportation'],
                'correct_answer': 'Academic Advising'
            },
            {
                'question': 'What is the main function of a university disability services office?',
                'options': ['Managing finances', 'Providing accessibility accommodations', 'Organizing events',
                            'Maintaining equipment'],
                'correct_answer': 'Providing accessibility accommodations'
            },
            {
                'question': 'Which university service typically handles parking permits and regulations?',
                'options': ['Library Services', 'Parking and Transportation', 'Student Government', 'Research Division'],
                'correct_answer': 'Parking and Transportation'
            },
            {
                'question': 'What does a university writing center usually offer?',
                'options': ['Computer repair', 'Writing assistance and tutoring', 'Athletic coaching', 'Event planning'],
                'correct_answer': 'Writing assistance and tutoring'
            }
        ]
        self.trivia_questions.extend(default_trivia)
        logging.info(f"Created {len(default_trivia)} default trivia questions")
    
    def load_trivia_from_csv(self, filename="trivia.csv"):
        if os.path.exists(filename):
            try:
                with open(filename, mode='r', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    header = reader.fieldnames
                    required_headers = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
                    if not header or not all(h in header for h in required_headers):
                        logging.warning(f"Invalid trivia CSV header: {header} in file: {filename}")
                        if self.DEBUG:
                            print(f"DEBUG: Invalid trivia CSV header on load: {header}")
                        return
                    
                    count = 0
                    for row in reader:
                        question = row['question'].strip()
                        options = [
                            row['option_a'].strip(),
                            row['option_b'].strip(),
                            row['option_c'].strip(),
                            row['option_d'].strip()
                        ]
                        correct_answer = row['correct_answer'].strip()
                        if question and all(options) and correct_answer:
                            self.trivia_questions.append({
                                'question': question,
                                'options': options,
                                'correct_answer': correct_answer
                            })
                            count += 1
                    if self.DEBUG:
                        print(f"DEBUG: Loaded {count} trivia questions from '{filename}' on startup")
            except Exception as e:
                logging.error(f"Error loading trivia questions from {filename}: {e}")
                if self.DEBUG:
                    print(f"DEBUG: Error loading trivia questions from {filename}: {e}")
        elif self.DEBUG:
            print(f"DEBUG: No trivia.csv found at {filename} on startup")
    
    def load_questions_from_csv(self, filename="questions.csv"):
        if os.path.exists(filename):
            try:
                with open(filename, mode='r', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    header = reader.fieldnames
                    if not header or 'question' not in header or 'answer1' not in header:
                        logging.warning(f"Invalid CSV header: {header} in file: {filename}")
                        if self.DEBUG:
                            print(f"DEBUG: Invalid CSV header on load: {header}")
                        return
                    
                    count = 0
                    for row in reader:
                        q = row['question'].strip().lower()
                        answers = []
                        for k in ['answer1', 'answer2', 'answer3', 'answer4']:
                            if k in row and row[k].strip():
                                answers.append(row[k].strip())
                        if q and answers:
                            self.questions[q] = answers
                            count += 1
                    if self.DEBUG:
                        print(f"DEBUG: Loaded {count} questions from '{filename}' on startup")
            except Exception as e:
                logging.error(f"Error loading questions from {filename}: {e}")
                if self.DEBUG:
                    print(f"DEBUG: Error loading questions from {filename}: {e}")
        elif self.DEBUG:
            print(f"DEBUG: No questions.csv found at {filename} on startup")
    
    def start_trivia_game(self, num_questions=10):
        if len(self.trivia_questions) < num_questions:
            if self.DEBUG:
                print(f"Error: Not enough trivia questions available. Need {num_questions}, have {len(self.trivia_questions)}")
            return False
        
        self.trivia_active = True
        self.trivia_score = 0
        self.trivia_total = 0
        self.trivia_questions_remaining = random.sample(self.trivia_questions, num_questions)
        
        if self.DEBUG:
            print("🎯 TRIVIA GAME ACTIVATED! 🎯")
            print(f"Get ready for {num_questions} multiple choice questions about university services!")
        
        return True
    
    def ask_next_trivia_question(self):
        if not self.trivia_questions_remaining:
            self.end_trivia_game()
            return None
        
        self.current_trivia_question = self.trivia_questions_remaining.pop(0)
        return {
            'question': self.current_trivia_question['question'],
            'options': self.current_trivia_question['options'],
            'question_number': (self.trivia_total + 1),
            'total_questions': (self.trivia_total + len(self.trivia_questions_remaining) + 1)
        }
    
    def process_trivia_answer(self, user_input):
        if not self.trivia_active or not self.current_trivia_question:
            return "no_active_game"
        
        user_answer = user_input.strip().upper()
        option_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        
        if user_answer not in option_map:
            return "invalid"
        
        selected_index = option_map[user_answer]
        correct_index = self.current_trivia_question['options'].index(
            self.current_trivia_question['correct_answer']
        )
        
        self.trivia_total += 1
        result = "incorrect"
        
        if selected_index == correct_index:
            self.trivia_score += 1
            result = "correct"
        
        correct_answer = self.current_trivia_question['correct_answer']
        self.current_trivia_question = None
        
        return {
            'result': result,
            'correct_answer': correct_answer,
            'score': self.trivia_score,
            'total': self.trivia_total
        }
    
    def end_trivia_game(self):
        if not self.trivia_active:
            return None
        
        self.trivia_active = False
        percentage = (self.trivia_score / self.trivia_total * 100) if self.trivia_total > 0 else 0
        
        result = {
            "score": self.trivia_score,
            "total": self.trivia_total,
            "percentage": percentage,
            "message": self._get_trivia_result_message(percentage)
        }
        
        # Reset game state
        self.trivia_score = 0
        self.trivia_total = 0
        self.current_trivia_question = None
        self.trivia_questions_remaining = []
        
        return result
    
    def _get_trivia_result_message(self, percentage):
        if percentage >= 90:
            return "🌟 Excellent! You're a university services expert!"
        elif percentage >= 70:
            return "👍 Great job! You know your way around university services!"
        elif percentage >= 50:
            return "👌 Not bad! You have good knowledge of university services!"
        else:
            return "📚 Keep learning about university services - there's always more to discover!"
    
    def add_trivia_question(self, question, option_a, option_b, option_c, option_d, correct_answer):
        if not all([question, option_a, option_b, option_c, option_d, correct_answer]):
            return False

        if correct_answer not in [option_a, option_b, option_c, option_d]:
            return False

        new_trivia = {
            'question': question.strip(),
            'options': [option_a.strip(), option_b.strip(), option_c.strip(), option_d.strip()],
            'correct_answer': correct_answer.strip()
        }

        self.trivia_questions.append(new_trivia)
        self.save_trivia_to_csv("trivia.csv")
        return True
    
    def add_question(self, question, answer):
        q = question.strip().lower()
        a = answer.strip()
        if not q or not a:
            return False
        
        if q in self.questions:
            if a not in self.questions[q]:
                self.questions[q].append(a)
        else:
            self.questions[q] = [a]
        
        self.save_questions_to_csv()
        return True
    
    def remove_question(self, question):
        q = question.strip().lower()
        if q in self.questions:
            del self.questions[q]
            self.save_questions_to_csv("questions.csv")
            return True
        return False
    
    def list_questions(self):
        return list(self.questions.keys())
    
    def list_trivia_questions(self):
        return [q['question'] for q in self.trivia_questions]
    
    def import_questions_from_csv(self, filename):
        if not os.path.exists(filename):
            logging.error(f"Import failed: File not found: {filename}")
            return False
        
        try:
            with open(filename, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                if not reader.fieldnames or 'question' not in reader.fieldnames or 'answer1' not in reader.fieldnames:
                    logging.warning(f"Import failed for {filename}: Missing required headers")
                    return False
                
                imported = 0
                for row in reader:
                    q = row['question'].strip().lower()
                    answers = [row[key].strip() for key in ['answer1', 'answer2', 'answer3', 'answer4'] 
                             if row.get(key) and row[key].strip()]
                    if q and answers:
                        self.questions[q] = answers
                        imported += 1
                
                logging.info(f"Successfully imported {imported} questions from {filename}")
                self.save_questions_to_csv("questions.csv")
                return True
        except Exception as e:
            logging.error(f"Failed to import questions from {filename}: {str(e)}")
            return False
    
    def answer_question(self, query):
        q = query.strip().lower()
        
        # Handle time/date questions
        if q in ("what is the time?", "what's the time?", "time?"):
            return {
                "response": f"The current time is {self.get_current_time()}.",
                "type": "time"
            }
        elif q in ("what is the date?", "what's the date?", "date?"):
            return {
                "response": f"Today's date is {self.get_current_date()}.",
                "type": "date"
            }
        
        # Handle trivia commands
        if q == "trivia":
            if self.trivia_active:
                result = self.end_trivia_game()
                return {
                    "response": f"Trivia game ended. Final score: {result['score']}/{result['total']}",
                    "trivia_result": result,
                    "type": "trivia_end"
                }
            else:
                if self.start_trivia_game(5):
                    next_question = self.ask_next_trivia_question()
                    return {
                        "response": "Trivia game started! Here's your first question:",
                        "trivia_question": next_question,
                        "type": "trivia_start"
                    }
                return {
                    "response": "Not enough trivia questions available to start the game.",
                    "type": "error"
                }
        
        # If trivia is active, treat all input as potential trivia answers
        if self.trivia_active:
            result = self.process_trivia_answer(query)
            if result == "no_active_game":
                return {
                    "response": "No active trivia game. Type 'trivia' to start one.",
                    "type": "error"
                }
            elif result == "invalid":
                return {
                    "response": "Please answer with A, B, C, or D.",
                    "type": "trivia_invalid"
                }
            else:
                response = {
                    "response": "✅ Correct!" if result['result'] == "correct" else "❌ Incorrect!",
                    "type": "trivia_answer",
                    "result": result['result'],
                    "correct_answer": result['correct_answer'],
                    "score": result['score'],
                    "total": result['total']
                }
                
                # Get next question or end game
                if len(self.trivia_questions_remaining) > 0:
                    next_question = self.ask_next_trivia_question()
                    response["next_question"] = next_question
                else:
                    final_result = self.end_trivia_game()
                    response["trivia_result"] = final_result
                    response["type"] = "trivia_final_result"
                
                return response
        
        # Answer regular questions
        if q in self.questions and self.questions[q]:
            return {
                "response": random.choice(self.questions[q]),
                "type": "answer"
            }
        
        return {
            "response": "I don't have an answer for that question. Try 'trivia' to play the trivia game!",
            "type": "unknown"
        }
    
    def interactive_mode(self):
        print("🤖 Chatbot Interactive Mode")
        print("Type your questions, 'trivia' to start trivia game, or 'quit' to exit.\n")

        while True:
            try:
                if self.trivia_active and self.current_trivia_question:
                    user_input = input("")  # No prompt as trivia shows its own
                else:
                    user_input = input("You: ")

                if user_input.strip().lower() in ['quit', 'exit', 'bye']:
                    if self.trivia_active:
                        print("Ending trivia game...")
                        self.end_trivia_game()
                    print("Goodbye!")
                    break

                result = self.answer_question(user_input)
                print(f"Bot: {result['response']}")
                
                if result['type'] == "unknown" and not self.trivia_active:
                    print("Bot: Try 'trivia' to play the trivia game!")

            except KeyboardInterrupt:
                if self.trivia_active:
                    print("\nEnding trivia game...")
                    self.end_trivia_game()
                print("\nGoodbye!")
                break
            except EOFError:
                if self.trivia_active:
                    print("\nEnding trivia game...")
                    self.end_trivia_game()
                print("\nGoodbye!")
                break

# Initialize chatbot
chatbot = ChatBot()

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/ask", methods=["POST"])
def ask_question():
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Invalid request format"}), 400
            
        response = chatbot.answer_question(data["question"])
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/question/add", methods=["POST"])
def add_question():
    try:
        data = request.get_json()
        if not data or 'question' not in data or 'answer' not in data:
            return jsonify({"error": "Invalid request format"}), 400
            
        success = chatbot.add_question(data["question"], data["answer"])
        if success:
            return jsonify({"status": "success", "message": "Question added successfully"})
        return jsonify({"error": "Failed to add question"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/question/remove", methods=["POST"])
def remove_question():
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Invalid request format"}), 400
            
        success = chatbot.remove_question(data["question"])
        if success:
            return jsonify({"status": "success", "message": "Question removed successfully"})
        return jsonify({"error": "Question not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/question/list", methods=["GET"])
def list_questions():
    try:
        questions = chatbot.list_questions()
        return jsonify({"questions": questions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/trivia/list", methods=["GET"])
def list_trivia_questions():
    try:
        questions = chatbot.list_trivia_questions()
        return jsonify({"trivia_questions": questions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/trivia/start", methods=["POST"])
def start_trivia():
    try:
        data = request.get_json()
        num_questions = min(int(data.get("num_questions", 5)), 20)  # Default to 5, max 20
        
        if chatbot.trivia_active:
            chatbot.end_trivia_game()
            
        success = chatbot.start_trivia_game(num_questions)
        if not success:
            return jsonify({
                "error": "Failed to start trivia",
                "details": "Not enough questions available"
            }), 400
            
        first_question = chatbot.ask_next_trivia_question()
        return jsonify({
            "status": "started",
            "current_question": first_question,
            "score": chatbot.trivia_score,
            "total": num_questions,
            "game_active": chatbot.trivia_active
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/trivia/answer", methods=["POST"])
def answer_trivia():
    try:
        data = request.get_json()
        if not data or 'answer' not in data:
            return jsonify({"error": "Invalid request format"}), 400
            
        result = chatbot.process_trivia_answer(data["answer"])
        
        if isinstance(result, str) and result == "no_active_game":
            return jsonify({"error": "No active trivia game"}), 400
        elif isinstance(result, str) and result == "invalid":
            return jsonify({"error": "Invalid answer format. Please use A, B, C, or D."}), 400
        
        response = {
            "status": "answered",
            "result": result['result'],
            "correct_answer": result['correct_answer'],
            "score": result['score'],
            "total": result['total']
        }
        
        # Check if there are more questions
        if chatbot.trivia_questions_remaining:
            next_question = chatbot.ask_next_trivia_question()
            response["next_question"] = next_question
        else:
            # Game over
            final_result = chatbot.end_trivia_game()
            response["game_over"] = True
            response["final_result"] = final_result
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/trivia/end", methods=["POST"])
def end_trivia():
    try:
        if chatbot.trivia_active:
            result = chatbot.end_trivia_game()
            return jsonify({
                "status": "ended",
                "final_score": result
            })
        return jsonify({"status": "no_active_game"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/trivia/status", methods=["GET"])
def trivia_status():
    return jsonify({
        "active": chatbot.trivia_active,
        "score": chatbot.trivia_score,
        "total": chatbot.trivia_total,
        "current_question": chatbot.current_trivia_question['question'] if chatbot.current_trivia_question else None
    })

@app.route("/api/trivia/add", methods=["POST"])
def add_trivia_question():
    try:
        data = request.get_json()
        required_fields = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
            
        success = chatbot.add_trivia_question(
            data['question'],
            data['option_a'],
            data['option_b'],
            data['option_c'],
            data['option_d'],
            data['correct_answer']
        )
        
        if success:
            return jsonify({"status": "success", "message": "Trivia question added successfully"})
        return jsonify({
            "error": "Failed to add trivia question",
            "details": "Make sure all fields are provided and correct answer matches one of the options"
        }), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/upload", methods=["POST"])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({
                "error": "Invalid file type",
                "allowed_types": list(ALLOWED_EXTENSIONS)
            }), 400
            
        filename = secure_filename(file.filename)
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        file.save(temp_path)
        
        try:
            if filename.endswith('.csv'):
                success = chatbot.import_questions_from_csv(temp_path)
            else:
                return jsonify({
                    "error": "Unsupported file type",
                    "allowed_types": ["csv"]
                }), 400
            
            if not success:
                return jsonify({
                    "error": "Failed to process file",
                    "details": "No valid questions found or invalid format"
                }), 400
                
            message = f"Successfully imported questions from {filename}"
            return jsonify({"message": message})
        except Exception as import_error:
            return jsonify({
                "error": "Failed to process file",
                "details": str(import_error)
            }), 400
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def main():
    parser = MyArgumentParser(
        description="A CLI-based chatbot for answering questions, managing a question-answer database, and playing trivia games.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--add', action='store_true', help='Add a new question and answer')
    group.add_argument('--remove', action='store_true', help='Remove a question (used with --question)')
    group.add_argument('--list', action='store_true', help='List all questions')
    group.add_argument('--list-trivia', action='store_true', help='List all trivia questions')
    group.add_argument('--import-questions', action='store_true', help='Import questions from a file')
    group.add_argument('--interactive', action='store_true', help='Run in interactive chat mode')
    group.add_argument('--add-trivia', action='store_true', help='Add a new trivia question')
    parser.add_argument('--question', help='Ask a question directly, or specify with --add/--remove')
    parser.add_argument('--answer', help='Answer for the new question (used with --add)')
    parser.add_argument('--trivia-question', help='Trivia question text (used with --add-trivia)')
    parser.add_argument('--option-a', help='Option A for trivia question (used with --add-trivia)')
    parser.add_argument('--option-b', help='Option B for trivia question (used with --add-trivia)')
    parser.add_argument('--option-c', help='Option C for trivia question (used with --add-trivia)')
    parser.add_argument('--option-d', help='Option D for trivia question (used with --add-trivia)')
    parser.add_argument('--correct-answer', help='Correct answer for trivia (must match one of the options)')
    parser.add_argument('--filepath', help='Path to the file for import (used with --import-questions)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()
    chatbot.DEBUG = args.debug

    if args.debug:
        print("DEBUG: Debug mode enabled")

    # Adding a question
    if args.add:
        if not args.question or not args.answer:
            print("Error: --question and --answer are required with --add")
            parser.print_help()
            sys.exit(2)
        success = chatbot.add_question(args.question, args.answer)
        print(f"Question {'added' if success else 'not added'}: {args.question}")
        return

    # Adding a trivia question
    if args.add_trivia:
        required_args = [args.trivia_question, args.option_a, args.option_b, args.option_c, args.option_d,
                         args.correct_answer]
        if not all(required_args):
            print("Error: All trivia question options are required with --add-trivia")
            parser.print_help()
            sys.exit(2)
        success = chatbot.add_trivia_question(args.trivia_question, args.option_a, args.option_b, 
                                             args.option_c, args.option_d, args.correct_answer)
        print(f"Trivia question {'added' if success else 'not added'}: {args.trivia_question}")
        return

    # Removing a question
    if args.remove:
        if not args.question:
            print("Error: --question is required with --remove")
            parser.print_help()
            sys.exit(2)
        removed = chatbot.remove_question(args.question)
        print(f"Question {'removed' if removed else 'not found'}: {args.question}")
        return

    # Listing questions
    if args.list:
        questions = chatbot.list_questions()
        if not questions:
            print("No questions in the database.")
            return
        print("Questions in the database:")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q}")
        return

    # Listing trivia questions
    if args.list_trivia:
        questions = chatbot.list_trivia_questions()
        if not questions:
            print("No trivia questions in the database.")
            return
        print("Trivia questions in the database:")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q}")
        return

    # Import questions from file
    if args.import_questions:
        if not args.filepath:
            print("Error: --filepath is required with --import-questions")
            parser.print_help()
            sys.exit(2)
        success = chatbot.import_questions_from_csv(args.filepath)
        print(f"Questions {'imported' if success else 'not imported'} from {args.filepath}")
        return

    # Interactive mode
    if args.interactive:
        chatbot.interactive_mode()
        return

    # Just answer a question
    if args.question:
        answer = chatbot.answer_question(args.question)
        print(f"Bot: {answer['response']}")
        return

    # If no arguments matched, show help
    parser.print_help()

if __name__ == "__main__":
    # Check if running in CLI mode or as Flask app
    if len(sys.argv) > 1:
        main()
    else:
        logging.basicConfig(level=logging.INFO)
        app.run(debug=True, host="0.0.0.0", port=5040)