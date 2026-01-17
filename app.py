import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# ==========================================
# SETUP LIBRARY AI (SAFE IMPORT) > Jika Fungsi AI Error Atau Tidak Tersedia Tidak Akan Menggangu Fungsi Utama Website
# ==========================================
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Simulasi Halte Bus - Monte Carlo",
    page_icon="🚌",
    layout="wide"
)

# Custom CSS 
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
    }
    .explanation-text {
        font-size: 0.9em;
        color: #333;
        margin-top: 5px;
        background-color: #e6f3ff;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #cce5ff;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR (INPUT PARAMETER)
# ==========================================
with st.sidebar:
    st.header("⚙️ Konfigurasi Simulasi")
    
    # Input Parameter
    SIMULATION_TIME = st.number_input("Durasi Simulasi (menit)", min_value=60, max_value=1440, value=120, step=10)
    MONTE_CARLO_RUNS = st.number_input("Jumlah Run (Monte Carlo)", min_value=10, max_value=500, value=50, step=10)
    
    st.markdown("---")
    st.subheader("Parameter Operasional")
    LAMBDA = st.slider("Rata-rata Kedatangan (λ orang/menit)", 1.0, 10.0, 2.0, 1.0) # Parameter Min Max Value Step bisa di buat per satu atau per 0.10
    BUS_INTERVAL = st.number_input("Interval Kedatangan Bus (menit)", min_value=1, max_value=60, value=10)
    BUS_CAPACITY = st.slider("Kapasitas Bus (Kursi)", 10, 100, 25, 1)
    
    START_HOUR = st.time_input("Jam Mulai Simulasi", value=datetime.strptime("17:00", "%H:%M"))
    
    st.markdown("---")
    
    # --- API KEY MANAGEMENT ---
    st.subheader("🤖 Otak AI (Groq)")
    
    # Cek Secrets (Prioritas 1)
    if "GROQ_API_KEY" in st.secrets:
        st.success("✅ API Key terdeteksi dari sistem!")
        api_key_input = st.secrets["GROQ_API_KEY"]
    else:
        # Input Manual (Prioritas 2)
        api_key_input = st.text_input("Masukkan Groq API Key", type="password", help="Dapatkan gratis di console.groq.com")
    
    # Tombol Eksekusi
    run_simulation = st.button("JALANKAN SIMULASI ▶️", type="primary", use_container_width=True)

# ==========================================
# 3. FUNGSI LOGIC MONTE CARLO
# ==========================================
def run_monte_carlo(sim_time, runs, lam, bus_int, bus_cap, start_time):
    
    def minute_to_time(min_val):
        dummy_date = datetime.combine(datetime.today(), start_time)
        return (dummy_date + timedelta(minutes=int(min_val))).strftime("%H:%M")

    results_summary = []
    events_log = []
    queue_history_matrix = np.zeros((runs, sim_time))

    progress_bar = st.progress(0)
    status_text = st.empty()

    for run in range(1, runs + 1):
        if run % 5 == 0:
            progress_bar.progress(run / runs)
            status_text.text(f"Running simulasi ke-{run} dari {runs}...")

        queue = []
        passenger_counter = 0
        total_wait_time_served = 0
        served_passengers = 0
        total_arrivals = 0
        sum_queue_length = 0
        bus_count = 0
        bus_full_count = 0
        total_capacity_offered = 0
        bus_id = 0

        for minute in range(1, sim_time + 1):
            # A. Kedatangan (Poisson)
            n_arrivals = np.random.poisson(lam)
            total_arrivals += n_arrivals
            for _ in range(n_arrivals):
                passenger_counter += 1
                queue.append({
                    "ID": passenger_counter,
                    "Arrival_Min": minute,
                    "Arrival_Time": minute_to_time(minute)
                })
            
            # B. Snapshot Antrian
            current_q_len = len(queue)
            sum_queue_length += current_q_len
            queue_history_matrix[run-1, minute-1] = current_q_len
            
            # C. Bus Datang
            if minute % bus_int == 0:
                bus_count += 1
                bus_id += 1
                total_capacity_offered += bus_cap
                
                boarding_count = min(len(queue), bus_cap) # FIFO
                if boarding_count == bus_cap:
                    bus_full_count += 1
                    
                for _ in range(boarding_count):
                    p = queue.pop(0)
                    wait_time = minute - p["Arrival_Min"]
                    total_wait_time_served += wait_time
                    served_passengers += 1
                    events_log.append({
                        "Run": run,
                        "Passenger_ID": p["ID"],
                        "Arrival_Time": p["Arrival_Time"],
                        "Boarding_Time": minute_to_time(minute),
                        "Wait_Time_Min": wait_time,
                        "Bus_ID": bus_id
                    })

        # D. Statistik per Run
        avg_wait = total_wait_time_served / served_passengers if served_passengers > 0 else 0
        avg_q_len = sum_queue_length / sim_time
        utilization = served_passengers / total_capacity_offered if total_capacity_offered > 0 else 0
        prob_full = bus_full_count / bus_count if bus_count > 0 else 0
        
        results_summary.append({
            "Run": run, "Avg_Wait_Time": avg_wait, "Avg_Queue_Len": avg_q_len,
            "Total_Arrivals": total_arrivals, "Served_Passengers": served_passengers,
            "Utilization": utilization, "Prob_Bus_Full": prob_full
        })
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results_summary), pd.DataFrame(events_log), queue_history_matrix

# ==========================================
# 4. FUNGSI AI (GROQ)
# ==========================================
def get_ai_analysis(api_key, wait_time, queue_len, util, prob_full, lam, interval, capacity):
    if not GROQ_AVAILABLE: return "⚠️ Library 'groq' belum terinstall. Jalankan `pip install groq`."
    if not api_key: return "⚠️ API Key belum dimasukkan."
    
    try:
        client = Groq(api_key=api_key)
        prompt = f"""
        Berperanlah sebagai Konsultan Transportasi Senior. Analisis data simulasi halte bus ini:
        
        DATA STATISTIK:
        - Rata-rata Waktu Tunggu: {wait_time:.2f} menit
        - Panjang Antrian: {queue_len:.1f} orang
        - Utilisasi Bus: {util*100:.1f}%
        - Kejadian Bus Penuh: {prob_full*100:.1f}%
        
        PARAMETER INPUT:
        - Demand Penumpang: {lam} orang/menit
        - Interval Bus: {interval} menit
        - Kapasitas: {capacity} kursi

        TUGAS:
        1. Berikan Analisis singkat tentang performa sistem.
        2. Berikan 3 Rekomendasi Solusi Teknis (bullet points) yang spesifik.
        
        Gunakan bahasa Indonesia yang profesional, tegas, dan berbasis data.
        """
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", temperature=0.7
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"❌ Error AI: {str(e)}"

# ==========================================
# 5. TAMPILAN UTAMA (DASHBOARD)
# ==========================================
st.title("🚌 Dashboard Simulasi Antrian Bus")
st.markdown("Simulasi Antrian Bus dengan Pendekatan **Monte Carlo**.")

# --- SESSION STATE ---
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None

if run_simulation:
    # Jalankan Simulasi
    df_summary, df_events, queue_matrix = run_monte_carlo(
        SIMULATION_TIME, MONTE_CARLO_RUNS, LAMBDA, BUS_INTERVAL, BUS_CAPACITY, START_HOUR
    )
    # Simpan ke Memory
    st.session_state.simulation_results = {
        'summary': df_summary,
        'events': df_events,
        'matrix': queue_matrix,
        'params': {'lambda': LAMBDA, 'interval': BUS_INTERVAL, 'capacity': BUS_CAPACITY}
    }

# --- RENDER HASIL JIKA ADA DATA ---
if st.session_state.simulation_results:
    results = st.session_state.simulation_results
    df_summary = results['summary']
    df_events = results['events']
    queue_matrix = results['matrix']
    params = results['params']

    # Hitung Global Stats
    global_avg_wait = df_summary["Avg_Wait_Time"].mean()
    global_avg_queue = df_summary["Avg_Queue_Len"].mean()
    global_utilization = df_summary["Utilization"].mean()
    global_prob_full = df_summary["Prob_Bus_Full"].mean()

    # --- KPI METRICS ---
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rata-rata Waktu Tunggu", f"{global_avg_wait:.2f} m", help="Target: < Interval Bus")
    col2.metric("Rata-rata Antrian", f"{global_avg_queue:.1f} org", help="Beban rata-rata di halte")
    col3.metric("Utilisasi Bus", f"{global_utilization*100:.1f} %", help="Optimal: 40-85%")
    col4.metric("Bus Penuh", f"{global_prob_full*100:.1f} %", help="Toleransi: 20%")

    # --- TABS VISUALISASI ---
    st.divider()
    tab1, tab2, tab3 = st.tabs(["📊 Grafik & Visualisasi", "🧠 Analisis & Rekomendasi", "📂 Data Mentah"])

    with tab1:
        # Grafik Confidence Interval
        mean_q = queue_matrix.mean(axis=0)
        std_q = queue_matrix.std(axis=0)
        ci_upper = mean_q + 1.96 * (std_q / np.sqrt(MONTE_CARLO_RUNS))
        ci_lower = mean_q - 1.96 * (std_q / np.sqrt(MONTE_CARLO_RUNS))
        ci_lower = np.maximum(ci_lower, 0)
        
        x_axis = list(range(1, SIMULATION_TIME + 1))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x = x_axis + x_axis[::-1], y = list(ci_upper) + list(ci_lower)[::-1],
            fill='toself', fillcolor='rgba(0,100,255,0.2)', line=dict(color='rgba(0,0,0,0)'), name='Confidence Interval 95%'))
        fig.add_trace(go.Scatter(x=x_axis, y=mean_q, mode='lines', line=dict(color='blue'), name='Rata-rata Antrian'))
        fig.add_trace(go.Scatter(x=x_axis, y=[params['capacity']]*len(x_axis), mode='lines', line=dict(color='red', dash='dash'), name=f"Kapasitas ({params['capacity']})"))
        
        fig.update_layout(title="Dinamika Panjang Antrian (Confidence Interval 95%)", xaxis_title="Waktu Simulasi (Menit)", yaxis_title="Jumlah Penumpang", hovermode="x unified", height=500)
        st.plotly_chart(fig, use_container_width=True)
        html_buffer = fig.to_html(full_html=True, include_plotlyjs='cdn')
        st.download_button(
        label="💾 Download Grafik Interaktif (HTML)",
        data=html_buffer,
        file_name="grafik_simulasi_antrian.html",
        mime="text/html",
        help="Download grafik ini agar bisa dibuka di browser secara offline dan tetap interaktif (bisa di-zoom)."
    )
    with tab2:
        st.header("📋 Analisis Kinerja Sistem (Rule-Based)")

        # LOGIC VARIABLES
        is_wait_long = global_avg_wait > params['interval']
        is_util_high = global_utilization > 0.85
        is_util_low = global_utilization < 0.40
        
        pct_full = global_prob_full * 100
        sla_safe = 5.0
        sla_max = 20.0
        
        # =============================================
        # 1. EVALUASI RISIKO
        # =============================================
        st.subheader("1. Evaluasi Risiko Kapasitas")
        
        col_risk_1, col_risk_2 = st.columns([1, 2])
        
        with col_risk_1:
            if pct_full <= sla_safe:
                st.success(f"✅ **SANGAT AMAN**\n\nSkor: {pct_full:.1f}%")
                risk_status = "AMAN"
            elif pct_full <= sla_max:
                st.warning(f"⚠️ **WASPADA**\n\nSkor: {pct_full:.1f}%")
                risk_status = "WARNING"
            else:
                st.error(f"❌ **KRITIS**\n\nSkor: {pct_full:.1f}%")
                risk_status = "BAHAYA"
        
        with col_risk_2:
            st.markdown("**🔍 Penjelasan Analisis:**")
            if risk_status == "AMAN":
                st.info(f"**AMAN:** Kejadian bus penuh ({pct_full:.1f}%) masih di bawah batas toleransi.")
            elif risk_status == "WARNING":
                st.warning(f"**WASPADA:** {pct_full:.1f}% bus datang penuh. Sistem mulai jenuh.")
            else:
                st.error(f"**KRITIS:** {pct_full:.1f}% bus penuh! Penumpang tertinggal & antrian meledak.")

        st.divider()

        # =============================================
        # 2. MATRIKS DIAGNOSA (UPDATED LOGIC)
        # =============================================
        st.subheader("2. Matriks Keputusan Operasional")
        
        # KASUS 1: SEKARAT
        if is_wait_long and is_util_high:
            diag_color = "red"
            diag_title = "🚨 OVERSATURATED (Kelebihan Beban)"
            diag_desc = "Sistem gagal total. Supply bus jauh di bawah demand."
            
        # KASUS 2: INEFISIEN
        elif is_wait_long and is_util_low:
            diag_color = "orange"
            diag_title = "⚠️ INEFISIENSI JADWAL (Frequency Mismatch)"
            diag_desc = "Masalah jadwal. Percuma bus besar kalau jarang datang."
            
        # KASUS 3: HIGH LOAD 
        elif not is_wait_long and is_util_high:
            diag_color = "orange"
            diag_title = "⚠️ HIGH LOAD (Hampir Overload)"
            diag_desc = f"Waktu tunggu masih aman, TAPI bus sangat padat (Utilisasi {global_utilization*100:.1f}%). Risiko kenyamanan rendah."

        # KASUS 4: PEMBOROSAN
        elif not is_wait_long and is_util_low:
            diag_color = "blue"
            diag_title = "💸 PEMBOROSAN (Oversupply)"
            diag_desc = "Terlalu banyak armada mengangkut angin."
            
        # KASUS 5: OPTIMAL
        else:
            diag_color = "green"
            diag_title = "✨ KONDISI PRIMA (Optimal State)"
            diag_desc = "Keseimbangan sempurna antara efisiensi dan kenyamanan."

        # Render Diagnosa
        if diag_color == "red": st.error(f"**{diag_title}**\n\n{diag_desc}")
        elif diag_color == "orange": st.warning(f"**{diag_title}**\n\n{diag_desc}")
        elif diag_color == "blue": st.info(f"**{diag_title}**\n\n{diag_desc}")
        else: st.success(f"**{diag_title}**\n\n{diag_desc}")

        st.divider()

        # =============================================
        # 3. REKOMENDASI SISTEM
        # =============================================
        st.subheader("3. Rekomendasi Berdasarkan Hasil Simulasi")
        
        rec_text = ""
        rec_type = "info" # default
        
        if is_wait_long and is_util_high:
            rec_type = "error"
            rec_text = "**Sistem Overload!** Wajib tambah armada atau gunakan Bus Gandeng."
            
        elif is_wait_long and is_util_low:
            rec_type = "warning"
            rec_text = "**Inefisiensi Jadwal!** Ganti ke Minibus dan percepat interval kedatangan."
            
        elif not is_wait_long and is_util_high:
            rec_type = "warning"
            rec_text = """
            **Peringatan High Load (Kenyamanan Rendah)**
            * **Kondisi:** Waktu tunggu aman, tapi bus sesak (Utilisasi > 85%).
            * **Solusi:** Sedikit percepat interval kedatangan untuk menurunkan kepadatan bus.
            """
            
        elif not is_wait_long and is_util_low:
            rec_type = "info"
            rec_text = "**Pemborosan Biaya!** Kurangi frekuensi kedatangan untuk menghemat BBM."
            
        else:
            rec_type = "success"
            rec_text = "**Pertahankan!** Konfigurasi sudah optimal."

        # Native Streamlit Alert agar warna teks aman di Dark Mode
        if rec_type == "error": st.error(rec_text)
        elif rec_type == "warning": st.warning(rec_text)
        elif rec_type == "success": st.success(rec_text)
        else: st.info(rec_text)

        # =============================================
        # 4. AI SUPPORT
        # =============================================
        st.divider()
        st.subheader("🤖 Asisten Cerdas (AI Support)")
        
        if st.button("✨ Minta Saran & Analisis AI"):
            if not api_key_input:
                st.warning("⚠️ API Key tidak ditemukan.")
            else:
                with st.spinner("Sedang menghubungi AI..."):
                    ai_res = get_ai_analysis(
                        api_key_input, global_avg_wait, global_avg_queue, 
                        global_utilization, global_prob_full, 
                        params['lambda'], params['interval'], params['capacity']
                    )
                
                # --- PERBAIKAN TAMPILAN AI (Pakai Chat Message) ---
                st.success("✅ **Analisis Selesai! Berikut saran dari AI:**")

                with st.chat_message("assistant"):
                    st.write(ai_res)

    with tab3:
        st.subheader("Data Hasil Simulasi")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Ringkasan per Run")
            st.dataframe(df_summary, use_container_width=True)
        with c2:
            st.write("Log Penumpang")
            st.dataframe(df_events, use_container_width=True)

else:
    st.info("👈 Masukkan parameter di sidebar dan klik **JALANKAN SIMULASI**.")