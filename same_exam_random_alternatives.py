#!/usr/bin/env python3
import os
import random
from fpdf import FPDF
from PIL import Image

exams_dir = "exams/2023-1"
output_file = "all_questions.pdf"

# Constants
DPI = 96
MM_PER_PIXEL = 25.4 / DPI
ALTERNATIVE_SCALE = 0.5
LETTER_CELL_WIDTH = 4
LETTER_CELL_MARGIN = 2
VERTICAL_GAP = 2
GAP_AFTER_QUESTION = 5
ALT_BOTTOM_GAP = 10
ALTERNATIVES_PRE_SPACE = 5

def load_all_questions(exams_dir):
    questions = []
    if not os.path.isdir(exams_dir):
        return questions
    for q_folder in sorted(os.listdir(exams_dir)):
        q_path = os.path.join(exams_dir, q_folder)
        if not os.path.isdir(q_path):
            continue
        question_img = os.path.join(q_path, "question.png")
        if not os.path.exists(question_img):
            continue
        all_pngs = [f for f in os.listdir(q_path) if f.lower().endswith('.png')]
        ignore = {"question.png", f"{q_folder}.png"}
        alternatives = [os.path.join(q_path, f) for f in all_pngs if f not in ignore]
        if len(alternatives) != 5:
            print(f"Warning: {q_path} has {len(alternatives)} alternatives (expected 5).")
        questions.append({
            "question_img": question_img,
            "alternatives": alternatives
        })
    return questions

def draw_question(pdf, question):
    available_width = pdf.w - pdf.l_margin - pdf.r_margin
    try:
        q_img = Image.open(question["question_img"])
        q_w, q_h = q_img.size
        display_height = available_width * (q_h / q_w)
    except Exception as e:
        print(f"Error loading question image {question['question_img']}: {e}")
        return

    alt_total_height = 0
    for alt in question["alternatives"]:
        try:
            im = Image.open(alt)
            _, h = im.size
            alt_total_height += (h * MM_PER_PIXEL) * ALTERNATIVE_SCALE
        except:
            continue

    required_height = display_height + GAP_AFTER_QUESTION + alt_total_height + (5 * VERTICAL_GAP) + ALT_BOTTOM_GAP
    if pdf.h - pdf.get_y() - pdf.b_margin < required_height:
        pdf.add_page()

    pdf.set_font("Arial", size=12)

    y_pos = pdf.get_y()
    pdf.image(question["question_img"], x=pdf.l_margin, y=y_pos, w=available_width, h=display_height)
    pdf.set_y(y_pos + display_height + GAP_AFTER_QUESTION)

    alt_images = question["alternatives"].copy()
    random.shuffle(alt_images)
    letters = ['a)', 'b)', 'c)', 'd)', 'e)']
    y = pdf.get_y()
    for i, alt in enumerate(alt_images):
        try:
            im = Image.open(alt)
            w, h = im.size
            scaled_w = (w * MM_PER_PIXEL) * ALTERNATIVE_SCALE
            scaled_h = (h * MM_PER_PIXEL) * ALTERNATIVE_SCALE
            max_width = available_width - (LETTER_CELL_WIDTH + LETTER_CELL_MARGIN)
            if scaled_w > max_width:
                scale = max_width / scaled_w
                scaled_w *= scale
                scaled_h *= scale
            pdf.text(x=pdf.l_margin + ALTERNATIVES_PRE_SPACE, y=y + scaled_h / 2, txt=letters[i])
            pdf.image(alt, x=pdf.l_margin + ALTERNATIVES_PRE_SPACE + LETTER_CELL_WIDTH + LETTER_CELL_MARGIN, y=y, w=scaled_w, h=scaled_h)
            y += scaled_h + VERTICAL_GAP
        except Exception as e:
            print(f"Error loading alternative image {alt}: {e}")
            continue
    pdf.set_y(y + ALT_BOTTOM_GAP)

def main():
    questions = load_all_questions(exams_dir)
    print(f"Loaded {len(questions)} question(s).")

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    for q in questions:
        draw_question(pdf, q)

    pdf.output(output_file)
    print(f"PDF saved to {output_file}")

if __name__ == "__main__":
    main()
