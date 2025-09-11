# Redeploy trigger
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from colorthief import ColorThief
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# --- Page Config ---
st.set_page_config(
    page_title="Emanations AI Data Readiness Assessment",
    page_icon="emanations_logo.png",
    layout="wide"
)

# --- Initialize colors ---
primary_color = "#1f4e79"   # fallback
secondary_color = "#ffcc00" # fallback
primary_color_light = primary_color  # default

logo_path = "emanations_logo.png"

def lighten_color(hex_color, factor=0.3):
    """Lighten a hex color by a factor (0-1)"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2],16)
    g = int(hex_color[2:4],16)
    b = int(hex_color[4:6],16)
    r = int(r + (255-r)*factor)
    g = int(g + (255-g)*factor)
    b = int(b + (255-b)*factor)
    return f'#{r:02x}{g:02x}{b:02x}'

if os.path.exists(logo_path):
    try:
        color_thief = ColorThief(logo_path)
        palette = color_thief.get_palette(color_count=2)
        primary_color = '#%02x%02x%02x' % palette[0]
        secondary_color = '#%02x%02x%02x' % palette[1] if len(palette) > 1 else "#ffcc00"
        primary_color_light = lighten_color(primary_color, 0.3)
    except Exception:
        st.warning("Could not extract colors from logo, using defaults.")
else:
    st.warning(f"Logo not found at {logo_path}. Using default colors.")

# --- Custom CSS ---
st.markdown(f"""
<style>
.stApp {{
    background-color: #f9f9fb;
}}
.stMarkdown h2 {{
    font-size: 18px !important;
    font-weight: bold !important;
    color: {primary_color_light} !important;
    border-bottom: 2px solid {secondary_color};
    padding-bottom: 4px;
}}
.stMarkdown h3 {{
    font-size: 18px !important;
    font-weight: bold !important;
    color: {primary_color_light} !important;
}}
.stSlider label {{
    font-size: 18px !important;
    font-weight: bold !important;
    color: #333 !important;
}}
.stTextInput label {{
    font-size: 18px !important;
    font-weight: 400 !important;
    color: {primary_color} !important;
}}
.stMarkdown, .stWrite, p {{
    font-size: 18px !important;
    color: #444 !important;
}}
</style>
""", unsafe_allow_html=True)

# --- Logo ---
if os.path.exists(logo_path):
    try:
        logo = Image.open(logo_path)
        st.image(logo, width=1000)
    except:
        st.warning("Could not open logo image. Skipping display.")

st.title("Emanations AI Data Readiness Assessment – Sandbox Tool")
st.write("Score each question from 0 (Not ready) to 10 (Fully ready). Add comments where needed.")

# --- Sections & Questions ---
sections = {
    "Data Availability": [
        "Relevant datasets exist for project goals",
        "Datasets are accessible internally or externally",
        "Data coverage is sufficient; minimal gaps"
    ],
    "Data Quality & Structure": [
        "Data is clean, accurate, and complete",
        "Data is structured, semi-structured, or usable for AI",
        "Metadata, dictionaries, or schema definitions exist",
        "Data is up-to-date for project needs"
    ],
    "Compliance & Ethics": [
        "Data usage complies with privacy laws (GDPR etc.)",
        "Sensitive data is anonymized/pseudonymized",
        "Ethical implications of AI use are considered",
        "Legal permissions and consent are documented"
    ],
    "Governance & Stewardship": [
        "Data ownership/responsibility is clear",
        "Policies exist for sharing, auditing, and security",
        "Procedures exist for ongoing monitoring/updating"
    ],
    "Technical Readiness": [
        "Data is stored securely and accessible offline",
        "Data can be ingested into AI/ML models",
        "Infrastructure supports experimentation (compute/storage)",
        "APIs, connectors, or pipelines are available"
    ],
    "Use Case Alignment": [
        "Data supports intended AI outcomes",
        "Datasets can be linked/enriched for insights",
        "Historical data available for training/testing",
        "Success metrics / KPIs are defined"
    ],
    "Collaboration & Sharing": [
        "Stakeholders are willing to share data safely",
        "Collaboration avoids privacy/IP issues",
        "Incentives/agreements in place for contributions"
    ]
}

total_score = 0
max_score = 0
section_scores = {}
results = {}

# --- Input Loop ---
for section, questions in sections.items():
    st.header(section)
    results[section] = {}
    section_total = 0
    section_max = 0

    for q in questions:
        col1, col2 = st.columns([1,3])
        with col1:
            score = st.slider(q, min_value=0, max_value=10, value=0, key=f"{section}-{q}-score")
        with col2:
            comment = st.text_input("Comment", key=f"{section}-{q}-comment")

        results[section][q] = {"score": score, "comment": comment}
        total_score += score
        max_score += 10
        section_total += score
        section_max += 10

    section_percentage = (section_total / section_max) * 100
    if section_percentage >= 75:
        st.success(f"{section} Readiness: {section_percentage:.0f}%")
    elif section_percentage >= 50:
        st.warning(f"{section} Readiness: {section_percentage:.0f}%")
    else:
        st.error(f"{section} Readiness: {section_percentage:.0f}%")
    section_scores[section] = section_percentage

# --- Overall Score ---
st.header("Overall Assessment")
overall_percentage = (total_score / max_score) * 100
if overall_percentage >= 75:
    st.success(f"High readiness – {overall_percentage:.0f}%")
elif overall_percentage >= 50:
    st.warning(f"Moderate readiness – {overall_percentage:.0f}%")
else:
    st.error(f"Low readiness – {overall_percentage:.0f}%")

# --- Radar Chart ---
st.subheader("Readiness by Section (Radar Chart)")
radar_buf = None
if section_scores:
    labels = list(section_scores.keys())
    values = list(section_scores.values())
    values += values[:1]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, "o-", linewidth=2, label="Readiness", color=primary_color_light)
    ax.fill(angles, values, alpha=0.25, color=primary_color_light)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10, color="#333333")
    ax.set_ylim(0, 100)
    ax.set_title("Section-wise Readiness", size=14, weight="bold", color=primary_color_light)
    ax.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))
    st.pyplot(fig)

    # Save radar chart to buffer for PDF
    radar_buf = BytesIO()
    plt.savefig(radar_buf, format="PNG")
    radar_buf.seek(0)
    plt.close(fig)

# --- CSV Download ---
if st.button("Download Results as CSV"):
    data_rows = []
    for section, qs in results.items():
        for q, vals in qs.items():
            data_rows.append({
                "Section": section,
                "Question": q,
                "Score": vals["score"],
                "Comment": vals["comment"]
            })
    df = pd.DataFrame(data_rows)
    df.to_csv("AI_Data_Readiness_Assessment.csv", index=False)
    st.success("CSV downloaded successfully!")

# --- PDF Download ---
def create_pdf(results, section_scores, overall_percentage, radar_buf, logo_path="emanations_logo.png"):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Logo
    if os.path.exists(logo_path):
        try:
            logo = ImageReader(logo_path)
            c.drawImage(logo, 50, height - 100, width=120, height=60, mask="auto")
        except:
            pass

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0.08, 0.6, 0.6)  # teal
    c.drawString(180, height - 60, "AI Data Readiness Report")

    # Overall score
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(50, height - 120, f"Overall Readiness: {overall_percentage:.0f}%")

    # Section scores
    y = height - 160
    for section, perc in section_scores.items():
        c.drawString(50, y, f"{section}: {perc:.0f}%")
        y -= 20

    # Radar chart
    if radar_buf:
        radar_img = ImageReader(radar_buf)
        c.drawImage(radar_img, 120, 200, width=350, height=350)

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(50, 50, "Generated by Emanations AI Readiness Sandbox")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

pdf_buffer = create_pdf(results, section_scores, overall_percentage, radar_buf)

st.download_button(
    label="📄 Download results as PDF",
    data=pdf_buffer,
    file_name="AI_Data_Readiness_Report.pdf",
    mime="application/pdf",
)
