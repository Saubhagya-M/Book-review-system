import mysql.connector
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import base64

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Book Review System",
    page_icon="📚",
    layout="wide"
)

# ---------- Background Function ----------
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


add_bg_from_local("Bg_BRS.jpg")

# ---------- Transparent Container ----------
st.markdown("""
<style>
.block-container {
background: rgba(0,0,0,0.5);
padding: 2rem;
border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------- Title ----------
st.markdown("<h1 style='color:white;'><b>Book Review System</b></h1>", unsafe_allow_html=True)
st.subheader("By Saubhagya Munsi")

# ---------- MYSQL CONNECTION ----------
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="book_review_system"
)

cursor = connection.cursor()

# ---------- CREATE TABLE ----------
cursor.execute("""
CREATE TABLE IF NOT EXISTS books(
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100),
selected_book VARCHAR(255),
rating INT,
review TEXT
)
""")

connection.commit()

# ---------- FILE UPLOAD ----------
file = st.file_uploader("Upload your CSV file", type=["csv"])

if file is not None:

    df = pd.read_csv(file)

    # ---------- DATA PREVIEW ----------
    st.subheader("Data Preview")
    st.dataframe(df)

    # ---------- DATA SUMMARY ----------
    st.subheader("Data Summary")
    st.write(df.describe())

    # ---------- UNIQUE BOOK COUNT ----------
    st.write("📚 Total Unique Books:", df["Book-Title"].nunique())

    # ---------- SEARCH ----------
    st.subheader("🔍 Search Book")

    search = st.text_input("Enter book name")

    if search:
        result = df[df["Book-Title"].str.contains(search, case=False)]
        st.dataframe(result)

    # ---------- AUTHOR FILTER ----------
    st.subheader("Filter by Author")

    authors = df["Book-Author"].dropna().unique()
    selected_author = st.selectbox("Select Author", authors)

    filtered_data = df[df["Book-Author"] == selected_author]
    st.dataframe(filtered_data)

    # ---------- REVIEW SYSTEM ----------
    st.subheader("✍ Submit Review")

    name = st.text_input("Enter your name")

    book_list = df["Book-Title"].dropna().unique()
    selected_book = st.selectbox("Select Book", book_list)

    rating = st.number_input(
        "Enter Rating (1-5)",
        min_value=1,
        max_value=5,
        step=1
    )

    review = st.text_area("Enter your Review")

    submit = st.button("Submit Review")

    if submit:

        if name.strip() == "":
            st.error("⚠ Name is required to submit rating and review.")

        elif review.strip() == "":
            st.error("⚠ Please write a review before submitting.")

        else:
            cursor.execute(
                "INSERT INTO books (name, selected_book, rating, review) VALUES (%s,%s,%s,%s)",
                (name, selected_book, rating, review)
            )

            connection.commit()

            st.success(f"✅ **Dear {name}, your review has been saved!**")

    # ---------- SHOW REVIEWS ----------
    st.subheader("📜 All Reviews")

    cursor.execute("SELECT name, selected_book, rating, review FROM books ORDER BY rating DESC")
    reviews = cursor.fetchall()

    reviews_df = pd.DataFrame(
        reviews,
        columns=["Name", "Book", "Rating", "Review"]
    )

    st.dataframe(reviews_df)

    # ---------- TOP RATED BOOKS ----------
    st.subheader("⭐ Top Rated Books")

    cursor.execute("""
    SELECT selected_book, AVG(rating) as avg_rating
    FROM books
    GROUP BY selected_book
    ORDER BY avg_rating DESC
    LIMIT 10
    """)

    top_books = cursor.fetchall()

    top_books_df = pd.DataFrame(
        top_books,
        columns=["Book", "Average Rating"]
    )

    st.dataframe(top_books_df)

    # ---------- RATING CHART ----------
    st.subheader("📊 Rating Distribution")

    cursor.execute("SELECT rating FROM books")
    ratings = cursor.fetchall()

    rating_df = pd.DataFrame(ratings, columns=["Rating"])

    if not rating_df.empty:

        fig, ax = plt.subplots()

        rating_df["Rating"].value_counts().sort_index().plot(
            kind="bar",
            ax=ax
        )

        ax.set_xlabel("Rating")
        ax.set_ylabel("Count")

        st.pyplot(fig)
