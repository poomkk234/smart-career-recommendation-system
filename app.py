import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. ตั้งค่าหน้าตาเว็บไซต์ (Page Configuration)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Smart Career Recommendation System",
    page_icon="🎓",
    layout="wide"
)

# ---------------------------------------------------------
# 2. ระบบปรับโทนสี ขาว-ดำ (Theme Toggle)
# ---------------------------------------------------------
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"

col_title, col_toggle = st.columns([5, 1])

with col_toggle:
    is_dark = st.toggle("🌙 โหมดมืด (Dark Theme)", value=(st.session_state.theme_mode == "Dark"))
    st.session_state.theme_mode = "Dark" if is_dark else "Light"

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #121212 !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4, [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown {
        color: #FFFFFF !important; font-weight: 600 !important;
    }
    div[data-baseweb="tab-list"] { background-color: #0A0A0A !important; padding: 6px; border-radius: 8px; }
    button[data-baseweb="tab"] { background-color: #1E1E1E !important; border-radius: 6px !important; margin-right: 4px !important; }
    button[data-baseweb="tab"] p, button[data-baseweb="tab"] span { color: #FFFFFF !important; font-weight: bold !important; }
    button[data-baseweb="tab"][aria-selected="true"] { background-color: #333333 !important; border-bottom: 3px solid #FFFFFF !important; }
    </style>
""", unsafe_allow_html=True)

if st.session_state.theme_mode == "Dark":
    st.markdown("<style>.stApp { background-color: #121212 !important; color: #FFFFFF !important; }</style>", unsafe_allow_html=True)
    chart_template = "plotly_dark"
    radar_color = "#64B5F6"
else:
    st.markdown("<style>.stApp { background-color: #FFFFFF; color: #000000; }</style>", unsafe_allow_html=True)
    chart_template = "plotly_white"
    radar_color = "#1E88E5"

# ---------------------------------------------------------
# 3. ฐานข้อมูลวิชาการเรียน (12 รายวิชา)
# ---------------------------------------------------------
SUBJECT_NAMES = {
    "math": "คณิตศาสตร์ (Mathematics)",
    "science": "วิทยาศาสตร์/ฟิสิกส์ (Science)",
    "tech": "วิทยาการคำนวณ/คอมพิวเตอร์ (Computer & Tech)",
    "english": "ภาษาอังกฤษ (English)",
    "art": "ศิลปะและการออกแบบ (Art & Design)",
    "social": "สังคมศึกษา/ประวัติศาสตร์ (Social Studies)",
    "finance": "การเงินและการบัญชี (Finance & Accounting)",
    "marketing": "การตลาดและธุรกิจ (Marketing & Business)",
    "lang3": "ภาษาที่สาม (Third Language)",
    "design_3d": "สถาปัตยกรรม/มัลติมีเดีย (Architecture & 3D)",
    "law": "กฎหมายและรัฐศาสตร์ (Law & Political Science)",
    "psychology": "จิตวิทยาและการแนะแนว (Psychology)"
}

# ---------------------------------------------------------
# 4. ฐานข้อมูลอาชีพ (CAREERS_DB)
# ---------------------------------------------------------
CAREERS_DB = [
    {
        "title": "นักพัฒนาอสังหาริมทรัพย์ / บริหารโครงการ (Real Estate Developer)",
        "primary": ["design_3d", "marketing"],
        "secondary": ["law", "finance"],
        "desc": "วางผังออกแบบโครงการ (Arch/3D) วิเคราะห์ตลาดและขาย (Marketing) พร้อมดูแลข้อกฎหมายที่ดินและสัญญา (Law)"
    },
    {
        "title": "ที่ปรึกษากฎหมายสิ่งปลูกสร้างและลิขสิทธิ์ (Architectural Legal Consultant)",
        "primary": ["law"],
        "secondary": ["design_3d", "marketing"],
        "desc": "ดูแลสัญญาจ้างออกแบบ ตรวจสอบลิขสิทธิ์แบบ 3D และคุ้มครองเครื่องหมายการค้าธุรกิจสถาปนิก"
    },
    {
        "title": "วิศวกรซอฟต์แวร์ / นักพัฒนาแอปพลิเคชัน (Software Engineer)",
        "primary": ["tech"],
        "secondary": ["math", "english"],
        "desc": "ใช้ตรรกะคณิตศาสตร์ เขียนโค้ดคอมพิวเตอร์ และอ่านเอกสารเทคโนโลยีภาษาอังกฤษ"
    },
    {
        "title": "นักวิเคราะห์ข้อมูลและ AI (Data Scientist / AI Specialist)",
        "primary": ["math"],
        "secondary": ["tech", "science"],
        "desc": "วิเคราะห์ข้อมูลขนาดใหญ่ด้วยคณิตศาสตร์ สถิติ วิทยาการคำนวณ และกระบวนการวิจัย"
    },
    {
        "title": "แพทย์ / นักวิจัยทางการแพทย์ (Medical Researcher)",
        "primary": ["science"],
        "secondary": ["math", "english"],
        "desc": "ใช้วิทยาศาสตร์ขั้นสูง คำนวณขนาดยา/สถิติ และสื่อสารภาษาอังกฤษเพื่อผลงานวิจัย"
    },
    {
        "title": "นักการเงินเชิงวิเคราะห์และนักลงทุน (Financial Analyst)",
        "primary": ["finance"],
        "secondary": ["math", "marketing"],
        "desc": "ประเมินความเสี่ยง ตรวจสอบตัวเลขการเงิน การคำนวณผลตอบแทน และวิเคราะห์แนวโน้มตลาด"
    },
    {
        "title": "นักออกแบบ UI/UX และผลิตภัณฑ์ดิจิทัล (UI/UX Designer)",
        "primary": ["art"],
        "secondary": ["tech", "psychology"],
        "desc": "ออกแบบความสวยงาม รวมกับระบบเทคโนโลยี และเข้าใจจิตวิทยาพฤติกรรมผู้ใช้งาน"
    },
    {
        "title": "สถาปนิกและนักออกแบบ 3D (Architect)",
        "primary": ["design_3d"],
        "secondary": ["math", "art"],
        "desc": "คำนวณโครงสร้างตามหลักวิศวกรรม/ฟิสิกส์ ผสานกับความสวยงามทางศิลปะและการเขียนแบบ"
    },
    {
        "title": "นักการตลาดดิจิทัลและกลยุทธ์แบรนด์ (Digital Strategist)",
        "primary": ["marketing"],
        "secondary": ["social", "tech"],
        "desc": "วางแผนธุรกิจ เข้าใจสังคมพฤติกรรมผู้บริโภค และใช้เครื่องมือดิจิทัลวิเคราะห์แคมเปญ"
    },
    {
        "title": "นักกฎหมายธุรกิจระหว่างประเทศ (International Corporate Lawyer)",
        "primary": ["law"],
        "secondary": ["english", "social"],
        "desc": "ใช้ข้อกฎหมายและระเบียบสังคม ร่างสัญญาภาษาอังกฤษ และเข้าใจบริบทธุรกิจ"
    },
    {
        "title": "นักจิตวิทยาคลินิก / นักที่ปรึกษาองค์กร (Corporate Psychologist)",
        "primary": ["psychology"],
        "secondary": ["social", "english"],
        "desc": "ใช้หลักจิตวิทยา วิเคราะห์พฤติกรรมมนุษย์และสังคม พร้อมการสื่อสารระดับสากล"
    },
    {
        "title": "นักวิเคราะห์และล่ามเจรจาธุรกิจข้ามชาติ (Global Business Analyst)",
        "primary": ["lang3"],
        "secondary": ["english", "marketing"],
        "desc": "ใช้ทักษะภาษาที่สาม ภาษาอังกฤษ และความรู้การตลาดในการเจรจาการค้าระหว่างประเทศ"
    }
]

# ฐานข้อมูลอาชีพอิสระ
FREELANCE_CAREERS_DB = {
    "math": {"title": "Tutor สอนคณิตศาสตร์ / Freelance Data Analyst", "desc": "รับสอนพิเศษออนไลน์ หรือรับงานวิเคราะห์ข้อมูลตัวเลขให้องค์กรต่างชาติ"},
    "science": {"title": "นักเขียนบทความวิทยาศาสตร์ / ครีเอเตอร์สาย Sci-Tech", "desc": "สร้างคอนเทนต์วิทยาศาสตร์ พิสูจน์อักษร หรืองานวิเคราะห์ข้อมูลสุขภาพ"},
    "tech": {"title": "Freelance Web/App Developer", "desc": "รับเขียนโปรแกรม สร้างเว็บไซต์ หรือพัฒนาระบบอัตโนมัติรับงานอิสระ"},
    "english": {"title": "นักแปลเอกสารอิสระ / Content Writer ภาษาอังกฤษ", "desc": "รับงานแปลภาษา พิสูจน์อักษร หรือเขียนบทความ SEO ต่างประเทศ"},
    "art": {"title": "Freelance Illustrator / NFT Artist", "desc": "รับวาดภาพประกอบ ออกแบบตัวละคร โลโก้ และกราฟิกดีไซน์"},
    "social": {"title": "นักวิเคราะห์เทรนด์สังคม / พอดแคสเตอร์อิสระ", "desc": "สร้างคอนเทนต์เกี่ยวกับประวัติศาสตร์ สังคม การเมือง หรือการวิเคราะห์เหตุการณ์บ้านเมือง"},
    "finance": {"title": "ที่ปรึกษาการเงินส่วนบุคคลอิสระ / Trader", "desc": "วางแผนการเงิน บัญชี และการลงทุนอิสระให้ลูกค้าบุคคล"},
    "marketing": {"title": "Freelance Social Media Admin & Ad Specialist", "desc": "รับบริหารเพจ วางแผนคอนเทนต์ และยิงโฆษณาออนไลน์ให้แบรนด์ต่างๆ"},
    "lang3": {"title": "ล่ามอิสระ / นักแปลภาษาเฉพาะทาง", "desc": "รับงานล่ามการประชุม ถ่ายทำ หรือแปลซับไตเติลภาพยนตร์"},
    "design_3d": {"title": "3D Modeler / Freelance Interior Visualizer", "desc": "รับขึ้นโมเดล 3D ออกแบบภาพทัศนียภาพห้องและอาคาร"},
    "law": {"title": "ที่ปรึกษากฎหมายอิสระ (Legal Consultant)", "desc": "ให้คำปรึกษาด้านสัญญา กฎหมายธุรกิจ และทรัพย์สินทางปัญญา"},
    "psychology": {"title": "Life Coach / คอนซัลต์พัฒนาบุคลิกภาพ", "desc": "ให้คำปรึกษาการดำรงชีวิต การจัดการความเครียด และการสื่อสารในองค์กร"}
}

# ฐานข้อมูลสื่อการเรียนรู้
LEARNING_RESOURCES_DB = {
    "math": {"title": "คณิตศาสตร์และสถิติ", "resources": ["Khan Academy Math", "Coursera: Calculus & Statistics", "Youtube: พี่ปั้น SmartMathPro"]},
    "science": {"title": "วิทยาศาสตร์และฟิสิกส์", "resources": ["EDX: Intro to Physics", "National Geographic Portal", "Youtube: คลังความรู้วิทยาศาสตร์ สสวท."]},
    "tech": {"title": "วิทยาการคำนวณและเขียนโค้ด", "resources": ["freeCodeCamp.org", "Codecademy Python", "Harvard CS50 Course"]},
    "english": {"title": "ภาษาอังกฤษเพื่อการทำงาน", "resources": ["Duolingo App", "BBC Learning English", "BBC / TED Talks Podcast"]},
    "art": {"title": "ศิลปะและการออกแบบกราฟิก", "resources": ["Canva Design School", "Skillshare Graphic Design", "Youtube: สอนใช้ Photoshop & Illustrator"]},
    "social": {"title": "สังคมศึกษาและความเข้าใจมนุษย์", "resources": ["edX: Global History", "Podcast: 8 Minutes History", "National Geographic Social Portal"]},
    "finance": {"title": "การเงิน บัญชี และการลงทุน", "resources": ["ตลาดหลักทรัพย์แห่งประเทศไทย (SET e-Learning)", "คอร์สการเงินบน Coursera", "Youtube: สรุปให้ / Money Buffalo"]},
    "marketing": {"title": "การตลาดดิจิทัลและธุรกิจ", "resources": ["Google Digital Garage", "HubSpot Academy", "Podcast: The Secret Sauce"]},
    "lang3": {"title": "ทักษะภาษาที่สาม", "resources": ["Memrise App", "Busuu Language Course", "Youtube: ช่องสอนภาษาต่างประเทศฟรี"]},
    "design_3d": {"title": "การขึ้นแบบ 3D และงานสถาปัตยกรรม", "resources": ["Blender Guru Tutorial", "SketchUp Official School", "Coursera: Architectural Design"]},
    "law": {"title": "ความรู้กฎหมายและรัฐศาสตร์", "resources": ["คอร์สความรู้กฎหมายประชาชน (จุฬาฯ MOOC)", "edX: International Law", "เว็บไซต์คลังกฎหมายไทย"]},
    "psychology": {"title": "จิตวิทยาพฤติกรรมและการสื่อสาร", "resources": ["Coursera: Introduction to Psychology (Yale)", "Psych2Go Youtube Channel", "หนังสือสรุปจิตวิทยาพฤติกรรม"]}
}

# ---------------------------------------------------------
# 5. ส่วน UI ฝั่งซ้าย: เมนูกรอกข้อมูล (Sidebar)
# ---------------------------------------------------------
st.sidebar.header("📝 1. กรอกคะแนนรายวิชา (0-100)")
st.sidebar.caption("ปรับระดับคะแนนตามผลการเรียนของคุณ:")

scores = {}
for code, name in SUBJECT_NAMES.items():
    scores[code] = st.sidebar.slider(name, 0, 100, 0)

st.sidebar.markdown("---")
st.sidebar.header("❤️ 2. วิชาที่คุณชอบที่สุด")
favorite_subject = st.sidebar.selectbox(
    "เลือกวิชาที่ชอบ (เพื่อคำนวณอาชีพอิสระ):",
    options=list(SUBJECT_NAMES.keys()),
    format_func=lambda x: SUBJECT_NAMES[x]
)

st.sidebar.markdown("---")
st.sidebar.header("🎨 3. เลือกรูปแบบ UI กราฟ")
chart_type = st.sidebar.radio(
    "เลือกประเภทการแสดงผลคะแนน:",
    ["🕸️ กราฟแมงมุม (Radar Chart)", "🍩 กราฟวงกลม (Donut Chart)", "📊 กราฟแท่ง (Bar Chart)", "📋 ตารางข้อมูล (Table)"]
)

# ---------------------------------------------------------
# 6. อัลกอริทึมและการแสดงผล (Main Layout)
# ---------------------------------------------------------
with col_title:
    st.title("🎓 Smart Career Recommendation System")
    st.caption("ระบบวิเคราะห์อาชีพหลัก อาชีพอิสระ จัดอันดับทักษะ พร้อมสื่อพัฒนาการเรียนรู้")

st.markdown("---")

active_scores = {k: v for k, v in scores.items() if v > 0}

if len(active_scores) == 0:
    st.error("🚫 **ไม่พบข้อมูลคะแนน**")
    st.warning("⚠️ กรุณากรอกคะแนนอย่างน้อย 1 วิชาในแถบสีดำฝั่งซ้าย เพื่อเปิดการประมวลผล")
    
    st.markdown("---")
    st.subheader("💡 คำแนะนำสื่อการเรียนรู้ปูพื้นฐาน (สำหรับวิชาที่มีคะแนน 0)")
    col_a, col_b = st.columns(2)
    sub_keys = list(SUBJECT_NAMES.keys())
    for idx, code in enumerate(sub_keys):
        res_info = LEARNING_RESOURCES_DB[code]
        target_col = col_a if idx % 2 == 0 else col_b
        with target_col.expander(f"📕 {SUBJECT_NAMES[code]}", expanded=False):
            st.write(f"**ขอบเขตเนื้อหา:** {res_info['title']}")
            st.markdown("**สื่อและแหล่งเรียนรู้ที่แนะนำ:**")
            for r in res_info["resources"]:
                st.markdown(f"- 📖 {r}")

else:
    def calculate_subject_overlap_pct(career_item, selected_subject_ids):
        all_reqs = career_item["primary"] + career_item["secondary"]
        matched = [s for s in selected_subject_ids if s in all_reqs]
        
        if not matched:
            return 0.0, []
        
        total_selected = len(selected_subject_ids)
        overlap_pct = round((len(matched) / total_selected) * 100, 1)
        return overlap_pct, matched

    def get_ranked_careers_with_pct(selected_subject_ids):
        results = []
        for career in CAREERS_DB:
            overlap_pct, matched_subs = calculate_subject_overlap_pct(career, selected_subject_ids)
            
            if overlap_pct > 0:
                results.append({
                    "details": career,
                    "match_pct": overlap_pct,
                    "matched_subs": matched_subs,
                    "primary_subs": career["primary"],
                    "secondary_subs": career["secondary"]
                })
        
        results.sort(key=lambda x: x["match_pct"], reverse=True)
        return results

    # --- ฟังก์ชันแสดงการ์ดอาชีพ (% ความสอดคล้องถูกย้ายมาอยู่ล่างสุด) ---
    def render_career_card(career_item, rank_label=""):
        c = career_item["details"]
        match_pct = career_item["match_pct"]
        
        if rank_label:
            st.markdown(f"#### {rank_label} {c['title']}")
        else:
            st.markdown(f"#### 🎯 **{c['title']}**")
            
        st.write(f"**รายละเอียดอาชีพ:** {c['desc']}")
        
        p_text = ", ".join([f"**{SUBJECT_NAMES[s]}** ({scores[s]} คะแนน)" for s in career_item["primary_subs"] if s in scores])
        s_text = ", ".join([f"{SUBJECT_NAMES[s]} ({scores[s]} คะแนน)" for s in career_item["secondary_subs"] if s in scores])
        
        st.markdown(f"💡 **วิชาหลักที่ใช้ประมวลผล:** {p_text}")
        if s_text:
            st.markdown(f"🛠️ **วิชาสนับสนุน:** {s_text}")
        
        # --- ย้ายความสอดคล้องมาไว้ส่วนล่างสุดของการ์ด ---
        st.progress(min(match_pct / 100, 1.0))
        st.caption(f"📊 **ระดับความเข้ากันของทักษะวิชา: {match_pct}%**")
        st.markdown("---")

    sorted_active = sorted(active_scores.items(), key=lambda x: x[1], reverse=True)
    num_active = len(sorted_active)

    st.subheader("🎯 อาชีพที่เหมาะสมที่สุดจากการประมวลผลทักษะวิชา")

    if num_active == 1:
        single_id, single_score = sorted_active[0]
        st.info(f"💡 **คุณกรอกคะแนน 1 วิชา:** {SUBJECT_NAMES[single_id]} ({single_score} คะแนน)")
        
        c_list = get_ranked_careers_with_pct([single_id])
        for i, item in enumerate(c_list[:3]):
            render_career_card(item, f"🎯 อันดับ {i+1}:")

    elif num_active == 2:
        s1_id, s1_score = sorted_active[0]
        s2_id, s2_score = sorted_active[1]
        st.info(f"💡 **คุณกรอกคะแนน 2 วิชา:** {SUBJECT_NAMES[s1_id]} ({s1_score} คะแนน), {SUBJECT_NAMES[s2_id]} ({s2_score} คะแนน)")
        
        c_list = get_ranked_careers_with_pct([s1_id, s2_id])
        for i, item in enumerate(c_list[:3]):
            badge = f"🥇 อันดับ {i+1} (เหมาะสมที่สุด):" if item["match_pct"] == 100 else f"⭐ อันดับ {i+1}:"
            render_career_card(item, badge)

    else:
        top_3 = sorted_active[:3]
        s1_id, s1_score = top_3[0]
        s2_id, s2_score = top_3[1]
        s3_id, s3_score = top_3[2]

        tab1, tab2, tab3 = st.tabs([
            "🧩 ผลลัพธ์ภาพรวม 3 วิชาหลัก", 
            "⚖️ การจับคู่ย่อย (2 วิชาหลัก)", 
            "💡 แยกตามวิชาเดี่ยว (1 วิชา)"
        ])

        with tab1:
            st.info(f"🎯 **กลุ่ม 3 วิชาเด่นของคุณ:** {SUBJECT_NAMES[s1_id]}, {SUBJECT_NAMES[s2_id]}, {SUBJECT_NAMES[s3_id]}")
            c_list = get_ranked_careers_with_pct([s1_id, s2_id, s3_id])
            
            for i, item in enumerate(c_list[:3]):
                pct = item["match_pct"]
                badge = f"🥇 **อันดับ {i+1} (เหมาะสมที่สุด):**" if pct == 100 else f"⭐ **อันดับ {i+1}:**"
                render_career_card(item, badge)

        with tab2:
            subtab2_1, subtab2_2, subtab2_3 = st.tabs([
                f"1️⃣ {SUBJECT_NAMES[s1_id]} + {SUBJECT_NAMES[s2_id]}",
                f"2️⃣ {SUBJECT_NAMES[s1_id]} + {SUBJECT_NAMES[s3_id]}",
                f"3️⃣ {SUBJECT_NAMES[s2_id]} + {SUBJECT_NAMES[s3_id]}"
            ])
            
            def render_pair_tab(sub1, sub2):
                pair_list = get_ranked_careers_with_pct([sub1, sub2])
                for i, item in enumerate(pair_list[:3]):
                    render_career_card(item, f"🎯 อันดับ {i+1}:")

            with subtab2_1:
                render_pair_tab(s1_id, s2_id)
            with subtab2_2:
                render_pair_tab(s1_id, s3_id)
            with subtab2_3:
                render_pair_tab(s2_id, s3_id)

        with tab3:
            subtab3_1, subtab3_2, subtab3_3 = st.tabs([
                f"🥇 {SUBJECT_NAMES[s1_id]} ({s1_score} คะแนน)",
                f"🥈 {SUBJECT_NAMES[s2_id]} ({s2_score} คะแนน)",
                f"🥉 {SUBJECT_NAMES[s3_id]} ({s3_score} คะแนน)"
            ])
            with subtab3_1:
                for item in get_ranked_careers_with_pct([s1_id])[:3]:
                    render_career_card(item)
            with subtab3_2:
                for item in get_ranked_careers_with_pct([s2_id])[:3]:
                    render_career_card(item)
            with subtab3_3:
                for item in get_ranked_careers_with_pct([s3_id])[:3]:
                    render_career_card(item)

    # --- ส่วนที่ 2: อาชีพอิสระจากวิชาที่ชอบ ---
    st.subheader("🚀 อาชีพอิสระ (Freelance) จากวิชาที่คุณชอบ")
    fav_freelance = FREELANCE_CAREERS_DB[favorite_subject]
    st.success(f"**วิชาที่คุณชอบ:** {SUBJECT_NAMES[favorite_subject]}\n\n"
               f"👉 **อาชีพอิสระที่แนะนำ:** **{fav_freelance['title']}**\n\n"
               f"📝 {fav_freelance['desc']}")

    st.markdown("---")

    # --- ส่วนที่ 3: กราฟสรุปผลคะแนน ---
    st.subheader(f"📊 ภาพรวมคะแนนวิชาทั้งหมด ({chart_type.split(' ')[1]})")

    df_chart = pd.DataFrame({
        "วิชา": [SUBJECT_NAMES[k] for k, v in active_scores.items()],
        "คะแนน": [v for k, v in active_scores.items()]
    })

    if "Radar" in chart_type:
        fig = go.Figure(data=go.Scatterpolar(
            r=df_chart["คะแนน"], theta=df_chart["วิชา"],
            fill='toself', fillcolor='rgba(30, 136, 229, 0.3)',
            line=dict(color=radar_color, width=3)
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False, template=chart_template, height=480
        )
        st.plotly_chart(fig, use_container_width=True)

    elif "Donut" in chart_type:
        fig = px.pie(df_chart, values='คะแนน', names='วิชา', hole=0.45, template=chart_template)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=480)
        st.plotly_chart(fig, use_container_width=True)

    elif "Bar" in chart_type:
        fig = px.bar(
            df_chart, x='วิชา', y='คะแนน', color='คะแนน', text='คะแนน',
            color_continuous_scale='Blues', template=chart_template
        )
        fig.update_traces(textposition='outside', textfont_size=14)
        fig.update_layout(yaxis=dict(range=[0, 115], title="ระดับคะแนน"), height=450)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.dataframe(df_chart, use_container_width=True, hide_index=True)

    st.markdown("---")

    # --- ส่วนที่ 4: สื่อการเรียนรู้สำหรับวิชาที่มีคะแนนต่ำ (< 30 คะแนน) ---
    st.subheader("💡 คำแนะนำสื่อการเรียนรู้เพื่อพัฒนาตนเอง")

    low_score_subjects = [item for item in sorted_active if item[1] < 30]

    if low_score_subjects:
        st.error(f"🚨 **พบทั้งหมด {len(low_score_subjects)} วิชาที่มีคะแนนต่ำกว่า 30 คะแนน (วิชาที่ควรเร่งพัฒนา):**")
        for s_id, score in low_score_subjects:
            res_info = LEARNING_RESOURCES_DB[s_id]
            with st.expander(f"📕 {SUBJECT_NAMES[s_id]} — ได้ {score} คะแนน", expanded=True):
                st.write(f"**ขอบเขตเนื้อหา:** {res_info['title']}")
                st.markdown("**สื่อและแหล่งเรียนรู้ที่แนะนำ:**")
                for r in res_info["resources"]:
                    st.markdown(f"- 📖 {r}")
    else:
        lowest_id, lowest_score = sorted_active[-1]
        res_info = LEARNING_RESOURCES_DB[lowest_id]
        st.info(f"🎉 **ไม่มีวิชาใดได้คะแนนต่ำกว่า 30 คะแนน!** แนะนำสื่อการเรียนรู้สำหรับวิชาที่ได้คะแนนน้อยที่สุดของคุณแทน:")
        with st.expander(f"📙 {SUBJECT_NAMES[lowest_id]} — ได้ {lowest_score} คะแนน", expanded=True):
            st.write(f"**ขอบเขตเนื้อหา:** {res_info['title']}")
            st.markdown("**สื่อและแหล่งเรียนรู้ที่แนะนำ:**")
            for r in res_info["resources"]:
                st.markdown(f"- 📖 {r}")
