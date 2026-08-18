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
# 2. ฐานข้อมูลวิชาการเรียนการสอน (เพิ่มครอบคลุม 12 วิชา)
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
# 3. ฐานข้อมูลอาชีพหลัก (ใช้วิชาประกอบในการคำนวณ)
# ---------------------------------------------------------
CAREERS_DB = [
    {
        "title": "วิศวกรซอฟต์แวร์ / นักพัฒนาแอปพลิเคชัน (Software Engineer)",
        "subjects": ["tech", "math", "english"],
        "desc": "ใช้ตรรกะคณิตศาสตร์ เขียนโค้ดคอมพิวเตอร์ และอ่านเอกสารเทคโนโลยีภาษาอังกฤษ"
    },
    {
        "title": "นักวิเคราะห์ข้อมูลและ AI (Data Scientist / AI Specialist)",
        "subjects": ["math", "tech", "science"],
        "desc": "วิเคราะห์ข้อมูลขนาดใหญ่ด้วยคณิตศาสตร์ สถิติ วิทยาการคำนวณ และกระบวนการวิจัย"
    },
    {
        "title": "แพทย์ / นักวิจัยทางการแพทย์ (Medical Researcher)",
        "subjects": ["science", "math", "english"],
        "desc": "ใช้วิทยาศาสตร์ขั้นสูง คำนวณขนาดยา/สถิติ และสื่อสารภาษาอังกฤษเพื่อผลงานวิจัย"
    },
    {
        "title": "นักการเงินเชิงวิเคราะห์และนักลงทุน (Financial Analyst)",
        "subjects": ["finance", "math", "marketing"],
        "desc": "ประเมินความเสี่ยง ตรวจสอบตัวเลขการเงิน การคำนวณผลตอบแทน และวิเคราะห์แนวโน้มตลาด"
    },
    {
        "title": "นักออกแบบ UI/UX และผลิตภัณฑ์ดิจิทัล (UI/UX Designer)",
        "subjects": ["art", "tech", "psychology"],
        "desc": "ออกแบบความสวยงาม รวมกับระบบเทคโนโลยี และเข้าใจจิตวิทยาพฤติกรรมผู้ใช้งาน"
    },
    {
        "title": "สถาปนิกและนักออกแบบ 3D (Architect)",
        "subjects": ["design_3d", "math", "art"],
        "desc": "คำนวณโครงสร้างตามหลักวิศวกรรม/ฟิสิกส์ ผสานกับความสวยงามทางศิลปะและการเขียนแบบ"
    },
    {
        "title": "นักการตลาดดิจิทัลและกลยุทธ์แบรนด์ (Digital Strategist)",
        "subjects": ["marketing", "social", "tech"],
        "desc": "วางแผนธุรกิจ เข้าใจสังคมพฤติกรรมผู้บริโภค และใช้เครื่องมือดิจิทัลวิเคราะห์แคมเปญ"
    },
    {
        "title": "นักกฎหมายธุรกิจระหว่างประเทศ (International Corporate Lawyer)",
        "subjects": ["law", "english", "social"],
        "desc": "ใช้ข้อกฎหมายและระเบียบสังคม ร่างสัญญาภาษาอังกฤษ และเข้าใจบริบทธุรกิจ"
    },
    {
        "title": "นักจิตวิทยาคลินิก / นักที่ปรึกษาองค์กร (Corporate Psychologist)",
        "subjects": ["psychology", "social", "english"],
        "desc": "ใช้หลักจิตวิทยา วิเคราะห์พฤติกรรมมนุษย์และสังคม พร้อมการสื่อสารระดับสากล"
    },
    {
        "title": "นักวิเคราะห์และล่ามเจรจาธุรกิจข้ามชาติ (Global Business Analyst)",
        "subjects": ["lang3", "english", "marketing"],
        "desc": "ใช้ทักษะภาษาที่สาม ภาษาอังกฤษ และความรู้การตลาดในการเจรจาการค้าระหว่างประเทศ"
    },
    {
        "title": "นักพัฒนาเกมและเอ็ฟเฟกต์ (Game Developer / FX Artist)",
        "subjects": ["tech", "art", "design_3d"],
        "desc": "การเขียนโปรแกรมระบบเกม ออกแบบตัวละคร และสร้างแบบจำลอง 3 มิติ"
    },
    {
        "title": "นักพิสูจน์หลักฐานและอาชญาวิทยา (Forensic Investigator)",
        "subjects": ["science", "law", "psychology"],
        "desc": "วิเคราะห์หลักฐานทางวิทยาศาสตร์ ประยุกต์ใช้ข้อกฎหมาย และวิเคราะห์พฤติกรรมอาชญากร"
    }
]

# ฐานข้อมูลอาชีพอิสระ (Freelance Database)
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
# 4. ส่วน UI ฝั่งซ้าย: เมนูกรอกข้อมูล (Sidebar)
# ---------------------------------------------------------
st.sidebar.header("📝 1. กรอกคะแนนรายวิชา (0-100)")
st.sidebar.caption("ปรับระดับคะแนนตามผลการเรียนของคุณ:")

scores = {}
for code, name in SUBJECT_NAMES.items():
    # 🔴 ปรับตั้งค่าเริ่มต้นให้ทุกวิชาเป็น 0
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
# 5. อัลกอริทึมและการแสดงผล (Main Layout)
# ---------------------------------------------------------
st.title("🎓 Smart Career Recommendation System")
st.caption("ระบบวิเคราะห์อาชีพหลัก อาชีพอิสระ พร้อมคำนวณจัดอันดับ 1-3 และสื่อการเรียนรู้")
st.markdown("---")

# 🔴 ตรวจสอบเงื่อนไข: หากคะแนนทุกวิชาเป็น 0
all_zero = all(value == 0 for value in scores.values())

if all_zero:
    # แสดงการแจ้งเตือนไม่พบอาชีพทันที
    st.error("🚫 **ไม่พบอาชีพที่เหมาะสม**")
    st.warning("⚠️ เนื่องจากคะแนนทุกวิชาของคุณเป็น **0 คะแนน** ระบบจึงไม่สามารถประมวลผลทักษะเพื่อคำนวณหาอาชีพได้ กรุณาปรับคะแนนในแถบเมนูฝั่งซ้ายอย่างน้อย 1 วิชา")
    
    st.markdown("---")
    st.subheader("💡 คำแนะนำสื่อการเรียนรู้ปูพื้นฐาน (สำหรับวิชาที่มีคะแนน 0)")
    for code, name in SUBJECT_NAMES.items():
        res_info = LEARNING_RESOURCES_DB[code]
        with st.expander(f"📕 {name}", expanded=False):
            st.write(f"**ขอบเขตเนื้อหา:** {res_info['title']}")
            for r in res_info["resources"]:
                st.markdown(f"- 📖 {r}")

else:
    # --- กรณีมีคะแนนมากกว่า 0 ---
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_3_ids = [item[0] for item in sorted_scores[:3]]
    top_2_ids = [item[0] for item in sorted_scores[:2]]

    # คำนวณความเข้ากันของอาชีพเมื่อนำ 3 วิชาหลักมารวมกัน
    career_rankings = []
    found_exact_3 = False

    for career in CAREERS_DB:
        c_subjs = career["subjects"]
        matches_in_top3 = len([s for s in c_subjs if s in top_3_ids])
        
        # คะแนนรวมจาก 3 วิชาของอาชีพนั้น
        total_score_match = sum([scores[s] for s in c_subjs])
        match_percentage = round((total_score_match / 300) * 100, 1)
        
        if matches_in_top3 == 3:
            found_exact_3 = True

        career_rankings.append({
            "details": career,
            "matches_count": matches_in_top3,
            "match_percentage": match_percentage,
            "total_score": total_score_match
        })

    # เรียงลำดับอาชีพตามความเข้ากันจากมากไปน้อย
    career_rankings.sort(key=lambda x: (x["matches_count"], x["match_percentage"]), reverse=True)
    top_3_careers = career_rankings[:3]

    # --- ส่วนที่ 1: แนะนำอาชีพเรียงอันดับ 1, 2, 3 ---
    st.subheader("🎯 อาชีพที่เหมาะสมที่สุดจากการนำ 3 วิชาหลักมารวมกัน (เรียงตามความเข้ากัน)")

    if not found_exact_3:
        st.warning(
            "⚠️ **แจ้งเตือนการคำนวณ:** ไม่พบอาชีพที่รองรับคะแนน 3 วิชาสูงสุดของคุณพร้อมกันตรงๆ 100% "
            "ระบบจึงปรับเปลี่ยนมาใช้คะแนนรวมและจุดเด่นจาก **2 วิชาหลักแรก** ในการคำนวณจัดอันดับแทน"
        )
    else:
        st.success("✅ **ระบบคำนวณสำเร็จ:** พบอาชีพที่สอดคล้องกับวิชาคะแนนสูงสุด 3 อันดับแรกของคุณอย่างสมบูรณ์")

    rank_icons = ["🥇 อันดับ 1 (เหมาะสมที่สุด)", "🥈 อันดับ 2 (เหมาะสมรองลงมา)", "🥉 อันดับ 3 (ตัวเลือกเพิ่มเติม)"]

    for i, item in enumerate(top_3_careers):
        c = item["details"]
        with st.container():
            st.markdown(f"### {rank_icons[i]}: **{c['title']}**")
            st.progress(item["match_percentage"] / 100)
            st.caption(f"📊 ระดับความเข้ากันของทักษะวิชา: **{item['match_percentage']}%**")
            st.write(f"**รายละเอียดอาชีพ:** {c['desc']}")
            
            used_sub_text = ", ".join([f"**{SUBJECT_NAMES[s]}** ({scores[s]} คะแนน)" for s in c["subjects"]])
            st.markdown(f"💡 **วิชาที่ใช้ประมวลผลอาชีพนี้:** {used_sub_text}")
            st.markdown("---")

    # --- ส่วนที่ 2: อาชีพอิสระจากวิชาที่ชอบ ---
    st.subheader("🚀 อาชีพอิสระ (Freelance) จากวิชาที่คุณชอบ")
    fav_freelance = FREELANCE_CAREERS_DB[favorite_subject]
    st.success(f"**วิชาที่คุณชอบ:** {SUBJECT_NAMES[favorite_subject]}\n\n"
               f"👉 **อาชีพอิสระที่แนะนำ:** **{fav_freelance['title']}**\n\n"
               f"📝 {fav_freelance['desc']}")

    st.markdown("---")

    # --- ส่วนที่ 3: แสดงผลกราฟ UI ตามตัวเลือก ---
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
            line_color='#1E88E5'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    elif "Donut" in chart_type:
        fig = px.pie(df_chart, values='คะแนน', names='วิชา', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    elif "Bar" in chart_type:
        fig = px.bar(df_chart, x='วิชา', y='คะแนน', color='คะแนน', color_continuous_scale='Blues')
        fig.update_layout(yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.dataframe(df_chart, use_container_width=True, hide_index=True)

    st.markdown("---")

    # --- ส่วนที่ 4: สื่อการเรียนรู้สำหรับวิชาที่ได้คะแนน < 30 ---
    st.subheader("💡 คำแนะนำสื่อการเรียนรู้เพื่อพัฒนาตนเอง")

    low_score_subjects = [item for item in sorted_scores if item[1] < 30]

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
        lowest_id, lowest_score = sorted_scores[-1]
        res_info = LEARNING_RESOURCES_DB[lowest_id]
        st.info(f"🎉 **ไม่มีวิชาใดได้คะแนนต่ำกว่า 30 คะแนน!** แนะนำสื่อการเรียนรู้สำหรับวิชาที่ได้คะแนนน้อยที่สุดของคุณแทน:")
        with st.expander(f"📙 {SUBJECT_NAMES[lowest_id]} — ได้ {lowest_score} คะแนน", expanded=True):
            st.write(f"**ขอบเขตเนื้อหา:** {res_info['title']}")
            st.markdown("**สื่อและแหล่งเรียนรู้ที่แนะนำ:**")
            for r in res_info["resources"]:
                st.markdown(f"- 📖 {r}")