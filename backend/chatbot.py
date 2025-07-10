import argparse
import csv
import os
import sys
import logging
import random
from datetime import datetime

questions = {}
trivia_questions = []
DEBUG = False

# Trivia game state
trivia_active = False
trivia_score = 0
trivia_total = 0
current_trivia_question = None
trivia_questions_remaining = []


class MyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.print_help(sys.stderr)
        self.exit(2, f'{self.prog}: error: {message}\n')


def get_current_time():
    return datetime.now().strftime("%H:%M:%S")


def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")


def setup_logging(enable_logging, log_level):
    if enable_logging:
        logging.basicConfig(
            filename='app.log',
            level=getattr(logging, log_level),
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            encoding='utf-8',
            force=True
        )


def save_questions_to_csv(filename="questions.csv", questions_dict=None):
    try:
        if questions_dict is None:
            data = questions
        else:
            data = questions_dict
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['question', 'answer1', 'answer2', 'answer3', 'answer4'])
            for question, answers in data.items():
                row = [question] + list(answers)[:4] + [''] * (4 - len(answers))
                writer.writerow(row)
        if DEBUG:
            print(f"DEBUG: Saved {len(questions)} questions to '{filename}'")
        return True
    except Exception as e:
        logging.error(f"Failed to save questions to '{filename}': {str(e)}")
        print(f"Error: Failed to save questions to '{filename}': {str(e)}")
        return False


def save_trivia_to_csv(filename="trivia.csv", trivia_list=None):
    """Save trivia questions to CSV file"""
    try:
        if trivia_list is None:
            data = trivia_questions
        else:
            data = trivia_list
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer'])
            for trivia in data:
                row = [
                    trivia['question'],
                    trivia['options'][0],
                    trivia['options'][1],
                    trivia['options'][2],
                    trivia['options'][3],
                    trivia['correct_answer']
                ]
                writer.writerow(row)
        if DEBUG:
            print(f"DEBUG: Saved {len(data)} trivia questions to '{filename}'")
        return True
    except Exception as e:
        logging.error(f"Failed to save trivia questions to '{filename}': {str(e)}")
        print(f"Error: Failed to save trivia questions to '{filename}': {str(e)}")
        return False


def load_trivia_from_csv(filename="trivia.csv"):
    """Load trivia questions from CSV file"""
    global trivia_questions
    if os.path.exists(filename):
        try:
            with open(filename, mode='r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                header = reader.fieldnames
                required_headers = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
                if not header or not all(h in header for h in required_headers):
                    logging.warning(f"Invalid trivia CSV header: {header} in file: {filename}")
                    if DEBUG:
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
                        trivia_questions.append({
                            'question': question,
                            'options': options,
                            'correct_answer': correct_answer
                        })
                        count += 1
                if DEBUG:
                    print(f"DEBUG: Loaded {count} trivia questions from '{filename}' on startup")
        except Exception as e:
            logging.error(f"Error loading trivia questions from {filename}: {e}")
            if DEBUG:
                print(f"DEBUG: Error loading trivia questions from {filename}: {e}")
    else:
        # Create default trivia questions if file doesn't exist
        create_default_trivia()
        save_trivia_to_csv(filename)
        logging.info(f"Created default trivia questions and saved to {filename}")
        if DEBUG:
            print(f"DEBUG: Created default trivia questions and saved to {filename}")


def create_default_trivia():
    """Create some default trivia questions about university services"""
    global trivia_questions
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
    trivia_questions.extend(default_trivia)


def start_trivia_game(num_questions=10):
    """Start a new trivia game"""
    global trivia_active, trivia_score, trivia_total, trivia_questions_remaining

    if len(trivia_questions) < num_questions:
        print(f"Error: Not enough trivia questions available. Need {num_questions}, have {len(trivia_questions)}")
        return False

    trivia_active = True
    trivia_score = 0
    trivia_total = 0
    trivia_questions_remaining = random.sample(trivia_questions, num_questions)

    print("🎯 TRIVIA GAME ACTIVATED! 🎯")
    print(f"Get ready for {num_questions} multiple choice questions about university services!")
    print("Answer with A, B, C, or D. Type 'trivia' anytime to see your score and exit.\n")

    ask_next_trivia_question()
    return True


def ask_next_trivia_question():
    """Ask the next trivia question"""
    global current_trivia_question

    if not trivia_questions_remaining:
        end_trivia_game()
        return

    current_trivia_question = trivia_questions_remaining.pop(0)
    current_question_num = trivia_total + 1
    total_questions = current_question_num + len(trivia_questions_remaining)

    # Progress and score indicator
    print(f"Question {current_question_num} of {total_questions}; Score {trivia_score}/{trivia_total}")
    print(f"{current_trivia_question['question']}")
    print(f"A) {current_trivia_question['options'][0]}")
    print(f"B) {current_trivia_question['options'][1]}")
    print(f"C) {current_trivia_question['options'][2]}")
    print(f"D) {current_trivia_question['options'][3]}")
    print("\nYour answer (A/B/C/D): ", end="")


def process_trivia_answer(user_input):
    """Process the user's trivia answer"""
    global trivia_score, trivia_total, current_trivia_question

    if not current_trivia_question:
        return

    trivia_total += 1
    user_answer = user_input.strip().upper()

    # Map letter to actual answer
    option_map = {
        'A': 0,
        'B': 1,
        'C': 2,
        'D': 3
    }

    if user_answer in option_map:
        selected_index = option_map[user_answer]
        correct_index = current_trivia_question['options'].index(current_trivia_question['correct_answer'])
        
        if selected_index == correct_index:
            trivia_score += 1
            print(f"✅ Correct! The answer is: {current_trivia_question['correct_answer']}")
            return "correct"
        else:
            print(f"❌ Incorrect. The correct answer is: {current_trivia_question['correct_answer']}")
            return "incorrect"
    else:
        print(f"❌ Invalid answer format. The correct answer is: {current_trivia_question['correct_answer']}")
        return "invalid"

    print(f"Current score: {trivia_score}/{trivia_total}\n")
    current_trivia_question = None
    ask_next_trivia_question()


def end_trivia_game():
    """End the trivia game and show final results"""
    global trivia_active

    trivia_active = False
    percentage = (trivia_score / trivia_total * 100) if trivia_total > 0 else 0

    print("🏆 TRIVIA GAME COMPLETED! 🏆")
    print(f"Final Score: {trivia_score}/{trivia_total} ({percentage:.1f}%)")

    if percentage >= 90:
        print("🌟 Excellent! You're a university services expert!")
    elif percentage >= 70:
        print("👍 Great job! You know your way around university services!")
    elif percentage >= 50:
        print("👌 Not bad! You have good knowledge of university services!")
    else:
        print("📚 Keep learning about university services - there's always more to discover!")

    print("\nReturning to regular chat mode...\n")


def add_trivia_question(question, option_a, option_b, option_c, option_d, correct_answer):
    """Add a new trivia question"""
    if not all([question, option_a, option_b, option_c, option_d, correct_answer]):
        return False

    if correct_answer not in [option_a, option_b, option_c, option_d]:
        return False

    new_trivia = {
        'question': question.strip(),
        'options': [option_a.strip(), option_b.strip(), option_c.strip(), option_d.strip()],
        'correct_answer': correct_answer.strip()
    }

    trivia_questions.append(new_trivia)
    save_trivia_to_csv("trivia.csv")
    return True


def import_questions_from_csv(filename):
    if not os.path.exists(filename):
        print(f"Error: File not found: {filename}")
        logging.error(f"Import failed: File not found: {filename}")
        return
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if not reader.fieldnames or 'question' not in reader.fieldnames or 'answer1' not in reader.fieldnames:
                logging.warning(f"Import failed for {filename}: Missing required headers")
                print(f"Warning: Unsupported CSV format. Missing required headers.")
                return
            imported = 0
            for row in reader:
                q = row['question'].strip().lower()
                answers = [row[key].strip() for key in ['answer1', 'answer2', 'answer3', 'answer4'] if
                           row.get(key) and row[key].strip()]
                if q and answers:
                    questions[q] = answers
                    imported += 1
            logging.info(f"Successfully imported {imported} questions from {filename}")
            if DEBUG:
                print(f"DEBUG: Imported {imported} questions from {filename}")
        save_questions_to_csv("questions.csv", questions)
    except UnicodeDecodeError:
        logging.warning(f"Import failed for {filename}: Not a valid UTF-8 CSV")
        print(f"Error: {filename} is not a valid UTF-8 CSV.")
    except PermissionError:
        logging.warning(f"Import failed for {filename}: Permission denied")
        print(f"Error: Permission denied for {filename}.")
    except Exception as e:
        logging.error(f"Failed to import questions from {filename}: {str(e)}")
        print(f"Error: Failed to import questions from {filename}: {str(e)}")


def load_questions_from_csv(filename):
    if os.path.exists(filename):
        try:
            with open(filename, mode='r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                header = reader.fieldnames
                if not header or 'question' not in header or 'answer1' not in header:
                    logging.warning(f"Invalid CSV header: {header} in file: {filename}")
                    if DEBUG:
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
                        questions[q] = answers
                        count += 1
                if DEBUG:
                    print(f"DEBUG: Loaded {count} questions from '{filename}' on startup")
        except Exception as e:
            logging.error(f"Error loading questions from {filename}: {e}")
            if DEBUG:
                print(f"DEBUG: Error loading questions from {filename}: {e}")
    else:
        logging.info(f"No questions.csv found at {filename} on startup")
        if DEBUG:
            print(f"DEBUG: No questions.csv found at {filename} on startup")


def add_question(question, answer):
    q = question.strip().lower()
    a = answer.strip()
    if not q or not a:
        return False
    if q in questions:
        # Prevent duplicate answers
        if a not in questions[q]:
            questions[q].append(a)
    else:
        questions[q] = [a]
    save_questions_to_csv("questions.csv", questions)
    return True


def remove_question(question):
    q = question.strip().lower()
    if q in questions:
        del questions[q]
        save_questions_to_csv("questions.csv", questions)
        return True
    return False


def list_questions():
    if not questions:
        print("No questions in the database.")
        return
    print("Questions in the database:")
    for i, q in enumerate(questions.keys(), 1):
        print(f"{i}. {q}")


def answer_question(query):
    global trivia_active

    q = query.strip().lower()
    if DEBUG:
        print("DEBUG: Entering answer_question")

    # Check if user wants to start/exit trivia game
    if q == "trivia":
        if trivia_active:
            # Exit trivia game
            print(f"Exiting trivia game. Current score: {trivia_score}/{trivia_total}")
            end_trivia_game()
            return f"Trivia game ended. Final score: {trivia_score}/{trivia_total}"
        else:
            # Start trivia game
            start_trivia_game(10)
            return "Trivia game started!"

    # If trivia is active and user didn't type 'trivia', process as trivia answer
    if trivia_active:
        process_trivia_answer(query)
        return "Trivia answer processed"

    # Regular question handling
    if q in ("what is the time?", "what's the time?", "time?"):
        time_str = get_current_time()
        answer = f"The current time is {time_str}."
        print(answer)
        return answer
    elif q in ("what is the date?", "what's the date?", "date?"):
        date_str = get_current_date()
        answer = f"Today's date is {date_str}."
        print(answer)
        return answer

    if q in questions and questions[q]:
        answer = random.choice(questions[q])
        print(answer)
        return answer
    else:
        msg = "I don't have an answer for that question."
        logging.warning(f"No answer found for question: {query}")
        print(msg)
        return msg


def interactive_mode():
    """Run the chatbot in interactive mode"""
    print("🤖 Chatbot Interactive Mode")
    print("Type your questions, 'trivia' to start trivia game, or 'quit' to exit.\n")

    while True:
        try:
            if trivia_active and current_trivia_question:
                user_input = input("")  # No prompt as trivia shows its own
            else:
                user_input = input("You: ")

            if user_input.strip().lower() in ['quit', 'exit', 'bye']:
                if trivia_active:
                    print("Ending trivia game...")
                    end_trivia_game()
                print("Goodbye!")
                break

            # In interactive mode, we can provide trivia suggestions
            result = answer_question(user_input)
            if result == "I don't have an answer for that question." and not trivia_active:
                print("Try 'trivia' to play the trivia game!")

        except KeyboardInterrupt:
            if trivia_active:
                print("\nEnding trivia game...")
                end_trivia_game()
            print("\nGoodbye!")
            break
        except EOFError:
            if trivia_active:
                print("\nEnding trivia game...")
                end_trivia_game()
            print("\nGoodbye!")
            break


def main():
    import argparse

    parser = MyArgumentParser(
        description="A CLI-based chatbot for answering questions, managing a question-answer database, and playing trivia games.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--add', action='store_true', help='Add a new question and answer')
    group.add_argument('--remove', action='store_true', help='Remove a question (used with --question)')
    group.add_argument('--list', action='store_true', help='List all questions')
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
    parser.add_argument('--filetype', choices=['CSV'], help='File type for import (used with --import-questions)')
    parser.add_argument('--filepath', help='Path to the file for import (used with --import-questions)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--enable-logging', action='store_true', help='Enable logging to app.log')
    parser.add_argument('--log-level', choices=['INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='WARNING',
                        help='Set logging level')

    args = parser.parse_args()
    global DEBUG
    DEBUG = args.debug

    if DEBUG:
        print("DEBUG: Debug mode enabled")

    setup_logging(args.enable_logging, args.log_level)
    load_questions_from_csv("questions.csv")
    load_trivia_from_csv("trivia.csv")

    # Adding a question
    if args.add:
        if not args.question or not args.answer:
            print("Error: --question and --answer are required with --add")
            parser.print_help()
            sys.exit(2)
        success = add_question(args.question, args.answer)
        if success and DEBUG:
            print(f"DEBUG: After adding, questions dictionary: {questions}")
        print(f"Question added: {args.question}")
        return

    # Adding a trivia question
    if args.add_trivia:
        required_args = [args.trivia_question, args.option_a, args.option_b, args.option_c, args.option_d,
                         args.correct_answer]
        if not all(required_args):
            print(
                "Error: --trivia-question, --option-a, --option-b, --option-c, --option-d, and --correct-answer are all required with --add-trivia")
            parser.print_help()
            sys.exit(2)
        success = add_trivia_question(args.trivia_question, args.option_a, args.option_b, args.option_c, args.option_d,
                                      args.correct_answer)
        if success:
            print(f"Trivia question added: {args.trivia_question}")
        else:
            print("Error: Could not add trivia question. Make sure the correct answer matches one of the options.")
        return

    # Removing a question
    if args.remove:
        if not args.question:
            print("Error: --question is required with --remove")
            parser.print_help()
            sys.exit(2)
        removed = remove_question(args.question)
        if removed:
            print(f"Question removed: {args.question}")
        else:
            print(f"Could not find question: {args.question}")
        return

    # Listing questions
    if args.list:
        list_questions()
        return

    # Import questions from file
    if args.import_questions:
        if args.filetype != 'CSV' or not args.filepath:
            print("Error: --filetype CSV and --filepath are required with --import-questions")
            parser.print_help()
            sys.exit(2)
        import_questions_from_csv(args.filepath)
        return

    # Interactive mode
    if args.interactive:
        interactive_mode()
        return

    # Just answer a question
    if args.question:
        answer_question(args.question)
        return

    # If no arguments matched, show help
    parser.print_help()


if __name__ == "__main__":
    main()
else:
    load_questions_from_csv("questions.csv")
    load_trivia_from_csv("trivia.csv")
