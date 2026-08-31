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
# 4. ฐานข้อมูลอาชีพ (เพิ่ม ทนาย, วิศวกรก่อสร้าง, วิศวกรออกแบบ)
# ---------------------------------------------------------
CAREERS_DB = [
    {
        "title": "ทนายความ / นิติกร / อัยการ (Lawyer / Legal Officer)",
        "primary": ["law", "psychology", "social"],
        "secondary": ["english", "finance", "design_3d"], 
        "desc": "ว่าความ คุ้มครองสิทธิทางกฎหมาย ให้คำปรึกษาข้อสัญญา และเข้าใจจิตวิทยามนุษย์ในการเจรจาพิจารณาคดี"
    },
    {
        "title": "วิศวกรโยธา / วิศวกรควบคุมงานก่อสร้าง (Civil / Construction Engineer)",
        "primary": ["math", "science", "design_3d"],
        "secondary": ["law", "finance", "tech"], 
        "desc": "คำนวณโครงสร้าง คำนวณความปลอดภัย ตรวจแบบ 3 มิติ คุมงานก่อสร้างอาคารและโครงสร้างพื้นฐาน"
    },
    {
        "title": "วิศวกรออกแบบและพัฒนาผลิตภัณฑ์ (Product Design Engineer)",
        "primary": ["design_3d", "tech", "math"],
        "secondary": ["art", "science", "psychology"], 
        "desc": "ออกแบบชิ้นส่วน เครื่องกล หรือผลิตภัณฑ์ 3 มิติ จำลองการรับแรง และพัฒนาฟังก์ชันให้เหมาะกับผู้ใช้งาน"
    },
    {
        "title": "สถาปนิก / นักออกแบบภายใน (Architect / Interior Designer)",
        "primary": ["design_3d", "art", "math"],
        "secondary": ["law", "science", "finance"], 
        "desc": "เขียนแบบบ้าน ออกแบบอาคาร ตกแต่งห้อง 3 มิติ พร้อมคำนวณพื้นที่และตรวจสอบกฎหมายผังเมือง/ควบคุมอาคาร"
    },
    {
        "title": "เจ้าของธุรกิจส่วนตัว / แม่ค้าพ่อค้าออนไลน์ (Online Business Owner)",
        "primary": ["marketing", "finance", "psychology"],
        "secondary": ["tech", "law", "design_3d"], 
        "desc": "บริหารร้านค้า จัดการสต็อกสินค้า วางแผนต้นทุนกำไร สื่อสารมัดใจลูกค้า และทำสื่อโปรโมตสินค้า"
    },
    {
        "title": "ครู / อาจารย์สอนคณิตศาสตร์ (Mathematics Teacher)",
        "primary": ["math", "psychology", "social"],
        "secondary": ["tech", "english"], 
        "desc": "ถ่ายทอดความรู้คณิตศาสตร์ วางแผนการสอน เข้าใจจิตวิทยาเด็กและพัฒนาการเรียนรู้"
    },
    {
        "title": "นักวิเคราะห์ตัวเลขและสถิติ (Data Analyst)",
        "primary": ["math", "tech", "finance"],
        "secondary": ["english", "marketing", "psychology"], 
        "desc": "นำตัวเลขและสถิติมาคำนวณ วิเคราะห์แนวโน้มธุรกิจและการเงินเพื่อช่วยการตัดสินใจ"
    },
    {
        "title": "โปรแกรมเมอร์ / นักพัฒนาแอปพลิเคชัน (Programmer / Developer)",
        "primary": ["tech", "math", "english"],
        "secondary": ["art", "design_3d", "psychology"], 
        "desc": "เขียนโค้ดสร้างเว็บไซต์และแอปพลิเคชัน แก้ปัญหาด้วยตรรกะ และอ่านคู่มือภาษาอังกฤษ"
    },
    {
        "title": "ครีเอเตอร์ / นักการตลาดออนไลน์ (Content Creator & Digital Marketer)",
        "primary": ["marketing", "art", "tech"],
        "secondary": ["english", "psychology", "design_3d"], 
        "desc": "คิดคอนเทนต์ ตัดต่อวิดีโอ โปรโมตสินค้าผ่านโซเชียลมีเดีย ยิงโฆษณาหาลูกค้า"
    },
    {
        "title": "นักการตลาดระหว่างประเทศ (International Marketer)",
        "primary": ["marketing", "english", "finance"],
        "secondary": ["lang3", "psychology", "social"], 
        "desc": "วางแผนกลยุทธ์การตลาดต่างประเทศ สื่อสารเจรจาขยายฐานลูกค้าทั่วโลก"
    },
    {
        "title": "นักบัญชี / เจ้าหน้าที่การเงิน (Accountant / Finance Officer)",
        "primary": ["finance", "math", "law"],
        "secondary": ["tech", "english", "marketing"], 
        "desc": "ทำรับ-จ่าย บันทึกบัญชี ตรวจสอบตัวเลขรายรับรายจ่าย ดูแลเรื่องภาษีถูกต้องตามกฎหมาย"
    },
    {
        "title": "แพทย์ / พยาบาล / เภสัชกร (Doctor / Nurse / Pharmacist)",
        "primary": ["science", "psychology", "english"],
        "secondary": ["tech", "math"], 
        "desc": "ใช้วิทยาศาสตร์ชีวภาพในการตรวจรักษาโรค จ่ายยา และสื่อสารดูแลจิตวิทยาผู้ป่วย"
    },
    {
        "title": "นักจิตวิทยา / เจ้าหน้าที่ฝ่ายบุคคล (Psychologist / HR Officer)",
        "primary": ["psychology", "social", "english"],
        "secondary": ["law", "marketing", "tech"], 
        "desc": "ให้คำปรึกษาปัญหาชีวิต ดูแลสุขภาพจิต สัมภาษณ์คัดเลือกคนเข้าทำงานและบริหารคน"
    },
    {
        "title": "กราฟิกดีไซเนอร์ / ช่างภาพ (Graphic Designer / Photographer)",
        "primary": ["art", "design_3d", "marketing"],
        "secondary": ["tech", "english", "psychology"], 
        "desc": "วาดภาพ วาดการ์ตูน ออกแบบโลโก้ แบนเนอร์ ปรับแต่งรูปภาพและวิดีโอเพื่อการประชาสัมพันธ์"
    },
    {
        "title": "ล่าม / นักแปล / ไกด์นำเที่ยว (Interpreter / Translator / Tour Guide)",
        "primary": ["lang3", "english", "social"],
        "secondary": ["psychology", "marketing", "art"], 
        "desc": "แปลภาษา เจรจาติดต่อสื่อสารกับชาวต่างชาติ แนะนำสถานที่ท่องเที่ยวและวัฒนธรรม"
    }
]

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
    "design_3d": {"title": "3D Modeler / Freelance Interior Visualizer / Draftsman", "desc": "รับขึ้นโมเดล 3D ออกแบบภาพทัศนียภาพห้องและโครงสร้างอาคาร"},
    "law": {"title": "ที่ปรึกษากฎหมายอิสระ (Legal Consultant)", "desc": "ให้คำปรึกษาด้านสัญญา กฎหมายธุรกิจ และทรัพย์สินทางปัญญา"},
    "psychology": {"title": "Life Coach / คอนซัลต์พัฒนาบุคลิกภาพ", "desc": "ให้คำปรึกษาการดำรงชีวิต การจัดการความเครียด และการสื่อสารในองค์กร"}
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
    st.caption("ระบบวิเคราะห์อาชีพหลัก อาชีพอิสระ จัดอันดับทักษะ พร้อมสื่อพัฒนาการเรียนรู้")

st.markdown("---")

all_zero = all(v == 0 for v in scores.values())

if all_zero:
    st.error("🚫 **ไม่พบอาชีพที่เหมาะสม (คะแนนเป็น 0 ทุกวิชา)**")
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
    # ---------------------------------------------------------
    # ฟังก์ชันคำนวณ: วิชาหลักคิด 85% + วิชาสนับสนุนคิด 15%
    # ---------------------------------------------------------
    def get_ranked_careers_by_subjects(target_subject_ids, require_all_matched=False):
        results = []
        for career in CAREERS_DB:
            p_subs = career["primary"]
            s_subs = career["secondary"]
            
            p_match = [s for s in p_subs if s in target_subject_ids]
            
            if not p_match:
                continue
                
            if require_all_matched:
                matched_in_primary = [s for s in target_subject_ids if s in p_subs]
                if len(matched_in_primary) < len(target_subject_ids):
                    continue

            p_score_sum = sum([scores[s] for s in p_match])
            p_avg = p_score_sum / len(p_match)
            base_fit = p_avg * 0.85
            
            s_match = [s for s in s_subs if scores[s] > 0]
            bonus_fit = 0
            if s_match:
                s_avg = sum([scores[s] for s in s_match]) / len(s_match)
                bonus_fit = (s_avg / 100.0) * 15.0
            
            final_score = round(min(base_fit + bonus_fit, 100.0), 1)
            
            if final_score > 0:
                results.append({
                    "details": career,
                    "fit_score": final_score
                })
        
        results.sort(key=lambda x: x["fit_score"], reverse=True)
        return results

    # ---------------------------------------------------------
    # ฟังก์ชันแสดง Card
    # ---------------------------------------------------------
    def render_career_card(item, rank_badge=""):
        c = item["details"]
        fit = item["fit_score"]
        
        if rank_badge:
            st.markdown(f"#### {rank_badge} **{c['title']}**")
        else:
            st.markdown(f"#### 🎯 **{c['title']}**")
            
        st.write(f"**รายละเอียดอาชีพ:** {c['desc']}")
        
        user_p_subs = [s for s in c["primary"] if scores[s] > 0]
        if user_p_subs:
            p_text = ", ".join([f"**{SUBJECT_NAMES[s]}** ({scores[s]} คะแนน)" for s in user_p_subs])
            st.markdown(f"💡 **วิชาหลักที่ใช้ประมวลผล:** {p_text}")
        else:
            p_text = ", ".join([f"**{SUBJECT_NAMES[s]}** ({scores[s]} คะแนน)" for s in c["primary"]])
            st.markdown(f"💡 **วิชาหลักที่ใช้ประมวลผล:** {p_text}")
        
        s_text = ", ".join([f"{SUBJECT_NAMES[s]} ({scores[s]} คะแนน)" for s in c["secondary"]])
        st.markdown(f"✨ **วิชาสนับสนุน (ทักษะเสริมที่ช่วยให้ทำอาชีพนี้ได้ดีขึ้น):** {s_text}")
        
        st.progress(min(fit / 100.0, 1.0))
        st.caption(f"📊 **ระดับความเข้ากันของทักษะวิชา: {fit}%**")
        st.markdown("---")

    active_sorted = sorted([(k, v) for k, v in scores.items() if v > 0], key=lambda x: x[1], reverse=True)
    num_active = len(active_sorted)

    st.subheader("🎯 อาชีพที่เหมาะสมที่สุดจากการประมวลผลทักษะวิชา")

    if num_active == 1:
        s1_id, s1_score = active_sorted[0]
        st.info(f"💡 **คุณกรอกคะแนน 1 วิชา:** {SUBJECT_NAMES[s1_id]} ({s1_score} คะแนน)")
        
        c_list = get_ranked_careers_by_subjects([s1_id])
        for i, item in enumerate(c_list[:3]):
            badges = ["🥇 อันดับ 1:", "🥈 อันดับ 2:", "🥉 อันดับ 3:"]
            render_career_card(item, badges[i])

    elif num_active == 2:
        s1_id, s1_score = active_sorted[0]
        s2_id, s2_score = active_sorted[1]
        
        st.info(f"💡 **คุณกรอกคะแนน 2 วิชา:** {SUBJECT_NAMES[s1_id]} ({s1_score} คะแนน) และ {SUBJECT_NAMES[s2_id]} ({s2_score} คะแนน)")
        
        tab_both, tab_s1, tab_s2 = st.tabs([
            f"🔗 อาชีพที่ใช้วิชาหลักคู่กัน ({SUBJECT_NAMES[s1_id].split(' ')[0]} + {SUBJECT_NAMES[s2_id].split(' ')[0]})",
            f"🥇 อาชีพเด่นจาก: {SUBJECT_NAMES[s1_id]}",
            f"🥈 อาชีพเด่นจาก: {SUBJECT_NAMES[s2_id]}"
        ])

        with tab_both:
            both_careers = get_ranked_careers_by_subjects([s1_id, s2_id], require_all_matched=True)
            if both_careers:
                st.success(f"✨ **พบ {len(both_careers)} อาชีพที่ดึง 2 วิชานี้มาใช้เป็นวิชาหลักคู่กัน:**")
                for i, item in enumerate(both_careers[:3]):
                    badges = ["🥇 อันดับ 1 (ตรงคู่ที่สุด):", "🥈 อันดับ 2:", "🥉 อันดับ 3:"]
                    render_career_card(item, badges[i])
            else:
                st.warning(f"⚠️ **ไม่พบอาชีพที่ดึง 2 วิชานี้มาเป็นวิชาหลักร่วมกันโดยตรง** ขอแนะนำอาชีพที่ใช้วิชาหนึ่งเป็นหลัก และอีกวิชาหนึ่งช่วยสนับสนุน:")
                c_list = get_ranked_careers_by_subjects([s1_id, s2_id], require_all_matched=False)
                for i, item in enumerate(c_list[:3]):
                    badges = ["🥇 อันดับ 1:", "🥈 อันดับ 2:", "🥉 อันดับ 3:"]
                    render_career_card(item, badges[i])

        with tab_s1:
            s1_careers = get_ranked_careers_by_subjects([s1_id])
            for i, item in enumerate(s1_careers[:3]):
                badges = ["🥇 อันดับ 1:", "🥈 อันดับ 2:", "🥉 อันดับ 3:"]
                render_career_card(item, badges[i])

        with tab_s2:
            s2_careers = get_ranked_careers_by_subjects([s2_id])
            for i, item in enumerate(s2_careers[:3]):
                badges = ["🥇 อันดับ 1:", "🥈 อันดับ 2:", "🥉 อันดับ 3:"]
                render_career_card(item, badges[i])

    else:
        top_3 = active_sorted[:3]
        s1_id, s1_score = top_3[0]
        s2_id, s2_score = top_3[1]
        s3_id, s3_score = top_3[2]

        tab1, tab2, tab3 = st.tabs([
            "🧩 ผลลัพธ์ภาพรวม (3 วิชาหลัก)", 
            "⚖️ การจับคู่ย่อย (2 วิชา)", 
            "💡 แยกตามวิชาเดี่ยว (1 วิชา)"
        ])

        with tab1:
            st.info(f"🎯 **กลุ่ม 3 วิชาเด่นของคุณ:** {SUBJECT_NAMES[s1_id]} ({s1_score} คะแนน), {SUBJECT_NAMES[s2_id]} ({s2_score} คะแนน), {SUBJECT_NAMES[s3_id]} ({s3_score} คะแนน)")
            c_list = get_ranked_careers_by_subjects([s1_id, s2_id, s3_id])
            for i, item in enumerate(c_list[:3]):
                badges = ["🥇 อันดับ 1 (เหมาะสมที่สุด):", "🥈 อันดับ 2:", "🥉 อันดับ 3:"]
                render_career_card(item, badges[i])

        with tab2:
            subtab2_1, subtab2_2, subtab2_3 = st.tabs([
                f"1️⃣ {SUBJECT_NAMES[s1_id]} + {SUBJECT_NAMES[s2_id]}",
                f"2️⃣ {SUBJECT_NAMES[s1_id]} + {SUBJECT_NAMES[s3_id]}",
                f"3️⃣ {SUBJECT_NAMES[s2_id]} + {SUBJECT_NAMES[s3_id]}"
            ])
            
            def render_pair(subA, subB):
                pair_list = get_ranked_careers_by_subjects([subA, subB])
                for i, item in enumerate(pair_list[:3]):
                    badges = ["🥇 อันดับ 1:", "🥈 อันดับ 2:", "🥉 อันดับ 3:"]
                    render_career_card(item, badges[i])

            with subtab2_1:
                render_pair(s1_id, s2_id)
            with subtab2_2:
                render_pair(s1_id, s3_id)
            with subtab2_3:
                render_pair(s2_id, s3_id)

        with tab3:
            subtab3_1, subtab3_2, subtab3_3 = st.tabs([
                f"🥇 {SUBJECT_NAMES[s1_id]} ({s1_score} คะแนน)",
                f"🥈 {SUBJECT_NAMES[s2_id]} ({s2_score} คะแนน)",
                f"🥉 {SUBJECT_NAMES[s3_id]} ({s3_score} คะแนน)"
            ])
            
            def render_single(sub_id):
                single_list = get_ranked_careers_by_subjects([sub_id])
                for i, item in enumerate(single_list[:3]):
                    badges = ["🥇 อันดับ 1:", "🥈 อันดับ 2:", "🥉 อันดับ 3:"]
                    render_career_card(item, badges[i])

            with subtab3_1:
                render_single(s1_id)
            with subtab3_2:
                render_single(s2_id)
            with subtab3_3:
                render_single(s3_id)

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
        "วิชา": [SUBJECT_NAMES[k] for k in SUBJECT_NAMES.keys()],
        "คะแนน": [scores[k] for k in SUBJECT_NAMES.keys()]
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

    low_score_subjects = [(k, v) for k, v in scores.items() if v < 30]

    if len(low_score_subjects) > 0:
        st.error(f"🚨 **พบทั้งหมด {len(low_score_subjects)} วิชาที่มีคะแนนต่ำกว่า 30 คะแนน (วิชาที่ควรเร่งพัฒนา):**")
        for s_id, score in low_score_subjects:
            res_info = LEARNING_RESOURCES_DB[s_id]
            with st.expander(f"📕 {SUBJECT_NAMES[s_id]} — ได้ {score} คะแนน", expanded=False):
                st.write(f"**ขอบเขตเนื้อหา:** {res_info['title']}")
                st.markdown("**สื่อและแหล่งเรียนรู้ที่แนะนำ:**")
                for r in res_info["resources"]:
                    st.markdown(f"- 📖 {r}")
    else:
        sorted_scores_asc = sorted(scores.items(), key=lambda x: x[1])
        lowest_id, lowest_score = sorted_scores_asc[0]
        res_info = LEARNING_RESOURCES_DB[lowest_id]
        st.info(f"🎉 **ไม่มีวิชาใดได้คะแนนต่ำกว่า 30 คะแนน!** แนะนำสื่อการเรียนรู้สำหรับวิชาที่ได้คะแนนน้อยที่สุดของคุณแทน:")
        with st.expander(f"📙 {SUBJECT_NAMES[lowest_id]} — ได้ {lowest_score} คะแนน", expanded=True):
            st.write(f"**ขอบเขตเนื้อหา:** {res_info['title']}")
            st.markdown("**สื่อและแหล่งเรียนรู้ที่แนะนำ:**")
            for r in res_info["resources"]:
                st.markdown(f"- 📖 {r}")
