# **📊 Salary Slip OCR & Google Sheet Uploader**

This project automates the process of **extracting salary slip details** from PDF files using **PaddleOCR** and then **uploading the extracted data into Google Sheets** with the Google Sheets API.  
It helps eliminate manual data entry, improves accuracy, and saves time.

## **🔧 Features**
- Extracts text and structured data from salary slip PDFs using OCR.  
- Cleans and formats the extracted data for better readability.  
- Uploads extracted data to a Google Sheet via API.  
- Secure handling of credentials (kept outside the repository).  
- Reproducible environment with `requirements.txt`.  

## **📂 Project Structure**
project-folder/ <br>
│── salaryslip.py # Extracts data from salary slip PDF <br>
│── googlesetupsheet.py # Uploads extracted data to Google Sheets <br>
│── requirements.txt # Python dependencies <br>
│── README.md # Project documentation <br>

## **🚀 Getting Started**

### 1. Clone the repository
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>

### 2. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Configure Google Sheets API
1.Go to Google Cloud Console
2.Create a Service Account and enable Google Sheets API.
3.Download the credentials JSON file.
4.Store the file outside this repository (for security).
5.Update your script to point to this credentials file.

### 5. Run the scripts
#### 1.Extract salary slip data:
python salaryslip.py

#### 2.Upload extracted data to Google Sheets:
python googlesetupsheet.py

## **📌 Example Workflow**
1.Place a salary slip PDF in your working directory.
2.Run salaryslip.py → data will be extracted using PaddleOCR.
3.Run googlesetupsheet.py → extracted data will be uploaded to your Google Sheet. 

## **⚠️ Security Notes**
Do not upload your Google API credentials JSON file to GitHub.
Add credentials file names to .gitignore.
Keep sensitive information (like Sheet IDs, credentials path) in environment variables or a .env file

## **📈 Future Enhancements**
Add support for multiple PDF uploads at once.
Build a simple frontend for file upload.

## **🤝 Contributing**
Contributions, issues, and feature requests are welcome!
Feel free to fork this repo and submit a pull request.

## **📝 License**
This project is for **educational, personal use and realtime problem solving**. Modify and adapt as needed.
