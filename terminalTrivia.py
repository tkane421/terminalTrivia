import csv
import os.path
import random
from datetime import datetime

def list_categories(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        category_counts = {}
        for row in reader:
            category = row['category']
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1
    return category_counts

def get_overall_stats(output_file_path):
    total_questions_asked = 0
    total_correct_answers = 0
    category_stats = {}

    if os.path.exists(output_file_path):
        with open(output_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                total_questions_asked += 1
                if row['Is Correct'] == 'True':
                    total_correct_answers += 1

                category = row['Category']
                if category not in category_stats:
                    category_stats[category] = {'questions_asked': 0, 'correct_answers': 0}
                category_stats[category]['questions_asked'] += 1
                if row['Is Correct'] == 'True':
                    category_stats[category]['correct_answers'] += 1

    if total_questions_asked > 0:
        overall_percentage_correct = (total_correct_answers / total_questions_asked) * 100
    else:
        overall_percentage_correct = 0.0

    print(
        f"Overall Total: {total_correct_answers} of {total_questions_asked} questions correct ({overall_percentage_correct:.2f}%)\n")

    # for category, stats in category_stats.items():
    #     if stats['questions_asked'] >= 10:
    #         percentage_correct = (stats['correct_answers'] / stats['questions_asked']) * 100

    return category_stats

def display_category_summary(category_stats):
    print("Updated Overall Summary of Categories:")
    for category, stats in category_stats.items():
        percentage_correct = (stats['correct_answers'] / stats['questions_asked']) * 100
        status = ""
        if stats['questions_asked'] >= 10:
            if percentage_correct > 90:
                status = " (STRONG)"
            elif percentage_correct < 30:
                status = " (WEAK)"
        print(f"{category}{status}: {stats['questions_asked']} questions asked, {percentage_correct:.2f}% correct")

def quiz_from_csv(file_path, output_file_path):
    # Display overall stats from previous quizzes if output.csv exists
    category_stats = get_overall_stats(output_file_path)

    # List available categories with the number of questions available in each category
    category_counts = list_categories(file_path)
    print("Available categories:\n")
    for category, count in category_counts.items():
        status = ""
        if category in category_stats and category_stats[category]['questions_asked'] >= 10:
            percentage_correct = (category_stats[category]['correct_answers'] / category_stats[category][
                'questions_asked']) * 100
            if percentage_correct > 90:
                status = " (STRONG)"
            elif percentage_correct < 30:
                status = " (WEAK)"
        print(f"{category}{status}: {count} question(s)")

    # Get the category from the user
    available_categories = [category.lower() for category in category_counts.keys()]
    while True:
        category = input("\nChoose a category (leave blank for all categories): ").strip().lower()
        if not category or category in available_categories:
            break
        else:
            print("Invalid category. Please choose from the available categories.")

    #Get the number of questions to ask from the user
    n = int(input(f"\nEnter the number of questions to ask (e.g. 10): "))

    with open(file_path, newline='') as csvfile:
        reader = list(csv.DictReader(csvfile))

        # Filter questions by category if a category is specified
        if category:
            filtered_questions = [row for row in reader if row['category'].lower() == category]
        else:
            filtered_questions = reader

        # Ensure there are enough questions in the selected category
        if len(filtered_questions) < n:
            print(f"Not enough questions in the selected category. Only {len(filtered_questions)} questions available.")
            return

        # Take a random sample of n questions
        sample_questions = random.sample(filtered_questions, n)

        # Randomise the order of the questions
        random.shuffle(sample_questions)

        correct_answers = 0
        total_questions_asked = 0

        # Open the output CSV file for writing
        with open(output_file_path, mode='a',newline='') as output_file:
            fieldnames = ['Timestamp', 'Category', 'Question', 'Selected Option', 'Correct Option', 'Is Correct',
                          'Attempts']
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)

            # Write header only if the file is empty
            if output_file.tell() == 0:
                writer.writeheader()

            for row in sample_questions:
                question = row['question']
                options = [row['option1'], row['option2'], row['option3'], row['option4']]
                answer = int(row['answer'])
                responses = {
                    "option_1": row['response1'],
                    "option_2": row['response2'],
                    "option_3": row['response3'],
                    "option_4": row['response4'],
                }

                # Create a list of tuples (option, response)
                options_with_responses = list(enumerate(options, 1))
                random.shuffle(options_with_responses)

                # Find the new index of the correct answer
                correct_answer = next(i for i, (index, option) in enumerate(options_with_responses) if index == answer) + 1

                first_attempt = True
                first_attempt_choice = None
                total_questions_asked += 1
                attempts = 0

                while True:
                    print(question)
                    for i, (index, option) in enumerate(options_with_responses, 1):
                        print(f"{i}. {option}")

                    user_input = input("Please select the correct option (1-4): ")
                    attempts += 1

                    try:
                        user_choice = int(user_input)
                        if user_choice not in range(1,5):
                            raise ValueError("Invalid Option")
                        if first_attempt_choice is None:
                            first_attempt_choice = user_choice
                        is_correct = user_choice == correct_answer
                        if is_correct:
                            print(responses[f"option_{options_with_responses[user_choice - 1][0]}"])
                            if first_attempt:
                                correct_answers += 1
                            break

                        else:
                            print(responses[f"option_{options_with_responses[user_choice - 1][0]}"])
                            print("Incorrect. Please try again. \n")
                            first_attempt = False
                    except(ValueError, KeyError):
                        print("Invalid input. Please enter a number between 1 and 4.\n")

                # Write the first attempt result to the output CSV file
                writer.writerow({
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Category': row['category'],
                    'Question': question,
                    'Selected Option': first_attempt_choice,
                    'Correct Option': correct_answer,
                    'Is Correct': first_attempt_choice == correct_answer,
                    'Attempts': attempts
                })

                # Calculate and print the running percentage of correct answers
                percentage_correct = (correct_answers / total_questions_asked) * 100
                questions_remaining = n - total_questions_asked
                print(
                    f"Running total: {percentage_correct:.2f}% ({correct_answers} of {total_questions_asked} questions correct)")
                print(f"{questions_remaining} questions remaining\n")

    # Display new overall summary of categories
    display_category_summary(get_overall_stats(output_file_path))

# Example usage: Start the quiz from the CSV file and store results in output.csv
quiz_from_csv('questions.csv', 'output.csv')