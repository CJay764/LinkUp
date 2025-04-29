import streamlit as st
import requests

st.set_page_config(layout="wide")

# Airtable credentials
PAT_TOKEN = "patPi0EkkyhssdmHm.07c7724fe2b05f2758bf0e4b2a278da2b8c9be08b91b019c1ac6c240fab92ffd"
BASE_ID = "app87RFuOmswJXa9Q"
TABLE_NAME = "User table"

# Airtable API URL
url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

# Headers with Authorization (Bearer token)
headers = {
    "Authorization": f"Bearer {PAT_TOKEN}",
    "Content-Type": "application/json"
}

# -------------------- Airtable Functions --------------------

def get_data_from_airtable():
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["records"]
    else:
        st.error(f"Failed to retrieve data from Airtable. Status code: {response.status_code}")
        st.error(f"Response: {response.text}")
        return []

def add_user_to_airtable(name, email, what_I_know, looking_for, bio):
    data = {
        "fields": {
            "Name": name,
            "Email": email,
            "What I know": what_I_know,
            "Looking For": looking_for,
            "Bio": bio
        }
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        st.success(f"{name}, your profile has been created successfully!")
    else:
        st.error(f"Failed to create profile. Status code: {response.status_code}")
        st.error(f"Error details: {response.text}")

# -------------------- Page Functions --------------------

def home_page():
    st.title("Welcome to LinkUp! 🎯")
    st.subheader("Connect. Learn. Grow.")
    st.write("""
    LinkUp is a platform where students can connect based on their skills and interests.
    - Share what you know.
    - Find what you're looking for.
    - Grow together!
    """)

def display_sign_up_form():
    st.title("Student Sign-Up ✍️")

    with st.form(key="signup_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        
        predefined_skills = ['Python', 'Java', 'JavaScript', 'C++', 'HTML', 'CSS']
        selected_skills = st.multiselect("Select your skills:", options=predefined_skills)
        selected_looking_for = st.multiselect("Select what you are looking for:", options=predefined_skills)
        bio = st.text_area("Bio")
        submit_button = st.form_submit_button("Sign Up")

        if submit_button:
            if name and email:
                add_user_to_airtable(name, email, selected_skills, selected_looking_for, bio)
            else:
                st.warning("Please fill out both Name and Email.")

def display_user_data():
    st.title("List of Students 📋")
    records = get_data_from_airtable()

    if records:
        for record in records:
            fields = record["fields"]
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader(fields.get('Name', 'N/A'))
                st.write(f"**Email:** {fields.get('Email', 'N/A')}")
                st.write(f"**Skills:** {', '.join(fields.get('What I know', ['N/A']))}")
                st.write(f"**Looking For:** {', '.join(fields.get('Looking For', ['N/A']))}")
                st.write(f"**Bio:** {fields.get('Bio', 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.write("No data found.")

def find_matches():
    st.title("Find Your Matches 🤝")

    records = get_data_from_airtable()
    if not records:
        st.warning("No users available for matching.")
        return

    users = []
    for record in records:
        fields = record.get("fields", {})
        users.append({
            "id": record.get("id"),
            "name": fields.get("Name", ""),
            "email": fields.get("Email", ""),
            "know": fields.get("What I know", []),
            "looking_for": fields.get("Looking For", []),
            "bio": fields.get("Bio", "")
        })

    selected_user_name = st.selectbox("Select your name:", [user["name"] for user in users])
    selected_user = next((user for user in users if user["name"] == selected_user_name), None)

    if not selected_user:
        st.error("User not found.")
        return

    match_type = st.radio(
        "Choose Match Type:",
        ("One-way Match (Find people who have what you want)", "Skill Exchange Match (You teach each other)")
    )

    if match_type == "One-way Match (Find people who have what you want)":
        st.subheader(f"One-Way Matches for {selected_user['name']} 🧩")
        matches = []

        for user in users:
            if user["id"] != selected_user["id"]:
                skills_you_want = set(selected_user["looking_for"])
                skills_they_have = set(user["know"])
                common_skills = skills_you_want.intersection(skills_they_have)
                if common_skills:
                    matches.append((user, common_skills))

        matches.sort(key=lambda x: len(x[1]), reverse=True)

        if matches:
            st.success(f"{len(matches)} match{'es' if len(matches) != 1 else ''} found.")
            for match_user, matched_skills in matches:
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.write(f"### {match_user['name']}")
                    st.write(f"**Email:** {match_user['email']}")
                    st.write(f"**They know:** {', '.join(matched_skills)}")
                    st.write(f"**Bio:** {match_user['bio']}")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No one-way matches found yet.")

    else:
        st.subheader(f"Skill Exchange Matches for {selected_user['name']} 🔄")
        matches = []

        for user in users:
            if user["id"] != selected_user["id"]:
                skills_you_want = set(selected_user["looking_for"])
                skills_they_have = set(user["know"])
                skills_they_want = set(user["looking_for"])
                skills_you_have = set(selected_user["know"])

                if skills_you_want.intersection(skills_they_have) and skills_they_want.intersection(skills_you_have):
                    matches.append((
                        user, 
                        skills_you_want.intersection(skills_they_have),
                        skills_they_want.intersection(skills_you_have)
                    ))

        matches.sort(key=lambda x: len(x[1]) + len(x[2]), reverse=True)

        if matches:
            st.success(f"{len(matches)} match{'es' if len(matches) != 1 else ''} found.")
            for match_user, what_they_have_for_you, what_you_have_for_them in matches:
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.write(f"### {match_user['name']}")
                    st.write(f"**Email:** {match_user['email']}")
                    st.write(f"**They can teach you:** {', '.join(what_they_have_for_you)}")
                    st.write(f"**You can teach them:** {', '.join(what_you_have_for_them)}")
                    st.write(f"**Bio:** {match_user['bio']}")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No skill exchange matches found yet.")

# -------------------- Main App --------------------

def run_app():
    st.markdown("""
    <style>
    button[data-baseweb="tab"] > div {
        font-size: 27px;
        font-weight: bold;
        padding: 12px 20px;
        margin: 0 5px;
        border-radius: 10px;
        background-color: #f0f2f6;
        color: #333333;
        transition: all 0.3s ease;
    }
    section.main > div {
        padding: 2rem 5rem;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #0066cc !important;
        color: white !important;
    }
    button[data-baseweb="tab"]:hover {
        background-color: #d6e4f0;
        color: black;
    }
    .card {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .stTextInput>div>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>div, .stMultiSelect>div>div {
        border-radius: 8px;
        padding: 10px;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "📝 Sign Up", "🔍 Find Matches", "📋 View Students"])

    with tab1:
        home_page()
    with tab2:
        display_sign_up_form()
    with tab3:
        find_matches()
    with tab4:
        display_user_data()

run_app()
