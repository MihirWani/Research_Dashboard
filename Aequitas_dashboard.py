import streamlit as st
import pandas as pd

# === Load your consolidated CSV ===
df = pd.read_csv("consolidated_notes.csv")

# === Page setup ===
st.set_page_config(page_title="Research Summary", layout="wide")
st.title("📘 Consolidated Research Insights")

# === Sidebar Filters ===
st.sidebar.header("🔍 Filter Insights")

# Optional filters with default to "show all"
analyst_options = df['Person'].dropna().unique().tolist()
sector_options = df['Sector'].dropna().unique().tolist()
company_options = df['Company'].dropna().unique().tolist()

selected_analysts = st.sidebar.multiselect("🧑‍💼 Analyst", options=analyst_options, default=analyst_options)
selected_sectors = st.sidebar.multiselect("🏷️ Sector", options=sector_options)
selected_companies = st.sidebar.multiselect("🏢 Company", options=company_options)

# Apply filters
filtered_df = df.copy()
if selected_analysts:
    filtered_df = filtered_df[filtered_df['Person'].isin(selected_analysts)]
if selected_sectors:
    filtered_df = filtered_df[filtered_df['Sector'].isin(selected_sectors)]
if selected_companies:
    filtered_df = filtered_df[filtered_df['Company'].isin(selected_companies)]

# === Keyword Search ===
search_query = st.sidebar.text_input("🔎 Search notes or topics")

if search_query:
    search_query = search_query.lower()
    filtered_df = filtered_df[
        filtered_df['Notes'].str.lower().str.contains(search_query, na=False) |
        filtered_df['Short notes'].str.lower().str.contains(search_query, na=False) |
        filtered_df['Topic'].str.lower().str.contains(search_query, na=False)
    ]
filtered_df['Company'].str.lower().str.contains(search_query, na=False)




# === Format cluster display ===
filtered_df['Cluster ID'] = filtered_df['Cluster ID'].fillna(-1).astype(int)
filtered_df = filtered_df.sort_values(by='Cluster ID')

def escape_dollar(text):
    return str(text).replace('$', '\\$')


# === Loop through clusters ===
for cluster_id in filtered_df['Cluster ID'].unique():
    cluster_notes = filtered_df[filtered_df['Cluster ID'] == cluster_id]

    # Cluster title: use Topic from first note if available
    topic_name = cluster_notes.iloc[0]['Topic']
    if pd.isna(topic_name) or topic_name.strip() == "":
        topic_name = f"Topic Cluster {cluster_id}"
    st.markdown(f"<h4 style='color:#444; margin-bottom:10px'>{topic_name}</h4>", unsafe_allow_html=True)

    # Loop through notes in this cluster
    for _, row in cluster_notes.iterrows():
        # Fallback-safe topic
        topic_preview = row['Topic'] if pd.notnull(row.get('Topic')) else ""

        # Preview from Short Notes or first 25 words of Notes
        preview = " ".join(str({escape_dollar(row['Notes'])}).split()[:25]) + "..."

        # Final expander title (with topic and preview)
        title = f"🔹 {row['Person']} – Sr. No. {int(row['Sr. No.'])} — 🧾 {topic_preview} — 🧵 _{preview}_"

        with st.expander(title):
            # Topic (highlighted)
            if pd.notnull(row.get('Topic')):
                st.markdown(f"<span style='font-size:18px; font-weight:600'>🧾 Topic: {row['Topic']}</span>", unsafe_allow_html=True)

            # Full Note (in gray card)
            st.markdown(f"""
            <div style='padding: 10px; background-color: #f9f9f9; border-radius: 5px; margin-top: 10px;'>
            <span style='font-size:16px; font-weight:600'>📝 Full Note:</span><br><br>
            {escape_dollar(row['Notes'])}
            </div>
            """, unsafe_allow_html=True)

            # Short Note
            if pd.notnull(row.get('Short notes')) and row['Short notes'].strip() != "":
                st.markdown(f"<span style='font-weight:500'>🧩 Short Note:</span> {row['Short notes']}", unsafe_allow_html=True)

            # Company
            if pd.notnull(row.get('Company')) and row['Company'].strip() != "":
                st.markdown(f"<span style='font-weight:500'>🏢 Company:</span> {row['Company']}", unsafe_allow_html=True)

            # Sector
            if pd.notnull(row.get('Sector')) and row['Sector'].strip() != "":
                st.markdown(f"<span style='font-weight:500'>🏷️ Sector:</span> {row['Sector']}", unsafe_allow_html=True)

            # Reference
            if pd.notnull(row.get('Reference')) and row['Reference'].strip() != "":
                st.markdown(f"<span style='font-weight:500'>🔗 Reference:</span> <a href='{row['Reference']}' target='_blank'>{row['Reference']}</a>", unsafe_allow_html=True)

            # Image
            if pd.notnull(row.get('Images')) and "http" in row['Images']:
                st.image(row['Images'].split("(")[-1].rstrip(")"), width=400)

    # Line between clusters
    st.markdown("---")
