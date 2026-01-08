import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import os
import re
import logging
from urllib.parse import urljoin
from datetime import datetime

# --- KONFIGURATION ---
BASE_URL = "https://westfaelisches-landestheater.de"
SOURCES = [
    {"url": f"{BASE_URL}/abendtheater/spielzeit-2025-2026/", "cat": "Abendtheater", "season": "2025/2026"},
    {"url": f"{BASE_URL}/abendtheater/spielzeit-2026-2027/", "cat": "Abendtheater", "season": "2026/2027"},
    {"url": f"{BASE_URL}/kinder-jugendtheater/spielzeit-2025-2026/", "cat": "KJT", "season": "2025/2026"},
    {"url": f"{BASE_URL}/kinder-jugendtheater/spielzeit-2026-2027/", "cat": "KJT", "season": "2026/2027"},
]
DATA_FILE = "wlt_repertoire.json"
MAX_CONCURRENT_REQUESTS = 10 # Etwas erhöht für Speed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def clean_text(text):
    if not text: return ""
    return " ".join(text.split())

def extract_duration(text):
    match = re.search(r'(\d{2,3})\s*Minuten', text)
    return int(match.group(1)) if match else None

def extract_id_from_url(url):
    """
    Holt die numerische ID sicher aus der URL.
    Beispiel: .../produktion_id/13658/ -> 13658
    """
    # Versuch 1: Suche nach /produktion_id/ZAHL
    match = re.search(r'produktion_id/(\d+)', url)
    if match:
        return match.group(1)
    
    # Versuch 2: Nimm einfach die letzte Zahl in der URL
    nums = re.findall(r'\d+', url)
    if nums:
        return nums[-1]
    
    # Fallback: Hash des Titels (Notlösung)
    return str(hash(url))

async def fetch_url(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            logger.error(f"HTTP {response.status} bei {url}")
    except Exception as e:
        logger.error(f"Fehler bei {url}: {e}")
    return None

async def scrape_detail_page(session, url, sem):
    """Scrapt Details asynchron."""
    async with sem:
        html = await fetch_url(session, url)
        if not html: return {}

        soup = BeautifulSoup(html, 'html.parser')
        data = {
            "besetzung": [],
            "inhalt": "",
            "termine": [],
            "medien": [],
            "presse": [],
            "meta_details": {
                "dauer_minuten": None,
                "hat_pause": False,
                "altersempfehlung": None,
                "schulklasse": None
            },
            "flags": {"tickets": False, "video": False, "audio": False}
        }

        # 1. Metadaten (Alter, Klasse)
        full_text = ""
        for div in soup.find_all('div', class_='detail-beschreibung-title'):
            txt = clean_text(div.get_text())
            full_text += txt + " "
            if "Jahren" in txt or "ab" in txt:
                data["meta_details"]["altersempfehlung"] = txt
            if "Klasse" in txt:
                data["meta_details"]["schulklasse"] = txt

        # 2. Besetzung
        cast_div = soup.find('div', class_='detail-cast')
        if cast_div:
            for span in cast_div.find_all('span'):
                role_tag = span.find('strong')
                if not role_tag: continue
                rolle = clean_text(role_tag.get_text()).rstrip(':')
                role_tag.extract()
                darsteller = clean_text(span.get_text())
                data["besetzung"].append({"rolle": rolle, "darsteller": darsteller})

        # 3. Inhalt
        header = soup.find('h2', class_='detail-beschreibung-header', string=lambda t: t and "Zum Stück" in t)
        if header:
            parts = []
            curr = header.find_next_sibling()
            while curr:
                if curr.name == 'div' and any(cls in curr.get('class', []) for cls in ['detail-image-box', 'detail-terminliste', 'detail-presse']):
                    break
                txt = clean_text(curr.get_text())
                full_text += txt + " "
                if curr.name == 'p' and 'download-anchor' not in curr.get('class', []):
                    if txt: parts.append(txt)
                curr = curr.find_next_sibling()
            data["inhalt"] = "\n\n".join(parts)

        if "Pause" in full_text: data["meta_details"]["hat_pause"] = True
        data["meta_details"]["dauer_minuten"] = extract_duration(full_text)

        # 4. Termine
        termin_list = soup.find('ul', class_='detail-beschreibung-terminliste')
        if termin_list:
            for li in termin_list.find_all('li'):
                time_tag = li.find('time')
                ticket_a = li.find('a', class_='ticketlink')
                
                # Ort bereinigen
                ort_span = li.find('span', class_='span-7')
                ort_text = ""
                if ort_span:
                    import copy
                    sc = copy.copy(ort_span)
                    if sc.find('a'): sc.find('a').decompose()
                    ort_text = clean_text(sc.get_text())

                has_ticket = bool(ticket_a and ticket_a.get('href'))
                if has_ticket: data["flags"]["tickets"] = True

                data["termine"].append({
                    "datum_iso": time_tag['datetime'] if time_tag else None,
                    "datum_anzeige": clean_text(time_tag.get_text()) if time_tag else "",
                    "uhrzeit": clean_text(li.find('span', class_='event-time').get_text()) if li.find('span', class_='event-time') else "",
                    "ort": ort_text,
                    "ticket_url": ticket_a['href'] if has_ticket else None
                })

        # 5. Medien
        if soup.find('div', attrs={'data-plyr-provider': 'youtube'}):
            data["flags"]["video"] = True
            yt_id = soup.find('div', attrs={'data-plyr-provider': 'youtube'}).get('data-plyr-embed-id')
            data["medien"].append({"typ": "youtube", "url": f"https://www.youtube.com/watch?v={yt_id}"})
        
        audio = soup.find('audio')
        if audio and audio.find('source'):
            data["flags"]["audio"] = True
            data["medien"].append({"typ": "audio", "url": urljoin(BASE_URL, audio.find('source')['src'])})

        img_box = soup.find('div', class_='detail-image-box')
        if img_box:
            for a in img_box.find_all('a', class_='fancybox'):
                if a.get('href') and "download" not in a.get('href', ''):
                    data["medien"].append({"typ": "bild", "url": urljoin(BASE_URL, a.get('href'))})

        # 6. Presse
        presse_div = soup.find('div', id='pressestimmen-content')
        if presse_div:
            for p in presse_div.find_all('p'):
                t = clean_text(p.get_text())
                if t: data["presse"].append(t)

        return data

async def main():
    logger.info("--- START SCRAPER ---")
    merged_data = {}
    sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async with aiohttp.ClientSession() as session:
        # SCHRITT 1: Listen laden und Basis-Daten sammeln
        for source in SOURCES:
            logger.info(f"Lade Index: {source['cat']} ({source['season']})")
            html = await fetch_url(session, source['url'])
            if not html: continue

            soup = BeautifulSoup(html, 'html.parser')
            # Hier war der Selektor: Wir suchen nach ALLEN Listeneinträgen
            items = soup.find_all('li', class_='produktion-list-item')

            for item in items:
                # Wir suchen nach dem ersten Link im Info-Bereich
                # Der alte Code suchte nach 'color-main-1', was manchmal fehlte
                link = item.find('a', href=True)
                if not link: continue
                
                # Prüfen ob es ein Repertoire-Link ist
                href = link['href']
                if "repertoire" not in href: 
                    # Versuch den nächsten Link zu finden (manchmal ist der erste Link nur ein Bild)
                    links = item.find_all('a', href=True)
                    for l in links:
                        if "repertoire" in l['href']:
                            link = l
                            href = l['href']
                            break
                    if "repertoire" not in href: continue

                titel = clean_text(link.get_text())
                if not titel: # Falls Link keinen Text hat (Bild-Link), Titel woanders suchen
                    # Fallback: Titel steht oft im info-div
                    titel_div = item.find('div', class_='termin-list-box')
                    if titel_div:
                        titel = clean_text(titel_div.find('a').get_text())

                full_url = urljoin(BASE_URL, href)
                
                # WICHTIG: Korrekte ID Extraktion
                prod_id = extract_id_from_url(full_url)

                # Basis-Daten (Untertitel/Genre)
                info_div = item.find('div', class_='termin-list-box')
                subtitel, genre = "", ""
                if info_div:
                    # div > div enthält den Text mit Pipes getrennt
                    inner_div = info_div.find('div')
                    if inner_div:
                        parts = [clean_text(x) for x in inner_div.get_text("|").split("|") if clean_text(x)]
                        # Der Titel ist oft Teil 0, Subtitel Teil 1
                        if len(parts) > 1: subtitel = parts[1]
                        if len(parts) > 2: genre = parts[2]

                # Daten zusammenführen
                if prod_id not in merged_data:
                    merged_data[prod_id] = {
                        "id": prod_id,
                        "titel": titel,
                        "subtitel": subtitel,
                        "genre_liste": genre,
                        "url": full_url,
                        "spielzeiten": set(),
                        "kategorien": set(),
                        "is_kjt": False
                    }
                
                merged_data[prod_id]["spielzeiten"].add(source['season'])
                merged_data[prod_id]["kategorien"].add(source['cat'])
                if source['cat'] == "KJT":
                    merged_data[prod_id]["is_kjt"] = True

        # SCHRITT 2: Details laden
        total_items = len(merged_data)
        logger.info(f"Basis-Scan fertig. {total_items} einzigartige Stücke gefunden. Lade Details...")
        
        tasks = []
        for pid, data in merged_data.items():
            tasks.append(scrape_detail_page(session, data["url"], sem))
        
        results = await asyncio.gather(*tasks)

        # Daten verknüpfen
        for i, (pid, _) in enumerate(merged_data.items()):
            details = results[i]
            merged_data[pid].update(details)
            
            # Sets zu Listen
            merged_data[pid]["spielzeiten"] = sorted(list(merged_data[pid]["spielzeiten"]))
            merged_data[pid]["kategorien"] = sorted(list(merged_data[pid]["kategorien"]))
            
            # Nächster Termin
            today = datetime.now().strftime("%Y-%m-%d")
            future = [t['datum_iso'] for t in merged_data[pid].get('termine', []) if t['datum_iso'] and t['datum_iso'] >= today]
            merged_data[pid]["naechster_termin_iso"] = min(future) if future else None

    # Speichern
    output_list = sorted(list(merged_data.values()), key=lambda x: x['titel'])
    final_json = {
        "meta": {"generiert": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "anzahl": len(output_list)},
        "daten": output_list
    }

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_json, f, ensure_ascii=False, indent=4)

    logger.info(f"FERTIG: {len(output_list)} Stücke erfolgreich gespeichert.")

if __name__ == "__main__":
    asyncio.run(main())