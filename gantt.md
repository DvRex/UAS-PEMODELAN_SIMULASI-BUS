gantt
    title Jadwal Pengembangan Aplikasi Health Check
    dateFormat  YYYY-MM-DD
    axisFormat  %W

    section Planning & Analysis
    Brainstorming & Konsep (Thoriq)      :a1, 2026-02-01, 7d
    Analisis Kebutuhan Sistem (Arham)    :a2, after a1, 7d
    Riset Data Kesehatan (Melquiano)     :a3, after a1, 5d

    section System Design
    Perancangan UML Diagram (Arham)      :b1, after a2, 7d
    Desain UI/UX Mockup (Aiyah/Akbar)    :b2, after a2, 10d
    Arsitektur Database & Code (Akbar)   :b3, after b1, 5d

    section Development (Coding)
    Setup Project & Repo (Akbar)         :c1, after b2, 3d
    Slicing UI (Frontend) (Akbar)        :c2, after c1, 14d
    Integrasi Logic & BMI (Akbar)        :c3, after c2, 7d
    Integrasi AI Groq API (Akbar)        :c4, after c3, 7d

    section Testing & QA
    Black Box Testing (Melquiano)        :d1, after c4, 5d
    Bug Fixing & Optimization (Akbar)    :d2, after d1, 5d

    section Deployment & Doc
    Deploy ke Vercel & Build APK (Akbar) :e1, after d2, 3d
    Penyusunan Laporan (Aiyah)           :e2, after c4, 14d
    Final Review & Presentasi (All)      :e3, after e2, 3d