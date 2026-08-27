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

# ---------------------------------------------------------
# CSS: ปรับแถบซ้าย (Sidebar) และ Tab เป็นสีดำ ตัวหนังสือขาว
# ---------------------------------------------------------
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
# 4. ฐานข้อมูลอาชีพ & สื่อการเรียนรู้ (DB)
# ---------------------------------------------------------
CAREERS_DB = [
    {
        "title": "นักจิตวิทยา / ที่ปรึกษาการแนะแนว (Psychologist / Counselor)",
        "subjects": ["psychology", "social"],
        "desc": "ให้คำปรึกษา เยียวยาจิตใจ เข้าใจพฤติกรรมมนุษย์และโครงสร้างสังคม"
    },
    {
        "title": "นักทรัพยากรบุคคล / HR (Human Resources Specialist)",
        "subjects": ["psychology", "social", "law"],
        "desc": "คัดเลือก พัฒนาบุคลากร คอยดูแลสวัสดิภาพและกฎหมายแรงงานในองค์กร"
    },
    {
        "title": "นักจัดกิจกรรมบำบัด / บำบัดพฤติกรรม (Behavior Therapist)",
        "subjects": ["psychology", "science"],
        "desc": "ฟื้นฟูสภาพจิตใจและพฤติกรรมผู้ป่วย โดยประยุกต์ใช้ความรู้ทางวิทยาศาสตร์และจิตวิทยา"
    },
    {
        "title": "พยาบาลวิชาชีพ (Registered Nurse)",
        "subjects": ["science", "psychology", "english"],
        "desc": "ดูแลผู้ป่วย ใช้ความรู้วิทยาศาสตร์ สื่อสารสร้างความอุ่นใจ (Psychology) และดูแลผู้ป่วยต่างชาติ"
    },
    {
        "title": "แพทย์ / หมอรักษาโรค (Medical Doctor)",
        "subjects": ["science", "math", "english"],
        "desc": "วินิจฉัยโรค ประยุกต์ใช้วิทยาศาสตร์ คำนวณขนาดยา และอ่านตำราต่างประเทศ"
    },
    {
        "title": "ผู้สร้างคอนเทนต์ / ยูทูปเบอร์ (Content Creator / YouTuber)",
        "subjects": ["art", "marketing", "tech"],
        "desc": "คิดคอนเทนต์ ตัดต่อวิดีโอ (Art/Tech) วางกลยุทธ์สร้างยอดวิว (Marketing)"
    },
    {
        "title": "พ่อค้าแม่ค้าออนไลน์ (E-commerce Seller)",
        "subjects": ["marketing", "finance", "tech"],
        "desc": "ยิงโฆษณาออนไลน์ บริหารต้นทุนกำไร และบริหารระบบขายสินค้าออนไลน์"
    },
    {
        "title": "นักวิเคราะห์ข้อมูล (Data Analyst)",
        "subjects": ["math", "tech", "finance"],
        "desc": "วิเคราะห์ข้อมูลยอดขายและสถิติธุรกิจด้วยคอมพิวเตอร์และคณิตศาสตร์"
    },
    {
        "title": "วิศวกรซอฟต์แวร์ / นักเขียนโปรแกรม (Software Developer)",
        "subjects": ["tech", "math", "english"],
        "desc": "เขียนโปรแกรมคอมพิวเตอร์ ใช้ตรรกะคณิตศาสตร์แก้ปัญหา"
    }
]

FREELANCE_CAREERS_DB = {
    "math": {"title": "Tutor สอนพิเศษคณิตศาสตร์", "desc": "รับสอนพิเศษวิชาคณิตศาสตร์ สถิติ หรือรับทำแบบวิเคราะห์ข้อมูลตัวเลข"},
    "science": {"title": "นักเขียนบทความสุขภาพและวิทยาศาสตร์", "desc": "รับเขียนบทความความรู้ สุขภาพ อาหาร และวิทยาศาสตร์ลงเพจ"},
    "tech": {"title": "Freelance รับทำเว็บไซต์ / ไอทีซัพพอร์ต", "desc": "รับสร้างเว็บไซต์ร้านค้า ปรับแต่งระบบคอมพิวเตอร์"},
    "english": {"title": "นักแปลเอกสารอิสระ", "desc": "รับแปลเอกสาร แปลซับไตเติล หรือเขียนอีเมลธุรกิจภาษาอังกฤษ"},
    "art": {"title": "Freelance Illustrator / ช่างภาพ", "desc": "รับวาดภาพ วาดสติกเกอร์ไลน์ หรือรับถ่ายภาพ"},
    "social": {"title": "นักเล่าเรื่องประวัติศาสตร์/สังคม", "desc": "ทำคลิปเล่าเรื่องประวัติศาสตร์ สังคม หรือเรื่องน่ารู้รอบโลก"},
    "finance": {"title": "รับทำบัญชีร้านค้า / วางแผนภาษี", "desc": "ช่วยร้านค้าเล็กๆ วางแผนภาษี ยื่นภาษี และสรุปรายรับรายจ่าย"},
    "marketing": {"title": "Freelance ดูแลเพจ / ยิงแอดโฆษณา", "desc": "รับเขียนโพสต์ขายของ ยิงแอด Facebook/TikTok"},
    "lang3": {"title": "ล่ามอิสระ / ไกด์นำเที่ยวต่างชาติ", "desc": "รับงานแปลภาษาเฉพาะกิจ ล่ามติดตาม หรือนำเที่ยวชาวต่างชาติ"},
    "design_3d": {"title": "Freelance ขึ้นโมเดล 3D / เขียนแบบ", "desc": "รับเขียนแบบบ้าน 3D ให้ลูกค้าเห็นภาพก่อนสร้างจริง"},
    "law": {"title": "ที่ปรึกษาข้อกฎหมายร้านค้าและสัญญาอิสระ", "desc": "ให้คำปรึกษาการทำสัญญาเช่า สัญญาจ้างงาน"},
    "psychology": {"title": "ที่ปรึกษาการปรับบุคลิกภาพ / Life Coach", "desc": "ให้คำปรึกษาเรื่องการสื่อสาร การพัฒนาตนเอง และจิตวิทยาเชิงบวก"}
}

LEARNING_RESOURCES_DB = {
    "math": {"title": "คณิตศาสตร์และสถิติ", "resources": ["Khan Academy Math", "Coursera: Essential Mathematics", "SmartMathPro"]},
    "science": {"title": "วิทยาศาสตร์และฟิสิกส์", "resources": ["edX: Introductory Physics", "National Geographic Portal", "คลังความรู้วิทยาศาสตร์ สสวท."]},
    "tech": {"title": "วิทยาการคำนวณและเขียนโค้ด", "resources": ["freeCodeCamp.org", "Codecademy Python", "Harvard CS50"]},
    "english": {"title": "ภาษาอังกฤษสากล", "resources": ["BBC Learning English", "Duolingo App", "TED Talks"]},
    "art": {"title": "ศิลปะและการออกแบบ", "resources": ["Canva Design School", "Skillshare Art Courses", "Youtube: Adobe Creative Cloud"]},
    "social": {"title": "สังคมศึกษาและการเมืองโลก", "resources": ["edX: Global History", "8 Minutes History Podcast", "National Geographic"]},
    "finance": {"title": "การเงิน บัญชี และการลงทุน", "resources": ["SET e-Learning (ตลาดหลักทรัพย์)", "Coursera Finance for Non-Finance", "Money Buffalo"]},
    "marketing": {"title": "การตลาดดิจิทัลและธุรกิจ", "resources": ["Google Digital Garage", "HubSpot Academy", "The Secret Sauce Podcast"]},
    "lang3": {"title": "ภาษาที่สาม", "resources": ["Memrise", "Busuu App", "คอร์สเรียนภาษาต่างประเทศออนไลน์"]},
    "design_3d": {"title": "สถาปัตยกรรมและ 3D", "resources": ["Blender Guru Tutorials", "SketchUp Campus", "Coursera: Architecture Design"]},
    "law": {"title": "กฎหมายและรัฐศาสตร์", "resources": ["คอร์สกฎหมายประชาชน (จุฬาฯ MOOC)", "edX: International Law", "คลังกฎหมายไทย"]},
    "psychology": {"title": "จิตวิทยาพฤติกรรม", "resources": ["Coursera: Intro to Psychology (Yale)", "Psych2Go Channel", "หนังสือสรุปจิตวิทยา"]}
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
# 6. อัลกอริทึมและการแสดงผล (Main Logic)
# ---------------------------------------------------------
with col_title:
    st.title("🎓 Smart Career Recommendation System")
    st.caption("ระบบวิเคราะห์อาชีพอัจฉริยะ (คำนวณแม่นยำ + กราฟดูง่าย + สื่อการเรียนรู้)")

st.markdown("---")

active_scores = {k: v for k, v in scores.items() if v > 0}

if len(active_scores) == 0:
    st.error("🚫 **ไม่พบข้อมูลคะแนน**")
    st.warning("⚠️ กรุณากรอกคะแนนอย่างน้อย 1 วิชาในแถบสีดำฝั่งซ้าย เพื่อเปิดการประมวลผล")
    
    st.markdown("---")
    st.subheader("📚 คลังสื่อการเรียนรู้แนะนำสำหรับผู้เริ่มต้นศึกษา (Learning Resources)")
    st.caption("คลิกที่แต่ละรายวิชาเพื่อดูคอร์สและแหล่งเรียนรู้ฟรีที่แนะนำ:")
    
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
    sorted_active = sorted(active_scores.items(), key=lambda x: x[1], reverse=True)
    num_active = len(sorted_active)

    def render_career_card(career_item, rank_label=""):
        c = career_item["details"]
        match_pct = career_item["match_pct"]
        
        if rank_label:
            st.markdown(f"#### {rank_label} {c['title']}")
        else:
            st.markdown(f"#### 🎯 **{c['title']}**")
            
        st.progress(min(match_pct / 100, 1.0))
        st.caption(f"📊 ดัชนีความสอดคล้อง: **{match_pct}%** (คะแนนวิชาที่ใช้คิด: {career_item['score_sum']} / {career_item['max_possible']})")
        st.write(f"**ลักษณะงานจริง:** {c['desc']}")
        
        used_sub_text = ", ".join([f"**{SUBJECT_NAMES[s]}** ({scores[s]} คะแนน)" for s in career_item["matched_subjects"]])
        st.markdown(f"💡 **องค์ความรู้ที่นำมาใช้ประมวลผล:** {used_sub_text}")
        st.markdown("---")

    def find_matching_careers(target_subject_ids):
        results = []
        for career in CAREERS_DB:
            c_subjs = career["subjects"]
            matched = [s for s in c_subjs if s in target_subject_ids and scores[s] > 0]
            
            if matched:
                score_sum = sum([scores[s] for s in matched])
                max_possible = sum([100 for s in matched])
                match_pct = round((score_sum / max_possible) * 100, 1)
                
                results.append({
                    "details": career,
                    "matched_subjects": matched,
                    "matched_count": len(matched),
                    "score_sum": score_sum,
                    "max_possible": max_possible,
                    "match_pct": match_pct
                })
        
        results.sort(key=lambda x: (x["matched_count"], x["match_pct"]), reverse=True)
        return results

    st.subheader("📌 ผลการวิเคราะห์และจัดอันดับอาชีพที่เหมาะสม")

    # === 1. การจัดอันดับอาชีพ ===
    if num_active == 1:
        single_id, single_score = sorted_active[0]
        st.info(f"💡 **คุณกรอกคะแนนเพียง 1 วิชา:** {SUBJECT_NAMES[single_id]} ({single_score} คะแนน)")
        st.caption("ระบบจะแสดงผลเฉพาะอาชีพที่ตรงกับวิชานี้เท่านั้น (ไม่ดึงวิชาคะแนน 0 มารวม)")
        
        c_list = find_matching_careers([single_id])
        if c_list:
            for i, item in enumerate(c_list[:3]):
                render_career_card(item, f"🥇 อันดับ {i+1}:" if i==0 else f"🎯 อันดับ {i+1}:")
        else:
            st.warning("ยังไม่พบอาชีพเฉพาะทางในฐานข้อมูลที่ใช้วิชานี้วิชาเดียว")

    elif num_active == 2:
        s1_id, s1_score = sorted_active[0]
        s2_id, s2_score = sorted_active[1]
        st.info(f"💡 **คุณกรอกคะแนน 2 วิชา:** {SUBJECT_NAMES[s1_id]} ({s1_score} คะแนน), {SUBJECT_NAMES[s2_id]} ({s2_score} คะแนน)")
        
        c_list = find_matching_careers([s1_id, s2_id])
        if c_list:
            for i, item in enumerate(c_list[:3]):
                render_career_card(item, f"🎯 อันดับ {i+1}:")
        else:
            st.warning("ไม่พบอาชีพที่สอดคล้องกับคู่วิชานี้")

    else:
        top_3 = sorted_active[:3]
        s1_id, s1_score = top_3[0]
        s2_id, s2_score = top_3[1]
        s3_id, s3_score = top_3[2]

        tab1, tab2, tab3 = st.tabs([
            "🧩 ผลลัพธ์จาก 3 วิชาหลัก", 
            "⚖️ การจับคู่ย่อย (2 วิชาหลัก)", 
            "💡 แยกตามวิชาเดี่ยว"
        ])

        with tab1:
            st.info(f"🎯 **กลุ่ม 3 วิชาเด่นของคุณ:** {SUBJECT_NAMES[s1_id]}, {SUBJECT_NAMES[s2_id]}, {SUBJECT_NAMES[s3_id]}")
            c_list = find_matching_careers([s1_id, s2_id, s3_id])
            
            if c_list:
                rank_badges = ["🥇 **อันดับ 1:**", "🥈 **อันดับ 2:**", "🥉 **อันดับ 3:**"]
                for i, item in enumerate(c_list[:3]):
                    badge = rank_badges[i] if i < len(rank_badges) else "🎯 **แนะนำเพิ่มเติม:**"
                    render_career_card(item, badge)
            else:
                st.warning("ไม่พบอาชีพในฐานข้อมูลที่สอดคล้องกับกลุ่มวิชานี้")

        with tab2:
            subtab2_1, subtab2_2, subtab2_3 = st.tabs([
                f"1️⃣ {SUBJECT_NAMES[s1_id]} + {SUBJECT_NAMES[s2_id]}",
                f"2️⃣ {SUBJECT_NAMES[s1_id]} + {SUBJECT_NAMES[s3_id]}",
                f"3️⃣ {SUBJECT_NAMES[s2_id]} + {SUBJECT_NAMES[s3_id]}"
            ])
            with subtab2_1:
                for item in find_matching_careers([s1_id, s2_id])[:3]:
                    render_career_card(item)
            with subtab2_2:
                for item in find_matching_careers([s1_id, s3_id])[:3]:
                    render_career_card(item)
            with subtab2_3:
                for item in find_matching_careers([s2_id, s3_id])[:3]:
                    render_career_card(item)

        with tab3:
            subtab3_1, subtab3_2, subtab3_3 = st.tabs([
                f"🥇 {SUBJECT_NAMES[s1_id]} ({s1_score} คะแนน)",
                f"🥈 {SUBJECT_NAMES[s2_id]} ({s2_score} คะแนน)",
                f"🥉 {SUBJECT_NAMES[s3_id]} ({s3_score} คะแนน)"
            ])
            with subtab3_1:
                for item in find_matching_careers([s1_id])[:3]:
                    render_career_card(item)
            with subtab3_2:
                for item in find_matching_careers([s2_id])[:3]:
                    render_career_card(item)
            with subtab3_3:
                for item in find_matching_careers([s3_id])[:3]:
                    render_career_card(item)

    # === 2. อาชีพอิสระ ===
    st.subheader("🚀 เส้นทางอาชีพอิสระ (Freelance Options)")
    fav_freelance = FREELANCE_CAREERS_DB[favorite_subject]
    st.success(f"**จากวิชาที่คุณชื่นชอบเป็นพิเศษ:** {SUBJECT_NAMES[favorite_subject]}\n\n"
               f"👉 **อาชีพอิสระที่แนะนำ:** **{fav_freelance['title']}**\n\n"
               f"📝 {fav_freelance['desc']}")

    st.markdown("---")

    # === 3. กราฟดีไซน์ใหม่ดูง่ายสบายตา ===
    st.subheader(f"📊 กราฟสรุปผลวิเคราะห์ทักษะ ({chart_type.split(' ')[0]})")

    df_chart = pd.DataFrame({
        "วิชา": [SUBJECT_NAMES[k] for k, v in active_scores.items()],
        "คะแนน": [v for k, v in active_scores.items()]
    })

    if "Bar" in chart_type:
        fig = px.bar(
            df_chart, 
            x='วิชา', 
            y='คะแนน', 
            color='คะแนน', 
            text='คะแนน', # แสดงตัวเลขยอดเสา
            color_continuous_scale='Blues', 
            template=chart_template
        )
        fig.update_traces(textposition='outside', textfont_size=14)
        fig.update_layout(
            yaxis=dict(range=[0, 115], title="ระดับคะแนน (0-100)"),
            xaxis=dict(title="วิชาที่มีคะแนน"),
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)

    elif "Radar" in chart_type:
        fig = go.Figure(data=go.Scatterpolar(
            r=df_chart["คะแนน"],
            theta=df_chart["วิชา"],
            fill='toself',
            fillcolor='rgba(30, 136, 229, 0.3)',
            line=dict(color=radar_color, width=3),
            marker=dict(size=8, color=radar_color)
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10)),
                angularaxis=dict(tickfont=dict(size=12, color=font_color))
            ),
            showlegend=False,
            template=chart_template,
            height=480
        )
        st.plotly_chart(fig, use_container_width=True)

    elif "Donut" in chart_type:
        fig = px.pie(
            df_chart, 
            values='คะแนน', 
            names='วิชา', 
            hole=0.45, 
            template=chart_template
        )
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=13)
        fig.update_layout(height=480, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.dataframe(df_chart, use_container_width=True, hide_index=True)

    st.markdown("---")

    # === 4. ระบบแนะนำสื่อการเรียนการสอน (Learning Resources) ===
    st.subheader("💡 ระบบแนะนำสื่อการเรียนรู้และพัฒนาทักษะ (Skill Enhancement)")
    
    # ดึงเฉพาะวิชาที่มีคะแนนกรอกไว้ แต่น้อยกว่า 50 คะแนน
    low_scores = [item for item in sorted_active if item[1] < 50]

    if low_scores:
        st.warning(f"🚨 **พบวิชาที่คุณได้คะแนนน้อยกว่า 50 คะแนน จำนวน {len(low_scores)} วิชาที่ควรเร่งพัฒนา:**")
        col_l1, col_l2 = st.columns(2)
        for i, (s_id, score) in enumerate(low_scores):
            res_info = LEARNING_RESOURCES_DB[s_id]
            target_col = col_l1 if i % 2 == 0 else col_l2
            with target_col.expander(f"📙 {SUBJECT_NAMES[s_id]} — ได้ {score} คะแนน", expanded=True):
                st.write(f"**ขอบเขตทักษะ:** {res_info['title']}")
                st.markdown("**สื่อคอร์สเรียนฟรีและช่องทางพัฒนา:**")
                for r in res_info["resources"]:
                    st.markdown(f"- 📖 {r}")
    else:
        # หากคะแนนสูงเกิน 50 ทุกวิชา
        lowest_id, lowest_score = sorted_active[-1]
        res_info = LEARNING_RESOURCES_DB[lowest_id]
        st.success(f"🎉 **ทักษะยอดเยี่ยมมาก! ไม่มีวิชาใดได้คะแนนต่ำกว่า 50 คะแนนเลย** (วิชาที่ได้น้อยสุดคือ {SUBJECT_NAMES[lowest_id]} ได้ {lowest_score} คะแนน)")
        
        with st.expander(f"📘 แนะนำคอร์สเรียนเสริมความเชี่ยวชาญสำหรับ: {SUBJECT_NAMES[lowest_id]}", expanded=False):
            st.write(f"**ขอบเขตทักษะ:** {res_info['title']}")
            st.markdown("**สื่อคอร์สเรียนแนะนำเพิ่มเติม:**")
            for r in res_info["resources"]:
                st.markdown(f"- 📖 {r}")
