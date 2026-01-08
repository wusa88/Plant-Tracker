import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pytz
import paho.mqtt.publish as publish

# --- KONFIGURATION ---
DB_FILE = "pflanzen_db.json"
BERLIN_TZ = pytz.timezone('Europe/Berlin')

MQTT_BROKER = "MQTT-Broker-IP"
MQTT_PORT = PORT 
MQTT_USER = "USERNAME"
MQTT_PASS = "PASWWORD"

# --- FUNKTIONEN ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []
    return []

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def send_mqtt_status(plant_name, status):
    clean_name = plant_name.replace(" ", "_").lower()
    topic = f"haus/pflanzen/{clean_name}/erinnerung"
    try:
        publish.single(
            topic=topic,
            payload=status,
            hostname=MQTT_BROKER,
            port=int(MQTT_PORT),
            auth={'username': MQTT_USER, 'password': MQTT_PASS},
            retain=True
        )
    except Exception as e:
        print(f"MQTT Fehler: {e}")

def check_overdue(last_watered_str, interval_days):
    if last_watered_str == "Noch nie":
        return True
    try:
        last_date = datetime.strptime(last_watered_str, "%d.%m.%Y, %H:%M")
        last_date = BERLIN_TZ.localize(last_date)
        due_date = last_date + timedelta(days=interval_days)
        return datetime.now(BERLIN_TZ) > due_date
    except:
        return False

# --- APP START ---
st.set_page_config(page_title="PlantCare Pro", page_icon="🌿", layout="wide")

# --- DESIGN: DARK MODE & COMPACT BUTTONS ---
st.markdown("""
    <style>
    .stApp { background-color: #1e1e1e; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #2d2d2d; }

    [data-testid="stExpander"] { 
        border: 1px solid #444; 
        border-radius: 12px; 
        background-color: #2d2d2d;
        margin-bottom: 10px;
    }

    [data-testid="stExpander"] summary p {
        color: #ffffff !important;
        font-weight: bold;
    }

    .block-container { padding-top: 1.5rem; }
    
    .status-label { font-size: 0.75rem; color: #aaaaaa; text-transform: uppercase; letter-spacing: 0.05rem; margin-top: 5px; }
    .status-red { color: #ff4b4b; font-weight: bold; font-size: 0.95rem; }
    .status-green { color: #28a745; font-weight: bold; font-size: 0.95rem; }
    
    .plant-info { font-size: 0.8rem; color: #cccccc; margin-top: 5px; margin-bottom: 5px; }
    
    .stImage { display: flex; justify-content: center; margin-bottom: 10px; }
    
    /* Buttons Abstand zueinander */
    .stButton { margin-bottom: -10px; }
    </style>
    """, unsafe_allow_html=True)

if 'plants' not in st.session_state:
    st.session_state.plants = load_data()

st.title("🌿 Pflanzen-Tracker Pro")

# --- SEITENLEISTE ---
with st.sidebar:
    st.header("Neue Pflanze")
    new_name = st.text_input("Name")
    new_interval = st.number_input("Intervall (Tage)", min_value=1, value=3)
    new_image = st.file_uploader("Bild", type=["jpg", "png", "jpeg"])
    
    if st.button("Speichern", use_container_width=True):
        if new_name and new_image:
            img_path = f"img_{new_name.replace(' ', '_').lower()}.jpg"
            with open(img_path, "wb") as f:
                f.write(new_image.getbuffer())
            
            st.session_state.plants.append({
                "name": new_name, "interval": new_interval, 
                "image": img_path, "last_watered": "Noch nie"
            })
            save_data(st.session_state.plants)
            send_mqtt_status(new_name, "false")
            st.rerun()

# --- HAUPTBEREICH: Gitter-Layout ---
if not st.session_state.plants:
    st.info("Noch keine Pflanzen angelegt.")
else:
    num_cols = 4 # Erhöht auf 4 Spalten für kompaktere Karten
    cols = st.columns(num_cols)

    for i, plant in enumerate(st.session_state.plants):
        with cols[i % num_cols]:
            is_overdue = check_overdue(plant['last_watered'], plant['interval'])
            
            if is_overdue:
                send_mqtt_status(plant['name'], "true")
                status_text = "⚠️ DURSTIG!"
                status_class = "status-red"
            else:
                status_text = "✅ OK"
                status_class = "status-green"

            with st.expander(f"{plant['name']}", expanded=True):
                # Bild klein und zentriert
                if os.path.exists(plant['image']):
                    st.image(plant['image'], width=120)
                
                # Info-Sektion
                st.markdown(f"<div class='status-label'>Status</div><div class='{status_class}'>{status_text}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='status-label'>Letztes Gießen</div><div class='plant-info'><b>{plant['last_watered']}</b></div>", unsafe_allow_html=True)
                
                # Intervall
                st.markdown("<div class='status-label'>Intervall (Tage)</div>", unsafe_allow_html=True)
                new_int = st.number_input("Tage", min_value=1, value=plant['interval'], key=f"int_{i}", label_visibility="collapsed")
                if new_int != plant['interval']:
                    st.session_state.plants[i]['interval'] = new_int
                    save_data(st.session_state.plants)
                    st.rerun()

                st.write("") # Abstand
                
                # Buttons untereinander
                if st.button(f"Gießen ✅", key=f"water_{i}", use_container_width=True):
                    now_str = datetime.now(BERLIN_TZ).strftime("%d.%m.%Y, %H:%M")
                    st.session_state.plants[i]['last_watered'] = now_str
                    save_data(st.session_state.plants)
                    send_mqtt_status(plant['name'], "false")
                    st.rerun()
                
                if st.button(f"Löschen 🗑️", key=f"del_{i}", use_container_width=True):
                    if os.path.exists(plant['image']):
                        try: os.remove(plant['image'])
                        except: pass
                    st.session_state.plants.pop(i)
                    save_data(st.session_state.plants)
                    st.rerun()
