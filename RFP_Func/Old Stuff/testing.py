import pdfplumber
import requests

url = 'https://rfpnlpworkspac7030084694.blob.core.windows.net/raw-proposal/14_Tampa Airport Prog Mgmt SOQ 2014.pdf?sp=racw&st=2022-01-15T19:38:41Z&se=2022-01-23T03:38:41Z&spr=https&sv=2020-08-04&sr=c&sig=BR30uOIWQYEYOOsyQ89wv8LiGAlrgArp%2B2wsvJBBPqo%3D'
def save_pdf(url):
    r = requests.get(url, stream=True)
    with open('rfp.pdf', 'wb') as fd:
        for chunk in r.iter_content(200):
            fd.write(chunk)

save_pdf(url = url)


all_text = '' # new line
with pdfplumber.open("rfp.pdf") as pdf:
    # page = pdf.pages[0] - comment out or remove line
    # text = page.extract_text() - comment out or remove line
    for pdf_page in pdf.pages:
        single_page_text = pdf_page.extract_text()
        # separate each page's text with newline
        all_text = all_text + '\n' + single_page_text
    with open('rfp.txt', 'w') as f:
        f.write(all_text)
    # print(text) - comment out or remove line
