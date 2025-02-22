import streamlit as st
import random
from datetime import datetime
import time
import json
from pathlib import Path
import csv
import io

# Create a data directory if it doesn't exist
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
JOURNAL_FILE = DATA_DIR / "journal_entries.json"
METRICS_FILE = DATA_DIR / "user_metrics.json"

# Function to load journal entries
def load_journal_entries():
    if JOURNAL_FILE.exists():
        with open(JOURNAL_FILE, 'r') as f:
            return json.load(f)
    return {}

# Function to load user metrics
def load_user_metrics():
    if METRICS_FILE.exists():
        with open(METRICS_FILE, 'r') as f:
            return json.load(f)
    return {"days_active": 0, "challenges_completed": 0, "last_active_date": None}

# Function to save user metrics
def save_user_metrics(metrics):
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f)

# Function to update user metrics
def update_user_metrics():
    entries = load_journal_entries()
    metrics = load_user_metrics()
    
    if entries:
        # Calculate days active
        dates = set(entry['date'] for entry in entries.values())
        metrics['days_active'] = len(dates)
        
        # Calculate challenges completed (assuming each entry represents a completed challenge)
        metrics['challenges_completed'] = len(entries)
        
        # Update last active date
        metrics['last_active_date'] = max(dates)
    
    save_user_metrics(metrics)
    return metrics

# Function to save journal entries
def save_journal_entry(entry):
    entries = load_journal_entries()
    
    # Create unique key for the entry using timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    entries[timestamp] = entry
    
    # Save to file
    with open(JOURNAL_FILE, 'w') as f:
        json.dump(entries, f, indent=4)
    
    # Update metrics after saving new entry
    update_user_metrics()

# Function to export journal entries to CSV
def export_to_csv(entries):
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Mood', 'Achievements', 'Lessons Learned', 'Challenges Faced', 'Tomorrow\'s Goals', 'Timestamp'])
    
    # Write entries
    for entry in entries.values():
        writer.writerow([
            entry['date'],
            entry['mood'],
            entry['achievements'],
            entry['lessons'],
            entry['challenges'],
            entry['tomorrow_goals'],
            entry['timestamp']
        ])
    
    return output.getvalue()

# Set page config
st.set_page_config(
    page_title="Growth Mindset Explorer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with animations and better styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    
    .main {
        font-family: 'Poppins', sans-serif;
    }
    
    .title-text {
        background: linear-gradient(45deg, #3494e6, #ec6ead);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 600 !important;
        margin-bottom: 2rem !important;
        animation: fadeIn 1s ease-in;
    }
    
    .challenge-box {
        padding: 20px;
        border-radius: 15px;
        background: linear-gradient(135deg, #f6f9fc 0%, #f0f2f6 100%);
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .challenge-box:hover {
        transform: translateY(-5px);
    }
    
    .quote-box {
        padding: 20px;
        border-left: 4px solid #3494e6;
        background-color: #f8f9fa;
        margin: 20px 0;
        border-radius: 0 15px 15px 0;
    }
    
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 10px 0;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(45deg, #3494e6, #ec6ead);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Your Progress")
    metrics = update_user_metrics()
    days_active = metrics['days_active']
    challenges_completed = metrics['challenges_completed']
    st.markdown(f"""
    <div class="metric-card">
        <h4>🎯 Days Active</h4>
        <h2>{days_active}</h2>
    </div>
    <div class="metric-card">
        <h4>✅ Challenges Completed</h4>
        <h2>{challenges_completed}</h2>
    </div>
    """, unsafe_allow_html=True)

# Main content
st.markdown('<h1 class="title-text">Growth Mindset Explorer</h1>', unsafe_allow_html=True)

# Motivational quotes
quotes = [
    {"text": "The only limit to our realization of tomorrow will be our doubts of today.", "author": "Franklin D. Roosevelt"},
    {"text": "Everything is hard before it is easy.", "author": "Goethe"},
    {"text": "The expert in anything was once a beginner.", "author": "Helen Hayes"},
    {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"}
]
daily_quote = random.choice(quotes)
st.markdown(f"""
<div class="quote-box">
    <i>"{daily_quote['text']}"</i><br>
    <small>- {daily_quote['author']}</small>
</div>
""", unsafe_allow_html=True)

# Tabs with animation effect
tabs = ["🎓 Learn", "🎯 Challenge", "📝 Reflect", "📈 Progress"]
tab1, tab2, tab3, tab4 = st.tabs(tabs)

with tab1:
    st.header("Understanding Growth Mindset")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Fixed Mindset")
        for item in ["I'm not good at this", "I give up", "This is too hard", "I can't do better"]:
            st.error(item)
    
    with col2:
        st.markdown("### Growth Mindset")
        for item in ["I can learn this", "I'll try a different approach", "This may take time and effort", "I can always improve"]:
            st.success(item)
    
    # Interactive learning section
    st.markdown("### 🧠 Brain Plasticity")
    st.markdown("""
    Your brain is like a muscle - the more you exercise it, the stronger it becomes!
    
    Try this exercise:
    1. Think of a skill you want to improve
    2. Break it down into small, manageable steps
    3. Track your progress daily
    """)

with tab2:
    st.header("Daily Growth Challenges")
    
    challenges = [
        "Learn 3 new words in a language you're interested in",
        "Solve a puzzle that challenges your mind",
        "Write down three things you learned today",
        "Teach someone something you know well",
        "Try a new approach to a problem you're facing",
        "Read an article about a topic you know nothing about",
        "Practice active listening in your next conversation",
        "Set a specific goal for tomorrow"
    ]
    
    if 'current_challenge' not in st.session_state:
        st.session_state.current_challenge = random.choice(challenges)
    
    st.markdown("### 🎯 Your Daily Challenge:")
    st.markdown(f"""
    <div class='challenge-box'>
        <h3>{st.session_state.current_challenge}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Get New Challenge"):
        st.session_state.current_challenge = random.choice(challenges)
        st.rerun()

with tab3:
    st.header("Reflection Journal")
    
    # Sub-tabs for writing and viewing entries
    journal_tab1, journal_tab2 = st.tabs(["✏️ Write Entry", "📖 View Previous Entries"])
    
    with journal_tab1:
        # Date picker
        reflection_date = st.date_input("Date", datetime.now())
        
        # Mood tracker
        mood = st.select_slider(
            "How are you feeling about your progress?",
            options=["😔", "😐", "🙂", "😊", "🤩"],
            value="🙂"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            achievements = st.text_area("Today's Achievements", height=100)
            lessons = st.text_area("Lessons Learned", height=100)
        
        with col2:
            challenges_faced = st.text_area("Challenges Faced", height=100)
            tomorrow_goals = st.text_area("Tomorrow's Goals", height=100)
        
        if st.button("Save Journal Entry"):
            if not achievements.strip() or not lessons.strip():
                st.warning("Please fill in at least the Achievements and Lessons fields!")
            else:
                with st.spinner("Saving your reflection..."):
                    # Create entry dictionary
                    entry = {
                        "date": reflection_date.strftime("%Y-%m-%d"),
                        "mood": mood,
                        "achievements": achievements,
                        "lessons": lessons,
                        "challenges": challenges_faced,
                        "tomorrow_goals": tomorrow_goals,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Save entry
                    save_journal_entry(entry)
                    
                    time.sleep(1)  # Simulate saving
                    st.success("Journal entry saved successfully! Keep up the great work! 🌟")
                    st.balloons()

                    # Wait for balloons to be visible before refresh
                    time.sleep(3)  # Give 2 seconds for balloons animation
                    
                    # Refresh the app to update the sidebar metrics
                    st.rerun()
    
    with journal_tab2:
        st.subheader("Previous Journal Entries")
        
        # Load and display entries
        entries = load_journal_entries()
        
        if not entries:
            st.info("No journal entries yet. Start writing your growth journey!")
        else:
            # Sort entries by date (newest first)
            sorted_entries = sorted(entries.items(), key=lambda x: x[1]['timestamp'], reverse=True)
            
            # Add a search/filter box
            search_term = st.text_input("🔍 Search entries...", "").lower()
            
            # Date filter
            date_filter = st.date_input("📅 Filter by date", None)
            
            # Export to CSV button
            if st.button("Export to CSV"):
                csv_string = export_to_csv(entries)
                st.download_button(
                    label="Download CSV",
                    data=csv_string,
                    file_name="growth_mindset_journal.csv",
                    mime="text/csv"
                )
            
            for _, entry in sorted_entries:
                # Apply filters
                entry_date = datetime.strptime(entry['date'], "%Y-%m-%d").date()
                entry_content = f"{entry['achievements']} {entry['lessons']} {entry['challenges']} {entry['tomorrow_goals']}".lower()
                
                if date_filter and entry_date != date_filter:
                    continue
                    
                if search_term and search_term not in entry_content:
                    continue
                
                with st.expander(f"📝 Entry from {entry['date']} ({entry['mood']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Achievements")
                        st.write(entry['achievements'])
                        
                        st.markdown("#### Lessons Learned")
                        st.write(entry['lessons'])
                    
                    with col2:
                        st.markdown("#### Challenges Faced")
                        st.write(entry['challenges'])
                        
                        st.markdown("#### Tomorrow's Goals")
                        st.write(entry['tomorrow_goals'])
                    
                    st.caption(f"Written on: {entry['timestamp']}")

with tab4:
    st.header("Growth Tracker")
    
    # Weekly progress
    st.subheader("Weekly Progress")
    progress_data = [random.randint(60, 100) for _ in range(7)]
    st.line_chart(progress_data)
    
    # Skill progress
    st.subheader("Skill Progress")
    skills = {
        "Problem Solving": random.randint(50, 100),
        "Critical Thinking": random.randint(50, 100),
        "Creativity": random.randint(50, 100),
        "Persistence": random.randint(50, 100)
    }
    
    for skill, progress in skills.items():
        st.markdown(f"### {skill}")
        st.progress(progress / 100)
        if progress < 70:
            st.info("Keep practicing! You're making progress! 💪")
        else:
            st.success("Excellent progress! Keep pushing your boundaries! 🌟")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built by Farwa Kanwal❤️ using Streamlit | Embracing Growth Mindset Every Day</p>
              <p>Remember: Your potential is unlimited. Keep growing! 🌱</p>
</div>
""", unsafe_allow_html=True)