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
# 2. ระบบปรับโทนสี ขาว-ดำ (Theme Toggle มุมขวาบน)
# ---------------------------------------------------------
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"

# สร้าง Layout สำหรับวางปุ่มสวิตช์มุมขวาบน
col_title, col_toggle = st.columns([5, 1])

with col_toggle:
    is_dark = st.toggle("🌙 โหมดมืด (Dark Theme)", value=(st.session_state.theme_mode == "Dark"))
    st.session_state.theme_mode = "Dark" if is_dark else "Light"

# ตกแต่ง CSS ให้รองรับโทนขาวดำแบบสมบูรณ์
if st.session_state.theme_mode == "Dark":
    st.markdown("""
        <style>
        /* พื้นหลังหลักและตัวหนังสือขาว */
        .stApp {
            background-color: #121212 !important;
            color: #FFFFFF !important;
        }
        /* แถบเมนูด้านข้าง */
        [data-testid="stSidebar"] {
            background-color: #1E1E1E !important;
        }
        /* บังคับตัวหนังสือทุกประเภทให้เป็นสีขาว */
        p, h1, h2, h3, h4, h5, h6, span, label, div, .stMarkdown {
            color: #FFFFFF !important;
        }
        /* ปรับแต่งกล่อง Expander และ Accordion */
        div[data-testid="stExpander"] {
            background-color: #1E1E1E !important;
            border: 1px solid #444444 !important;
            color: #FFFFFF !important;
        }
        /* ปรับกล่องข้อความแจ้งเตือน (Alerts & Info) */
        div[data-baseweb="notification"] {
            background-color: #262626 !important;
            border: 1px solid #444444 !important;
            color: #FFFFFF !important;
        }
        /* ปรับสีตัวหนังสือใน Tab */
        button[data-baseweb="tab"] p {
            color: #FFFFFF !important;
        }
        </style>
    """, unsafe_allow_html=True)
    chart_template = "plotly_dark"
    radar_color = "#64B5F6"
else:
    st.markdown("""
        <style>
        .stApp {
            background-color: #FFFFFF;
            color: #000000;
        }
        </style>
    """, unsafe_allow_html=True)
    chart_template = "plotly_white"
    radar_color = "#1E88E5"

# ---------------------------------------------------------
# 3. ฐานข้อมูลวิชาการเรียนการสอน (12 วิชา)
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
# 4. ฐานข้อมูลอาชีพครอบคลุมหลากหลายสายงาน
# ---------------------------------------------------------
CAREERS_DB = [
    # --- สายการแพทย์ สาธารณสุข และเภสัชกรรม ---
    {
        "title": "แพทย์ / หมอ (Medical Doctor)",
        "subjects": ["science", "math", "english"],
        "desc": "วินิจฉัยและรักษาโรค ใช้วิทยาศาสตร์ขั้นสูง คำนวณขนาดยา และศึกษาตำราต่างประเทศ"
    },
    {
        "title": "พยาบาลวิชาชีพ (Registered Nurse)",
        "subjects": ["science", "psychology", "english"],
        "desc": "ดูแลผู้ป่วย ประยุกต์ใช้วิทยาศาสตร์การแพทย์ จิตวิทยาการบริการ และภาษาในการสื่อสาร"
    },
    {
        "title": "เภสัชกร / คนจ่ายยา (Pharmacist)",
        "subjects": ["science", "math", "english"],
        "desc": "เชี่ยวชาญด้านยาและสารเคมี คำนวณปริมาณยา และอ่านเอกสารกำกับยาวิทยาศาสตร์"
    },
    {
        "title": "ทันตแพทย์ (Dentist)",
        "subjects": ["science", "art", "math"],
        "desc": "รักษาโรคฟันและช่องปาก อาศัยความแม่นยำทางวิทยาศาสตร์และประณีตศิลป์ในการทำหัตถการ"
    },
    
    # --- สายเทคโนโลยีและวิศวกรรม ---
    {
        "title": "วิศวกรซอฟต์แวร์ / นักพัฒนาแอป (Software Engineer)",
        "subjects": ["tech", "math", "english"],
        "desc": "ใช้ตรรกะคณิตศาสตร์ เขียนโค้ดคอมพิวเตอร์ และอ่านเอกสารเทคโนโลยีภาษาอังกฤษ"
    },
    {
        "title": "นักวิเคราะห์ข้อมูลและ AI (Data Scientist)",
        "subjects": ["math", "tech", "science"],
        "desc": "วิเคราะห์ข้อมูลขนาดใหญ่ด้วยคณิตศาสตร์ สถิติ วิทยาการคำนวณ และกระบวนการวิจัย"
    },
    {
        "title": "นักพัฒนาเกมและเอ็ฟเฟกต์ (Game Developer)",
        "subjects": ["tech", "art", "design_3d"],
        "desc": "เขียนโปรแกรมระบบเกม ออกแบบตัวละคร และสร้างแบบจำลอง 3 มิติ"
    },

    # --- สายออกแบบและสถาปัตยกรรม ---
    {
        "title": "นักออกแบบ UI/UX (UI/UX Designer)",
        "subjects": ["art", "tech", "psychology"],
        "desc": "ออกแบบความสวยงาม ผสานระบบเทคโนโลยี และเข้าใจจิตวิทยาผู้ใช้งาน"
    },
    {
        "title": "สถาปนิกและมัณฑนากร (Architect / Interior Designer)",
        "subjects": ["design_3d", "math", "art"],
        "desc": "คำนวณโครงสร้าง ผสานความสวยงามทางศิลปะและการเขียนแบบ 3D"
    },

    # --- สายธุรกิจ การเงิน และการตลาด ---
    {
        "title": "นักการเงินเชิงวิเคราะห์ (Financial Analyst)",
        "subjects": ["finance", "math", "marketing"],
        "desc": "ประเมินความเสี่ยง ตรวจสอบตัวเลขการเงิน คำนวณผลตอบแทน และวิเคราะห์ตลาด"
    },
    {
        "title": "นักการตลาดดิจิทัล (Digital Marketing Strategist)",
        "subjects": ["marketing", "social", "tech"],
        "desc": "วางแผนธุรกิจ เข้าใจสังคมพฤติกรรมผู้บริโภค และใช้เครื่องมือดิจิทัล"
    },
    {
        "title": "นักวิเคราะห์ธุรกิจระหว่างประเทศ (Global Business Analyst)",
        "subjects": ["lang3", "english", "marketing"],
        "desc": "ใช้ทักษะภาษาที่สาม ภาษาอังกฤษ และความรู้การตลาดเจรจาการค้า"
    },

    # --- สายสังคม กฎหมาย การบิน และบริการ ---
    {
        "title": "นักกฎหมายธุรกิจ (Corporate Lawyer)",
        "subjects": ["law", "english", "social"],
        "desc": "ใช้ข้อกฎหมายและระเบียบสังคม ร่างสัญญาภาษาอังกฤษ และเข้าใจบริบทธุรกิจ"
    },
    {
        "title": "นักจิตวิทยาคลินิก / ที่ปรึกษาองค์กร (Psychologist)",
        "subjects": ["psychology", "social", "english"],
        "desc": "ใช้หลักจิตวิทยา วิเคราะห์พฤติกรรมมนุษย์และสังคม พร้อมการสื่อสารสากล"
    },
    {
        "title": "นักบินพาณิชย์ (Commercial Pilot)",
        "subjects": ["science", "math", "english"],
        "desc": "คำนวณเส้นทางบินและเชื้อเพลิง เข้าใจระบบฟิสิกส์การบิน และสื่อสารภาษาอังกฤษสากล"
    },
    {
        "title": "พนักงานต้อนรับบนเครื่องบิน (Flight Attendant)",
        "subjects": ["english", "lang3", "psychology"],
        "desc": "สื่อสารหลายภาษา แก้ปัญหาเฉพาะหน้า และใช้จิตวิทยาดูแลผู้โดยสาร"
    },
    {
        "title": "ครู / อาจารย์ผู้สอน (Teacher / Educator)",
        "subjects": ["social", "psychology", "english"],
        "desc": "ถ่ายทอดความรู้ เข้าใจจิตวิทยาเด็กและการเรียนรู้ สื่อสารและถ่ายทอดข้อมูล"
    }
]

FREELANCE_CAREERS_DB = {
    "math": {"title": "Tutor สอนคณิตศาสตร์ / Freelance Data Analyst", "desc": "รับสอนพิเศษออนไลน์ หรือรับงานวิเคราะห์ข้อมูลตัวเลข"},
    "science": {"title": "นักเขียนบทความวิทยาศาสตร์ / ครีเอเตอร์สาย Sci-Tech", "desc": "สร้างคอนเทนต์วิทยาศาสตร์ พิสูจน์อักษร งานวิเคราะห์สุขภาพ"},
    "tech": {"title": "Freelance Web/App Developer", "desc": "รับเขียนโปรแกรม สร้างเว็บไซต์ หรือพัฒนาระบบอัตโนมัติ"},
    "english": {"title": "นักแปลเอกสารอิสระ / Content Writer ภาษาอังกฤษ", "desc": "รับงานแปลภาษา พิสูจน์อักษร หรือเขียนบทความ SEO"},
    "art": {"title": "Freelance Illustrator / Graphic Artist", "desc": "รับวาดภาพประกอบ ออกแบบตัวละคร โลโก้ และกราฟิกดีไซน์"},
    "social": {"title": "นักวิเคราะห์เทรนด์สังคม / พอดแคสเตอร์อิสระ", "desc": "สร้างคอนเทนต์ประวัติศาสตร์ สังคม การเมือง หรือข่าวสาร"},
    "finance": {"title": "ที่ปรึกษาการเงินส่วนบุคคลอิสระ / Trader", "desc": "วางแผนการเงิน บัญชี และการลงทุนอิสระให้ลูกค้า"},
    "marketing": {"title": "Freelance Social Media Manager", "desc": "รับบริหารเพจ วางแผนคอนเทนต์ และยิงโฆษณาออนไลน์"},
    "lang3": {"title": "ล่ามอิสระ / นักแปลภาษาเฉพาะทาง", "desc": "รับงานล่ามการประชุม ถ่ายทำ หรือแปลซับไตเติลภาพยนตร์"},
    "design_3d": {"title": "3D Modeler / Freelance Visualizer", "desc": "รับขึ้นโมเดล 3D ออกแบบภาพทัศนียภาพห้องและอาคาร"},
    "law": {"title": "ที่ปรึกษากฎหมายอิสระ (Legal Consultant)", "desc": "ให้คำปรึกษาด้านสัญญา กฎหมายธุรกิจ และทรัพย์สินทางปัญญา"},
    "psychology": {"title": "Life Coach / คอนซัลต์พัฒนาบุคลิกภาพ", "desc": "ให้คำปรึกษาการดำรงชีวิต การจัดการความเครียด และการสื่อสาร"}
}

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
    st.caption("ระบบวิเคราะห์จัดอันดับอาชีพ รองรับโหมดสีสว่าง/มืด และแยกตามโครงสร้างการจับคู่รายวิชา")

st.markdown("---")

all_zero = all(value == 0 for value in scores.values())

if all_zero:
    st.error("🚫 **ไม่พบอาชีพที่เหมาะสม**")
    st.warning("⚠️ กรุณาปรับคะแนนในแถบเมนูฝั่งซ้ายอย่างน้อย 1 วิชา เพื่อให้ระบบประมวลผลคำนวณหาอาชีพ")
    
    st.markdown("---")
    st.subheader("💡 คำแนะนำสื่อการเรียนรู้ปูพื้นฐาน (สำหรับวิชาที่มีคะแนน 0)")
    for code, name in SUBJECT_NAMES.items():
        res_info = LEARNING_RESOURCES_DB[code]
        with st.expander(f"📕 {name}", expanded=False):
            st.write(f"**ขอบเขตเนื้อหา:** {res_info['title']}")
            for r in res_info["resources"]:
                st.markdown(f"- 📖 {r}")

else:
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_3 = sorted_scores[:3]  # [(id1, score1), (id2, score2), (id3, score3)]
    
    s1_id, s1_score = top_3[0]
    s2_id, s2_score = top_3[1]
    s3_id, s3_score = top_3[2]

    # ฟังก์ชันช่วยแสดงผลการ์ดอาชีพ
    def render_career_card(career_item, max_score_possible, rank_label=""):
        c = career_item["details"]
        match_pct = round((career_item["score"] / max_score_possible) * 100, 1) if max_score_possible > 0 else 0
        
        if rank_label:
            st.markdown(f"#### {rank_label} {c['title']}")
        else:
            st.markdown(f"#### 🎯 **{c['title']}**")
            
        st.progress(min(match_pct / 100, 1.0))
        st.caption(f"📊 ระดับความเข้ากัน: **{match_pct}%** (คะแนนวิชาที่ใช้: {career_item['score']} / {max_score_possible})")
        st.write(f"**รายละเอียดอาชีพ:** {c['desc']}")
        
        used_sub_text = ", ".join([f"**{SUBJECT_NAMES[s]}** ({scores[s]} คะแนน)" for s in c["subjects"] if s in career_item["active_subjects"]])
        st.markdown(f"💡 **วิชาที่ดึงมาประมวลผล:** {used_sub_text}")
        st.markdown("---")

    # ฟังก์ชันค้นหาอาชีพที่ตรงกับกลุ่มวิชาที่กำหนด
    def get_careers_for_subjects(target_subject_ids):
        results = []
        max_possible = sum([scores[s] for s in target_subject_ids])
        for career in CAREERS_DB:
            c_subjs = career["subjects"]
            matches = [s for s in c_subjs if s in target_subject_ids]
            if len(matches) > 0:
                score_sum = sum([scores[s] for s in matches])
                results.append({
                    "details": career,
                    "matches_count": len(matches),
                    "score": score_sum,
                    "active_subjects": matches
                })
        results.sort(key=lambda x: (x["matches_count"], x["score"]), reverse=True)
        return results, max_possible

    st.subheader("📌 เลือกดูอันดับอาชีพตามการรวมกลุ่มวิชา")
    
    tab1, tab2, tab3 = st.tabs([
        "🧩 รวม 3 วิชาหลัก", 
        "⚖️ รวม 2 วิชาหลัก (จับคู่ 3 หมวดหมู่)", 
        "💡 รวม 1 วิชาเดี่ยว (3 หมวดตามอันดับคะแนน)"
    ])

    # --- TAB 1: 3 วิชาหลักรวมกัน ---
    with tab1:
        st.info(f"🎯 **วิชาหลัก 3 อันดับแรกของคุณ:** {SUBJECT_NAMES[s1_id]}, {SUBJECT_NAMES[s2_id]}, {SUBJECT_NAMES[s3_id]}")
        careers_3, max_3 = get_careers_for_subjects([s1_id, s2_id, s3_id])
        
        if careers_3:
            rank_badges = ["🥇 **อันดับ 1:**", "🥈 **อันดับ 2:**", "🥉 **อันดับ 3:**"]
            for i, item in enumerate(careers_3[:3]):
                render_career_card(item, max_3, rank_badges[i])
        else:
            st.warning("ไม่พบอาชีพที่ตรงกับเงื่อนไข")

    # --- TAB 2: รวม 2 วิชาแบบจับคู่เป็น 3 หมวดหมู่ย่อย ---
    with tab2:
        st.caption("จับคู่ 2 วิชาจาก 3 วิชาหลักของคุณ ออกเป็น 3 หมวดหมู่ย่อย:")
        
        pair1_ids = [s1_id, s2_id]
        pair2_ids = [s1_id, s3_id]
        pair3_ids = [s2_id, s3_id]

        subtab2_1, subtab2_2, subtab2_3 = st.tabs([
            f"1️⃣ คู่ที่ 1: {SUBJECT_NAMES[s1_id]} + {SUBJECT_NAMES[s2_id]}",
            f"2️⃣ คู่ที่ 2: {SUBJECT_NAMES[s1_id]} + {SUBJECT_NAMES[s3_id]}",
            f"3️⃣ คู่ที่ 3: {SUBJECT_NAMES[s2_id]} + {SUBJECT_NAMES[s3_id]}"
        ])

        with subtab2_1:
            c_list, max_p = get_careers_for_subjects(pair1_ids)
            for item in c_list[:3]:
                render_career_card(item, max_p)

        with subtab2_2:
            c_list, max_p = get_careers_for_subjects(pair2_ids)
            for item in c_list[:3]:
                render_career_card(item, max_p)

        with subtab2_3:
            c_list, max_p = get_careers_for_subjects(pair3_ids)
            for item in c_list[:3]:
                render_career_card(item, max_p)

    # --- TAB 3: วิชาเดี่ยว 3 หมวดตามอันดับ 1, 2, 3 ---
    with tab3:
        st.caption("จำแนกอาชีพตามวิชาเดี่ยว เรียงตามอันดับคะแนนของคุณ:")
        
        subtab3_1, subtab3_2, subtab3_3 = st.tabs([
            f"🥇 อันดับ 1: {SUBJECT_NAMES[s1_id]} ({s1_score} คะแนน)",
            f"🥈 อันดับ 2: {SUBJECT_NAMES[s2_id]} ({s2_score} คะแนน)",
            f"🥉 อันดับ 3: {SUBJECT_NAMES[s3_id]} ({s3_score} คะแนน)"
        ])

        with subtab3_1:
            c_list, max_p = get_careers_for_subjects([s1_id])
            for item in c_list[:3]:
                render_career_card(item, max_p)

        with subtab3_2:
            c_list, max_p = get_careers_for_subjects([s2_id])
            for item in c_list[:3]:
                render_career_card(item, max_p)

        with subtab3_3:
            c_list, max_p = get_careers_for_subjects([s3_id])
            for item in c_list[:3]:
                render_career_card(item, max_p)

    # --- ส่วนที่ 2: อาชีพอิสระ ---
    st.subheader("🚀 อาชีพอิสระ (Freelance) จากวิชาที่คุณชอบ")
    fav_freelance = FREELANCE_CAREERS_DB[favorite_subject]
    st.success(f"**วิชาที่คุณชอบ:** {SUBJECT_NAMES[favorite_subject]}\n\n"
               f"👉 **อาชีพอิสระที่แนะนำ:** **{fav_freelance['title']}**\n\n"
               f"📝 {fav_freelance['desc']}")

    st.markdown("---")

    # --- ส่วนที่ 3: แสดงผลกราฟ ---
    st.subheader(f"📊 ภาพรวมคะแนนวิชาทั้งหมด ({chart_type.split(' ')[1]})")

    df_chart = pd.DataFrame({
        "วิชา": [SUBJECT_NAMES[item[0]] for item in sorted_scores],
        "คะแนน": [item[1] for item in sorted_scores]
    })

    if "Radar" in chart_type:
        fig = go.Figure(data=go.Scatterpolar(
            r=df_chart["คะแนน"],
            theta=df_chart["วิชา"],
            fill='toself',
            line_color=radar_color
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            template=chart_template,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    elif "Donut" in chart_type:
        fig = px.pie(df_chart, values='คะแนน', names='วิชา', hole=0.4, template=chart_template)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    elif "Bar" in chart_type:
        fig = px.bar(df_chart, x='วิชา', y='คะแนน', color='คะแนน', color_continuous_scale='Blues', template=chart_template)
        fig.update_layout(yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.dataframe(df_chart, use_container_width=True, hide_index=True)

    st.markdown("---")

    # --- ส่วนที่ 4: สื่อการเรียนรู้ ---
    st.subheader("💡 คำแนะนำสื่อการเรียนรู้เพื่อพัฒนาตนเอง")
    low_score_subjects = [item for item in sorted_scores if item[1] < 30]

    if low_score_subjects:
        st.error(f"🚨 **พบทั้งหมด {len(low_score_subjects)} วิชาที่มีคะแนนต่ำกว่า 30 คะแนน:**")
        for s_id, score in low_score_subjects:
            res_info = LEARNING_RESOURCES_DB[s_id]
            with st.expander(f"📕 {SUBJECT_NAMES[s_id]} — ได้ {score} คะแนน", expanded=True):
                st.write(f"**ขอบเขตเนื้อหา:** {res_info['title']}")
                st.markdown("**สื่อและแหล่งเรียนรู้ที่แนะนำ:**")
                for r in res_info["resources"]:
                    st.markdown(f"- 📖 {r}")
    else:
        lowest_id, lowest_score = sorted_scores[-1]
        res_info = LEARNING_RESOURCES_DB[lowest_id]
        st.info(f"🎉 **ไม่มีวิชาใดได้คะแนนต่ำกว่า 30 คะแนน!** แนะนำสื่อการเรียนรู้สำหรับวิชาที่ได้คะแนนน้อยที่สุดแทน:")
        with st.expander(f"📙 {SUBJECT_NAMES[lowest_id]} — ได้ {lowest_score} คะแนน", expanded=True):
            st.write(f"**ขอบเขตเนื้อหา:** {res_info['title']}")
            st.markdown("**สื่อและแหล่งเรียนรู้ที่แนะนำ:**")
            for r in res_info["resources"]:
                st.markdown(f"- 📖 {r}")
