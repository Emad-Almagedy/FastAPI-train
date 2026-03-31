import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

# ----------------------------
# API HELPERS
# ----------------------------

def login(email, password):
    return requests.post(
        f"{BASE_URL}/auth/jwt/login",
        data={"username": email, "password": password}
    )

def register(email, password):
    return requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": email, "password": password}
    )

def get_my_donations(token):
    return requests.get(
        f"{BASE_URL}/donations/me",
        headers={"Authorization": f"Bearer {token}"}
    )

def create_donation(token, data):
    return requests.post(
        f"{BASE_URL}/donations",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )

def get_all_donations(token):
    return requests.get(
        f"{BASE_URL}/admin/donations",
        headers={"Authorization": f"Bearer {token}"}
    )

def update_donation(token, donation_id, data):
    return requests.patch(
        f"{BASE_URL}/admin/donations/{donation_id}",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )

def make_admin(token, user_id):
    return requests.patch(
        f"{BASE_URL}/admin/make-admin/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

# ----------------------------
# CONFIG
# ----------------------------

st.set_page_config(page_title="Donation System", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None

# ----------------------------
# AUTH SECTION
# ----------------------------

if not st.session_state.token:
    st.title("🔐 Login / Register")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # ---------------- LOGIN ----------------
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_btn"):
            res = login(email, password)

            if res.status_code == 200:
                st.session_state.token = res.json()["access_token"]
                st.success("Login successful")
                st.rerun()
            else:
                st.error(res.text)

    # ---------------- REGISTER ----------------
    with tab2:
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")

        if st.button("Register", key="register_btn"):
            res = register(email, password)

            if res.status_code in [200, 201]:
                st.success("Registered successfully")
            else:
                st.error(res.text)

# ----------------------------
# MAIN APP
# ----------------------------

else:
    st.sidebar.title("Navigation")

    page = st.sidebar.radio(
        "Go to",
        ["User Dashboard", "Admin Dashboard", "Logout"],
        key="nav_radio"
    )

    # ---------------- LOGOUT ----------------
    if page == "Logout":
        st.session_state.token = None
        st.rerun()

    # ---------------- USER ----------------
    elif page == "User Dashboard":
        st.title("👤 User Dashboard")

        st.subheader("➕ Create Donation")

        mobile = st.text_input("Mobile Number", key="user_mobile")
        neighbourhood = st.text_input("Neighbourhood", key="user_neighbourhood")
        donation_type = st.selectbox(
            "Donation Type",
            ["shoes", "clothes", "electronics","furniture","other"],
            key="user_donation_type"
        )

        if st.button("Submit Donation", key="submit_donation"):
            res = create_donation(st.session_state.token, {
                "mobile_number": mobile,
                "neighbourhood": neighbourhood,
                "donation_type": donation_type
            })

            if res.status_code == 200:
                st.success("Donation created")
            else:
                st.error(res.text)

        st.subheader("📄 My Donations")

        res = get_my_donations(st.session_state.token)

        if res.status_code == 200:
            for i, d in enumerate(res.json()):
                st.json(d)
        else:
            st.error("Failed to load donations")

    # ---------------- ADMIN ----------------
    elif page == "Admin Dashboard":
        st.title("🛠 Admin Dashboard")

        st.subheader("📊 All Donations")

        res = get_all_donations(st.session_state.token)

        if res.status_code == 200:
            donations = res.json()

            for i, d in enumerate(donations):
                st.write(f"Donation ID: {d['id']}")
                st.json(d)

                new_status = st.selectbox(
                    "Update Status",
                    ["submitted", "processing", "processed"],
                    key=f"status_{d['id']}_{i}"
                )

                if st.button("Update", key=f"update_{d['id']}_{i}"):
                    update_donation(
                        st.session_state.token,
                        d["id"],
                        {"status": new_status}
                    )
                    st.success("Updated")

                st.divider()

        else:
            st.error("Failed to load admin data")

        st.subheader("👑 Promote User")

        user_id = st.text_input("User ID", key="admin_user_id")

        if st.button("Make Admin", key="make_admin_btn"):
            res = make_admin(st.session_state.token, user_id)

            if res.status_code == 200:
                st.success("User promoted")
            else:
                st.error("Failed to promote user")