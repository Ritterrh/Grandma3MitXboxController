import requests
import json
import re

def migrate_data():
    url = "https://raw.githubusercontent.com/Ritterrh/Grandma3MitXboxController/refs/heads/main/wlt_data.json"
    
    # Daten laden
    print("Lade Daten von GitHub...")
    response = requests.get(url)
    old_data = response.json()
    
    # Schlagworte für den "Stab" (alles was kein Schauspieler im klassischen Sinne ist)
    staff_keywords = [
        'inszenierung', 'ausstattung', 'choreografie', 'dramaturgie', 
        'theaterpädagogik', 'regie', 'leitung', 'kostüme', 'bühne', 'assistenz'
    ]

    new_plays = []

    for item in old_data.get('daten', []):
        # 1. Besetzung & Stab trennen
        darsteller_list = []
        stab_list = []
        
        for person in item.get('besetzung', []):
            rolle = person.get('rolle', '')
            name = person.get('darsteller', 'Unbekannt')
            
            # Slug generieren (z.B. "Karin Eppler" -> "karin-eppler")
            slug = name.lower().replace(' ', '-').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
            slug = re.sub(r'[^a-z-]', '', slug)
            
            person_obj = {
                "name": name,
                "rolle_funktion": rolle,
                "person_slug": slug,
                "link": f"/team/{slug}"
            }
            
            # Check ob Stab oder Darsteller
            if any(keyword in rolle.lower() for keyword in staff_keywords):
                stab_list.append(person_obj)
            else:
                darsteller_list.append(person_obj)

        # 2. Medien sortieren (YouTube ID extrahieren)
        processed_medien = []
        for med in item.get('medien', []):
            m_obj = dict(med)
            if med['typ'] == 'youtube':
                # Extrahiert die ID aus https://www.youtube.com/watch?v=fJGROTL_IbY
                vid_id = med['url'].split('v=')[-1]
                m_obj['video_id'] = vid_id
            processed_medien.append(m_obj)

        # 3. Neues Objekt bauen (Vollständig!)
        new_entry = {
            "id": item.get("id"),
            "stamm_daten": {
                "titel": item.get("titel"),
                "subtitel": item.get("subtitel"),
                "genre_text": item.get("genre_liste"),
                "web_url": item.get("url"),
                "is_kjt": item.get("is_kjt", False),
                "spielzeiten": item.get("spielzeiten", [])
            },
            "inhalt": {
                "text": item.get("inhalt"),
                "presse": item.get("presse", []),
                "stimmen": item.get("publicumStimmen", []),
                "meta": item.get("meta_details", {})
            },
            "besetzung": {
                "darsteller": darsteller_list,
                "stab": stab_list
            },
            "termine": item.get("termine", []),
            "medien": processed_medien,
            "flags": item.get("flags", {}),
            "next_date": item.get("naechster_termin_iso")
        }
        new_plays.append(new_entry)

    # In neue Datei speichern
    output = {"daten": new_plays}
    with open('wlt_data_neu.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    
    print(f"Erfolgreich migriert! {len(new_plays)} Stücke in 'wlt_data_neu.json' gespeichert.")

if __name__ == "__main__":
    migrate_data()