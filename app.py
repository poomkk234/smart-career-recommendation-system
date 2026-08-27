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
# 3. ฐานข้อมูลวิชาการเรียน
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
# 4. ฐานข้อมูลอาชีพ (เพิ่มอาชีพสายผสม Niche Careers)
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
        "title": "นักวาดภาพประกอบ / คอมมิคระดับโลก (Global Illustrator)",
        "primary": ["art"],
        "secondary": ["english", "lang3"],
        "desc": "สร้างสรรค์ผลงานศิลปะ วาดภาพประกอบ และสื่อสารกับผู้ว่าจ้างต่างประเทศ"
    },
    {
        "title": "นักออกแบบ UI/UX สายนานาชาติ (International UI/UX Designer)",
        "primary": ["art"],
        "secondary": ["english", "tech"],
        "desc": "ออกแบบหน้าตาแอปพลิเคชันและเว็บไซต์โดยใช้หลักศิลปะ ร่วมกับทีมต่างชาติ"
    },
    {
        "title": "ล่ามและนักแปลภาษาต่างประเทศ (Interpreter / Translator)",
        "primary": ["lang3"],
        "secondary": ["english", "social"],
        "desc": "แปลภาษา ฟัง-พูด สื่อสารระหว่างประเทศ แปลเอกสารหรือทำหน้าที่ล่าม"
    },
    {
        "title": "พนักงานต้อนรับบนเครื่องบิน (Flight Attendant)",
        "primary": ["lang3"],
        "secondary": ["english", "psychology"],
        "desc": "ดูแลความปลอดภัย บริการผู้โดยสารบนเครื่องบิน และใช้ภาษาต่างประเทศ"
    },
    {
        "title": "แพทย์ / หมอรักษาโรค (Medical Doctor)",
        "primary": ["science"],
        "secondary": ["math", "english"],
        "desc": "วินิจฉัยโรค ประยุกต์ใช้วิทยาศาสตร์ คำนวณขนาดยา และอ่านตำราต่างประเทศ"
    },
    {
        "title": "วิศวกรซอฟต์แวร์ (Software Developer)",
        "primary": ["tech"],
        "secondary": ["math", "english"],
        "desc": "เขียนโปรแกรมคอมพิวเตอร์ ใช้ตรรกะคณิตศาสตร์แก้ปัญหา"
    },
    {
        "title": "สถาปนิก / นักออกแบบ 3D (Architect / 3D Designer)",
        "primary": ["design_3d"],
        "secondary": ["art", "math"],
        "desc": "ออกแบบอาคารสถานที่ วาดแบบ 3D และคำนวณโครงสร้างตามหลักสถาปัตยกรรม"
    },
    {
        "title": "นักกฎหมาย / ทนายความ (Lawyer / Legal Advisor)",
        "primary": ["law"],
        "secondary": ["social", "english"],
        "desc": "ตีความกฎหมาย ร่างสัญญา ดำเนินคดี และว่าความในชั้นศาล"
    },
    {
        "title": "นักการตลาดดิจิทัล (Digital Marketer)",
        "primary": ["marketing"],
        "secondary": ["tech", "finance"],
        "desc": "วางแผนกลยุทธ์การตลาด วิเคราะห์โฆษณาออนไลน์และบริหารงบประมาณ"
    }
]

FREELANCE_CAREERS_DB = {
    "math": {"title": "Tutor สอนพิเศษคณิตศาสตร์ / Data Freelance", "desc": "รับสอนพิเศษวิชาคณิตศาสตร์ หรือรับทำวิเคราะห์ข้อมูลสถิติ"},
    "science": {"title": "นักเขียนบทความสุขภาพและวิทยาศาสตร์", "desc": "รับเขียนบทความความรู้ สุขภาพ อาหาร และวิทยาศาสตร์"},
    "tech": {"title": "Freelance รับทำเว็บไซต์ / ไอทีซัพพอร์ต", "desc": "รับสร้างเว็บไซต์ พัฒนาแอปพลิเคชัน และดูแลระบบคอมพิวเตอร์"},
    "english": {"title": "นักแปลเอกสารอิสระ / พิสูจน์อักษร", "desc": "รับแปลเอกสาร แปลซับไตเติล หรือเขียนอีเมลติดต่อธุรกิจต่างประเทศ"},
    "art": {"title": "Freelance Illustrator / ช่างภาพ", "desc": "รับวาดภาพประกอบ วาดสติกเกอร์ไลน์ ถ่ายภาพ และออกแบบกราฟิก"},
    "social": {"title": "นักสร้างคอนเทนต์ประวัติศาสตร์/สังคม", "desc": "ทำคลิปเล่าเรื่องประวัติศาสตร์ สังคมวิทยา หรือเรื่องน่ารู้รอบโลก"},
    "finance": {"title": "รับทำบัญชีร้านค้า / วางแผนภาษีบุคคล", "desc": "ช่วยร้านค้าเล็กๆ วางแผนภาษี ยื่นภาษี และสรุปงบการเงิน"},
    "marketing": {"title": "Freelance ดูแลเพจ / ยิงแอดโฆษณา", "desc": "รับเขียนโพสต์ขายของ วางแผนคอนเทนต์ และยิงแอด Facebook/TikTok"},
    "lang3": {"title": "ล่ามอิสระ / มัคคุเทศก์ภาษาเฉพาะ", "desc": "รับงานแปลภาษาเฉพาะกิจ ล่ามติดตาม หรือนำเที่ยวชาวต่างชาติ"},
    "design_3d": {"title": "Freelance ขึ้นโมเดล 3D / เขียนแบบบ้าน", "desc": "รับขึ้นโมเดล 3D สินค้า หรือออกแบบและเขียนแบบบ้าน"},
    "law": {"title": "ที่ปรึกษาข้อกฎหมายร้านค้าและตรวจสัญญา", "desc": "ให้คำปรึกษาการทำสัญญาเช่า สัญญาจ้างงาน และตรวจข้อตกลงทางกฎหมาย"},
    "psychology": {"title": "ที่ปรึกษาพัฒนาบุคลิกภาพ / Life Coach", "desc": "ให้คำปรึกษาเรื่องการสื่อสาร การบริหารจิตใจ และพัฒนาศักยภาพ"}
}

LEARNING_RESOURCES_DB = {
    "math": {"title": "คณิตศาสตร์และสถิติ", "resources": ["Khan Academy Math", "Coursera Mathematics"]},
    "science": {"title": "วิทยาศาสตร์และเทคโนโลยี", "resources": ["edX Introductory Physics", "สสวท."]},
    "tech": {"title": "วิทยาการคำนวณและโปรแกรมมิ่ง", "resources": ["freeCodeCamp.org", "Harvard CS50"]},
    "english": {"title": "ภาษาอังกฤษเพื่อการสื่อสาร", "resources": ["BBC Learning English", "Duolingo"]},
    "art": {"title": "ศิลปะและการออกแบบ", "resources": ["Canva Design School", "Skillshare"]},
    "social": {"title": "สังคมศึกษาและการเมืองโลก", "resources": ["8 Minutes History", "National Geographic"]},
    "finance": {"title": "การเงิน บัญชี และการลงทุน", "resources": ["SET e-Learning", "Money Buffalo"]},
    "marketing": {"title": "การตลาดดิจิทัลและธุรกิจ", "resources": ["Google Digital Garage", "HubSpot Academy"]},
    "lang3": {"title": "ภาษาที่สาม (3rd Language)", "resources": ["Memrise", "Busuu App"]},
    "design_3d": {"title": "สถาปัตยกรรมและ 3D Design", "resources": ["Blender Guru", "SketchUp Campus"]},
    "law": {"title": "กฎหมายและรัฐศาสตร์", "resources": ["จุฬาฯ MOOC กฎหมาย", "คลังกฎหมายไทย"]},
    "psychology": {"title": "จิตวิทยาพฤติกรรมมนุษย์", "resources": ["Coursera Intro to Psychology", "Psych2Go"]}
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
# 6. อัลกอริทึมคำนวณ % ความสอดคล้อง (Percentage Match)
# ---------------------------------------------------------
with col_title:
    st.title("🎓 Smart Career Recommendation System")
    st.caption("ระบบวิเคราะห์อาชีพอัจฉริยะ (Weighted % Match System)")

st.markdown("---")

active_scores = {k: v for k, v in scores.items() if v > 0}

if len(active_scores) == 0:
    st.error("🚫 **ไม่พบข้อมูลคะแนน**")
    st.warning("⚠️ กรุณากรอกคะแนนอย่างน้อย 1 วิชาในแถบสีดำฝั่งซ้าย เพื่อเปิดการประมวลผล")
else:
    # --- ฟังก์ชันคำนวณ % ความสอดคล้องระหว่างวิชาที่เลือก กับ โครงสร้างอาชีพ ---
    def calculate_subject_overlap_pct(career_item, selected_subject_ids):
        all_reqs = career_item["primary"] + career_item["secondary"]
        matched = [s for s in selected_subject_ids if s in all_reqs]
        
        if not matched:
            return 0.0, []
        
        # คำนวณสัดส่วน % จากวิชาที่ตรงกัน
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
        
        # เรียงลำดับตาม % สอดคล้องจากมากไปน้อย
        results.sort(key=lambda x: x["match_pct"], reverse=True)
        return results

    def render_career_card(career_item, rank_label=""):
        c = career_item["details"]
        match_pct = career_item["match_pct"]
        
        if rank_label:
            st.markdown(f"#### {rank_label} {c['title']}")
        else:
            st.markdown(f"#### 🎯 **{c['title']}**")
            
        st.progress(min(match_pct / 100, 1.0))
        st.caption(f"📊 ความสอดคล้องกับวิชาที่คุณเลือก: **{match_pct}%**")
        st.write(f"**ลักษณะงานจริง:** {c['desc']}")
        
        p_text = ", ".join([f"**{SUBJECT_NAMES[s]}** ({scores[s]} คะแนน)" for s in career_item["primary_subs"] if s in scores])
        s_text = ", ".join([f"{SUBJECT_NAMES[s]} ({scores[s]} คะแนน)" for s in career_item["secondary_subs"] if s in scores])
        
        st.markdown(f"🔑 **วิชาหลัก:** {p_text}")
        st.markdown(f"🛠️ **วิชาสนับสนุน:** {s_text}")
        st.markdown("---")

    sorted_active = sorted(active_scores.items(), key=lambda x: x[1], reverse=True)
    num_active = len(sorted_active)

    st.subheader("📌 ผลการวิเคราะห์และจัดอันดับอาชีพที่เหมาะสม")

    # =========================================================
    # การแสดงผลแบ่งตามจำนวนวิชาที่กรอก
    # =========================================================
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
        
        # ดึงอาชีพที่สอดคล้อง % สูงสุดมาโชว์
        for i, item in enumerate(c_list[:3]):
            badge = f"🥇 อันดับ {i+1} (ตรง 100%):" if item["match_pct"] == 100 else f"⭐ อันดับ {i+1} (ตรง {item['match_pct']}%):"
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
            
            # แสดงอาชีพเรียงตาม % ความสอดคล้องเสมอ (ไม่มีหน้าว่างเปล่า)
            for i, item in enumerate(c_list[:3]):
                pct = item["match_pct"]
                if pct == 100:
                    badge = f"🥇 **ตรงสาย 100% (อันดับ {i+1}):**"
                else:
                    badge = f"⭐ **ความสอดคล้อง {pct}% (อันดับ {i+1}):**"
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
                    render_career_card(item, f"🎯 อันดับ {i+1} ({item['match_pct']}% Match):")

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
