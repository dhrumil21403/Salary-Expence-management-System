import os
import re
import json
from pdf2image import convert_from_path
from paddleocr import PaddleOCR
import cv2
import numpy as np
import datetime

POPPLER_PATH = r'C:\\Program Files (x86)\\poppler-24.08.0\\Library\\bin'
ocr = PaddleOCR(use_angle_cls=True, lang='en')

SALARY_FIELDS = {
    "Employee Number": ["employee number"],
    "Department": ["department", "emp id"],
    "Sub Department":[" Sub Department"],
    "Designation": ["designation", "position", "job title"],
    "Payment mode":["Payment Mode"],
    "Actual Payable Days": ["actual payable days"],
    "Total Working Days": ["total working days"],
    "Loss Of Pay Days": ["loss of pay days"],
    "Days Payable": ["days payable"],
    "Basic": ["basic"],
    "HRA": ["hra"],
    "Conveyance Allowance": ["conveyance allowance"],
    "Other Allowance": ["other allowance"],
    "City Compensatory Allowance": ["city compensatory allowance"],
    "Total Earnings (A)": ["total earnings (a)"],
    "PF Employee": ["pf employee"],
    "ESI Employee": ["esi employee"],
    "ESI Employer": ["esi employer"],
    "Employee Gratuity contributio": ["employee gratuity contributio"],
    "Total Contributions (B)": ["total contributions (b)"],
    "Professional Tax": ["professional tax"],
    "Total Taxes & Deductions (C)": ["total taxes & deductions (c)"],
    # "Net Salary Payable (A - B - C)": ["net salary payable", "net salary payable ( a - b - c )"]
        "Net Salary Payable (A - B - C)": [
        "net salary payable",
        "net salary payable (a - b - c)",
        "net salary payable ( a - b - c )",
        "net salary payable a-b-c"
    ]
}

def preprocess_image(img_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    sharpened = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(sharpened)
    _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    return processed

def pdf_to_images(pdf_path, output_folder="Output"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    image_paths = []
    for i, img in enumerate(images):
        img_path = os.path.join(output_folder, f"page_{i+1}.png")
        img.save(img_path)
        processed = preprocess_image(img_path)
        cv2.imwrite(img_path, processed)
        image_paths.append(img_path)
    return image_paths

def extract_text_lines(image_path):
    result = ocr.ocr(image_path, cls=True)
    print(f"\n--- OCR output for: {image_path} ---")
    idx = 0
    for page in result:
        for line in page:
            print(f"{idx}: {line[1][0]}")
            idx += 1
    lines = []
    for page in result:
        for line in page:
            text = line[1][0]
            lines.append(text.strip())
    return lines

def normalize_text(text):
    return re.sub(r'\s+', ' ', text).strip().lower()
def extract_salary_fields_from_lines(lines):
    output = {key: None for key in SALARY_FIELDS}
    
    all_keywords = [kw.lower() for kws in SALARY_FIELDS.values() for kw in kws]
    
    FIELD_LINE_OFFSETS = {
    "Employee Number": 4,
    "Department": 4,
    "Sub Department":4,
    "Designation": 4,
    "Payment mode":4,
    "Actual Payable Days":4,
    "Total Working Days":4,
    "Loss Of Pay Days": 4,
    "Days Payable": 4,
    "Basic": 1,
    "HRA": 1,
    "Conveyance Allowance": 1,
    "Other Allowance": 1,
    "City Compensatory Allowance": 1,
    "Total Earnings (A)": 1,
    "PF Employee": 1,
    "ESI Employee": 1,
    "ESI Employer": 1,
    "Employee Gratuity contributio": 1,
    "Total Contributions (B)": 1,
    "Professional Tax": 1,
    "Total Taxes & Deductions (C)": 1,
    "Net Salary Payable (A - B - C)": 1
    }
    
    n = len(lines)
    idx = 0
    
    while idx < n:
        line_lower = normalize_text(lines[idx])
        for field, keywords in SALARY_FIELDS.items():
            if output[field] is not None:
                continue
            for kw in keywords:
                kw_norm = normalize_text(kw)
                if kw_norm in line_lower:
                    line = lines[idx].strip()
                    value = ''
                    # Inline value extraction (':' or '-')
                    if ':' in line:
                        value = line.split(':', 1)[1].strip()
                        if value:
                            output[field] = value
                            break
                    elif '-' in line:
                        # Make sure this '-' split does not accidentally split the key name itself (e.g. A - B - C)
                        # So in particular for this field, ignore if it looks like key
                        # Try to extract with regex: after last '-' if followed by numbers or value chars
                        parts = line.split('-')
                        last_part = parts[-1].strip()
                        if last_part and re.search(r'\d', last_part):  # roughly contains digits, treat as value
                            output[field] = last_part
                            break
                    # Use offset-based next line as value
                    offset = FIELD_LINE_OFFSETS.get(field, None)
                    if offset is not None:
                        target_idx = idx + offset
                        if target_idx < n:
                            candidate = lines[target_idx].strip()
                            candidate_lower = normalize_text(candidate)
                            # Confirm candidate doesn't contain any other keyword
                            if all(k not in candidate_lower for k in all_keywords if k != kw_norm):
                                output[field] = candidate
                                break
                    else:
                        # fallback generic lookahead (optional)
                        look_ahead_limit = 6
                        val_found = None
                        for look_idx in range(1, look_ahead_limit + 1):
                            next_idx = idx + look_idx
                            if next_idx >= n:
                                break
                            next_line = lines[next_idx].strip()
                            next_line_lower = normalize_text(next_line)
                            if not next_line:
                                continue
                            if any(k in next_line_lower for k in all_keywords if k != kw_norm):
                                break
                            val_found = next_line
                            break
                        if val_found:
                            output[field] = val_found
                    if output[field]:
                        break
            if output[field]:
                break
        idx += 1
    return output

import re

def extract_month_year_from_lines(lines):
    month_year_pattern = re.compile(r'\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(\d{4})\b', re.IGNORECASE)
    for line in lines:
        match = month_year_pattern.search(line)
        if match:
            month_str = match.group(1).capitalize()  # e.g., "Aug"
            year_str = match.group(2)                 # e.g., "2025"
            # Convert to datetime object (1st of the month)
            dt = datetime.datetime.strptime(f"04-{month_str}-{year_str}", "%d-%b-%Y")
            # Format as "MMM-yyyy"
            return dt.strftime("%b-%Y")  # e.g., "Aug-2025"
    return None

def extract_salary_slip_fields(pdf_file):
    image_paths = pdf_to_images(pdf_file)
    all_lines = []
    for img_path in image_paths:
        lines = extract_text_lines(img_path)
        all_lines.extend(lines)

    extracted = extract_salary_fields_from_lines(all_lines)

    # Extract Month-Year field from text lines
    month_year = extract_month_year_from_lines(all_lines)
    if month_year:
        extracted["Month-Year"] = month_year

    return extracted

def process_salary_slip(pdf_file, output_folder=None):
    if output_folder and not os.path.exists(output_folder):
        os.makedirs(output_folder)
    base_filename = os.path.splitext(os.path.basename(pdf_file))[0]
    output_json_path = None
    if output_folder:
        output_json_path = os.path.join(output_folder, base_filename + ".json")
    extracted = extract_salary_slip_fields(pdf_file)
    print(json.dumps(extracted, indent=4, ensure_ascii=False))
    if output_json_path:
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(extracted, f, ensure_ascii=False, indent=4)
    return extracted

if __name__ == "__main__":
    pdf_file = r"" #<-- your salaryslip file path.
    output_folder = r"D:\dataslipocr\Output"
    process_salary_slip(pdf_file, output_folder)
