import pdfplumber
import openpyxl

with pdfplumber.open('BlockChain.pdf') as pdf:
    page = pdf.pages[0]  # Select the appropriate page
    text = page.extract_text()
    print