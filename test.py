import requests
from bs4 import BeautifulSoup
def debug_html():
    url = f"https://www.op.gg/summoners/euw/Locust-LCT"
    soup= BeautifulSoup((requests.get(url).text), 'html.parser')
    content_divs = soup.find_all('div', class_='content')

    # Mostrar el segundo div con clase 'content'
    if len(content_divs) > 1:
        print(content_divs[1].text.strip())
    else:
        print("No se encontró el contenido esperado.")

if __name__ == "__main__":
    debug_html()
