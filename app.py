import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

DB_FILE = "safeguards_monitoring.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.cursor().execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_name TEXT, location TEXT,
            latitude REAL, longitude REAL, has_complaint TEXT, complaint_category TEXT,
            complaint_narration TEXT, grm_status TEXT, affected_people INTEGER,
            safe_hours INTEGER, lti_count INTEGER, rehab_hectares REAL, survival_rate REAL, report_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_report(d):
    conn = sqlite3.connect(DB_FILE)
    conn.cursor().execute('''
        INSERT INTO reports (
            project_name, location, latitude, longitude, has_complaint, complaint_category,
            complaint_narration, grm_status, affected_people, safe_hours, lti_count, rehab_hectares, survival_rate, report_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (d['p_name'], d['loc'], d['lat'], d['lon'], d['has_c'], d['c_cat'], d['c_narr'], d['g_stat'], d['aff'], d['safe'], d['lti'], d['rehab'], d['surv'], d['date']))
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM reports", conn)
    conn.close()
    return df

def generate_kfw_report_text(df):
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    txt = f"========================================================================\n"
    txt += f"                      KFW SAFEGUARDS MONITORING REPORT\n"
    txt += f"========================================================================\n"
    txt += f"Generated: {t} | Prepared by: Safeguards & HSSE Unit (Gunung Batu)\n\n"
    txt += f"1. EXECUTIVE SUMMARY\n"
    txt += f"- Total Sites Monitored: {len(df)} site(s)\n"
    txt += f"- Total Safe Hours: {df['safe_hours'].sum():,} Hours\n"
    txt += f"- Total LTI Incidents: {df['lti_count'].sum()}\n"
    txt += f"- Total Rehab Area: {df['rehab_hectares'].sum():.2f} Ha\n\n"
    txt += f"2. SITE BREAKDOWN\n"
    for _, r in df.iterrows():
        txt += f"-[SITE #{r['id']}] {r['location']} ({r['project_name']})\n"
        txt += f"  OHS: {r['safe_hours']:,} Hours | LTI: {r['lti_count']} | Rehab: {r['rehab_hectares']:.2f} Ha | Survival: {r['survival_rate']}%\n"
        txt += f"  GRM: Active Complaint? {r['has_complaint']} | Status: {r['grm_status']}\n"
        txt += f"  Narration: \"{r['complaint_narration'] if r['complaint_narration'] else 'No dispute reported.'}\"\n\n"
    return txt

st.set_page_config(page_title="Digital Safeguards Monitoring Dashboard", layout="wide")
init_db()

# --- KAMUS DUA BAHASA (BILINGUAL DICTIONARY) ---
st.sidebar.title("🌐 Language / Bahasa")
lang = st.sidebar.selectbox("Choose Language / Pilih Bahasa", ["English", "Bahasa Indonesia"])

# Alokasi teks berdasarkan pilihan bahasa
T = {
    "title": "Digital Safeguards Monitoring & Reporting System" if lang=="English" else "Sistem Pelaporan & Pemantauan Safeguards Digital",
    "menu_label": "Navigation Menu" if lang=="English" else "Menu Navigasi",
    "menu_1": "📋 Data Input Form (Field Staff)" if lang=="English" else "📋 Formulir Input Data (Staf Lapangan)",
    "menu_2": "📊 Executive Analytics Dashboard (HQ/Gunung Batu)" if lang=="English" else "📊 Dasbor Analitik Eksekutif (Pusat/Gunung Batu)",
    "f_header": "📝 Field Safeguards Report Entry Form" if lang=="English" else "📝 Formulir Entri Laporan Safeguards Lapangan",
    "p_name": "Sub-Project Name" if lang=="English" else "Nama Sub-Proyek",
    "loc": "Site Location (Village/District)" if lang=="English" else "Lokasi Tapak (Desa / Kecamatan)",
    "loc_ph": "e.g., Sei Nagalawan Village" if lang=="English" else "Contoh: Desa Sei Nagalawan",
    "date": "Reporting Period Date" if lang=="English" else "Tanggal Periode Pelaporan",
    "safe": "Total Safe Working Hours This Month" if lang=="English" else "Total Jam Kerja Selamat Bulan Ini",
    "lti": "Loss Time Injury (LTI) Count" if lang=="English" else "Jumlah Kecelakaan Kerja (LTI)",
    "rehab": "Total Rehabilitated Area (Hectares)" if lang=="English" else "Total Luas Area Direhabilitasi (Ha)",
    "surv": "Plant Survival Rate (%)" if lang=="English" else "Persentase Hidup Bibit (Survival Rate %)",
    "social_sec": "🛡️ Grievance Redress Mechanism / GRM" if lang=="English" else "🛡️ Mekanisme Penanganan Keluhan / GRM",
    "has_c": "Are there any active community grievances this month?" if lang=="English" else "Apakah terdapat keluhan aktif dari masyarakat bulan ini?",
    "c_yes": "Yes" if lang=="English" else "Ya",
    "c_no": "No" if lang=="English" else "Tidak",
    "c_cat": "Grievance Category" if lang=="English" else "Kategori Aduan",
    "aff": "Estimated Affected Communities (People)" if lang=="English" else "Jumlah Warga Terdampak (Jiwa)",
    "g_stat": "GRM Resolution Status" if lang=="English" else "Status Penanganan (GRM Status)",
    "c_narr": "Detailed Grievance Narration (Qualitative Input)" if lang=="English" else "Kronologi Detail Aduan (Input Kualitatif)",
    "submit": "🚀 Submit Report to Central Database" if lang=="English" else "🚀 Kirim Laporan ke Database Pusat",
    "err_loc": "Failed: Site Location column is required!" if lang=="English" else "Gagal: Kolom Nama Lokasi Desa wajib diisi!",
    "success": "✅ Report successfully saved and synced." if lang=="English" else "✅ Laporan berhasil disimpan dan disinkronisasi.",
    "d_header": "📊 Executive Overview & Analytics Dashboard" if lang=="English" else "📊 Dasbor Pemantauan & Analitik Utama",
    "no_data": "⚠️ No reporting data available in the database." if lang=="English" else "⚠️ Belum ada data pelaporan yang masuk.",
    "kpi_rep": "📋 Total Reports" if lang=="English" else "📋 Total Laporan",
    "kpi_safe": "🛡️ Safe Hours" if lang=="English" else "🛡️ Jam Selamat",
    "kpi_rehab": "🌱 Total Reforestation" if lang=="English" else "🌱 Total Area Restorasi",
    "kpi_social": "⚠️ Active Social Disputes" if lang=="English" else "⚠️ Sengketa Sosial Aktif",
    "kpi_ok": "0 Conflicts" if lang=="English" else "0 Konflik",
    "kpi_ok_sub": "Stable Social Condition" if lang=="English" else "Kondisi Kondusif",
    "exp_sec": "📥 Export & Reporting Center" if lang=="English" else "📥 Export & Reporting Center",
    "exp_sub": "Convert real-time field data into an official compliance text report for KfW auditors." if lang=="English" else "Konversikan data lapangan instan menjadi draf laporan kepatuhan resmi untuk donor Jerman.",
    "graph_1": "📈 Quantitative OHS & Environmental Metrics" if lang=="English" else "📈 Matriks Kuantitatif Lingkungan & K3",
    "graph_2": "🚨 Qualitative Social Grievance Log" if lang=="English" else "🚨 Pelacak Narasi Isu Sosial & Keluhan (Kualitatif)",
    "no_c": "🎉 No active localized social disputes reported." if lang=="English" else "🎉 Tidak ada sengketa sosial aktif.",
    "map_sec": "🗺️ Geospatial GIS Distribution Map" if lang=="English" else "🗺️ Peta Geospasial Distribusi Lokasi Monitoring"
}

st.title(f"🌐 {T['title']}")
st.markdown("---")

menu = st.sidebar.radio(T["menu_label"], [T["menu_1"], T["menu_2"]])

if menu == T["menu_1"]:
    st.header(T["l_header"])
    with st.form("safeguards_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            p_name = st.selectbox(T["p_name"], ["Target Programme VI (TP VI) Mangrove", "BMTM1 - KfW Phase 1 Cosystem"])
            loc = st.text_input(T["loc"], placeholder=T["loc_ph"])
            lat = st.number_input("Latitude GPS", value=0.0, format="%.6f")
            lon = st.number_input("Longitude GPS", value=0.0, format="%.6f")
            date = st.date_input(T["date"], datetime.now())
        with c2:
            safe = st.number_input(T["safe"], min_value=0, value=0)
            iti = st.number_input(T["iti"], min_value=0, value=0)
            rehab = st.number_input(T["rehab"], min_value=0.0, value=0.0, format="%.2f")
            surv = st.slider(T["surv"], 0, 100, 85)
        
        st.markdown("---")
        st.subheader(T["social_sec"])
        has_c = st.radio(T["has_c"], [T["c_no"], T["c_yes"]])
        
        # Inisialisasi variabel default
        c_cat, c_narr, g_stat, aff = "N/A", "", "N/A", 0
        
        # Kondisi ini sekarang aman di dalam form karena perubahan pilihan radio tidak akan mereset teks di atas
        if has_c == T["c_yes"]:
            c_cat = st.selectbox(T["c_cat"], ["Land Dispute", "Environmental Damage", "Labor Complaint", "Other"])
            c_narr = st.text_area(T["c_narr"])
            g_stat = st.selectbox(T["g_stat"], ["Open", "In Progress", "Resolved"])
            aff = st.number_input(T["aff"], min_value=0, value=0)
            
        submit_button = st.form_submit_button(T["submit"])
        
        if submit_button:
            if not loc:
                st.error(T["err_loc"])
            else:
                save_report(p_name, loc, lat, lon, date, has_c, c_cat, c_narr, g_stat, aff, safe, iti, rehab, surv)
                st.success(T["success"])

elif menu == T["menu_2"]:
    st.header(T["d_header"])
    
    # === LANGKAH 1: FITUR FILTER LOKASI ===
    df_raw = load_data()
    sdf_raw = load_data()
    
    # Membuat filter pilihan di sidebar
    lokasi_pilihan = st.sidebar.multiselect(
        "🔍 Filter Berdasarkan Lokasi:",
        options=list(df_raw['location'].unique()),
        default=list(df_raw['location'].unique())
    )
    
    # Menyaring data berdasarkan pilihan pengguna
    df = df_raw[df_raw['location'].isin(lokasi_pilihan)]
    if 'location' in sdf_raw.columns:
        sdf = sdf_raw[sdf_raw['location'].isin(lokasi_pilihan)]
    else:
        sdf = sdf_raw

    if df.empty:
        st.warning(T["no_data"])
        st.stop()
        
    else:

        k1, k2, k3, k4 = st.columns(4)
        k1.metric(T["kpi_rep"], f"{len(df)} Sites")
        k2.metric(T["kpi_safe"], f"{df['safe_hours'].sum():,} Hrs", f"-{df['lti_count'].sum()} LTI", delta_color="inverse")
        k3.metric(T["kpi_rehab"], f"{df['rehab_hectares'].sum():.2f} Ha")
        act = len(df[df['grm_status'].isin(['Open (Aduan Baru)', 'In Progress (Mediasi)'])])
        if act > 0: k4.metric(T["kpi_social"], f"{act} Cases", delta_color="inverse")
        else: k4.metric(T["kpi_social"], T["kpi_ok"], T["kpi_ok_sub"])
        
        st.markdown("---")
        st.subheader(T["exp_sec"])

        st.markdown(T["exp_sub"])
        st.download_button(label="📥 Download Official KfW Safeguards Report (.txt)", data=generate_kfw_report_text(df), file_name="KfW Report.txt")
        st.markdown("---")
        colg1, colg2 = st.columns(2)
        with colg1:
                st.subheader(T["graph_1"])
                st.dataframe(df, use_container_width=True)

        with colg2:
                st.bar_chart(df, x="project_name", y="safe_hours", color="#2ecc71")
                st.subheader(T["graph_2"])
                st.bar_chart(df, x="location", y="safe_hours", color="#2ecc71")
  
    if sdf.empty:
        st.success(T["no_cl"])
    else:
        for _, r in sdf.iterrows():
            with st.expander(f"⚠️ {r['complaint_category']} | Site {r['location']}"):
                st.write(f"Status: {r['grm_status']} | Affected: {r['affected_people']} People")
                st.write(r['complaint_narration'])
        st.markdown("---")
    st.subheader(T["map_sec"])
    st.map(df[['latitude', 'longitude']].rename(columns={'latitude': 'lat', 'longitude': 'lon'}))
