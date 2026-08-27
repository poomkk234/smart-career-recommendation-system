import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. ตั้งค่าหน้าตาเว็บไซต์ (Page Configuration)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Smart Career Recommendation System (Everyday Careers Edition)",
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
# CSS: ปรับเปลี่ยน UI แถบซ้าย (Sidebar) และ Tab เป็นสีดำ ตัวหนังสือขาวทั้งหมด
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* ----------------------------------------------------- */
    /* 🎯 1. ปรับแถบกรอกคะแนนรายวิชา (SIDEBAR) เป็นสีดำ ตัวหนังสือขาว */
    /* ----------------------------------------------------- */
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

    /* ----------------------------------------------------- */
    /* 🎯 2. ปรับแต่ง TAB ทุกอันให้เป็น สีดำ + ตัวหนังสือสีขาว  */
    /* ----------------------------------------------------- */
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

    div[data-testid="stToggle"] label p {
        color: inherit !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

if st.session_state.theme_mode == "Dark":
    st.markdown("""
        <style>
        .stApp {
            background-color: #121212 !important;
            color: #FFFFFF !important;
        }
        .stMain p, .stMain h1, .stMain h2, .stMain h3, .stMain h4, .stMain h5, .stMain h6, .stMain span, .stMain div, .stMain .stMarkdown {
            color: #FFFFFF !important;
        }
        div[data-testid="stExpander"] {
            background-color: #1E1E1E !important;
            border: 1px solid #444444 !important;
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
# 4. ฐานข้อมูลอาชีพในชีวิตประจำวันและอาชีพทั่วไป (Comprehensive Real-World DB)
# ---------------------------------------------------------
CAREERS_DB = [
    # === กลุ่มอาชีพในชีวิตประจำวัน & ครีเอเตอร์ดิจิทัล (Everyday & Digital Careers) ===
    {
        "title": "ผู้สร้างคอนเทนต์ / ยูทูปเบอร์ (Content Creator / YouTuber / TikToker)",
        "subjects": ["art", "marketing", "tech"],
        "desc": "คิดคอนเทนต์ ตัดต่อวิดีโอ (Art/Tech) วางกลยุทธ์สร้างยอดวิวและเข้าถึงผู้ติดตาม (Marketing)"
    },
    {
        "title": "พ่อค้าแม่ค้าออนไลน์ / เจ้าของร้านค้า E-commerce",
        "subjects": ["marketing", "finance", "tech"],
        "desc": "ยิงโฆษณาออนไลน์ (Marketing) บริหารต้นทุนและกำไร (Finance) ใช้แพลตฟอร์มสำเร็จรูปขายสินค้า (Tech)"
    },
    {
        "title": "เจ้าของร้านกาแฟ / บาริสต้า (Barista & Coffee Shop Owner)",
        "subjects": ["marketing", "finance", "art"],
        "desc": "ออกแบบตกแต่งร้านและเครื่องดื่ม (Art) คำนวณรายรับ-รายจ่าย (Finance) และทำการตลาดเรียกลูกค้า (Marketing)"
    },
    {
        "title": "เชฟ / พ่อครัว / แม่ครัว (Chef & Culinary Specialist)",
        "subjects": ["science", "art", "marketing"],
        "desc": "เข้าใจปฏิกิริยาเคมีของอาหารและความร้อน (Science) ตกแต่งจานอาหารให้สวยงาม (Art) และสร้างแบรนด์ร้านอาหาร (Marketing)"
    },

    # === กลุ่มงานออฟฟิศ องค์กร & การบริหาร (Office & Business Operations) ===
    {
        "title": "นักบัญชี / พนักงานบัญชีบริษัท (Corporate Accountant)",
        "subjects": ["finance", "math", "law"],
        "desc": "บันทึกบัญชี ตรวจสอบงบการเงิน (Finance/Math) และยื่นภาษีตามข้อกำหนดของกฎหมาย (Law)"
    },
    {
        "title": "เจ้าหน้าที่ฝ่ายทรัพยากรบุคคล (HR / Human Resources)",
        "subjects": ["psychology", "social", "law"],
        "desc": "คัดเลือกและดูแลพนักงาน (Psychology) สร้างวัฒนธรรมองค์กร (Social) และดูแลกฎหมายแรงงาน (Law)"
    },
    {
        "title": "พนักงานฝ่ายขาย / เซลส์ (Sales Executive)",
        "subjects": ["marketing", "psychology", "english"],
        "desc": "นำเสนอสินค้า จูงใจผู้ซื้อ (Marketing) เข้าใจความต้องการของลูกค้า (Psychology) และสื่อสารขายงานต่างชาติ (English)"
    },
    {
        "title": "เจ้าหน้าที่ฝ่ายการตลาด (Marketing Executive)",
        "subjects": ["marketing", "social", "art"],
        "desc": "วิเคราะห์พฤติกรรมผู้บริโภคในสังคม (Social) คิดแคมเปญโฆษณา (Marketing) และบรีฟงานออกแบบกราฟิก (Art)"
    },

    # === กลุ่มข้าราชการ สังคม & กฎหมาย (Government, Law & Public Sector) ===
    {
        "title": "ข้าราชการพลเรือน / เจ้าหน้าที่รัฐ (Civil Servant)",
        "subjects": ["social", "law", "psychology"],
        "desc": "ปฏิบัติตามระเบียบและข้อกฎหมาย (Law) บริการประชาชน (Social) และประสานงานองค์กร (Psychology)"
    },
    {
        "title": "ทหาร / ตำรวจ (Military / Police Officer)",
        "subjects": ["social", "law", "science"],
        "desc": "บังคับใช้กฎหมายรักษาความสงบ (Law) เข้าใจโครงสร้างสังคม (Social) และใช้วิทยาศาสตร์พิสูจน์หลักฐาน/ยุทธวิธี (Science)"
    },
    {
        "title": "นักข่าว / ผู้ประกาศข่าว (Journalist / News Reporter)",
        "subjects": ["social", "english", "law"],
        "desc": "ติดตามสถานการณ์บ้านเมือง (Social) รายงานข่าวภาษาไทยและสากล (English) และยึดหลักจริยธรรมกฎหมายสื่อ (Law)"
    },
    {
        "title": "ทนายความ / ที่ปรึกษากฎหมาย (Lawyer / Attorney)",
        "subjects": ["law", "social", "english"],
        "desc": "ว่าความ ตีความกฎหมาย (Law) ช่วยเหลือสังคม (Social) และจัดการสัญญาระหว่างประเทศ (English)"
    },

    # === กลุ่มอสังหาริมทรัพย์ สถาปัตยกรรม & งานช่าง (Real Estate, Arch & Craft) ===
    {
        "title": "นักพัฒนาอสังหาริมทรัพย์ (Real Estate Developer)",
        "subjects": ["design_3d", "finance", "law"],
        "desc": "วางโครงสร้างอาคารและแบบ 3D (Design 3D) คำนวณการลงทุนและงบประมาณ (Finance) และจัดการกฎหมายที่ดิน (Law)"
    },
    {
        "title": "มัณฑนากร / นักออกแบบภายใน (Interior Designer)",
        "subjects": ["design_3d", "art", "math"],
        "desc": "ออกแบบตกแต่งภายใน (Art/3D) คำนวณระยะ สัดส่วน และพื้นที่ใช้งานให้คุ้มค่า (Math)"
    },
    {
        "title": "วิศวกรบริการ / ช่างไฟฟ้าและระบบ (Systems & Service Engineer)",
        "subjects": ["science", "tech", "math"],
        "desc": "ตรวจเช็กระบบไฟฟ้า วางระบบเทคโนโลยี (Science/Tech) และคำนวณกำลังไฟกับความปลอดภัย (Math)"
    },

    # === กลุ่มการแพทย์ สุขภาพ & บริการ (Healthcare & Service Industry) ===
    {
        "title": "แพทย์ / หมอรักษาโรค (Medical Doctor)",
        "subjects": ["science", "math", "english"],
        "desc": "วินิจฉัยโรค ประยุกต์ใช้วิทยาศาสตร์ คำนวณขนาดยา และอ่านตำราต่างประเทศ"
    },
    {
        "title": "พยาบาลวิชาชีพ (Registered Nurse)",
        "subjects": ["science", "psychology", "english"],
        "desc": "ดูแลผู้ป่วย ใช้ความรู้วิทยาศาสตร์ สื่อสารสร้างความอุ่นใจ (Psychology) และดูแลผู้ป่วยต่างชาติ (English)"
    },
    {
        "title": "เภสัชกรหน้าร้าน / เภสัชกรโรงพยาบาล (Pharmacist)",
        "subjects": ["science", "math", "english"],
        "desc": "จ่ายยา ให้คำแนะนำการใช้ยาอย่างปลอดภัย คำนวณสัดส่วนตามน้ำหนักตัวผู้ป่วย"
    },
    {
        "title": "พนักงานต้อนรับโรงแรม / ต้อนรับลูกค้า (Hotel Receptionist / Concierge)",
        "subjects": ["english", "lang3", "psychology"],
        "desc": "สื่อสารภาษาอังกฤษและภาษาที่สาม บริการด้วยจิตวิทยาและการแก้ปัญหาเฉพาะหน้าให้ลูกค้า"
    },
    {
        "title": "พนักงานต้อนรับบนเครื่องบิน (Flight Attendant / ลูกเรือ)",
        "subjects": ["english", "lang3", "psychology"],
        "desc": "สื่อสารหลายภาษา ดูแลความปลอดภัยผู้โดยสารด้วยจิตวิทยาและการบริการสากล"
    },

    # === กลุ่มเทคโนโลยี ซอฟต์แวร์ & AI (IT & Tech Industry) ===
    {
        "title": "วิศวกรซอฟต์แวร์ / นักเขียนโปรแกรม (Software Developer)",
        "subjects": ["tech", "math", "english"],
        "desc": "เขียนโปรแกรมคอมพิวเตอร์ ใช้ตรรกะคณิตศาสตร์แก้ปัญหา และอ่านคู่มือภาษาอังกฤษ"
    },
    {
        "title": "นักวิเคราะห์ข้อมูล (Data Analyst)",
        "subjects": ["math", "tech", "finance"],
        "desc": "วิเคราะห์ข้อมูลยอดขายและสถิติธุรกิจด้วยคอมพิวเตอร์และคณิตศาสตร์"
    },
    {
        "title": "นักออกแบบหน้าเว็บและแอปพลิเคชัน (UI/UX Designer)",
        "subjects": ["art", "tech", "psychology"],
        "desc": "ออกแบบปุ่ม หน้าตาเว็บ (Art) ผสานระบบเทคโนโลยี (Tech) และศึกษาพฤติกรรมผู้ใช้ (Psychology)"
    }
]

FREELANCE_CAREERS_DB = {
    "math": {"title": "Tutor สอนพิเศษคณิตศาสตร์ / รับติวเตอร์ออนไลน์", "desc": "รับสอนพิเศษวิชาคณิตศาสตร์ สถิติ หรือรับทำแบบวิเคราะห์ข้อมูลตัวเลข"},
    "science": {"title": "นักเขียนบทความสุขภาพและวิทยาศาสตร์", "desc": "รับเขียนบทความความรู้ สุขภาพ อาหาร และวิทยาศาสตร์ลงเว็บไซต์/เพจ"},
    "tech": {"title": "Freelance รับทำเว็บไซต์ / ซ่อมคอมพิวเตอร์และระบบ", "desc": "รับสร้างเว็บไซต์ร้านค้า ปรับแต่งระบบคอมพิวเตอร์ หรือดูแลระบบไอที"},
    "english": {"title": "นักแปลเอกสารอิสระ / รับเขียนคอนเทนต์ภาษาอังกฤษ", "desc": "รับแปลเอกสาร แปลซับไตเติล หรือเขียนอีเมลธุรกิจภาษาอังกฤษ"},
    "art": {"title": "Freelance Illustrator / ช่างภาพอิสระ", "desc": "รับวาดภาพ วาดสติกเกอร์ไลน์ ออกแบบโลโก้ หรือรับถ่ายภาพงานต่างๆ"},
    "social": {"title": "นักสร้างคอนเทนต์ประวัติศาสตร์/เล่าเรื่อง", "desc": "ทำคลิปเล่าเรื่องประวัติศาสตร์ สังคม หรือเรื่องน่ารู้รอบโลก"},
    "finance": {"title": "รับทำบัญชีร้านค้าออนไลน์ / ที่ปรึกษาภาษีส่วนบุคคล", "desc": "ช่วยร้านค้าเล็กๆ วางแผนภาษี ยื่นภาษี และสรุปบัญชีรายรับรายจ่าย"},
    "marketing": {"title": "Freelance รับดูแลเพจ / ยิงโฆษณาออนไลน์", "desc": "รับเขียนโพสต์ขายของ ยิงแอด Facebook/TikTok ให้กับร้านค้าต่างๆ"},
    "lang3": {"title": "ล่ามอิสระ / ไกด์นำเที่ยวต่างชาติ", "desc": "รับงานแปลภาษาเฉพาะกิจ ล่ามติดตาม หรือนำเที่ยวชาวต่างชาติ"},
    "design_3d": {"title": "Freelance ขึ้นโมเดล 3D / เขียนแบบบ้าน", "desc": "รับเขียนแบบบ้าน 3D ให้ลูกค้าเห็นภาพก่อนสร้างจริง"},
    "law": {"title": "ที่ปรึกษาข้อกฎหมายร้านค้าและสัญญาอิสระ", "desc": "ให้คำปรึกษาการทำสัญญาเช่า สัญญาจ้างงาน และกฎหมายการค้า"},
    "psychology": {"title": "ที่ปรึกษาการปรับบุคลิกภาพ / Life Coach", "desc": "ให้คำปรึกษาเรื่องการสื่อสาร การทำงานร่วมกับผู้อื่น และการพัฒนาตนเอง"}
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
# 5. UI ฝั่งซ้าย: เมนูกรอกข้อมูล (Sidebar - Dark Styled)
# ---------------------------------------------------------
st.sidebar.header("📝 1. กรอกคะแนนรายวิชา (0-100)")
st.sidebar.caption("ปรับระดับคะแนนตามความถนัดของคุณ:")

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
st.sidebar.header("🎨 3. เลือกรูปแบบ UI กราฟ")
chart_type = st.sidebar.radio(
    "รูปแบบการแสดงผลคะแนน:",
    ["🕸️ กราฟแมงมุม (Radar Chart)", "🍩 กราฟวงกลม (Donut Chart)", "📊 กราฟแท่ง (Bar Chart)", "📋 ตารางข้อมูล (Table)"]
)

# ---------------------------------------------------------
# 6. อัลกอริทึมประมวลผลคำนวณ (Main Logic)
# ---------------------------------------------------------
with col_title:
    st.title("🎓 Smart Career Recommendation System")
    st.caption("ระบบวิเคราะห์และจัดอันดับอาชีพอัจฉริยะ ครอบคลุมอาชีพในชีวิตประจำวันและสายงานจริงในโลก")

st.markdown("---")

all_zero = all(value == 0 for value in scores.values())

if all_zero:
    st.error("🚫 **ไม่พบข้อมูลคะแนน**")
    st.warning("⚠️ กรุณาปรับคะแนนในแถบเมนูสีดำฝั่งซ้ายอย่างน้อย 1 วิชา เพื่อเปิดการทำงานของระบบประมวลผล")
    
    st.markdown("---")
    st.subheader("💡 สื่อการเรียนรู้แนะนำสำหรับผู้เริ่มต้น")
    for code, name in SUBJECT_NAMES.items():
        res_info = LEARNING_RESOURCES_DB[code]
        with st.expander(f"📕 {name}", expanded=False):
            st.write(f"**ขอบเขตเนื้อหา:** {res_info['title']}")
            for r in res_info["resources"]:
                st.markdown(f"- 📖 {r}")

else:
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_3 = sorted_scores[:3]
    
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
        st.caption(f"📊 ดัชนีความสอดคล้อง: **{match_pct}%** (คำนวณจากคะแนนวิชา: {career_item['score']} / {max_score_possible})")
        st.write(f"**ลักษณะงานจริง:** {c['desc']}")
        
        used_sub_text = ", ".join([f"**{SUBJECT_NAMES[s]}** ({scores[s]} คะแนน)" for s in c["subjects"] if s in career_item["active_subjects"]])
        st.markdown(f"💡 **องค์ความรู้ที่นำมาใช้ประมวลผล:** {used_sub_text}")
        st.markdown("---")

    # ฟังก์ชันคำนวณจับคู่ที่มีตรรกะกรองขั้นต่ำ (Prevent Logic Errors)
    def get_careers_for_subjects(target_subject_ids, min_matches=1):
        results = []
        max_possible = sum([scores[s] for s in target_subject_ids])
        
        for career in CAREERS_DB:
            c_subjs = career["subjects"]
            matches = [s for s in c_subjs if s in target_subject_ids]
            
            # ต้องมีวิชาตรงตามเกณฑ์ขั้นต่ำ min_matches
            if len(matches) >= min_matches:
                score_sum = sum([scores[s] for s in matches])
                results.append({
                    "details": career,
                    "matches_count": len(matches),
                    "score": score_sum,
                    "active_subjects": matches
                })
                
        # จัดอันดับด้วย จำนวนวิชาที่ตรงกันก่อน ตามด้วย ผลรวมคะแนน
        results.sort(key=lambda x: (x["matches_count"], x["score"]), reverse=True)
        return results, max_possible

    st.subheader("📌 ผลการวิเคราะห์และจัดอันดับอาชีพที่เหมาะสม")
    
    tab1, tab2, tab3 = st.tabs([
        "🧩 ผลลัพธ์จาก 3 วิชาหลัก", 
        "⚖️ การจับคู่ย่อย (2 วิชาหลัก)", 
        "💡 แยกตามวิชาเดี่ยว (3 อันดับแรก)"
    ])

    # --- TAB 1: 3 วิชาหลักรวมกัน ---
    with tab1:
        st.info(f"🎯 **กลุ่ม 3 วิชาเด่นของคุณ:** {SUBJECT_NAMES[s1_id]}, {SUBJECT_NAMES[s2_id]}, {SUBJECT_NAMES[s3_id]}")
        # กรองให้ตรงอย่างน้อย 2 วิชาขึ้นไป เพื่อป้องกันการแนะนำอาชีพหลุดธีม
        careers_3, max_3 = get_careers_for_subjects([s1_id, s2_id, s3_id], min_matches=2)
        
        if not careers_3:
            # Fallback หากเงื่อนไขเข้มเกินไป
            careers_3, max_3 = get_careers_for_subjects([s1_id, s2_id, s3_id], min_matches=1)

        if careers_3:
            rank_badges = ["🥇 **อันดับ 1:**", "🥈 **อันดับ 2:**", "🥉 **อันดับ 3:**"]
            for i, item in enumerate(careers_3[:3]):
                badge = rank_badges[i] if i < len(rank_badges) else "🎯 **แนะนำเพิ่มเติม:**"
                render_career_card(item, max_3, badge)
        else:
            st.warning("ไม่พบอาชีพในฐานข้อมูลที่สอดคล้องกับกลุ่มวิชานี้")

    # --- TAB 2: รวม 2 วิชาแบบจับคู่ ---
    with tab2:
        st.caption("จับคู่ผสมผสาน 2 วิชาจาก 3 วิชาหลักของคุณ:")
        
        pair1_ids = [s1_id, s2_id]
        pair2_ids = [s1_id, s3_id]
        pair3_ids = [s2_id, s3_id]

        subtab2_1, subtab2_2, subtab2_3 = st.tabs([
            f"1️⃣ {SUBJECT_NAMES[s1_id]} + {SUBJECT_NAMES[s2_id]}",
            f"2️⃣ {SUBJECT_NAMES[s1_id]} + {SUBJECT_NAMES[s3_id]}",
            f"3️⃣ {SUBJECT_NAMES[s2_id]} + {SUBJECT_NAMES[s3_id]}"
        ])

        with subtab2_1:
            c_list, max_p = get_careers_for_subjects(pair1_ids, min_matches=1)
            for item in c_list[:3]:
                render_career_card(item, max_p)

        with subtab2_2:
            c_list, max_p = get_careers_for_subjects(pair2_ids, min_matches=1)
            for item in c_list[:3]:
                render_career_card(item, max_p)

        with subtab2_3:
            c_list, max_p = get_careers_for_subjects(pair3_ids, min_matches=1)
            for item in c_list[:3]:
                render_career_card(item, max_p)

    # --- TAB 3: วิชาเดี่ยว ---
    with tab3:
        st.caption("แนะนำอาชีพเฉพาะทางแยกตามรายวิชาที่ได้คะแนนสูงสุด:")
        
        subtab3_1, subtab3_2, subtab3_3 = st.tabs([
            f"🥇 {SUBJECT_NAMES[s1_id]} ({s1_score} คะแนน)",
            f"🥈 {SUBJECT_NAMES[s2_id]} ({s2_score} คะแนน)",
            f"🥉 {SUBJECT_NAMES[s3_id]} ({s3_score} คะแนน)"
        ])

        with subtab3_1:
            c_list, max_p = get_careers_for_subjects([s1_id], min_matches=1)
            for item in c_list[:3]:
                render_career_card(item, max_p)

        with subtab3_2:
            c_list, max_p = get_careers_for_subjects([s2_id], min_matches=1)
            for item in c_list[:3]:
                render_career_card(item, max_p)

        with subtab3_3:
            c_list, max_p = get_careers_for_subjects([s3_id], min_matches=1)
            for item in c_list[:3]:
                render_career_card(item, max_p)

    # --- ส่วนที่ 2: อาชีพอิสระ ---
    st.subheader("🚀 เส้นทางอาชีพอิสระในชีวิตประจำวัน (Freelance Options)")
    fav_freelance = FREELANCE_CAREERS_DB[favorite_subject]
    st.success(f"**จากวิชาที่คุณชื่นชอบเป็นพิเศษ:** {SUBJECT_NAMES[favorite_subject]}\n\n"
               f"👉 **อาชีพอิสระที่แนะนำ:** **{fav_freelance['title']}**\n\n"
               f"📝 {fav_freelance['desc']}")

    st.markdown("---")

    # --- ส่วนที่ 3: แสดงผลกราฟ ---
    st.subheader(f"📊 กราฟสรุปผลวิเคราะห์ทักษะ ({chart_type.split(' ')[1]})")

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
    st.subheader("💡 ข้อเสนอแนะเพื่อการพัฒนาทักษะ (Skill Enhancement)")
    low_score_subjects = [item for item in sorted_scores if item[1] < 30]

    if low_score_subjects:
        st.error(f"🚨 **พบวิชาที่มีคะแนนน้อยกว่า 30 คะแนน จำนวน {len(low_score_subjects)} วิชา:**")
        for s_id, score in low_score_subjects:
            res_info = LEARNING_RESOURCES_DB[s_id]
            with st.expander(f"📕 {SUBJECT_NAMES[s_id]} — ได้ {score} คะแนน", expanded=False):
                st.write(f"**ขอบเขตเนื้อหา:** {res_info['title']}")
                st.markdown("**คอร์สและสื่อการเรียนรู้แนะนำ:**")
                for r in res_info["resources"]:
                    st.markdown(f"- 📖 {r}")
    else:
        lowest_id, lowest_score = sorted_scores[-1]
        res_info = LEARNING_RESOURCES_DB[lowest_id]
        st.info(f"🎉 **เยี่ยมมาก! ไม่มีวิชาใดได้คะแนนต่ำกว่า 30 คะแนน** (วิชาที่ได้น้อยที่สุดคือ {SUBJECT_NAMES[lowest_id]} ได้ {lowest_score} คะแนน)")
        with st.expander(f"📙 แนะนำคอร์สเพิ่มทักษะสำหรับ: {SUBJECT_NAMES[lowest_id]}", expanded=False):
            st.write(f"**ขอบเขตเนื้อหา:** {res_info['title']}")
            st.markdown("**คอร์สและสื่อการเรียนรู้แนะนำ:**")
            for r in res_info["resources"]:
                st.markdown(f"- 📖 {r}")
