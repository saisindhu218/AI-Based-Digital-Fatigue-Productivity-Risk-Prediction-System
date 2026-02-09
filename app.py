import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Digital Fatigue Dashboard", layout="wide")

st.title("🧠 AI-Based Digital Fatigue & Productivity Estimation System")
st.write(
    "This dashboard shows predicted digital fatigue levels, productivity loss, "
    "and personalized insights based on digital usage behavior."
)

# -----------------------------
# Load data
# -----------------------------
DATA_PATH = "datasets/predicted_fatigue_results.csv"

try:
    df = pd.read_csv(DATA_PATH)
    st.success("✅ Dataset loaded successfully")
except Exception as e:
    st.error("❌ Error loading dataset")
    st.exception(e)
    st.stop()

# -----------------------------
# Show raw data
# -----------------------------
st.subheader("📊 Usage Data Preview")
st.dataframe(df.head())

# -----------------------------
# Key Metrics
# -----------------------------
st.subheader("📈 Key Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Avg Screen Time", f"{df['screen_time'].mean():.2f} hrs")

with col2:
    st.metric("Avg Productivity Loss", f"{df['productivity_loss'].mean():.2f} hrs/week")

with col3:
    st.metric("Most Common Fatigue Level", df['predicted_fatigue'].mode()[0])

# -----------------------------
# Fatigue Distribution
# -----------------------------
st.subheader("😵 Fatigue Level Distribution")

fig, ax = plt.subplots()
df['predicted_fatigue'].value_counts().plot(kind='bar', ax=ax)
ax.set_xlabel("Fatigue Level")
ax.set_ylabel("Count")
st.pyplot(fig)

# -----------------------------
# Productivity Zone Analysis
# -----------------------------
st.subheader("⏰ Productivity Zones")

fig2, ax2 = plt.subplots()
df['productivity_zone'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax2)
ax2.set_ylabel("")
st.pyplot(fig2)

# -----------------------------
# Recommendations (simple logic)
# -----------------------------
st.subheader("💡 Sample Recommendation")

row = df.iloc[0]

if row['predicted_fatigue'] == "High":
    rec = "Reduce screen time, increase breaks, avoid night usage."
elif row['night_ratio'] > 0.5:
    rec = "Avoid late-night screen usage to improve focus."
else:
    rec = "Maintain current digital habits."

st.info(rec)
