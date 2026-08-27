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

# Custom CSS ตกแต่ง Sidebar และ Tabs
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #121212 !important;
    }
    
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 1px solid #444444 !important;
    }
    
    [data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #FFFFFF !important;
    }

    div[data-baseweb="tab-list"] {
        background-color: #0A0A0A !important;
        padding: 6px;
        border-radius: 8px;
    }
    
    button[data-baseweb="tab"] {
        background-color: #1E1E1E !important;
        border-radius: 6px !important;
        margin-right: 4px !important;
        padding: 8px 16px !important;
    }

    button[data-baseweb="tab"] p, 
    button[data-baseweb="tab"] span, 
    button[data-baseweb="tab"] div {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #333333 !important;
        border-bottom: 3px solid #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

if st.session_state.theme_mode == "Dark":
    st.markdown("""
        <style>
        .stApp { background-color: #121212 !important; color: #FFFFFF !important; }
        .stMain p, .stMain h1, .stMain h2, .stMain h3, .stMain h4, .stMain h5, .stMain h6, .stMain span, .stMain div, .stMain .stMarkdown {
            color: #FFFFFF !important;
        }
        div[data-testid="stExpander"] { background-color: #1E1E1E !important; border: 1px solid #444444 !important; }
        </style>
    """, unsafe_allow_html=True)
    chart_template = "plotly_dark"
    radar_color = "#64B5F6"
    font_color = "#FFFFFF"
else:
    st.markdown("""
        <style>
        .stApp { background-color: #FFFFFF; color: #000000; }
        </style>
    """, unsafe_allow_html=True)
    chart_template = "plotly_white"
    radar_color = "#1E88E5"
    font_color = "#212121"

# ---------------------------------------------------------
# 3. ฐานข้อมูลวิชาการเรียน (12 รายวิชา)
# ---------------------------------------------------------
SUBJECT_NAMES = {
    "math": "คณิตศาสตร์ (Math)",
    "science": "วิทยาศาสตร์ (Science)",
    "tech": "คอมพิวเตอร์ (Tech)",
    "english": "ภาษาอังกฤษ (English)",
    "art": "ศิลปะและการออกแบบ (Art)",
    "social": "สังคมศึกษา (Social)",
    "finance": "การเงินและการบัญชี (Finance)",
    "marketing": "การตลาดและธุรกิจ (Marketing)",
    "lang3": "ภาษาที่สาม (3rd Lang)",
    "design_3d": "สถาปัตยกรรม (3D/Arch)",
    "law": "กฎหมายและรัฐศาสตร์ (Law)",
    "psychology": "จิตวิทยา (Psychology)"
}

# ---------------------------------------------------------
# 4. ฐานข้อมูลอาชีพ ครบถ้วนและครอบคลุม
# ---------------------------------------------------------
CAREERS_DB = [
    # --- สายผสม ภาษาอังกฤษ + ศิลปะ ---
    {
        "title": "นักวาดภาพประกอบ / คอมมิคระดับโลก (Global Illustrator / Comic Artist)",
        "primary": ["art"],
        "secondary": ["english", "lang3"],
        "desc": "สร้างสรรค์ผลงานศิลปะ วาดภาพประกอบ และสื่อสารกับผู้ว่าจ้าง/แฟนคลับในต่างประเทศ"
    },
    {
        "title": "นักออกแบบ UI/UX สายนานาชาติ (International UI/UX Designer)",
        "primary": ["art"],
        "secondary": ["english", "tech"],
        "desc": "ออกแบบหน้าตาแอปพลิเคชันและเว็บไซต์โดยใช้หลักศิลปะ ร่วมกับการทำงานทีมต่างชาติ"
    },
    # --- สายภาษาที่สาม ---
    {
        "title": "ล่ามและนักแปลภาษาต่างประเทศ (Interpreter / Translator)",
        "primary": ["lang3"],
        "secondary": ["english", "social"],
        "desc": "แปลภาษา ฟัง-พูด สื่อสารระหว่างประเทศ แปลเอกสารหรือทำหน้าที่ล่ามในการประชุม"
    },
    {
        "title": "พนักงานต้อนรับบนเครื่องบิน (Flight Attendant / Cabin Crew)",
        "primary": ["lang3"],
        "secondary": ["english", "psychology"],
        "desc": "ดูแลความปลอดภัย บริการผู้โดยสารบนเครื่องบิน และใช้ทักษะภาษาต่างประเทศในการสื่อสาร"
    },
    {
        "title": "เจ้าหน้าที่การทูต / วิเทศสัมพันธ์ (Diplomat / Foreign Affairs Officer)",
        "primary": ["lang3"],
        "secondary": ["social", "law"],
        "desc": "เจรจาความสัมพันธ์ระหว่างประเทศ ดูแลงานการทูต และประสานงานองค์กรต่างประเทศ"
    },
    # --- สายวิทยาศาสตร์/แพทย์ ---
    {
        "title": "แพทย์ / หมอรักษาโรค (Medical Doctor)",
        "primary": ["science"],
        "secondary": ["math", "english"],
        "desc": "วินิจฉัยโรค ประยุกต์ใช้วิทยาศาสตร์ คำนวณขนาดยา และอ่านตำราต่างประเทศ"
    },
    {
        "title": "พยาบาลวิชาชีพ (Registered Nurse)",
        "primary": ["science"],
        "secondary": ["psychology", "english"],
        "desc": "ดูแลผู้ป่วย ใช้ความรู้วิทยาศาสตร์ สื่อสารสร้างความอุ่นใจ และดูแลผู้ป่วยต่างชาติ"
    },
    # --- สายจิตวิทยา ---
    {
        "title": "นักจิตวิทยา / ที่ปรึกษาการแนะแนว (Psychologist / Counselor)",
        "primary": ["psychology"],
        "secondary": ["social", "science"],
        "desc": "ให้คำปรึกษา เยียวยาจิตใจ เข้าใจพฤติกรรมมนุษย์และโครงสร้างสังคม"
    },
    {
        "title": "นักทรัพยากรบุคคล / HR (Human Resources Specialist)",
        "primary": ["psychology"],
        "secondary": ["social", "law"],
        "desc": "คัดเลือก พัฒนาบุคลากร คอยดูแลสวัสดิภาพและกฎหมายแรงงานในองค์กร"
    },
    # --- สายคอมพิวเตอร์และคณิตศาสตร์ ---
    {
        "title": "วิศวกรซอฟต์แวร์ / นักเขียนโปรแกรม (Software Developer)",
        "primary": ["tech"],
        "secondary": ["math", "english"],
        "desc": "เขียนโปรแกรมคอมพิวเตอร์ ใช้ตรรกะคณิตศาสตร์แก้ปัญหา"
    },
    {
        "title": "นักวิเคราะห์ข้อมูล (Data Analyst)",
        "primary": ["math", "tech"],
        "secondary": ["finance"],
        "desc": "วิเคราะห์ข้อมูลยอดขายและสถิติธุรกิจด้วยคอมพิวเตอร์และคณิตศาสตร์"
    },
    # --- สายศิลปะและ 3D ---
    {
        "title": "ผู้สร้างคอนเทนต์ / ยูทูปเบอร์ (Content Creator / YouTuber)",
        "primary": ["art"],
        "secondary": ["marketing", "tech"],
        "desc": "คิดคอนเทนต์ ตัดต่อวิดีโอ (Art/Tech) วางกลยุทธ์สร้างยอดวิว (Marketing)"
    },
    {
        "title": "สถาปนิก / นักออกแบบ 3D (Architect / 3D Designer)",
        "primary": ["design_3d"],
        "secondary": ["art", "math"],
        "desc": "ออกแบบอาคารสถานที่ วาดแบบ 3D และคำนวณโครงสร้างตามหลักสถาปัตยกรรม"
    },
    # --- สายธุรกิจและการเงิน ---
    {
        "title": "พ่อค้าแม่ค้าออนไลน์ (E-commerce Seller)",
        "primary": ["marketing"],
        "secondary": ["finance", "tech"],
        "desc": "ยิงโฆษณาออนไลน์ บริหารต้นทุนกำไร และบริหารระบบขายสินค้าออนไลน์"
    },
    {
        "title": "นักการเงิน / ผู้จัดการกองทุน (Financial Analyst / Fund Manager)",
        "primary": ["finance"],
        "secondary": ["math", "marketing"],
        "desc": "วิเคราะห์การลงทุน บริหารความเสี่ยงทางการเงิน และจัดการผลตอบแทน"
    },
    # --- สายกฎหมายและสังคม ---
    {
        "title": "นักกฎหมาย / ทนายความ (Lawyer / Legal Advisor)",
        "primary": ["law"],
        "secondary": ["social", "english"],
        "desc": "ตีความกฎหมาย ร่างสัญญา ดำเนินคดี และว่าความในชั้นศาล"
    }
]

FREELANCE_CAREERS_DB = {
    "math": {"title": "Tutor สอนพิเศษคณิตศาสตร์ / Data Freelance", "desc": "รับสอนพิเศษวิชาคณิตศาสตร์ สถิติ หรือรับทำวิเคราะห์ข้อมูลสถิติเชิงลึก"},
    "science": {"title": "นักเขียนบทความสุขภาพและวิทยาศาสตร์", "desc": "รับเขียนบทความความรู้ สุขภาพ อาหาร และวิทยาศาสตร์ลงสื่อออนไลน์"},
    "tech": {"title": "Freelance รับทำเว็บไซต์ / ไอทีซัพพอร์ต", "desc": "รับสร้างเว็บไซต์ร้านค้า พัฒนาแอปพลิเคชัน และดูแลระบบคอมพิวเตอร์"},
    "english": {"title": "นักแปลเอกสารอิสระ / พิสูจน์อักษร", "desc": "รับแปลเอกสาร แปลซับไตเติล หรือเขียนอีเมลติดต่อธุรกิจภาษาต่างประเทศ"},
    "art": {"title": "Freelance Illustrator / ช่างภาพ", "desc": "รับวาดภาพประกอบ วาดสติกเกอร์ไลน์ ถ่ายภาพ และออกแบบกราฟิก"},
    "social": {"title": "นักสร้างคอนเทนต์ประวัติศาสตร์/สังคม", "desc": "ทำคลิปเล่าเรื่องประวัติศาสตร์ สังคมวิทยา หรือเรื่องน่ารู้รอบโลก"},
    "finance": {"title": "รับทำบัญชีร้านค้า / วางแผนภาษีบุคคล", "desc": "ช่วยร้านค้าเล็กๆ วางแผนภาษี ยื่นภาษี และสรุปงบการเงินรายรับรายจ่าย"},
    "marketing": {"title": "Freelance ดูแลเพจ / ยิงแอดโฆษณา", "desc": "รับเขียนโพสต์ขายของ วางแผนคอนเทนต์ และยิงแอด Facebook/TikTok"},
    "lang3": {"title": "ล่ามอิสระ / มัคคุเทศก์ภาษาเฉพาะ", "desc": "รับงานแปลภาษาเฉพาะกิจ ล่ามติดตาม หรือนำเที่ยวชาวต่างชาติ"},
    "design_3d": {"title": "Freelance ขึ้นโมเดล 3D / เขียนแบบบ้าน", "desc": "รับขึ้นโมเดล 3D สินค้า หรือออกแบบและเขียนแบบบ้านให้ลูกค้า"},
    "law": {"title": "ที่ปรึกษาข้อกฎหมายร้านค้าและตรวจสัญญา", "desc": "ให้คำปรึกษาการทำสัญญาเช่า สัญญาจ้างงาน และตรวจข้อตกลงทางกฎหมาย"},
    "psychology": {"title": "ที่ปรึกษาพัฒนาบุคลิกภาพ / Life Coach", "desc": "ให้คำปรึกษาเรื่องการสื่อสาร การบริหารจิตใจ และการพัฒนาศักยภาพตนเอง"}
}

LEARNING_RESOURCES_DB = {
    "math": {"title": "คณิตศาสตร์และสถิติ", "resources": ["Khan Academy Math", "Coursera: Essential Mathematics", "SmartMathPro"]},
    "science": {"title": "วิทยาศาสตร์และเทคโนโลยี", "resources": ["edX: Introductory Physics", "National Geographic Science", "คลังความรู้วิทยาศาสตร์ สสวท."]},
    "tech": {"title": "วิทยาการคำนวณและโปรแกรมมิ่ง", "resources": ["freeCodeCamp.org", "Codecademy Python", "Harvard CS50"]},
    "english": {"title": "ภาษาอังกฤษเพื่อการสื่อสาร", "resources": ["BBC Learning English", "Duolingo App", "TED Talks"]},
    "art": {"title": "ศิลปะและการออกแบบ", "resources": ["Canva Design School", "Skillshare Art Courses", "Adobe Creative Cloud Tutorials"]},
    "social": {"title": "สังคมศึกษาและการเมืองโลก", "resources": ["edX: Global History", "8 Minutes History Podcast", "National Geographic"]},
    "finance": {"title": "การเงิน บัญชี และการลงทุน", "resources": ["SET e-Learning (ตลาดหลักทรัพย์)", "Coursera Finance for Non-Finance", "Money Buffalo"]},
    "marketing": {"title": "การตลาดดิจิทัลและธุรกิจ", "resources": ["Google Digital Garage", "HubSpot Academy", "The Secret Sauce Podcast"]},
    "lang3": {"title": "ภาษาที่สาม (3rd Language)", "resources": ["Memrise", "Busuu App", "คอร์สเรียนภาษาต่างประเทศออนไลน์"]},
    "design_3d": {"title": "สถาปัตยกรรมและ 3D Design", "resources": ["Blender Guru Tutorials", "SketchUp Campus", "Coursera: Architecture Design"]},
    "law": {"title": "กฎหมายและรัฐศาสตร์", "resources": ["คอร์สกฎหมายประชาชน (จุฬาฯ MOOC)", "edX: International Law", "คลังกฎหมายไทย"]},
    "psychology": {"title": "จิตวิทยาพฤติกรรมมนุษย์", "resources": ["Coursera: Intro to Psychology (Yale)", "Psych2Go Channel", "หนังสือสรุปจิตวิทยา"]}
}

# ---------------------------------------------------------
# 5. เมนูกรอกข้อมูล Sidebar
# ---------------------------------------------------------
st.sidebar.header("📝 1. กรอกคะแนนรายวิชา (0-100)")
scores = {}
for code, name in SUBJECT_NAMES.items():
    scores[code] = st.sidebar.slider(name, 0, 100, 0)

st.sidebar.markdown("---")
st.sidebar.header("❤️ 2. วิชาที่คุณชอบที่สุด")
favorite_subject = st.sidebar.selectbox(
    "เลือกวิชาที่ชอบ (คำนวณอาชีพอิสระ):",
    options=list(SUBJECT_NAMES.keys()),
    format_func=lambda x: SUBJECT_NAMES[x]
)

st.sidebar.markdown("---")
chart_type = st.sidebar.radio(
    "รูปแบบการแสดงผลคะแนน:",
    ["📊 กราฟแท่งเข้าใจง่าย (Bar Chart)", "🕸️ กราฟแมงมุม (Radar Chart)", "🍩 กราฟวงกลม (Donut Chart)", "📋 ตารางข้อมูล (Table)"]
)

# ---------------------------------------------------------
# 6. อัลกอริทึมและการประมวลผล (Main Logic)
# ---------------------------------------------------------
with col_title:
    st.title("🎓 Smart Career Recommendation System")
    st.caption("ระบบวิเคราะห์อาชีพอัจฉริยะ (Strict Matching + Fallback Notification)")

st.markdown("---")

active_scores = {k: v for k, v in scores.items() if v > 0}

if len(active_scores) == 0:
    st.error("🚫 **ไม่พบข้อมูลคะแนน**")
    st.warning("⚠️ กรุณากรอกคะแนนอย่างน้อย 1 วิชาในแถบสีดำฝั่งซ้าย เพื่อเปิดการประมวลผล")
    
    st.markdown("---")
    st.subheader("📚 คลังสื่อการเรียนรู้แนะนำสำหรับผู้เริ่มต้นศึกษา (Learning Resources)")
    col_a, col_b = st.columns(2)
    sub_keys = list(SUBJECT_NAMES.keys())
    for idx, code in enumerate(sub_keys):
        res_info = LEARNING_RESOURCES_DB[code]
        target_col = col_a if idx % 2 == 0 else col_b
        with target_col.expander(f"📖 {SUBJECT_NAMES[code]}", expanded=False):
            st.write(f"**เน้นทักษะด้าน:** {res_info['title']}")
            for r in res_info["resources"]:
                st.markdown(f"- 🔗 {r}")

else:
    # --- อัลกอริทึมคำนวณความสอดคล้องที่แท้จริง (คิดเฉพาะวิชาที่มีคะแนน > 0) ---
    def calculate_weighted_career_match(career):
        primary_subs = career["primary"]
        secondary_subs = career["secondary"]
        
        active_primary = [s for s in primary_subs if scores[s] > 0]
        active_secondary = [s for s in secondary_subs if scores[s] > 0]
        
        if not active_primary:
            return 0.0, [], primary_subs, secondary_subs

        p_avg = sum(scores[s] for s in active_primary) / len(active_primary)
        
        if active_secondary:
            s_avg = sum(scores[s] for s in active_secondary) / len(active_secondary)
            final_match = (p_avg * 0.60) + (s_avg * 0.40)
        else:
            final_match = p_avg

        matched_used = active_primary + active_secondary
        return round(final_match, 1), matched_used, primary_subs, secondary_subs

    # --- ฟังก์ชันกรองอาชีพแบบ Strict AND Logic ---
    def get_all_ranked_careers(filter_subject_ids=None):
        ranked = []
        for career in CAREERS_DB:
            all_reqs = career["primary"] + career["secondary"]
            
            if filter_subject_ids:
                # บังคับว่าอาชีพนั้นต้องมีโครงสร้างรายวิชาตรงกับที่เลือก "ครบทุกวิชา"
                has_all_subjects = all(s in all_reqs for s in filter_subject_ids)
                if not has_all_subjects:
                    continue
            
            match_pct, matched_used, p_subs, s_subs = calculate_weighted_career_match(career)
            
            if match_pct > 0:
                ranked.append({
                    "details": career,
                    "match_pct": match_pct,
                    "matched_used": matched_used,
                    "primary_subs": p_subs,
                    "secondary_subs": s_subs
                })
        
        ranked.sort(key=lambda x: x["match_pct"], reverse=True)
        return ranked

    def render_career_card(career_item, rank_label=""):
        c = career_item["details"]
        match_pct = career_item["match_pct"]
        
        if rank_label:
            st.markdown(f"#### {rank_label} {c['title']}")
        else:
            st.markdown(f"#### 🎯 **{c['title']}**")
            
        st.progress(min(match_pct / 100, 1.0))
        st.caption(f"📊 ดัชนีความสอดคล้องที่แท้จริง: **{match_pct}%**")
        st.write(f"**ลักษณะงานจริง:** {c['desc']}")
        
        p_text = ", ".join([f"**{SUBJECT_NAMES[s]}** ({scores[s]} คะแนน)" for s in career_item["primary_subs"]])
        s_text = ", ".join([f"{SUBJECT_NAMES[s]} ({scores[s]} คะแนน)" for s in career_item["secondary_subs"]])
        
        st.markdown(f"🔑 **วิชาหลัก (60%):** {p_text}")
        st.markdown(f"🛠️ **วิชาสนับสนุน (40%):** {s_text}")
        st.markdown("---")

    sorted_active = sorted(active_scores.items(), key=lambda x: x[1], reverse=True)
    num_active = len(sorted_active)

    st.subheader("📌 ผลการวิเคราะห์และจัดอันดับอาชีพที่เหมาะสม")

    # === การจัดอันดับและแท็บแสดงผล ===
    if num_active == 1:
        single_id, single_score = sorted_active[0]
        st.info(f"💡 **คุณกรอกคะแนนเพียง 1 วิชา:** {SUBJECT_NAMES[single_id]} ({single_score} คะแนน)")
        
        c_list = get_all_ranked_careers([single_id])
        if c_list:
            for i, item in enumerate(c_list[:3]):
                render_career_card(item, f"🥇 อันดับ {i+1}:" if i==0 else f"🎯 อันดับ {i+1}:")
        else:
            st.warning("ยังไม่พบอาชีพในฐานข้อมูลที่ใช้วิชานี้")

    elif num_active == 2:
        s1_id, s1_score = sorted_active[0]
        s2_id, s2_score = sorted_active[1]
        st.info(f"💡 **คุณกรอกคะแนน 2 วิชา:** {SUBJECT_NAMES[s1_id]} ({s1_score} คะแนน), {SUBJECT_NAMES[s2_id]} ({s2_score} คะแนน)")
        
        c_list = get_all_ranked_careers([s1_id, s2_id])
        if c_list:
            for i, item in enumerate(c_list[:3]):
                render_career_card(item, f"🎯 อันดับ {i+1}:")
        else:
            # 🔔 FALLBACK NOTIFICATION: เมื่อไม่พบความสอดคล้องคู่กัน
            st.warning(f"⚠️ **ไม่พบอาชีพในฐานข้อมูลที่ต้องใช้ทักษะแบบผสมระหว่าง [{SUBJECT_NAMES[s1_id]}] + [{SUBJECT_NAMES[s2_id]}] พร้อมกัน**")
            st.notice("💡 **คำแนะนำในการดูผลลัพธ์:**\n"
                      f"1. สองวิชานี้อาจเป็นทักษะคนละสายงาน กรุณาเลือกเปิดดูความสอดคล้อง **แยกตามรายวิชาเดี่ยว (1 วิชา)** ในแท็บด้านล่าง\n"
                      f"2. หรือลองกรอกคะแนนเพิ่มอีก 1 วิชา เพื่อเปิดดูการประมวลผล **ภาพรวม 3 วิชา**")
            
            subtab_single1, subtab_single2 = st.tabs([
                f"🥇 แยกดูเฉพาะ: {SUBJECT_NAMES[s1_id]}",
                f"🥈 แยกดูเฉพาะ: {SUBJECT_NAMES[s2_id]}"
            ])
            with subtab_single1:
                for item in get_all_ranked_careers([s1_id])[:3]:
                    render_career_card(item)
            with subtab_single2:
                for item in get_all_ranked_careers([s2_id])[:3]:
                    render_career_card(item)

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
            c_list = get_all_ranked_careers([s1_id, s2_id, s3_id])
            
            if c_list:
                rank_badges = ["🥇 **อันดับ 1:**", "🥈 **อันดับ 2:**", "🥉 **อันดับ 3:**"]
                for i, item in enumerate(c_list[:3]):
                    badge = rank_badges[i] if i < len(rank_badges) else "🎯 **แนะนำเพิ่มเติม:**"
                    render_career_card(item, badge)
            else:
                st.warning("⚠️ **ไม่พบอาชีพสายตรงที่ต้องใช้ทักษะทั้ง 3 วิชานี้ร่วมกันทั้งหมด**")
                st.info("👉 กรุณาคลิกเลือกแท็บ **'⚖️ การจับคู่ย่อย (2 วิชาหลัก)'** หรือ **'💡 แยกตามวิชาเดี่ยว'** ด้านบน เพื่อดูอาชีพที่สอดคล้องทดแทน")

        with tab2:
            subtab2_1, subtab2_2, subtab2_3 = st.tabs([
                f"1️⃣ {SUBJECT_NAMES[s1_id]} + {SUBJECT_NAMES[s2_id]}",
                f"2️⃣ {SUBJECT_NAMES[s1_id]} + {SUBJECT_NAMES[s3_id]}",
                f"3️⃣ {SUBJECT_NAMES[s2_id]} + {SUBJECT_NAMES[s3_id]}"
            ])
            
            # ฟังก์ชันช่วยสร้าง Fallback Warning ในแท็บคู่ย่อย
            def render_pair_tab(sub1, sub2):
                pair_list = get_all_ranked_careers([sub1, sub2])
                if pair_list:
                    for item in pair_list[:3]:
                        render_career_card(item)
                else:
                    st.warning(f"⚠️ **ไม่พบความสอดคล้องระหว่าง [{SUBJECT_NAMES[sub1]}] + [{SUBJECT_NAMES[sub2]}]**")
                    st.info(f"💡 สองวิชานี้ไม่ได้ใช้ร่วมกันโดยตรงในสายอาชีพมาตรฐาน แนะนำให้ไปที่แท็บ **'🧩 ผลลัพธ์ภาพรวม 3 วิชาหลัก'** หรือ **'💡 แยกตามวิชาเดี่ยว (1 วิชา)'** เพื่อดูผลวิเคราะห์ที่เหมาะสมที่สุดแทนครับ")

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
                for item in get_all_ranked_careers([s1_id])[:3]:
                    render_career_card(item)
            with subtab3_2:
                for item in get_all_ranked_careers([s2_id])[:3]:
                    render_career_card(item)
            with subtab3_3:
                for item in get_all_ranked_careers([s3_id])[:3]:
                    render_career_card(item)

    # === อาชีพอิสระ ===
    st.subheader("🚀 เส้นทางอาชีพอิสระ (Freelance Options)")
    fav_freelance = FREELANCE_CAREERS_DB[favorite_subject]
    st.success(f"**จากวิชาที่คุณชื่นชอบเป็นพิเศษ:** {SUBJECT_NAMES[favorite_subject]}\n\n"
               f"👉 **อาชีพอิสระที่แนะนำ:** **{fav_freelance['title']}**\n\n"
               f"📝 {fav_freelance['desc']}")

    st.markdown("---")

    # === กราฟแสดงผลคะแนน ===
    st.subheader(f"📊 กราฟสรุปผลวิเคราะห์ทักษะ ({chart_type.split(' ')[0]})")

    df_chart = pd.DataFrame({
        "วิชา": [SUBJECT_NAMES[k] for k, v in active_scores.items()],
        "คะแนน": [v for k, v in active_scores.items()]
    })

    if "Bar" in chart_type:
        fig = px.bar(
            df_chart, x='วิชา', y='คะแนน', color='คะแนน', text='คะแนน',
            color_continuous_scale='Blues', template=chart_template
        )
        fig.update_traces(textposition='outside', textfont_size=14)
        fig.update_layout(yaxis=dict(range=[0, 115], title="ระดับคะแนน"), height=450)
        st.plotly_chart(fig, use_container_width=True)

    elif "Radar" in chart_type:
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

    else:
        st.dataframe(df_chart, use_container_width=True, hide_index=True)

    st.markdown("---")

    # === ระบบแนะนำสื่อการเรียนรู้ ===
    st.subheader("💡 ระบบแนะนำสื่อการเรียนรู้และพัฒนาทักษะ (Skill Enhancement)")
    low_scores = [item for item in sorted_active if item[1] < 50]

    if low_scores:
        st.warning(f"🚨 **พบวิชาที่คุณได้คะแนนน้อยกว่า 50 คะแนน จำนวน {len(low_scores)} วิชาที่ควรเร่งพัฒนา:**")
        col_l1, col_l2 = st.columns(2)
        for i, (s_id, score) in enumerate(low_scores):
            res_info = LEARNING_RESOURCES_DB[s_id]
            target_col = col_l1 if i % 2 == 0 else col_l2
            with target_col.expander(f"📙 {SUBJECT_NAMES[s_id]} — ได้ {score} คะแนน", expanded=True):
                st.write(f"**ขอบเขตทักษะ:** {res_info['title']}")
                for r in res_info["resources"]:
                    st.markdown(f"- 📖 {r}")
    else:
        lowest_id, lowest_score = sorted_active[-1]
        res_info = LEARNING_RESOURCES_DB[lowest_id]
        st.success(f"🎉 **ทักษะยอดเยี่ยมมาก! ไม่มีวิชาใดได้คะแนนต่ำกว่า 50 คะแนนเลย**")
        with st.expander(f"📘 แนะนำคอร์สเรียนเสริมความเชี่ยวชาญสำหรับ: {SUBJECT_NAMES[lowest_id]}", expanded=False):
            st.write(f"**ขอบเขตทักษะ:** {res_info['title']}")
            for r in res_info["resources"]:
                st.markdown(f"- 📖 {r}")
