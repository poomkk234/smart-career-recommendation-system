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
# 4. ฐานข้อมูลอาชีพในชีวิตประจำวัน (ปรับปรุงให้หลากหลายและสมจริง)
# ---------------------------------------------------------
CAREERS_DB = [
    {
        "title": "นักสถิติ / นักคณิตศาสตร์ประกันภัย (Actuary)",
        "primary": ["math"],
        "secondary": ["finance", "tech"],
        "desc": "ใช้ทักษะคำนวณคณิตศาสตร์ขั้นสูง วิเคราะห์ความเสี่ยงทางการเงินและสถิติประชากร"
    },
    {
        "title": "ครู / อาจารย์สอนวิชาคณิตศาสตร์ (Mathematics Teacher)",
        "primary": ["math"],
        "secondary": ["psychology", "social"],
        "desc": "ถ่ายทอดความรู้ทางคณิตศาสตร์ ถ่ายทอดตรรกะความรู้ เข้าใจจิตวิทยาการเรียนรู้ของนักเรียน"
    },
    {
        "title": "วิศวกรซอฟต์แวร์ / นักพัฒนาแอปพลิเคชัน (Software Engineer)",
        "primary": ["tech"],
        "secondary": ["math", "english"],
        "desc": "ออกแบบและเขียนโค้ดพัฒนาระบบคอมพิวเตอร์ ใช้ตรรกะคณิตศาสตร์และภาษาอังกฤษในการศึกษาเทคโนโลยี"
    },
    {
        "title": "นักการตลาดออนไลน์ / ครีเอเตอร์ดิจิทัล (Digital Content Creator & Marketer)",
        "primary": ["marketing"],
        "secondary": ["art", "tech"],
        "desc": "วางแผนกลยุทธ์การขาย สร้างสรรค์คอนเทนต์รูปภาพ/วิดีโอ และใช้เครื่องมือโซเชียลมีเดีย"
    },
    {
        "title": "ผู้ประกอบการ / เจ้าของธุรกิจส่วนตัว (Entrepreneur / SME Business Owner)",
        "primary": ["marketing"],
        "secondary": ["finance", "psychology"],
        "desc": "บริหารจัดการธุรกิจ วางแผนการเงิน การขาย บริหารทีมงานและเจรจาพฤติกรรมลูกค้า"
    },
    {
        "title": "นักบัญชี / สมุห์บัญชีองค์กร (Accountant)",
        "primary": ["finance"],
        "secondary": ["math", "law"],
        "desc": "ตรวจสอบและบันทึกรายการทางการเงิน คำนวณภาษี และกำกับดูแลเอกสารตามข้อกฎหมาย"
    },
    {
        "title": "แพทย์ / พยาบาล / เภสัชกร (Medical Professional)",
        "primary": ["science"],
        "secondary": ["psychology", "english"],
        "desc": "ใช้วิทยาศาสตร์สุขภาพในการวินิจฉัยและรักษา ดูแลจิตวิทยาผู้ป่วย และใช้วิชาการภาษาอังกฤษ"
    },
    {
        "title": "ทนายความ / ที่ปรึกษากฎหมาย (Lawyer / Legal Advisor)",
        "primary": ["law"],
        "secondary": ["social", "psychology"],
        "desc": "ให้คำแนะนำทางกฎหมาย วิจารณ์ระเบียบสังคม ตรวจสอบสัญญาและใช้จิตวิทยาในการว่าความ"
    },
    {
        "title": "นักจิตวิทยาปรึกษา / เจ้าหน้าที่ทรัพยากรบุคคล (HR Manager / Counselor)",
        "primary": ["psychology"],
        "secondary": ["social", "english"],
        "desc": "คัดเลือกและดูแลบุคลากรในองค์กร ให้คำปรึกษาปัญหาความเครียด พัฒนาศักยภาพมนุษย์"
    },
    {
        "title": "กราฟิกดีไซเนอร์ / นักวาดภาพประกอบ (Graphic Designer / Illustrator)",
        "primary": ["art"],
        "secondary": ["design_3d", "marketing"],
        "desc": "สร้างสรรค์ผลงานศิลปะ ออกแบบอัตลักษณ์แบรนด์ โลโก้ และงานสื่อสิ่งพิมพ์/สื่อดิจิทัล"
    },
    {
        "title": "สถาปนิก / มัณฑนากรตกแต่งภายใน (Architect / Interior Designer)",
        "primary": ["design_3d"],
        "secondary": ["art", "math"],
        "desc": "ออกแบบโครงสร้างอาคารและพื้นที่ใช้สอย คำนวณขนาดตามหลักวิศวกรรม ผสานความสวยงามทางศิลปะ"
    },
    {
        "title": "นักแปล / ล่าม / เจ้าหน้าที่การต่างประเทศ (Translator / Interpreter)",
        "primary": ["lang3"],
        "secondary": ["english", "social"],
        "desc": "แปลภาษาทางการ สื่อสารเจรจาข้ามวัฒนธรรม และประสานงานความสัมพันธ์ระหว่างประเทศ"
    },
    {
        "title": "เชฟ / นักรังสรรค์อาหาร (Chef / Culinary Artist)",
        "primary": ["science"],
        "secondary": ["art", "marketing"],
        "desc": "ประยุกต์ใช้วิทยาศาสตร์อาหาร (โภชนาการ/เคมี) ตกแต่งหน้าตาจานอาหาร และบริหารต้นทุนร้าน"
    },
    {
        "title": "นักบิน / เจ้าหน้าที่ควบคุมการจราจรทางอากาศ (Pilot / Air Traffic Controller)",
        "primary": ["science"],
        "secondary": ["english", "math"],
        "desc": "ใช้วิทยาศาสตร์การบิน คำนวณพิกัดคณิตศาสตร์ และสื่อสารภาษาอังกฤษตามมาตรฐานสากล"
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

# ตรวจสอบว่ามีคะแนนมากกว่า 0 หรือไม่
all_zero = all(v == 0 for v in scores.values())

if all_zero:
    st.error("🚫 **ไม่พบอาชีพที่เหมาะสม (คะแนนเป็น 0 ทุกวิชา)**")
    st.warning("⚠️ คุณยังไม่ได้ปรับคะแนนรายวิชา กรุณาปรับคะแนนในแถบเมนูฝั่งซ้ายอย่างน้อย 1 วิชา เพื่อให้ระบบคำนวณหาอาชีพ")
    
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
    # --- อัลกอริทึมคำนวณความสอดคล้องใหม่ (Weighted Matching Logic) ---
    def calculate_career_fit(career):
        primary_subs = career["primary"]
        secondary_subs = career["secondary"]
        
        # คำนวณคะแนนเฉลี่ยวิชาหลัก (น้ำหนัก 70%)
        p_scores = [scores[s] for s in primary_subs]
        p_avg = sum(p_scores) / len(p_scores) if p_scores else 0
        
        # คำนวณคะแนนเฉลี่ยวิชาสนับสนุน (น้ำหนัก 30%)
        s_scores = [scores[s] for s in secondary_subs]
        s_avg = sum(s_scores) / len(s_scores) if s_scores else 0
        
        # คะแนนรวมสุทธิ
        total_fit = (p_avg * 0.7) + (s_avg * 0.3)
        return round(total_fit, 1)

    # จัดอันดับอาชีพตามคะแนนความสอดคล้อง
    career_rankings = []
    for career in CAREERS_DB:
        fit_score = calculate_career_fit(career)
        if fit_score > 0:
            career_rankings.append({
                "details": career,
                "fit_score": fit_score
            })

    career_rankings.sort(key=lambda x: x["fit_score"], reverse=True)

    # --- ส่วนที่ 1: แสดงอาชีพที่เหมาะสมที่สุด ---
    st.subheader("🎯 อาชีพที่เหมาะสมที่สุดจากการประมวลผลทักษะวิชา")

    active_user_subs = [f"{SUBJECT_NAMES[k]} ({v} คะแนน)" for k, v in scores.items() if v > 0]
    st.info(f"💡 **วิชาที่คุณกรอกคะแนน:** {', '.join(active_user_subs)}")

    for i, item in enumerate(career_rankings[:3]):
        c = item["details"]
        fit = item["fit_score"]
        
        rank_badges = ["🥇 อันดับ 1 (เหมาะสมที่สุด)", "🥈 อันดับ 2", "🥉 อันดับ 3"]
        st.markdown(f"#### {rank_badges[i]}: **{c['title']}**")
        st.write(f"**รายละเอียดอาชีพ:** {c['desc']}")
        
        p_text = ", ".join([f"**{SUBJECT_NAMES[s]}** ({scores[s]} คะแนน)" for s in c["primary"]])
        s_text = ", ".join([f"{SUBJECT_NAMES[s]} ({scores[s]} คะแนน)" for s in c["secondary"]])
        
        st.markdown(f"💡 **วิชาหลักที่ใช้ประมวลผล:** {p_text}")
        st.markdown(f"🛠️ **วิชาสนับสนุน:** {s_text}")
        
        st.progress(min(fit / 100.0, 1.0))
        st.caption(f"📊 **ระดับความเข้ากันของทักษะวิชา: {fit}%**")
        st.markdown("---")

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
