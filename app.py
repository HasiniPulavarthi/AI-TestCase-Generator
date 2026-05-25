import streamlit as st
from google import genai
import pandas as pd
import json
from io import BytesIO
import time

# -------------------------------
# Gemini API
# -------------------------------

client = genai.Client(
<<<<<<< HEAD
    api_key="AIzaSyAkaZSZjsQr6cHtM_apNAJ0jvuVuilzLfU"
=======
    api_key="Gemini_API_Key"
>>>>>>> dda169716e0320eedf243481602aef046d06e129
)

# -------------------------------
# App Title
# -------------------------------

st.title("AI Test Case Generator for QA Teams")

# -------------------------------
# Upload/Input section
# -------------------------------

uploaded_file = st.file_uploader(
    "Upload requirement file (.txt)",
    type=["txt"]
)

if uploaded_file:

    requirement = uploaded_file.read().decode("utf-8")

    st.subheader("Requirement Loaded")
    st.write(requirement)

else:

    requirement = st.text_area(
        "Enter Requirement"
    )

# -------------------------------
# Generate button
# -------------------------------

if st.button("Generate Test Cases"):

    if requirement.strip() == "":

        st.warning(
            "Please enter/upload requirements"
        )

    else:

        try:

            prompt = f"""
Generate test cases for:

{requirement}

Rules:
- Functional = successful scenarios
- Negative = invalid/error scenarios
- Edge = boundary conditions
- Add Priority (High/Medium/Low)

Return ONLY JSON in this format:

[
 {{
   "Test_ID":"TC001",
   "Category":"Functional",
   "Priority":"High",
   "Test_Case":"Sample"
 }}
]

Do not include explanations or markdown.
"""

            with st.spinner(
                "Generating AI test cases..."
            ):

                response = None

                for attempt in range(3):

                    try:

                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt
                        )

                        break

                    except Exception as e:

                        if "503" in str(e):

                            st.warning(
                                f"Server busy. Retrying ({attempt+1}/3)"
                            )

                            time.sleep(3)

                        else:
                            raise e

                if response is None:

                    st.error(
                        "Gemini server busy. Try again later."
                    )

                    st.stop()

            # Clean output
            clean_text = (
                response.text
                .replace("```json", "")
                .replace("```", "")
            )

            data = json.loads(clean_text)

            df = pd.DataFrame(data)

            # Save dataframe
            st.session_state["df"] = df

            st.success(
                "Test cases generated successfully!"
            )

        except Exception as e:

            st.error(
                f"Error: {e}"
            )

# -------------------------------
# Display only if data exists
# -------------------------------

if "df" in st.session_state:

    df = st.session_state["df"]

    # -------------------------------
    # Summary
    # -------------------------------

    st.subheader("Summary")

    total = len(df)

    functional = len(
        df[df["Category"] == "Functional"]
    )

    negative = len(
        df[df["Category"] == "Negative"]
    )

    edge = len(
        df[df["Category"] == "Edge"]
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total",
        total
    )

    col2.metric(
        "Functional",
        functional
    )

    col3.metric(
        "Negative",
        negative
    )

    col4.metric(
        "Edge",
        edge
    )

    # -------------------------------
    # Filter
    # -------------------------------

    st.subheader("Filter")

    category_filter = st.selectbox(
        "Filter by Category",
        [
            "All",
            "Functional",
            "Negative",
            "Edge"
        ]
    )

    filtered_df = df.copy()

    if category_filter != "All":

        filtered_df = filtered_df[
            filtered_df["Category"] ==
            category_filter
        ]

    # -------------------------------
    # Table
    # -------------------------------

    st.subheader(
        "Generated Test Cases"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=400
    )

    # -------------------------------
    # CSV Download
    # -------------------------------

    csv = filtered_df.to_csv(
        index=False
    )

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="test_cases.csv",
        mime="text/csv"
    )

    # -------------------------------
    # Excel Download
    # -------------------------------

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        filtered_df.to_excel(
            writer,
            index=False
        )

    excel_data = output.getvalue()

    st.download_button(
        label="Download Excel",
        data=excel_data,
        file_name="test_cases.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
