import streamlit as st
import random
from datetime import datetime
import time
import json
from pathlib import Path
import csv
import io
from passlib.context import CryptContext

# Create data directory structure
DATA_DIR = Path("data")
USER_DATA_DIR = DATA_DIR / "users"
DATA_DIR.mkdir(exist_ok=True)
USER_DATA_DIR.mkdir(exist_ok=True)

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User management functions
def load_users():
    users_file = DATA_DIR / "users.json"
    if users_file.exists():
        with open(users_file, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    users_file = DATA_DIR / "users.json"
    with open(users_file, 'w') as f:
        json.dump(users, f)

# User-specific data functions
def get_user_dir(username):
    return USER_DATA_DIR / username

def load_journal_entries(username):
    user_dir = get_user_dir(username)
    journal_file = user_dir / "journal_entries.json"
    if journal_file.exists():
        with open(journal_file, 'r') as f:
            return json.load(f)
    return {}

def load_user_metrics(username):
    user_dir = get_user_dir(username)
    metrics_file = user_dir / "user_metrics.json"
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            return json.load(f)
    return {"days_active": 0, "challenges_completed": 0, "last_active_date": None}

def save_user_metrics(username, metrics):
    user_dir = get_user_dir(username)
    metrics_file = user_dir / "user_metrics.json"
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f)

def update_user_metrics(username):
    entries = load_journal_entries(username)
    metrics = load_user_metrics(username)
    
    if entries:
        dates = set(entry['date'] for entry in entries.values())
        metrics['days_active'] = len(dates)
        metrics['challenges_completed'] = len(entries)
        metrics['last_active_date'] = max(entry['date'] for entry in entries.values())
    
    save_user_metrics(username, metrics)
    return metrics

def save_journal_entry(username, entry):
    entries = load_journal_entries(username)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    entries[timestamp] = entry
    
    user_dir = get_user_dir(username)
    journal_file = user_dir / "journal_entries.json"
    with open(journal_file, 'w') as f:
        json.dump(entries, f, indent=4)
    
    update_user_metrics(username)

def export_to_csv(entries):
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Date', 'Mood', 'Achievements', 'Lessons Learned', 
                    'Challenges Faced', 'Tomorrow\'s Goals', 'Timestamp'])
    
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

# Dynamic content functions
def get_challenges():
    return [
        "Learn 3 new words in a language you're interested in",
        "Watch a tutorial about a skill you want to develop",
        "Read a chapter from an educational book",
        "Write down three things you learned today",
        "Journal about a recent success and what made it possible",
        "Identify one limiting belief and reframe it positively",
        "Try a new approach to a problem you're facing",
        "Teach someone something you know well",
        "Practice a skill for 15 focused minutes",
        "List 5 areas where you've improved recently",
        "Compliment someone else's growth mindset",
        "Visualize yourself overcoming a current challenge"
    ]

def get_quotes():
    return [
        {"text": "The only limit to our realization of tomorrow will be our doubts of today.", "author": "Franklin D. Roosevelt"},
        {"text": "Everything is hard before it is easy.", "author": "Goethe"},
        {"text": "The expert in anything was once a beginner.", "author": "Helen Hayes"},
        {"text": "Success is the sum of small efforts, repeated day in and day out.", "author": "Robert Collier"},
        {"text": "You don't have to be great to start, but you have to start to be great.", "author": "Zig Ziglar"},
        {"text": "Progress is progress, no matter how small.", "author": "Unknown"}
    ]

# Set page config
st.set_page_config(
    page_title="Growth Mindset Explorer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None

# Sidebar authentication
with st.sidebar:
    if not st.session_state.authenticated:
        st.header("Welcome to Growth Mindset Explorer!")
        auth_choice = st.radio("Choose action:", ["Login", "Sign Up"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if auth_choice == "Login":
            if st.button("Login"):
                users = load_users()
                if username in users and pwd_context.verify(password, users[username]):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        else:
            if st.button("Sign Up"):
                if len(username) < 4:
                    st.error("Username must be at least 4 characters")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    users = load_users()
                    if username in users:
                        st.error("Username already exists")
                    else:
                        users[username] = pwd_context.hash(password)
                        save_users(users)
                        # Create user directory
                        user_dir = get_user_dir(username)
                        user_dir.mkdir(parents=True, exist_ok=True)
                        # Initialize empty files
                        (user_dir / "journal_entries.json").write_text("{}")
                        (user_dir / "user_metrics.json").write_text(json.dumps(
                            {"days_active": 0, "challenges_completed": 0, "last_active_date": None}
                        ))
                        st.success("Account created successfully! Please login.")
    else:
        st.markdown(f"### 👤 Logged in as {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
        
        # Progress metrics
        st.markdown("---")
        st.markdown("### 📊 Your Progress")
        metrics = load_user_metrics(st.session_state.username)
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
if st.session_state.authenticated:
    st.markdown('<h1 class="title-text">Growth Mindset Explorer</h1>', unsafe_allow_html=True)

    # Motivational quotes
    daily_quote = random.choice(get_quotes())
    st.markdown(f"""
    <div class="quote-box">
        <i>"{daily_quote['text']}"</i><br>
        <small>- {daily_quote['author']}</small>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
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
        
        challenges = get_challenges()
        
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
        
        journal_tab1, journal_tab2 = st.tabs(["✏️ Write Entry", "📖 View Previous Entries"])
        
        with journal_tab1:
            reflection_date = st.date_input("Date", datetime.now())
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
                        entry = {
                            "date": reflection_date.strftime("%Y-%m-%d"),
                            "mood": mood,
                            "achievements": achievements,
                            "lessons": lessons,
                            "challenges": challenges_faced,
                            "tomorrow_goals": tomorrow_goals,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        save_journal_entry(st.session_state.username, entry)
                        time.sleep(1)
                        st.success("Journal entry saved successfully! Keep up the great work! 🌟")
                        st.balloons()
                        time.sleep(3)
                        st.rerun()
        
        with journal_tab2:
            st.subheader("Previous Journal Entries")
            entries = load_journal_entries(st.session_state.username)
            
            if not entries:
                st.info("No journal entries yet. Start writing your growth journey!")
            else:
                search_term = st.text_input("🔍 Search entries...", "").lower()
                date_filter = st.date_input("📅 Filter by date", None)
                
                if st.button("Export to CSV"):
                    csv_string = export_to_csv(entries)
                    st.download_button(
                        label="Download CSV",
                        data=csv_string,
                        file_name="growth_mindset_journal.csv",
                        mime="text/csv"
                    )
                
                sorted_entries = sorted(entries.items(), key=lambda x: x[1]['timestamp'], reverse=True)
                
                for _, entry in sorted_entries:
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
        
        st.subheader("Weekly Progress")
        entries = load_journal_entries(st.session_state.username)
        progress_data = [len([e for e in entries.values() 
                            if datetime.strptime(e['date'], "%Y-%m-%d").weekday() == day]) 
                    for day in range(7)]
        st.line_chart(progress_data)
        
        st.subheader("Skill Progress")
        metrics = load_user_metrics(st.session_state.username)
        base_progress = min(metrics['challenges_completed'] * 2, 100)
        skills = {
            "Problem Solving": base_progress + random.randint(-10, 10),
            "Critical Thinking": base_progress + random.randint(-10, 10),
            "Creativity": base_progress + random.randint(-10, 10),
            "Persistence": base_progress + random.randint(-10, 10)
        }
        
        for skill, progress in skills.items():
            progress = max(0, min(100, progress))
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
        <p>Built by Farwa Kanwal ❤️ with using Streamlit | Embracing Growth Mindset Every Day</p>
        <p>Remember: Your potential is unlimited. Keep growing! 🌱</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown('<h1 class="title-text">Growth Mindset Explorer</h1>', unsafe_allow_html=True)
    st.info("Please login or sign up from the sidebar to access your personal growth journey!")