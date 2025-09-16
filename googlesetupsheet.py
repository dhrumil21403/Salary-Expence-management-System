import json
import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = ''  # your JSON path
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

def upload_data_from_file_to_sheet(data_file_path):
    with open(data_file_path, 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    SPREADSHEET_ID = '' # your googlesheetid
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    worksheet = spreadsheet.worksheet('Salaryslip')

    FIELD_LINE_OFFSETS = [
        "Employee Number",
        "Department",
        "Sub Department",
        "Designation",
        "Payment mode",
        "Actual Payable Days",
        "Total Working Days",
        "Loss Of Pay Days",
        "Days Payable",
        "Basic",
        "HRA",
        "Conveyance Allowance",
        "Other Allowance",
        "City Compensatory Allowance",
        "Total Earnings (A)",
        "PF Employee",
        "ESI Employee",
        "ESI Employer",
        "Employee Gratuity contributio",
        "Total Contributions (B)",
        "Professional Tax",
        "Total Taxes & Deductions (C)",
        "Net Salary Payable (A - B - C)",
        "Month-Year"
    ]
    existing_headers = worksheet.row_values(1)
    if existing_headers != FIELD_LINE_OFFSETS:
        worksheet.insert_row(FIELD_LINE_OFFSETS, 1)
        print("Column headers inserted.")

    # Debug print each field and its value
    print("Field values to upload:")
    row = []
    for idx, field in enumerate(FIELD_LINE_OFFSETS, start=1):
        value = extracted_data.get(field, "")
        print(f"Column {idx} ({field}): '{value}'")
        row.append(value)

    # Append the row ensuring that missing or empty values don't cause misalignment
    worksheet.append_row(row)

    # worksheet.append_row(row)
    print("Data uploaded to Google Sheets successfully!")

if __name__ == "__main__":
    data_file = r""  # pass your JSON file with extracted data here
    upload_data_from_file_to_sheet(data_file)
