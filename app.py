import streamlit as st
import pandas as pd
import math
import json
import os

# -----------------------------------------------------------------------------
# 1. INITIALISIERUNG DER DATEN (SESSION STATE)
# -----------------------------------------------------------------------------
def save_data():
    data = {
        "course_db": json.loads(st.session_state.course_db.to_json(orient="records", force_ascii=False)),
        "plan": json.loads(st.session_state.plan.to_json(orient="records", force_ascii=False))
    }
    with open("studienplan.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def init_data():
    if 'course_db' not in st.session_state or 'plan' not in st.session_state:
        if os.path.exists("studienplan.json"):
            with open("studienplan.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            st.session_state.course_db = pd.DataFrame(data.get("course_db", []))
            
            plan_df = pd.DataFrame(data.get("plan", []))
            if plan_df.empty:
                st.session_state.plan = pd.DataFrame(columns=["Semester", "Name", "ECTS", "HSG_ECTS", "Kategorie", "Vertiefung", "Sprache", "Austausch", "Austausch_Typ", "Firma", "Dauer", "Ort", "Geschoben_Nach"])
            else:
                st.session_state.plan = plan_df
        else:
            # Hardcoded Pflichtkurse
            initial_courses = [
                {"Name": "Marketing", "ECTS": 4, "Kategorie": "Pflichtbereich", "Vertiefung": "", "Zwangssprache": None},
                {"Name": "Strategisches Management", "ECTS": 4, "Kategorie": "Pflichtbereich", "Vertiefung": "", "Zwangssprache": None},
                {"Name": "Methoden: Empirische Sozialforschung", "ECTS": 4, "Kategorie": "Pflichtbereich", "Vertiefung": "", "Zwangssprache": None},
                {"Name": "Methoden: Statistik", "ECTS": 4, "Kategorie": "Pflichtbereich", "Vertiefung": "", "Zwangssprache": None},
                {"Name": "Leadership & Human Resource Management", "ECTS": 4, "Kategorie": "Pflichtbereich", "Vertiefung": "", "Zwangssprache": None},
                {"Name": "Mikroökonomie II", "ECTS": 4, "Kategorie": "Pflichtbereich", "Vertiefung": "", "Zwangssprache": None},
                {"Name": "Makroökonomie II", "ECTS": 4, "Kategorie": "Pflichtbereich", "Vertiefung": "", "Zwangssprache": None},
                {"Name": "Grundlagen und Methoden der Informatik", "ECTS": 8, "Kategorie": "Pflichtbereich", "Vertiefung": "", "Zwangssprache": None},
                {"Name": "Corporate Finance (Eng)", "ECTS": 4, "Kategorie": "Pflichtbereich", "Vertiefung": "", "Zwangssprache": "EN"},
                {"Name": "Accounting, Controlling, Auditing", "ECTS": 4, "Kategorie": "Pflichtbereich", "Vertiefung": "", "Zwangssprache": None},
                {"Name": "Einführung in das Operations-Management", "ECTS": 4, "Kategorie": "Pflichtbereich", "Vertiefung": "", "Zwangssprache": None},
                {"Name": "Wirtschafts- und Steuerrecht", "ECTS": 8, "Kategorie": "Pflichtbereich", "Vertiefung": "", "Zwangssprache": None},
                {"Name": "Capstone-Projekt", "ECTS": 8, "Kategorie": "Pflichtbereich", "Vertiefung": "", "Zwangssprache": None},
            ]
            df = pd.DataFrame(initial_courses)
            df["Austausch"] = False
            df["Austausch_Typ"] = None
            st.session_state.course_db = df

            # Speicher für die geplante Semesterbelegung
            st.session_state.plan = pd.DataFrame(columns=["Semester", "Name", "ECTS", "HSG_ECTS", "Kategorie", "Vertiefung", "Sprache", "Austausch", "Austausch_Typ", "Firma", "Dauer", "Ort", "Geschoben_Nach"])
            
            save_data()

    # Spalten nachträglich absichern, falls eine veraltete JSON geladen wurde
    if "Austausch" not in st.session_state.course_db.columns:
        st.session_state.course_db["Austausch"] = False
        st.session_state.course_db["Austausch_Typ"] = None
    if "Austausch" not in st.session_state.plan.columns:
        st.session_state.plan["Austausch"] = False
        st.session_state.plan["Austausch_Typ"] = None
    if "HSG_ECTS" not in st.session_state.plan.columns:
        st.session_state.plan["HSG_ECTS"] = st.session_state.plan["ECTS"]
    if "Firma" not in st.session_state.plan.columns:
        st.session_state.plan["Firma"] = ""
        st.session_state.plan["Dauer"] = ""
        st.session_state.plan["Ort"] = ""
    if "Geschoben_Nach" not in st.session_state.plan.columns:
        st.session_state.plan["Geschoben_Nach"] = 0
        
    # Migration: Vertiefung statt Finance
    if "Vertiefung" not in st.session_state.course_db.columns:
        if "Finance" in st.session_state.course_db.columns:
            st.session_state.course_db["Vertiefung"] = st.session_state.course_db["Finance"].apply(lambda x: "Finance" if x else "")
        else:
            st.session_state.course_db["Vertiefung"] = ""
            
    if "Vertiefung" not in st.session_state.plan.columns:
        if "Finance" in st.session_state.plan.columns:
            st.session_state.plan["Vertiefung"] = st.session_state.plan["Finance"].apply(lambda x: "Finance" if x else "")
        else:
            st.session_state.plan["Vertiefung"] = ""
            
    if "Finance" in st.session_state.course_db.columns:
        st.session_state.course_db.drop(columns=["Finance"], inplace=True)
    if "Finance" in st.session_state.plan.columns:
        st.session_state.plan.drop(columns=["Finance"], inplace=True)
        
    # Bugfix: Corporate Finance ist nur Basisfach und zählt nicht zur Vertiefung
    if "Name" in st.session_state.course_db.columns:
        st.session_state.course_db.loc[st.session_state.course_db["Name"] == "Corporate Finance (Eng)", "Vertiefung"] = ""
    if "Name" in st.session_state.plan.columns:
        st.session_state.plan.loc[st.session_state.plan["Name"] == "Corporate Finance (Eng)", "Vertiefung"] = ""

    # Migration: Kontext-Kategorien umbenennen, damit alte Speicherstände weiterhin funktionieren
    if "Kategorie" in st.session_state.course_db.columns:
        st.session_state.course_db["Kategorie"] = st.session_state.course_db["Kategorie"].replace(
            {"Kontext-Fokus": "Fokusbereich", "Kontext-Sprache": "Skills und Sprachen"}
        )
    if "Kategorie" in st.session_state.plan.columns:
        st.session_state.plan["Kategorie"] = st.session_state.plan["Kategorie"].replace(
            {"Kontext-Fokus": "Fokusbereich", "Kontext-Sprache": "Skills und Sprachen"}
        )
        
    # Migration & Bugfix: Vertiefungskurs im Austausch ist Pflichtwahlbereich
    if "Austausch_Typ" in st.session_state.course_db.columns:
        st.session_state.course_db.loc[st.session_state.course_db["Austausch_Typ"] == "1:1 Vertiefungskurs für Finance", "Austausch_Typ"] = "1:1 Vertiefungskurs"
        st.session_state.course_db.loc[st.session_state.course_db["Austausch_Typ"] == "1:1 Vertiefungskurs", "Kategorie"] = "Pflichtwahlbereich"
    if "Austausch_Typ" in st.session_state.plan.columns:
        st.session_state.plan.loc[st.session_state.plan["Austausch_Typ"] == "1:1 Vertiefungskurs für Finance", "Austausch_Typ"] = "1:1 Vertiefungskurs"
        st.session_state.plan.loc[st.session_state.plan["Austausch_Typ"] == "1:1 Vertiefungskurs", "Kategorie"] = "Pflichtwahlbereich"

# -----------------------------------------------------------------------------
# 2. HILFSFUNKTIONEN FÜR LOGIK & BERECHNUNG
# -----------------------------------------------------------------------------
def add_to_db(name, ects, category, vertiefung, is_exchange=False, exchange_type=None):
    new_course = {"Name": name, "ECTS": float(ects), "Kategorie": category, "Vertiefung": vertiefung, "Zwangssprache": None, "Austausch": is_exchange, "Austausch_Typ": exchange_type}
    st.session_state.course_db = pd.concat([st.session_state.course_db, pd.DataFrame([new_course])], ignore_index=True)
    save_data()

def add_to_plan(semester, course_name, language, is_exchange=False, exchange_type=None, custom_ects=None, hsg_ects=None):
    if is_exchange and exchange_type in ["1:1 Vertiefungskurs", "Pauschalanrechnung", "Sprachkurs (Landessprache Gast-Uni)"]:
        category = "Pflichtwahlbereich" if exchange_type == "1:1 Vertiefungskurs" else "Pauschalanrechnung"
        # Dynamische Logik: 1:1 Vertiefungskurs wird automatisch der aktuellen Vertiefung zugeordnet
        vert_val = st.session_state.target_vertiefung if (exchange_type == "1:1 Vertiefungskurs" and st.session_state.target_vertiefung != "Keine Vertiefung") else ""
        new_plan_entry = {
            "Semester": semester, 
            "Name": course_name, 
            "ECTS": float(custom_ects), 
            "HSG_ECTS": float(hsg_ects) if hsg_ects is not None else float(custom_ects),
            "Kategorie": category, 
            "Vertiefung": vert_val, 
            "Sprache": language,
            "Austausch": True,
            "Austausch_Typ": exchange_type,
            "Geschoben_Nach": 0
        }
    else:
        db_match = st.session_state.course_db[st.session_state.course_db["Name"] == course_name]
        if db_match.empty:
            return
        course_data = db_match.iloc[0]
        if pd.notna(course_data["Zwangssprache"]):
            language = course_data["Zwangssprache"]
            
        final_is_exch = is_exchange or course_data.get("Austausch", False)
        final_exch_type = exchange_type or course_data.get("Austausch_Typ", None)
            
        final_ects = float(custom_ects) if custom_ects is not None else float(course_data["ECTS"])
        final_hsg = float(hsg_ects) if hsg_ects is not None else final_ects
            
        new_plan_entry = {
            "Semester": semester, 
            "Name": course_data["Name"], 
            "ECTS": final_ects,
            "HSG_ECTS": final_hsg,
            "Kategorie": course_data["Kategorie"], 
            "Vertiefung": course_data.get("Vertiefung", ""), 
            "Sprache": language,
            "Austausch": final_is_exch,
            "Austausch_Typ": final_exch_type,
            "Geschoben_Nach": 0
        }
    st.session_state.plan = pd.concat([st.session_state.plan, pd.DataFrame([new_plan_entry])], ignore_index=True)
    save_data()

def add_internship_to_plan(semester, firma, dauer, ort):
    new_plan_entry = {
        "Semester": semester, 
        "Name": f"Praktikum: {firma}", 
        "ECTS": 0.0,
        "HSG_ECTS": 0.0,
        "Kategorie": "Praktikum", 
        "Vertiefung": "", 
        "Sprache": "DE",
        "Austausch": False,
        "Austausch_Typ": None,
        "Firma": firma,
        "Dauer": dauer,
        "Ort": ort,
        "Geschoben_Nach": 0
    }
    st.session_state.plan = pd.concat([st.session_state.plan, pd.DataFrame([new_plan_entry])], ignore_index=True)
    save_data()

def remove_from_plan(course_name):
    st.session_state.plan = st.session_state.plan[st.session_state.plan["Name"] != course_name]
    save_data()

# -----------------------------------------------------------------------------
# 3. BENUTZEROBERFLÄCHE (UI)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="HSG BWL Studienplaner", layout="wide")
init_data()

st.title("🎓 HSG Studienplaner (Major BWL)")

VERTIEFUNGEN = [
    "Accounting, Controlling, Auditing",
    "Entrepreneurship",
    "Finance",
    "International Management",
    "Leadership & Human Resource Management",
    "Marketing",
    "Operations- und Innovationsmanagement",
    "Strategisches Management",
    "Unternehmerische Informatik"
]

if "target_vertiefung" not in st.session_state:
    st.session_state.target_vertiefung = "Keine Vertiefung"
if "auto_detected_vert" not in st.session_state:
    st.session_state.auto_detected_vert = ""

# Automatische Erkennung der Vertiefung (3 oder mehr Kurse)
plan_verts = st.session_state.plan[st.session_state.plan["Vertiefung"].isin(VERTIEFUNGEN)]["Vertiefung"].value_counts()
if not plan_verts.empty and plan_verts.iloc[0] >= 3:
    auto_vert = plan_verts.index[0]
    if st.session_state.auto_detected_vert != auto_vert:
        st.session_state.target_vertiefung = auto_vert
        st.session_state.auto_detected_vert = auto_vert
        st.toast(f"🎯 Automatisch Vertiefung '{auto_vert}' ausgewählt (3+ Kurse erkannt).")

# Farb-Mapping für die Kategorien (rgba für schöne Transparenz in Hell- & Dunkelmodus)
CATEGORY_COLORS = {
    "Pflichtbereich": "rgba(160, 100, 60, 0.4)",       # Braun
    "Pflichtwahlbereich": "rgba(28, 131, 225, 0.4)",   # Blau (Vertiefung / PW)
    "Wahlbereich": "rgba(9, 171, 59, 0.4)",            # Grün
    "Fokusbereich": "rgba(255, 210, 0, 0.4)",          # Gelb (Kontext)
    "Skills und Sprachen": "rgba(255, 210, 0, 0.4)",   # Gelb (Kontext)
    "Bachelorarbeit": "rgba(150, 0, 200, 0.4)",        # Violett (kein Rot!)
    "Pauschalanrechnung": "rgba(160, 160, 160, 0.4)",  # Grau
    "Praktikum": "rgba(0, 150, 255, 0.4)"              # Hellblau
}

# Tabs für die zwei Hauptbereiche
tab1, tab2 = st.tabs(["📊 Dashboard & Kurs-Datenbank", "🗓️ Semester-Planung"])

# --- BEREICH A: DASHBOARD & DATENBANK ---
with tab1:
    st.header("🎯 Deine Ziel-Vertiefung")
    st.selectbox(
        "Ziel-Vertiefung wählen",
        options=["Keine Vertiefung"] + VERTIEFUNGEN,
        key="target_vertiefung"
    )
    st.divider()

    plan_df = st.session_state.plan
    
    # Daten aufteilen für Berechnungen
    regular_df = plan_df[plan_df["Austausch"] != True]
    exchange_df = plan_df[plan_df["Austausch"] == True]
    
    has_capstone_or_ba = plan_df["Name"].isin(["Capstone-Projekt", "Bachelorarbeit"]).any()
    
    # Base Berechnungen (Ohne Austausch)
    eng_ects = regular_df[regular_df["Sprache"] == "EN"]["ECTS"].sum()
    
    target_v = st.session_state.target_vertiefung
    vertiefung_courses_ects = 0.0
    if target_v != "Keine Vertiefung":
        vertiefung_courses_ects = regular_df[(regular_df["Vertiefung"] == target_v) & (regular_df["Kategorie"].isin(["Pflichtbereich", "Pflichtwahlbereich"]))]["ECTS"].sum()
    
    pw_ects = regular_df[regular_df["Kategorie"] == "Pflichtwahlbereich"]["ECTS"].sum()
    w_ects = regular_df[regular_df["Kategorie"] == "Wahlbereich"]["ECTS"].sum()
    skills_ects = regular_df[regular_df["Kategorie"] == "Skills und Sprachen"]["ECTS"].sum()
    fokus_ects = regular_df[regular_df["Kategorie"] == "Fokusbereich"]["ECTS"].sum()
    
    total_ects = regular_df["ECTS"].sum()
    
    vert_exch_courses_used = 0
    pauschal_pool = 0.0
    pauschal_sources = []
    
    # Austausch Semester Logik
    for sem in exchange_df["Semester"].unique():
        sem_exch = exchange_df[exchange_df["Semester"] == sem]
        sem_total = sem_exch["ECTS"].sum()
        
        if sem_total >= 16.0: # Minimum-Check für das Semester
            eng_ects += sem_exch[sem_exch["Sprache"] == "EN"]["ECTS"].sum()
            
            pflicht_ects = 0.0
            pw_vert_ects = 0.0
            pauschal_this_sem = 0.0
            
            for _, row in sem_exch.iterrows():
                if row["Austausch_Typ"] == "1:1 Pflichtkurs":
                    hsg_e = row.get("HSG_ECTS", st.session_state.course_db[st.session_state.course_db["Name"] == row["Name"]].iloc[0]["ECTS"])
                    allowed = min(row["ECTS"], hsg_e)
                    overflow = max(0.0, row["ECTS"] - allowed)
                    pflicht_ects += allowed
                    if overflow > 0:
                        pauschal_this_sem += overflow
                        pauschal_sources.append({"name": f"{row['Name']} (Überschuss)", "ects": overflow})
                elif row["Austausch_Typ"] == "1:1 Vertiefungskurs":
                    hsg_e = row.get("HSG_ECTS", 4.0)
                    if vert_exch_courses_used < 1:
                        allowed = min(row["ECTS"], hsg_e)
                        overflow = max(0.0, row["ECTS"] - allowed)
                        pw_vert_ects += allowed
                        if target_v != "Keine Vertiefung" and row.get("Vertiefung") == target_v:
                            vertiefung_courses_ects += allowed
                        if overflow > 0:
                            pauschal_this_sem += overflow
                            pauschal_sources.append({"name": f"{row['Name']} (Überschuss)", "ects": overflow})
                        vert_exch_courses_used += 1
                    else:
                        pauschal_this_sem += row["ECTS"]
                        pauschal_sources.append({"name": f"{row['Name']} (als Pauschal)", "ects": row["ECTS"]})
                elif row["Austausch_Typ"] == "Pauschalanrechnung":
                    pauschal_this_sem += row["ECTS"]
                    pauschal_sources.append({"name": row["Name"], "ects": row["ECTS"]})
                elif row["Austausch_Typ"] == "Sprachkurs (Landessprache Gast-Uni)":
                    hsg_e = row.get("HSG_ECTS", 4.0)
                    allowed = min(row["ECTS"], hsg_e)
                    pauschal_this_sem += allowed
                    pauschal_sources.append({"name": f"{row['Name']} (Sprachkurs)", "ects": allowed})
            
            # Maximum-Check: 32 ECTS pro Semester
            total_this_sem = pflicht_ects + pw_vert_ects + pauschal_this_sem
            if total_this_sem > 32.0:
                excess = total_this_sem - 32.0
                pauschal_this_sem = max(0.0, pauschal_this_sem - excess)
                pauschal_sources.append({"name": f"Kappung Semester {int(sem)} (> 32 ECTS)", "ects": -excess})
            
            total_ects += (pflicht_ects + pw_vert_ects)
            pauschal_pool += pauschal_this_sem
            pw_ects += pw_vert_ects
            
    # Pauschalanrechnung Wasserfall
    pauschal_pool_floor = math.floor(pauschal_pool)
    if pauschal_pool > pauschal_pool_floor:
        pauschal_sources.append({"name": "Abrundung (nur ganze ECTS)", "ects": -(pauschal_pool - pauschal_pool_floor)})
    pauschal_pool = pauschal_pool_floor
    
    total_pauschal_distributed = 0.0
    pauschal_distributions = []
    
    # SCHRITT 1: Wahlbereich (Wahlbereich_Max = 16 ECTS)
    space_wahl_base = max(0.0, 16.0 - w_ects)
    space_wahl_master = max(0.0, 20.0 - w_ects - pw_ects)
    space_wahl = min(space_wahl_base, space_wahl_master)
    
    fill_wahl = min(pauschal_pool, space_wahl)
    w_ects += fill_wahl
    pauschal_pool -= fill_wahl
    total_pauschal_distributed += fill_wahl
    if fill_wahl > 0:
        pauschal_distributions.append({"target": "Wahlbereich", "ects": fill_wahl})
    
    # SCHRITT 2: Fokusbereich (Maximal auffüllen bis Kontext-Total = 24 ECTS)
    space_fokus = max(0.0, 24.0 - skills_ects - fokus_ects)
    fill_fokus = min(pauschal_pool, space_fokus)
    fokus_ects += fill_fokus
    pauschal_pool -= fill_fokus
    total_pauschal_distributed += fill_fokus
    if fill_fokus > 0:
        pauschal_distributions.append({"target": "Fokusbereich", "ects": fill_fokus})
    
    # SCHRITT 3: Pflichtwahlbereich (Pflichtwahl_Max = 4 ECTS)
    fill_pw = 0.0
    if vert_exch_courses_used == 0:
        space_pw_base = max(0.0, 4.0 - pw_ects)
        space_pw_master = max(0.0, 20.0 - w_ects - pw_ects)
        space_pw = min(space_pw_base, space_pw_master)
        
        fill_pw = min(pauschal_pool, space_pw)
        pw_ects += fill_pw
        pauschal_pool -= fill_pw
        total_pauschal_distributed += fill_pw
        if fill_pw > 0:
            pauschal_distributions.append({"target": "Pflichtwahlbereich", "ects": fill_pw})
            
    total_ects += total_pauschal_distributed
    
    st.header("📈 Dein Studienfortschritt")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1. Major-Studium (120 ECTS)")
        st.progress(min(total_ects / 120.0, 1.0))
        st.write(f"**{total_ects} / 120 ECTS**")
        
        st.write("---")
        st.write("**Zusatzbedingungen:**")
        st.write(f"✅ Pflichtwahl (min. 4): {pw_ects} ECTS" if pw_ects >= 4 else f"❌ Pflichtwahl (min. 4): {pw_ects} ECTS")
        st.write(f"✅ PW + Wahl (exakt 20): {pw_ects + w_ects} ECTS" if (pw_ects + w_ects) >= 20 else f"❌ PW + Wahl (Ziel: 20): {pw_ects + w_ects} ECTS")
        st.write(f"✅ Fokusbereich (12-24): {fokus_ects} ECTS" if 12 <= fokus_ects <= 24 else f"❌ Fokusbereich (min. 12, max. 24): {fokus_ects} ECTS")
        st.write(f"✅ Skills und Sprachen (0-12): {skills_ects} ECTS" if 0 <= skills_ects <= 12 else f"❌ Skills und Sprachen (max. 12): {skills_ects} ECTS")
        st.write(f"✅ Kontext Total (exakt 24): {fokus_ects + skills_ects} ECTS" if (fokus_ects + skills_ects) == 24 else f"❌ Kontext Total (Ziel: 24): {fokus_ects + skills_ects} ECTS")

    with col2:
        st.subheader("2. Englisch-Regel (12 ECTS)")
        st.progress(min(eng_ects / 12.0, 1.0))
        st.write(f"**{eng_ects} / 12 ECTS** (auf Englisch)")
    
    with col3:
        if target_v == "Keine Vertiefung":
            st.subheader("3. Vertiefung")
            st.info("Keine Ziel-Vertiefung in den Einstellungen ausgewählt.")
        else:
            st.subheader(f"3. Vertiefung: {target_v}")
            st.progress(min(vertiefung_courses_ects / 16.0, 1.0))
            st.write(f"**{vertiefung_courses_ects} / 16 ECTS** ({target_v})")
            
            if target_v in ["International Management", "Entrepreneurship"]:
                st.info("Achtung: Diese Vertiefung hat keine klassische Pflichtveranstaltung. Es müssen stattdessen die spezifischen Pflichtwahlveranstaltungen dieser Bereiche sowie 3 weitere Pflichtwahlkurse daraus belegt werden.")
                
            if has_capstone_or_ba:
                st.success("✅ Capstone-Projekt oder Bachelorarbeit absolviert.")
            else:
                st.warning("❌ Capstone-Projekt oder Bachelorarbeit fehlt.")
            
            if vertiefung_courses_ects >= 16 and has_capstone_or_ba:
                st.success(f"🎉 Bedingungen für Vertiefung '{target_v}' erfüllt!")

    st.divider()

    st.header("🪣 Visuelle Gefäss-Übersicht (Diagramme)")
    st.markdown("Hier siehst du auf einen Blick, wie weit deine Gefässe gefüllt sind. **Fahre mit der Maus über die farbigen Abschnitte**, um zu sehen, welcher Kurs wie viele ECTS ausmacht!")
    
    def render_bucket_bar(title, target_ects, segments):
        total_ects = sum(s[1] for s in segments)
        denominator = target_ects if target_ects > 0 else 1
        
        html = f'<div style="margin-bottom: 25px; font-family: sans-serif;">'
        html += f'<div style="display: flex; justify-content: space-between; margin-bottom: 8px;">'
        html += f'<strong style="font-size: 16px;">{title}</strong>'
        html += f'<span style="color: #888; font-size: 15px; font-weight: bold;">{total_ects} / {target_ects} ECTS</span>'
        html += f'</div>'
        html += f'<div style="display: flex; height: 48px; width: 100%; background-color: rgba(128,128,128,0.15); border-radius: 6px; overflow: hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);">'
        
        drawn_pct = 0.0
        for name, ects, color in segments:
            if ects > 0:
                width_pct = (ects / denominator) * 100
                if drawn_pct + width_pct > 100.0:
                    width_pct = 100.0 - drawn_pct
                
                if width_pct > 0:
                    html += f'<div title="{name} ({ects} ECTS)" style="width: {width_pct}%; background-color: {color}; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #111; border-right: 1px solid rgba(255,255,255,0.5); white-space: nowrap; overflow: hidden; text-shadow: 0px 0px 4px rgba(255,255,255,0.8); padding: 0 4px;">'
                    html += f'<span style="font-size: 13px; font-weight: bold; line-height: 1.2;">{ects}</span>'
                    html += f'<span style="font-size: 10px; font-weight: normal; line-height: 1.2; text-overflow: ellipsis; overflow: hidden; max-width: 100%;">{name}</span>'
                    html += f'</div>'
                drawn_pct += width_pct
                
        html += '</div></div>'
        st.markdown(html, unsafe_allow_html=True)

    # Diagramm 1: Pflichtbereich
    b1_segments = []
    pflicht_courses = plan_df[plan_df["Kategorie"] == "Pflichtbereich"]
    for _, r in pflicht_courses.iterrows():
        name = r["Name"]
        is_vert = r.get("Vertiefung", "") == target_v and target_v != "Keine Vertiefung"
        if r["Austausch"] and r["Austausch_Typ"] == "1:1 Pflichtkurs":
            hsg_e = r.get("HSG_ECTS", st.session_state.course_db[st.session_state.course_db["Name"] == name].iloc[0]["ECTS"])
            ects = min(r['ECTS'], hsg_e)
        else:
            ects = r['ECTS']
            
        if ects > 0:
            color = CATEGORY_COLORS["Pflichtwahlbereich"] if is_vert else CATEGORY_COLORS["Pflichtbereich"]
            b1_segments.append((name, ects, color))
            
    render_bucket_bar("📕 Pflichtbereich", 64.0, b1_segments)

    # Diagramm 2: PW + Wahlbereich
    b2_segments = []
    pw_courses = regular_df[regular_df["Kategorie"] == "Pflichtwahlbereich"]
    for _, r in pw_courses.iterrows():
        is_vert = r.get("Vertiefung", "") == target_v and target_v != "Keine Vertiefung"
        color = CATEGORY_COLORS["Pflichtwahlbereich"] if is_vert else CATEGORY_COLORS["Pflichtwahlbereich"]
        b2_segments.append((r["Name"], r["ECTS"], color))
        
    vert_exch_courses = exchange_df[exchange_df["Austausch_Typ"] == "1:1 Vertiefungskurs"]
    vert_exch_drawn = 0
    for _, r in vert_exch_courses.iterrows():
        if vert_exch_drawn < 1:
            hsg_e = r.get("HSG_ECTS", 4.0)
            ects = min(r['ECTS'], hsg_e)
            if ects > 0:
                b2_segments.append((r["Name"] + " [Vert.]", ects, CATEGORY_COLORS["Pflichtwahlbereich"]))
            vert_exch_drawn += 1

    w_courses = regular_df[regular_df["Kategorie"] == "Wahlbereich"]
    for _, r in w_courses.iterrows():
        is_vert = r.get("Vertiefung", "") == target_v and target_v != "Keine Vertiefung"
        color = CATEGORY_COLORS["Pflichtwahlbereich"] if is_vert else CATEGORY_COLORS["Wahlbereich"]
        b2_segments.append((r["Name"], r["ECTS"], color))
    if fill_pw > 0:
        b2_segments.append(("✨ Pauschalanrechnung (in PW)", fill_pw, CATEGORY_COLORS["Pauschalanrechnung"]))
    if fill_wahl > 0:
        b2_segments.append(("✨ Pauschalanrechnung (in Wahl)", fill_wahl, CATEGORY_COLORS["Pauschalanrechnung"]))
        
    render_bucket_bar("📘 PW + Wahlbereich", 20.0, b2_segments)

    # Diagramm 3: Kontextstudium
    b3_segments = []
    f_courses = regular_df[regular_df["Kategorie"] == "Fokusbereich"]
    for _, r in f_courses.iterrows():
        b3_segments.append((r["Name"], r["ECTS"], CATEGORY_COLORS["Fokusbereich"]))
    s_courses = regular_df[regular_df["Kategorie"] == "Skills und Sprachen"]
    for _, r in s_courses.iterrows():
        b3_segments.append((r["Name"], r["ECTS"], CATEGORY_COLORS["Skills und Sprachen"]))
    if fill_fokus > 0:
        b3_segments.append(("✨ Pauschalanrechnung (in Fokus)", fill_fokus, CATEGORY_COLORS["Pauschalanrechnung"]))
        
    render_bucket_bar("📒 Kontextstudium (Fokus + Skills)", 24.0, b3_segments)

    # Diagramm 4: Bachelorarbeit (falls vorhanden)
    b4_segments = []
    ba_courses = regular_df[regular_df["Kategorie"] == "Bachelorarbeit"]
    for _, r in ba_courses.iterrows():
        b4_segments.append((r["Name"], r["ECTS"], CATEGORY_COLORS["Bachelorarbeit"]))
    if b4_segments:
        render_bucket_bar("🎓 Abschluss (Bachelorarbeit)", sum(s[1] for s in b4_segments), b4_segments)

    if pauschal_sources or pauschal_distributions:
        with st.expander("✨ Details zur Zusammensetzung und Verteilung der Pauschalanrechnung"):
            c_src, c_dist = st.columns(2)
            
            with c_src:
                st.markdown("**1. Herkunft (Pool-Aufbau):**")
                for src in pauschal_sources:
                    prefix = "+" if src["ects"] > 0 else "-"
                    st.write(f"- {src['name']}: **{prefix} {abs(src['ects'])} ECTS**")
                st.markdown(f"**Total Pool: {pauschal_pool_floor} ECTS**")
                
            with c_dist:
                st.markdown("**2. Verteilung (Wasserfall):**")
                if pauschal_distributions:
                    for dist in pauschal_distributions:
                        st.write(f"- Aufgefüllt in **{dist['target']}**: **{dist['ects']} ECTS**")
                else:
                    st.write("- *Keine ECTS verteilt.*")
                    
                if pauschal_pool > 0:
                    st.write(f"- ⚠️ **Verfallen**: **{pauschal_pool} ECTS**")

    if pauschal_pool > 0:
        st.info(f"ℹ️ **{pauschal_pool} ECTS** überschüssige Credits können nicht verbucht werden.")

    st.divider()

    st.header("💼 Deine geplanten Praktika")
    internships_df = plan_df[plan_df["Kategorie"] == "Praktikum"]
    if not internships_df.empty:
        for idx, row in internships_df.iterrows():
            st.success(f"**{int(row['Semester'])}. Semester:** Praktikum bei **{row['Firma']}** in {row['Ort']} (Dauer: {row['Dauer']})")
    else:
        st.info("Es sind noch keine Praktika geplant.")

    st.divider()

    st.header(" Deine Semester-Zusammenfassung")
    if not plan_df.empty:
        first_vert_exch_idx = None
        vert_exch_matches = plan_df[plan_df["Austausch_Typ"] == "1:1 Vertiefungskurs"]
        if not vert_exch_matches.empty:
            first_vert_exch_idx = vert_exch_matches.index[0]

        for s in sorted(plan_df["Semester"].unique()):
            s_df = plan_df[(plan_df["Semester"] == s) & (plan_df["Kategorie"] != "Praktikum")]
            s_intern = plan_df[(plan_df["Semester"] == s) & (plan_df["Kategorie"] == "Praktikum")]
            course_badges = []
            
            for _, r in s_intern.iterrows():
                bg_color = CATEGORY_COLORS["Praktikum"]
                name_display = f"💼 Praktikum ({r['Firma']})"
                course_badges.append(f"<span style='background-color: {bg_color}; padding: 2px 6px; border-radius: 4px; margin-right: 4px; margin-bottom: 4px; display: inline-block;'>{name_display}</span>")
                
            for idx, r in s_df.iterrows():
                is_vert = r.get("Vertiefung", "") == target_v and target_v != "Keine Vertiefung"
                is_exch_vert = (r.get("Austausch_Typ") == "1:1 Vertiefungskurs")
                
                if is_exch_vert:
                    if idx == first_vert_exch_idx:
                        bg_color = CATEGORY_COLORS["Pflichtwahlbereich"]
                        name_display = r['Name']
                    else:
                        bg_color = CATEGORY_COLORS["Pauschalanrechnung"]
                        name_display = f"{r['Name']} (Pauschal)"
                else:
                    bg_color = CATEGORY_COLORS["Pflichtwahlbereich"] if is_vert else CATEGORY_COLORS.get(r['Kategorie'], "rgba(160, 160, 160, 0.4)")
                    name_display = r['Name']
                    
                schieben = int(r.get('Geschoben_Nach', 0)) if pd.notna(r.get('Geschoben_Nach')) else 0
                if schieben > 0:
                    name_display = f"<del>{name_display}</del> ➡️ Sem {schieben}"
                    
                course_badges.append(f"<span style='background-color: {bg_color}; padding: 2px 6px; border-radius: 4px; margin-right: 4px; margin-bottom: 4px; display: inline-block;'>{name_display}</span>")
                
            s_geschoben = plan_df[(plan_df["Geschoben_Nach"] == s) & (plan_df["Kategorie"] != "Praktikum")]
            for idx, r in s_geschoben.iterrows():
                bg_color = "rgba(200, 200, 200, 0.4)"
                name_display = f"📌 {r['Name']} (aus Sem {int(r['Semester'])})"
                course_badges.append(f"<span style='background-color: {bg_color}; padding: 2px 6px; border-radius: 4px; margin-right: 4px; margin-bottom: 4px; display: inline-block;'>{name_display}</span>")
                
            ects_sum = s_df["ECTS"].sum()
            st.markdown(f"**{s}. Semester ({ects_sum} ECTS):** {' '.join(course_badges)}", unsafe_allow_html=True)
    else:
        st.info("Es sind noch keine Kurse geplant.")

    st.divider()

    # Kurs hinzufügen UI
    st.header("📚 Eigene Kurse zur Datenbank hinzufügen")
    with st.container():
        db_len = len(st.session_state.course_db)
        is_exch_db = st.checkbox("Im Austauschsemester absolviert?", key="exch_db")
        if is_exch_db:
            c1, c2, c3 = st.columns([1, 2, 3])
            with c1:
                new_ects = st.number_input("ECTS", min_value=1.0, max_value=20.0, value=4.0, step=0.5, key="ects_db")
            with c2:
                exch_type_db = st.selectbox("Austausch-Typ", ["1:1 Vertiefungskurs", "Pauschalanrechnung", "Sprachkurs (Landessprache Gast-Uni)"], key="type_db")
            with c3:
                new_name = st.text_input("Kursname", key=f"name_db_{db_len}")
            
            if st.button("Kurs zur Datenbank hinzufügen", key="btn_add_exch_db"):
                if new_name:
                    if new_name not in st.session_state.course_db["Name"].values:
                        cat = "Pflichtwahlbereich" if exch_type_db == "1:1 Vertiefungskurs" else "Pauschalanrechnung"
                        v_val = st.session_state.target_vertiefung if (exch_type_db == "1:1 Vertiefungskurs" and st.session_state.target_vertiefung != "Keine Vertiefung") else ""
                        add_to_db(new_name, new_ects, cat, v_val, is_exchange=True, exchange_type=exch_type_db)
                        st.success(f"'{new_name}' erfolgreich hinzugefügt!")
                        st.rerun()
                    else:
                        st.error("Ein Kurs mit diesem Namen existiert bereits.")
                else:
                    st.warning("Bitte gib einen Kursnamen ein.")
        else:
            c1, c2, c3, c4 = st.columns([1, 2, 1, 2])
            with c1:
                new_ects = st.number_input("ECTS", min_value=1.0, max_value=20.0, value=4.0, step=0.5, key="ects_db_norm")
            with c2:
                new_category = st.selectbox("Kategorie", ["Pflichtwahlbereich", "Wahlbereich", "Fokusbereich", "Skills und Sprachen", "Bachelorarbeit"], key="cat_db_norm")
            with c3:
                new_vert_selection = st.selectbox("Gehört zu Vertiefung?", ["Keine"] + VERTIEFUNGEN, key="vert_db_norm")
                new_vertiefung = new_vert_selection if new_vert_selection != "Keine" else ""
            with c4:
                new_name = st.text_input("Kursname", key=f"name_db_norm_{db_len}")
            
            if st.button("Kurs zur Datenbank hinzufügen", key="btn_add_norm_db"):
                if new_name:
                    if new_name not in st.session_state.course_db["Name"].values:
                        add_to_db(new_name, new_ects, new_category, new_vertiefung, is_exchange=False, exchange_type=None)
                        st.success(f"'{new_name}' erfolgreich hinzugefügt!")
                        st.rerun()
                    else:
                        st.error("Ein Kurs mit diesem Namen existiert bereits.")
                else:
                    st.warning("Bitte gib einen Kursnamen ein.")

    with st.expander("Ganze Kurs-Datenbank ansehen & bearbeiten"):
        st.info("💡 **Tipp:** Klicke direkt in die Tabelle, um Namen, ECTS oder Kategorien zu ändern. Um einen Kurs zu löschen, markiere die Zeile ganz links und drücke die 'Delete/Löschen'-Taste auf deiner Tastatur (oder klicke auf das Papierkorb-Symbol). Pflichtkurse, die noch keinem Semester zugewiesen sind, werden **rot** markiert. *(Hinweis: Eigene, nicht geplante Kurse werden hier zur Übersichtlichkeit ausgeblendet.)*")
        
        display_db = st.session_state.course_db.copy()
        
        if not st.session_state.plan.empty:
            planned_names = st.session_state.plan["Name"].unique()
            plan_mapping = st.session_state.plan.groupby("Name")["Semester"].apply(lambda x: ", ".join(map(str, sorted(set(x))))).to_dict()
        else:
            planned_names = []
            plan_mapping = {}
            
        display_db["Geplant in Semester"] = display_db["Name"].map(plan_mapping).fillna("-")
        
        # Zeige nur Pflichtkurse ODER bereits geplante Kurse
        is_visible = (display_db["Kategorie"] == "Pflichtbereich") | (display_db["Name"].isin(planned_names))
        visible_db = display_db[is_visible].copy()
        
        def highlight_unplanned(row):
            if row["Kategorie"] == "Pflichtbereich" and row["Geplant in Semester"] == "-":
                return ["background-color: rgba(255, 75, 75, 0.4)"] * len(row)
            return [""] * len(row)
            
        styled_db = visible_db.style.apply(highlight_unplanned, axis=1)
        
        edited_db = st.data_editor(
            styled_db, 
            num_rows="dynamic", 
            use_container_width=True,
            disabled=["Geplant in Semester"]
        )
        
        if "Geplant in Semester" in edited_db.columns:
            edited_db_clean = edited_db.drop(columns=["Geplant in Semester"])
        else:
            edited_db_clean = edited_db
            
        visible_db_clean = visible_db.drop(columns=["Geplant in Semester"])
            
        if not edited_db_clean.equals(visible_db_clean):
            # Leere Namen herausfiltern, falls aus Versehen eine leere Zeile eingefügt wurde
            edited_db_clean = edited_db_clean.dropna(subset=["Name"])
            edited_db_clean = edited_db_clean[edited_db_clean["Name"].astype(str).str.strip() != ""]
            
            hidden_db = st.session_state.course_db[~is_visible].copy()
            
            st.session_state.course_db = pd.concat([edited_db_clean, hidden_db], ignore_index=True)
            save_data()
            st.rerun()


# --- BEREICH B: SEMESTER-PLANUNG ---
with tab2:
    st.header("🗓️ Semesterübersicht")
    
    first_vert_exch_idx = None
    vert_exch_matches = st.session_state.plan[st.session_state.plan["Austausch_Typ"] == "1:1 Vertiefungskurs"]
    if not vert_exch_matches.empty:
        first_vert_exch_idx = vert_exch_matches.index[0]
        
    highest_planned = 6
    if not st.session_state.plan.empty:
        highest_planned = int(st.session_state.plan["Semester"].max())
        
    if "max_sem" not in st.session_state:
        st.session_state.max_sem = max(6, highest_planned)
        
    if total_ects >= 120:
        st.session_state.max_sem = max(6, highest_planned)
    else:
        st.session_state.max_sem = max(st.session_state.max_sem, highest_planned)
        
    semesters = list(range(3, st.session_state.max_sem + 1))
        
    # Verfügbare Kurse ermitteln (die noch nicht geplant wurden)
    planned_course_names = st.session_state.plan["Name"].tolist()
    available_courses = st.session_state.course_db[~st.session_state.course_db["Name"].isin(planned_course_names)]
    
    semester_tabs = st.tabs([f"{sem}. Semester" for sem in semesters] + ["➕"])
    
    for i, sem in enumerate(semesters):
        with semester_tabs[i]:
            st.subheader(f"{sem}. Semester")
            
            st.markdown("##### 📚 Kurse planen")

            # Formular um Kurse zu diesem Semester hinzuzufügen
            with st.container():
                plan_len = len(st.session_state.plan)
                is_exchange = st.checkbox("Im Austauschsemester absolviert?", key=f"exch_{sem}")
                
                if is_exchange:
                    exch_type = st.radio("Art der Anrechnung", ["1:1 Pflichtkurs", "1:1 Vertiefungskurs", "Pauschalanrechnung", "Sprachkurs (Landessprache Gast-Uni)"], key=f"exch_type_{sem}")
                    
                    c_course, c_a, c_h, c_lang = st.columns([2, 1, 1, 1])
                    
                    with c_course:
                        if exch_type == "1:1 Pflichtkurs":
                            forbidden = ["Methoden: Statistik", "Methoden: Empirische Sozialforschung", "Grundlagen und Methoden der Informatik", "Einführung in das Operations-Management"]
                            avail_pflicht = available_courses[(available_courses["Kategorie"] == "Pflichtbereich") & (~available_courses["Name"].isin(forbidden))]
                            selected_course = st.selectbox("1:1 Pflichtkurs wählen", avail_pflicht["Name"].tolist(), index=None, placeholder="Suchen & Enter...", key=f"sel_course_pflicht_{sem}_{plan_len}")
                        elif exch_type == "1:1 Vertiefungskurs":
                            selected_course = st.text_input("Name (Vertiefung) + Enter", key=f"sel_course_vert_{sem}_{plan_len}")
                        elif exch_type == "Sprachkurs (Landessprache Gast-Uni)":
                            selected_course = st.text_input("Name (Sprachkurs) + Enter", key=f"sel_course_lang_{sem}_{plan_len}")
                        else:
                            selected_course = st.text_input("Kursname + Enter", key=f"sel_course_pausch_{sem}_{plan_len}")
                            
                    with c_a:
                        custom_ects = st.number_input("Austausch-ECTS", min_value=0.5, max_value=32.0, value=6.0, step=0.5, key=f"ects_a_{sem}")

                    with c_h:
                        if exch_type == "Pauschalanrechnung":
                            hsg_ects = custom_ects
                            st.number_input("HSG-ECTS", value=float(custom_ects), disabled=True, key=f"ects_h_{sem}")
                        elif exch_type == "Sprachkurs (Landessprache Gast-Uni)":
                            hsg_ects = st.number_input("HSG-ECTS (max 4.0)", min_value=0.5, max_value=4.0, value=min(4.0, float(custom_ects)), step=0.5, key=f"ects_h_{sem}")
                        else:
                            default_hsg = 4.0
                            if exch_type == "1:1 Pflichtkurs" and selected_course:
                                db_match = st.session_state.course_db[st.session_state.course_db["Name"] == selected_course]
                                if not db_match.empty:
                                    default_hsg = float(db_match.iloc[0]["ECTS"])
                            hsg_ects = st.number_input("HSG-ECTS", min_value=0.5, max_value=32.0, value=default_hsg, step=0.5, key=f"ects_h_{sem}")

                    with c_lang:
                        selected_lang = st.selectbox("Sprache", ["EN", "DE"], key=f"sel_lang_exch_{sem}")
                            
                    if selected_course:
                        add_to_plan(sem, selected_course, selected_lang, is_exchange, exch_type, custom_ects, hsg_ects)
                        st.rerun()
                else:
                    c_lang, c_course = st.columns([1, 3])
                    with c_lang:
                        selected_lang = st.selectbox("Sprache", ["DE", "EN"], key=f"sel_lang_{sem}")
                    with c_course:
                        options = ["✨ Neuen Kurs anlegen..."] + available_courses["Name"].tolist()
                        selected_course = st.selectbox("Kurs wählen oder neu anlegen", options, index=None, placeholder="Suchen & auswählen...", key=f"sel_course_{sem}_{plan_len}")
                
                    if selected_course:
                        if selected_course == "✨ Neuen Kurs anlegen...":
                            manual_name = st.text_input("Wie soll der neue Kurs heißen?", key=f"manual_name_{sem}_{plan_len}")
                            
                            if manual_name:
                                if manual_name in st.session_state.course_db["Name"].values:
                                    add_to_plan(sem, manual_name, selected_lang, False, None, None, None)
                                    st.rerun()
                                else:
                                    st.warning(f"Der Kurs '{manual_name}' ist noch nicht in der Datenbank.")
                                    st.write("Möchtest du ihn anlegen und direkt planen?")
                                    c_ects, c_cat, c_fin, c_btn = st.columns([1, 2, 1, 1.5])
                                    with c_ects:
                                        new_ects = st.number_input("ECTS", 1.0, 20.0, 4.0, 0.5, key=f"nc_ects_{sem}")
                                    with c_cat:
                                        new_cat = st.selectbox("Kategorie", ["Pflichtwahlbereich", "Wahlbereich", "Fokusbereich", "Skills und Sprachen"], key=f"nc_cat_{sem}")
                                    with c_fin:
                                        new_vert_sel = st.selectbox("Vertiefung?", ["Keine"] + VERTIEFUNGEN, key=f"nc_vert_{sem}")
                                        new_vert = new_vert_sel if new_vert_sel != "Keine" else ""
                                    with c_btn:
                                        st.write("")
                                        if st.button("➕ Hinzufügen", key=f"nc_btn_{sem}"):
                                            add_to_db(manual_name, new_ects, new_cat, new_vert)
                                            add_to_plan(sem, manual_name, selected_lang, False, None, None, None)
                                            st.rerun()
                        else:
                            add_to_plan(sem, selected_course, selected_lang, False, None, None, None)
                            st.rerun()
            
            # Bereits geplante Kurse für dieses Semester anzeigen
            sem_plan = st.session_state.plan[(st.session_state.plan["Semester"] == sem) & (st.session_state.plan["Kategorie"] != "Praktikum")]
            geschoben_plan = st.session_state.plan[(st.session_state.plan["Geschoben_Nach"] == sem) & (st.session_state.plan["Kategorie"] != "Praktikum")]
            
            if not sem_plan.empty or not geschoben_plan.empty:
                has_exch = False
                if not sem_plan.empty: has_exch = has_exch or sem_plan["Austausch"].any()
                if not geschoben_plan.empty: has_exch = has_exch or geschoben_plan["Austausch"].any()
                
                hc1, hc_a, hc_h, hc3, hc_s, hc4 = st.columns([3, 1, 1, 1, 1.2, 0.5])
                hc1.caption("KURSNAME")
                if has_exch:
                    hc_a.caption("AUSTAUSCH-ECTS")
                    hc_h.caption("HSG-ECTS")
                else:
                    hc_a.caption("ECTS")
                hc3.caption("SPRACHE")
                hc_s.caption("SCHIEBEN NACH")
                
                if not sem_plan.empty:
                    for idx, row in sem_plan.iterrows():
                        cc1, cc_a, cc_h, cc3, cc_s, cc4 = st.columns([3, 1, 1, 1, 1.2, 0.5])
                        
                        is_exch_vert = (row.get("Austausch_Typ") == "1:1 Vertiefungskurs")
                        is_overflow_vert = is_exch_vert and idx != first_vert_exch_idx
                        
                        if is_overflow_vert:
                            exch_label = " 🌍 (als Pauschalanrechnung)"
                            bg_color = CATEGORY_COLORS["Pauschalanrechnung"]
                            display_type = "Pauschalanrechnung"
                        else:
                            exch_label = f" 🌍 ({row['Austausch_Typ']})" if row.get("Austausch") else f" ({row['Kategorie']})"
                            is_vert = (row.get("Vertiefung", "") == target_v and target_v != "Keine Vertiefung") or is_exch_vert
                            bg_color = CATEGORY_COLORS["Pflichtwahlbereich"] if is_vert else CATEGORY_COLORS.get(row['Kategorie'], "rgba(160, 160, 160, 0.4)")
                            display_type = row.get("Austausch_Typ")
                            
                        name_html = f"📖 <b>{row['Name']}</b>"
                        if row.get("Geschoben_Nach", 0) > 0:
                            name_html = f"<del>{name_html}</del>"
                            
                        cc1.markdown(f"<div style='background-color: {bg_color}; padding: 5px 8px; border-radius: 4px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;' title='{row['Name']}'>{name_html}{exch_label}</div>", unsafe_allow_html=True)
                        
                        if row.get("Austausch"):
                            new_ects = cc_a.number_input("Austausch", 0.5, 32.0, float(row['ECTS']), 0.5, key=f"edit_ects_{row['Name']}_{sem}", label_visibility="collapsed", help="Austausch ECTS")
                            new_hsg = cc_h.number_input("HSG", 0.5, 32.0, float(row.get('HSG_ECTS', row['ECTS'])), 0.5, key=f"edit_hsg_{row['Name']}_{sem}", label_visibility="collapsed", help="HSG ECTS")
                        else:
                            new_ects = cc_a.number_input("ECTS", 0.5, 32.0, float(row['ECTS']), 0.5, key=f"edit_ects_{row['Name']}_{sem}", label_visibility="collapsed", help="ECTS")
                            new_hsg = new_ects
                            cc_h.write("")
                        
                        changed = False
                        if new_ects != float(row['ECTS']):
                            st.session_state.plan.loc[st.session_state.plan["Name"] == row["Name"], "ECTS"] = new_ects
                            changed = True
                        if new_hsg != float(row.get('HSG_ECTS', row['ECTS'])):
                            st.session_state.plan.loc[st.session_state.plan["Name"] == row["Name"], "HSG_ECTS"] = new_hsg
                            changed = True
                        if changed:
                            save_data()
                            st.rerun()
                        
                        new_lang = cc3.selectbox(
                            "Sprache", 
                            options=["DE", "EN"], 
                            index=0 if row['Sprache'] == "DE" else 1, 
                            key=f"edit_lang_{row['Name']}_{sem}",
                            label_visibility="collapsed"
                        )
                        
                        if new_lang != row['Sprache']:
                            st.session_state.plan.loc[st.session_state.plan["Name"] == row["Name"], "Sprache"] = new_lang
                            save_data()
                            st.rerun()
                            
                        # Schieben Nach UI
                        current_schieben = int(row.get("Geschoben_Nach", 0)) if pd.notna(row.get("Geschoben_Nach")) else 0
                        schieben_options = [0] + list(range(sem + 1, st.session_state.max_sem + 2))
                        if current_schieben != 0 and current_schieben not in schieben_options:
                            schieben_options.append(current_schieben)
                            schieben_options = sorted(list(set(schieben_options)))
                            
                        new_schieben = cc_s.selectbox(
                            "Schieben",
                            options=schieben_options,
                            format_func=lambda x: "-" if x == 0 else f"Semester {x}",
                            index=schieben_options.index(current_schieben),
                            key=f"edit_schieben_{row['Name']}_{sem}",
                            label_visibility="collapsed"
                        )
                        
                        if new_schieben != current_schieben:
                            st.session_state.plan.loc[st.session_state.plan["Name"] == row["Name"], "Geschoben_Nach"] = new_schieben
                            save_data()
                            st.rerun()
                            
                        if cc4.button("❌", key=f"del_{row['Name']}_{sem}"):
                            remove_from_plan(row['Name'])
                            st.rerun()

                if not geschoben_plan.empty:
                    for idx, row in geschoben_plan.iterrows():
                        cc1, cc_a, cc_h, cc3, cc_s, cc4 = st.columns([3, 1, 1, 1, 1.2, 0.5])
                        
                        bg_color = "rgba(200, 200, 200, 0.3)"
                        name_html = f"<div style='margin-left: 20px; background-color: {bg_color}; padding: 5px 8px; border-radius: 4px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;' title='{row['Name']}'>📌 <b>[Geschoben] {row['Name']}</b> <span style='font-size: 0.85em; color: #555;'>(aus Sem {int(row['Semester'])})</span></div>"
                        cc1.markdown(name_html, unsafe_allow_html=True)
                        
                        if row.get("Austausch"):
                            cc_a.markdown(f"<div style='padding-top: 5px;'>{row['ECTS']}</div>", unsafe_allow_html=True)
                            cc_h.markdown(f"<div style='padding-top: 5px;'>{row.get('HSG_ECTS', row['ECTS'])}</div>", unsafe_allow_html=True)
                        else:
                            cc_a.markdown(f"<div style='padding-top: 5px;'>{row['ECTS']}</div>", unsafe_allow_html=True)
                            cc_h.write("")
                            
                        cc3.markdown(f"<div style='padding-top: 5px;'>{row['Sprache']}</div>", unsafe_allow_html=True)
                        cc_s.write("")
                        cc4.write("")

                ects_staying = sem_plan[sem_plan["Geschoben_Nach"] == 0]['ECTS'].sum() if not sem_plan.empty else 0.0
                ects_incoming = geschoben_plan['ECTS'].sum() if not geschoben_plan.empty else 0.0
                total_sem_ects = ects_staying + ects_incoming
                st.info(f"**Total Semester {sem}: {total_sem_ects} ECTS**")
                
                # Validierung für Austauschsemester
                if not sem_plan.empty:
                    exch_plan = sem_plan[sem_plan["Austausch"] == True]
                    if not exch_plan.empty:
                        exch_ects = exch_plan["ECTS"].sum()
                        if exch_ects < 16.0:
                            st.error(f"⚠️ Warnung: Im Austauschsemester müssen mindestens 16 ECTS absolviert werden. Aktuell: {exch_ects} ECTS. Diese Kurse werden im Dashboard momentan nicht angerechnet!")
                        if exch_ects > 32.0:
                            st.warning(f"⚠️ Warnung: Es können maximal 32 ECTS aus dem Austausch angerechnet werden. Aktuell geplant: {exch_ects} ECTS. (Überzählige ECTS werden bei der Anrechnung gekappt)")
            else:
                st.write("Noch keine Kurse geplant.")
                
            st.divider()
            
            # Praktikum und Bachelorarbeit kompakt am Ende
            st.markdown("##### 💼 Praktikum & 🎓 Bachelorarbeit")
            c_prak, c_ba = st.columns(2)
            
            with c_prak:
                internships = st.session_state.plan[(st.session_state.plan["Semester"] == sem) & (st.session_state.plan["Kategorie"] == "Praktikum")]
                if not internships.empty:
                    for idx, row in internships.iterrows():
                        st.success(f"**{row['Firma']}** ({row['Ort']}, {row['Dauer']})")
                        if st.button("❌ Praktikum Löschen", key=f"del_intern_{sem}_{idx}"):
                            st.session_state.plan = st.session_state.plan.drop(idx)
                            save_data()
                            st.rerun()
                else:
                    with st.expander("➕ Praktikum eintragen"):
                        with st.form(key=f"intern_form_{sem}"):
                            firma = st.text_input("Firma")
                            ort = st.text_input("Ort")
                            
                            st.write("Zeitraum:")
                            c_sm, c_sy = st.columns(2)
                            c_em, c_ey = st.columns(2)
                            months = [f"{m:02d}" for m in range(1, 13)]
                            years = [str(y) for y in range(2020, 2035)]
                            s_m = c_sm.selectbox("Start Monat", months, key=f"sm_{sem}")
                            s_y = c_sy.selectbox("Start Jahr", years, index=years.index("2024"), key=f"sy_{sem}")
                            e_m = c_em.selectbox("End Monat", months, key=f"em_{sem}")
                            e_y = c_ey.selectbox("End Jahr", years, index=years.index("2024"), key=f"ey_{sem}")
                            
                            if st.form_submit_button("Speichern"):
                                if firma:
                                    dauer_monate = (int(e_y) - int(s_y)) * 12 + int(e_m) - int(s_m) + 1
                                    if dauer_monate <= 0:
                                        dauer_str = f"Ungültiger Zeitraum ({s_m}.{s_y} - {e_m}.{e_y})"
                                    elif dauer_monate == 1:
                                        dauer_str = f"1 Monat ({s_m}.{s_y} - {e_m}.{e_y})"
                                    else:
                                        dauer_str = f"{dauer_monate} Monate ({s_m}.{s_y} - {e_m}.{e_y})"
                                    add_internship_to_plan(sem, firma, dauer_str, ort)
                                    st.rerun()
                                else:
                                    st.error("Bitte eine Firma angeben.")
                                    
            with c_ba:
                ba_df = st.session_state.plan[(st.session_state.plan["Semester"] == sem) & (st.session_state.plan["Kategorie"] == "Bachelorarbeit")]
                if not ba_df.empty:
                    for idx, row in ba_df.iterrows():
                        st.success(f"Bachelorarbeit ({row['ECTS']} ECTS) geplant.")
                        if st.button("❌ BA Löschen", key=f"del_ba_{sem}_{idx}"):
                            st.session_state.plan = st.session_state.plan.drop(idx)
                            save_data()
                            st.rerun()
                else:
                    with st.expander("➕ Bachelorarbeit einplanen"):
                        ba_ects = st.number_input("ECTS für BA", min_value=6.0, max_value=24.0, value=12.0, step=1.0, key=f"ba_ects_{sem}")
                        if st.button("Speichern", key=f"add_ba_{sem}"):
                            if "Bachelorarbeit" not in st.session_state.course_db["Name"].values:
                                add_to_db("Bachelorarbeit", ba_ects, "Bachelorarbeit", "")
                            add_to_plan(sem, "Bachelorarbeit", "DE", False, None, ba_ects, ba_ects)
                            st.rerun()

    with semester_tabs[-1]:
        st.info("Brauchst du ein weiteres Semester für deine Kursplanung, eine Bachelorarbeit oder ein Praktikum?")
        if st.button(f"➕ {st.session_state.max_sem + 1}. Semester hinzufügen"):
            st.session_state.max_sem += 1
            st.rerun()