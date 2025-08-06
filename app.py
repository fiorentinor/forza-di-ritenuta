import streamlit as st
import pandas as pd

# Dizionario delle traduzioni
translations = {
    "it": {
        "title": "🚂 Calcolo della forza di ritenuta minima",
        "select_lang": "Select language",
        "convoy_params_header": "Dati necessari per il calcolo",
        "loco1_label": "Seleziona la prima locomotiva (opzionale)",
        "loco2_label": "Seleziona la seconda locomotiva (opzionale)",
        "peso_label": "Inserisci il peso totale in tonnellate",
        "pendenza_label": "Inserisci la pendenza in ‰",
        "min_force": "💪 Forza di ritenuta minima necessaria:",
        "loco_force": "🚂 Forza di ritenuta della locomotiva:",
        "rem_force": "🚧 Forza di ritenuta da raggiungere con altri mezzi di frenatura :",
        "pendenza_warning": "⚠️ La pendenza supera il limite massimo gestito (30 ‰).",
        "staffa_warning": "ℹ️ **Avviso:** Per pendenze superiori al 20‰ o nelle sue immediate vicinanze, assicurare con una staffa d'arresto in più della forza di ritenuta minima.",
        "staffa_header": "🔧 Calcolo forza generata da una staffa",
        "staffa_peso_label": "Peso (t)",
        "staffa_assi_label": "Numero di assi",
        "staffa_button": "Calcola forza staffa",
        "staffa_result": "La staffa genera una forza di:",
        "max_kn": "(massimo 40 kN)",
    },
    "de": {
        "title": "🚂 Berechnung der Mindestfesthaltekraft",
        "select_lang": "Select language",
        "convoy_params_header": "Erforderliche Daten für die Berechnung",
        "loco1_label": "Erste Lokomotive auswählen (optional)",
        "loco2_label": "Zweite Lokomotive auswählen (optional)",
        "peso_label": "Gesamtgewicht in Tonnen eingeben",
        "pendenza_label": "Gefälle in ‰ eingeben",
        "min_force": "💪 Mindestfesthaltekraft:",
        "loco_force": "🚂 Lok-Festhaltekraft:",
        "rem_force": "🚧 Festhaltekraft, die mit anderen Bremseinrichtungen am Wagen erreicht werden muss:",
        "pendenza_warning": "⚠️ Das Gefälle überschreitet den maximal zulässigen Wert (30 ‰).",
        "staffa_warning": "ℹ️ **Hinweis:** Abgestellte Fahrzeuge mit oder unmittelbar gegen ein Gefälle von mehr als 20‰ sind in jedem Fall zusätzlich zur erforderlichen Mindestfesthaltekraft mit einem Hemmschuh zu sichern.",
        "staffa_header": "🔧 Berechnung der Hemmschuhkraft",
        "staffa_peso_label": "Gewicht (t)",
        "staffa_assi_label": "Anzahl der Achsen",
        "staffa_button": "Hemmschuhkraft berechnen",
        "staffa_result": "Der Hemmschuh erzeugt eine Kraft von:",
        "max_kn": "(maximal 40 kN)",
    }
}

# Selettore per la lingua
language = st.selectbox(translations["it"]["select_lang"], ["Italiano", "Deutsch"])
lang_code = "it" if language == "Italiano" else "de"
t = translations[lang_code]

# Titolo della pagina
st.title(t["title"])

# Caricamento del file CSV
try:
    df = pd.read_csv("ritenuta.csv", index_col=0)
    
    # Pulizia delle colonne
    df = df[[col for col in df.columns if col.replace(',', '.').replace('‰', '').strip().replace(' ', '').isdigit()]]
    df.columns = df.columns.astype(float)
    slopes = df.columns
    weights = df.index.astype(float)

    # Dizionario delle locomotive e forza generata
    locomotive_forze = {'Re 420': 50, 'Re 421': 50, 'Re 430': 50, 'Ae 1042': 56, 'Re 482': 57, 'Tm III': 19, 'Tm IV': 19, 'Re 474': 53, 'BR 185': 57, 'BR 187': 53, 'BR 186': 54, 'BR 189': 53, 'BR 193': 56}

    # Messaggi speciali per le locomotive che hanno 2 freni a mano
special_loco_messages = {
    "it": "(entrambi i freni a mano)",
    "de": "(beide Handbremse)"
    
    # Contenitore per gli input
    with st.container():
        st.header(t["convoy_params_header"])
        col1, col2 = st.columns(2)
        with col1:
            loco1 = st.selectbox(t["loco1_label"], [""] + list(locomotive_forze.keys()))
        with col2:
            loco2 = st.selectbox(t["loco2_label"], [""] + list(locomotive_forze.keys()))
        
        peso = st.number_input(t["peso_label"], min_value=0, step=1)
        pendenza = st.number_input(t["pendenza_label"], min_value=0, step=1)

    # Funzione di calcolo
    def calcola_forza(peso, pendenza):
        if pendenza > 30:
            return None

        # Interpolazione per la pendenza
        pendenza_bassa = max([s for s in slopes if s <= pendenza], default=slopes.min())
        pendenza_alta = min([s for s in slopes if s >= pendenza], default=slopes.max())

        # Interpola per il peso alla pendenza_bassa
        peso_basso_forza_pendenza_bassa = df.loc[weights[weights <= peso].max(), pendenza_bassa] if any(weights <= peso) else df.loc[weights.min(), pendenza_bassa]
        peso_alto_forza_pendenza_bassa = df.loc[weights[weights >= peso].min(), pendenza_bassa] if any(weights >= peso) else df.loc[weights.max(), pendenza_bassa]
        
        if peso_basso_forza_pendenza_bassa == peso_alto_forza_pendenza_bassa:
            forza_pendenza_bassa = peso_basso_forza_pendenza_bassa
        else:
            forza_pendenza_bassa = peso_basso_forza_pendenza_bassa + (peso_alto_forza_pendenza_bassa - peso_basso_forza_pendenza_bassa) * ((peso - weights[weights <= peso].max()) / (weights[weights >= peso].min() - weights[weights <= peso].max()))

        # Interpola per il peso alla pendenza_alta
        peso_basso_forza_pendenza_alta = df.loc[weights[weights <= peso].max(), pendenza_alta] if any(weights <= peso) else df.loc[weights.min(), pendenza_alta]
        peso_alto_forza_pendenza_alta = df.loc[weights[weights >= peso].min(), pendenza_alta] if any(weights >= peso) else df.loc[weights.max(), pendenza_alta]
        
        if peso_basso_forza_pendenza_alta == peso_alto_forza_pendenza_alta:
            forza_pendenza_alta = peso_basso_forza_pendenza_alta
        else:
            forza_pendenza_alta = peso_basso_forza_pendenza_alta + (peso_alto_forza_pendenza_alta - peso_basso_forza_pendenza_alta) * ((peso - weights[weights <= peso].max()) / (weights[weights >= peso].min() - weights[weights <= peso].max()))

        # Interpola il risultato finale e lo arrotonda a un intero
        if pendenza_bassa == pendenza_alta:
            return int(round(forza_pendenza_bassa))
        else:
            return int(round(forza_pendenza_bassa + (forza_pendenza_alta - forza_pendenza_bassa) * ((pendenza - pendenza_bassa) / (pendenza_alta - pendenza_bassa))))

    # Calcolo e visualizzazione dei risultati
    st.markdown("---")
    if peso > 0 and pendenza >= 0:
        forza_totale = calcola_forza(peso, pendenza)
        if forza_totale is None:
            st.warning(t["pendenza_warning"])
        else:
            forza_loco = 0
            if loco1 in locomotive_forze:
                forza_loco += locomotive_forze[loco1]
            if loco2 in locomotive_forze:
                forza_loco += locomotive_forze[loco2]

            forza_rimanente = max(forza_totale - forza_loco, 0)
            
            st.success(f"{t['min_force']} **{forza_totale:,.0f} kN**")
             if forza_loco > 0:
            special_message = ""
            if loco1 in ['Re 420', 'Re 421', 'Re 430'] or loco2 in ['Re 420', 'Re 421', 'Re 430']:
                special_message = special_loco_messages[lang_code]
                
            st.info(f"{t['loco_force']} **{forza_loco} kN** {special_message}")
            st.warning(f"{t['rem_force']} **{forza_rimanente:,.0f} kN**")
            
        if pendenza > 20:
            st.info(t["staffa_warning"])            if forza_loco > 0:
                st.info(f"{t['loco_force']} **{forza_loco} kN**")
                st.warning(f"{t['rem_force']} **{forza_rimanente:,.0f} kN**")
            if pendenza > 20:
                st.info(t["staffa_warning"])

    # Funzione per calcolare la forza generata da una staffa
    def forza_staffa(peso, assi):
        if assi <= 0:
            return 0
        peso_assiale = peso / assi
        forza = peso_assiale * 2
        return min(forza, 40)

    # Sezione per calcolo forza staffa
    st.markdown("---")
    st.subheader(t["staffa_header"])
    with st.container():
        col_staffa1, col_staffa2 = st.columns(2)
        with col_staffa1:
            peso_staffa = st.number_input(t["staffa_peso_label"], min_value=0, value=60, step=1)
        with col_staffa2:
            assi_staffa = st.number_input(t["staffa_assi_label"], min_value=1, value=4, step=1)

        if st.button(t["staffa_button"]):
            forza_generata = forza_staffa(peso_staffa, assi_staffa)
            st.success(f"**{t['staffa_result']} {int(round(forza_generata)):,.0f} kN** {t['max_kn']}")

except FileNotFoundError:
    st.error("Errore: Il file CSV non è stato trovato. Assicurati che il percorso sia corretto.")
