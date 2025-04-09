#!/usr/bin/env python3
import os
import random
from fpdf import FPDF
from PIL import Image

exams_dir = "exams"
output_folder = "simulations"

# Constants
DPI = 96
MM_PER_PIXEL = 25.4 / DPI     # Conversion factor from pixels to millimeters.
ALTERNATIVE_SCALE = 0.6       # Scale factor to resize alternative images.
LETTER_CELL_WIDTH = 4         # Width (in mm) reserved for the letter label.
LETTER_CELL_MARGIN = 2        # Gap (in mm) between the letter label and the alternative image.
VERTICAL_GAP = 2              # Gap (in mm) between alternative rows.
LABEL_HEIGHT = 7              # Height for the question label cell.
GAP_AFTER_QUESTION = 5        # Gap (in mm) after the question image.
ALT_BOTTOM_GAP = 10           # Additional gap (in mm) after the alternatives block.

def load_questions(exams_dir):
    """
    Walk through the exam folder structure and collect questions.
    
    Expected structure:
      exams/<exam_folder>/<question_folder>/
    
    Each question folder must contain:
      - A file "question.png" (the question image)
      - 5 alternative PNG files (ignoring also the file with the same name as the folder).
    
    The label for printing is the relative path "exam_folder/question_folder".
    """
    questions = []
    for exam_folder in os.listdir(exams_dir):
        exam_path = os.path.join(exams_dir, exam_folder)
        if not os.path.isdir(exam_path):
            continue
        for q_folder in os.listdir(exam_path):
            q_path = os.path.join(exam_path, q_folder)
            if not os.path.isdir(q_path):
                continue
            question_img_path = os.path.join(q_path, "question.png")
            if not os.path.exists(question_img_path):
                print(f"Skipping '{q_path}': 'question.png' not found.")
                continue
            # List all PNG files in the folder.
            all_png = [f for f in os.listdir(q_path) if f.lower().endswith('.png')]
            # Exclude "question.png" and the file named exactly like the folder.
            ignore = {"question.png", f"{q_folder}.png"}
            alternatives = [os.path.join(q_path, f) for f in all_png if f not in ignore]
            if len(alternatives) != 5:
                print(f"Warning: In folder '{q_path}' expected 5 alternative images but found {len(alternatives)}.")
            questions.append({
                "label": os.path.join(exam_folder, q_folder),  # e.g., "2023-2/q1"
                "question_img": question_img_path,
                "alternatives": alternatives,
            })
    return questions

def draw_question(pdf, question):
    """
    Draws a question block in the PDF.
    It includes:
      - A label (question folder path)
      - The question image (scaled to full width)
      - A gap after the question image.
      - The 5 alternative images (with a letter label, shuffled).
    Checks available vertical space and adds a new page if needed.
    """
    available_width = pdf.w - pdf.l_margin - pdf.r_margin

    # --- Compute the space needed by the question image ---
    try:
        q_im = Image.open(question["question_img"])
        q_im_width, q_im_height = q_im.size
    except Exception as e:
        print(f"Error opening question image {question['question_img']}: {e}")
        return
    display_height = available_width * (q_im_height / q_im_width)

    # --- Compute total alternatives height ---
    alt_total_scaled_height = 0
    for alt_path in question["alternatives"]:
        try:
            alt_im = Image.open(alt_path)
            alt_w, alt_h = alt_im.size
            scaled_h = (alt_h * MM_PER_PIXEL) * ALTERNATIVE_SCALE
            alt_total_scaled_height += scaled_h
        except Exception as e:
            print(f"Error opening alternative image {alt_path}: {e}")
            continue

    # Total height needed for this question block.
    required_height = (LABEL_HEIGHT +
                       display_height +
                       GAP_AFTER_QUESTION +
                       (alt_total_scaled_height + (5 * VERTICAL_GAP) + ALT_BOTTOM_GAP))
    
    available_space = pdf.h - pdf.get_y() - pdf.b_margin
    if required_height > available_space:
        pdf.add_page()

    # --- Print the question label ---
    pdf.set_font("Arial", size=12)
    pdf.cell(0, LABEL_HEIGHT, question["label"], ln=True)

    # --- Insert the question image ---
    current_y = pdf.get_y()
    pdf.image(question["question_img"], x=pdf.l_margin, y=current_y,
              w=available_width, h=display_height)
    pdf.set_y(current_y + display_height + GAP_AFTER_QUESTION)

    # --- Place the alternatives vertically (shuffled) ---
    alt_images = question["alternatives"].copy()
    random.shuffle(alt_images)
    letters = ['a)', 'b)', 'c)', 'd)', 'e)']
    
    current_alt_y = pdf.get_y()
    pdf.set_font("Arial", size=12)
    for i, alt_path in enumerate(alt_images):
        letter = letters[i]
        try:
            alt_im = Image.open(alt_path)
            alt_w, alt_h = alt_im.size
        except Exception as e:
            print(f"Error opening alternative image {alt_path}: {e}")
            continue
        # Compute scaled dimensions for the alternative image.
        scaled_w = (alt_w * MM_PER_PIXEL) * ALTERNATIVE_SCALE
        scaled_h = (alt_h * MM_PER_PIXEL) * ALTERNATIVE_SCALE

        available_alt_width = available_width - (LETTER_CELL_WIDTH + LETTER_CELL_MARGIN)
        if scaled_w > available_alt_width:
            factor_width = available_alt_width / scaled_w
            scaled_w = scaled_w * factor_width
            scaled_h = scaled_h * factor_width

        # Print the letter label on the left.
        letter_x = pdf.l_margin
        letter_y = current_alt_y + scaled_h / 2
        pdf.text(x=letter_x, y=letter_y, txt=letter)
        
        # Print the alternative image to the right of the letter.
        image_x = pdf.l_margin + LETTER_CELL_WIDTH + LETTER_CELL_MARGIN
        pdf.image(alt_path, x=image_x, y=current_alt_y, w=scaled_w, h=scaled_h)
        
        # Move down for the next alternative.
        current_alt_y += scaled_h + VERTICAL_GAP
    pdf.set_y(current_alt_y + ALT_BOTTOM_GAP)

def create_simulation_exams(questions, output_folder):
    """
    Creates random simulation exams.
    The questions list is shuffled globally, and then each exam contains 40 questions.
    """
    random.shuffle(questions)
    num_exams = len(questions) // 40
    if num_exams == 0:
        print("Not enough questions to create a simulation exam (need at least 40).")
        return

    for exam_num in range(num_exams):
        exam_questions = questions[exam_num * 40 : (exam_num + 1) * 40]
        pdf = FPDF(format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()  # Start the first page

        for q in exam_questions:
            draw_question(pdf, q)
        
        pdf_filename = os.path.join(output_folder, f"simulation_exam_{exam_num + 1}.pdf")
        pdf.output(pdf_filename)
        print(f"Created {pdf_filename}")

def create_full_exams(questions, output_folder):
    """
    Creates full exam PDFs for each exam folder.
    For each exam folder (as taken from the question label), all its questions are included
    in sorted order. Only the alternatives order is randomized.
    """
    # Group questions by exam folder (first component of the label).
    exams = {}
    for q in questions:
        exam_id = q["label"].split(os.sep)[0]
        exams.setdefault(exam_id, []).append(q)
    
    for exam_id, qs in exams.items():
        # Sort questions by their folder name (the second part of the label).
        qs.sort(key=lambda x: x["label"])
        pdf = FPDF(format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        for q in qs:
            draw_question(pdf, q)
        pdf_filename = os.path.join(output_folder, f"full_exam_{exam_id}.pdf")
        pdf.output(pdf_filename)
        print(f"Created {pdf_filename}")

def main():
    os.makedirs(output_folder, exist_ok=True)

    questions = load_questions(exams_dir)
    total_q = len(questions)
    print(f"Found {total_q} question(s).")
    
    # Ask user for mode selection.
    print("Select exam mode:")
    print("  1 - Random mock exams (mix questions from different exams, 40 per PDF).")
    print("  2 - Full exam with randomized alternatives (all questions per exam folder).")
    mode = input("Enter 1 or 2: ").strip()
    
    print("Creating exams...")
    if mode == "1":
        create_simulation_exams(questions, output_folder)
    elif mode == "2":
        create_full_exams(questions, output_folder)
    else:
        print("Invalid selection. Exiting.")

if __name__ == "__main__":
    main()
