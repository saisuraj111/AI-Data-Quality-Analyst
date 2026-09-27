import re
import streamlit as st
import pandas as pd


# ---------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Data Quality Analyst",
    page_icon="📊",
    layout="wide"
)


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def clean_name(name):
    """Make column names easier to match with user questions."""
    name = str(name)
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    name = name.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", name).strip().lower()


def find_column(question, columns):
    """Find a column mentioned in a natural-language question."""
    question = clean_name(question)

    # Exact/partial phrase match
    for column in columns:
        column_clean = clean_name(column)

        if column_clean in question:
            return column

    # Word-based matching
    best_column = None
    best_score = 0

    question_words = set(question.split())

    for column in columns:
        column_words = set(clean_name(column).split())

        if not column_words:
            continue

        score = len(question_words & column_words) / len(column_words)

        if score > best_score:
            best_score = score
            best_column = column

    if best_score >= 0.5:
        return best_column

    return None


def detect_date_columns(df):
    """Detect columns that mostly contain dates."""
    date_columns = []

    for column in df.columns:
        if df[column].isna().all():
            continue

        converted = pd.to_datetime(df[column], errors="coerce")
        valid_ratio = converted.notna().mean()

        if valid_ratio >= 0.8:
            date_columns.append(column)

    return date_columns


def get_iqr_anomalies(df, column):
    """Return the number of IQR-based anomalies."""
    series = df[column].dropna()

    if len(series) < 4:
        return 0

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:
        return 0

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    return int(((series < lower) | (series > upper)).sum())


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

st.title("📊 AI Data Quality Analyst")
st.write(
    "Upload a CSV file to automatically profile, "
    "check and analyse your data."
)


# ---------------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

if uploaded_file is None:
    st.info("👆 Upload a CSV file to get started.")
    st.stop()


try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Could not read the CSV file: {e}")
    st.stop()


if df.empty:
    st.warning("The uploaded CSV contains no data.")
    st.stop()


# ---------------------------------------------------------
# COLUMN DETECTION
# ---------------------------------------------------------

numeric_columns = df.select_dtypes(
    include="number"
).columns.tolist()

text_columns = df.select_dtypes(
    include=["object", "category"]
).columns.tolist()

date_columns = detect_date_columns(df)


# ---------------------------------------------------------
# DATASET OVERVIEW
# ---------------------------------------------------------

st.header("📋 Dataset Overview")

total_missing = int(df.isna().sum().sum())
duplicate_rows = int(df.duplicated().sum())

col1, col2, col3, col4 = st.columns(4)

col1.metric("Rows", f"{len(df):,}")
col2.metric("Columns", len(df.columns))
col3.metric("Missing Values", f"{total_missing:,}")
col4.metric("Duplicate Rows", f"{duplicate_rows:,}")


# ---------------------------------------------------------
# DATA PREVIEW
# ---------------------------------------------------------

with st.expander("👀 View Data", expanded=False):
    st.dataframe(
        df.head(10),
        use_container_width=True
    )


# ---------------------------------------------------------
# DATA TYPES
# ---------------------------------------------------------

st.header("🔍 Automatic Data Profiling")

profile_col1, profile_col2, profile_col3 = st.columns(3)

with profile_col1:
    st.write("**Numeric Columns**")
    if numeric_columns:
        st.write(", ".join(numeric_columns))
    else:
        st.write("None detected")

with profile_col2:
    st.write("**Categorical Columns**")
    if text_columns:
        st.write(", ".join(text_columns))
    else:
        st.write("None detected")

with profile_col3:
    st.write("**Date Columns**")
    if date_columns:
        st.write(", ".join(date_columns))
    else:
        st.write("None detected")


# ---------------------------------------------------------
# DATA QUALITY
# ---------------------------------------------------------

st.header("✅ Data Quality Checks")

quality_data = []

for column in df.columns:
    quality_data.append({
        "Column": column,
        "Data Type": str(df[column].dtype),
        "Missing Values": int(df[column].isna().sum()),
        "Unique Values": int(df[column].nunique(dropna=True))
    })

quality_df = pd.DataFrame(quality_data)

st.dataframe(
    quality_df,
    use_container_width=True,
    hide_index=True
)

if total_missing == 0:
    st.success("✅ No missing values detected.")
else:
    st.warning(
        f"⚠️ {total_missing:,} missing values detected."
    )

if duplicate_rows == 0:
    st.success("✅ No duplicate rows detected.")
else:
    st.warning(
        f"⚠️ {duplicate_rows:,} duplicate rows detected."
    )


# ---------------------------------------------------------
# NUMERIC PROFILE
# ---------------------------------------------------------

if numeric_columns:

    st.header("🔢 Numeric Data Profile")

    numeric_profile = df[numeric_columns].describe().T

    numeric_profile = numeric_profile.rename(
        columns={
            "count": "Count",
            "mean": "Average",
            "std": "Std Dev",
            "min": "Minimum",
            "25%": "25%",
            "50%": "Median",
            "75%": "75%",
            "max": "Maximum"
        }
    )

    st.dataframe(
        numeric_profile.round(2),
        use_container_width=True
    )


# ---------------------------------------------------------
# CATEGORICAL PROFILE
# ---------------------------------------------------------

if text_columns:

    st.header("🏷️ Categorical Data Profile")

    categorical_data = []

    for column in text_columns:
        mode = df[column].mode(dropna=True)

        categorical_data.append({
            "Column": column,
            "Unique Values": df[column].nunique(
                dropna=True
            ),
            "Most Common Value": (
                mode.iloc[0] if not mode.empty else "N/A"
            )
        })

    categorical_df = pd.DataFrame(categorical_data)

    st.dataframe(
        categorical_df,
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------------------------
# ANOMALY DETECTION
# ---------------------------------------------------------

if numeric_columns:

    st.header("🚨 Anomaly Detection")

    anomaly_data = []

    for column in numeric_columns:
        anomalies = get_iqr_anomalies(df, column)

        anomaly_data.append({
            "Column": column,
            "Potential Anomalies": anomalies
        })

    anomaly_df = pd.DataFrame(anomaly_data)

    st.dataframe(
        anomaly_df,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Anomalies are detected using the IQR method. "
        "They indicate statistically unusual values, "
        "not necessarily incorrect data."
    )


# ---------------------------------------------------------
# GENERIC DATASET INSIGHTS
# ---------------------------------------------------------

st.header("💡 Dataset Insights")

insight_col1, insight_col2, insight_col3 = st.columns(3)

with insight_col1:
    st.metric(
        "Numeric Fields",
        len(numeric_columns)
    )

with insight_col2:
    st.metric(
        "Categorical Fields",
        len(text_columns)
    )

with insight_col3:
    st.metric(
        "Date Fields",
        len(date_columns)
    )


# Most common categorical value
if text_columns:

    st.subheader("Most Common Categories")

    category_data = []

    for column in text_columns:
        mode = df[column].mode(dropna=True)

        if not mode.empty:
            category_data.append({
                "Column": column,
                "Most Common Value": mode.iloc[0],
                "Count": int(
                    (df[column] == mode.iloc[0]).sum()
                )
            })

    if category_data:
        st.dataframe(
            pd.DataFrame(category_data),
            use_container_width=True,
            hide_index=True
        )


# ---------------------------------------------------------
# BUSINESS-SPECIFIC INSIGHTS
# ---------------------------------------------------------

if all(
    column in df.columns
    for column in ["Sales", "Profit", "Quantity"]
):

    st.subheader("💼 Business Metrics")

    sales = df["Sales"].sum()
    profit = df["Profit"].sum()
    quantity = df["Quantity"].sum()

    business_col1, business_col2, business_col3 = st.columns(3)

    business_col1.metric(
        "Total Sales",
        f"${sales:,.2f}"
    )

    business_col2.metric(
        "Total Profit",
        f"${profit:,.2f}"
    )

    business_col3.metric(
        "Total Quantity",
        f"{quantity:,.0f}"
    )

    if "Category" in df.columns:

        category_sales = (
            df.groupby("Category")["Sales"]
            .sum()
            .sort_values(ascending=False)
        )

        st.write("**Sales by Category**")

        st.bar_chart(category_sales)

    if "Region" in df.columns:

        region_sales = (
            df.groupby("Region")["Sales"]
            .sum()
            .sort_values(ascending=False)
        )

        st.write("**Sales by Region**")

        st.bar_chart(region_sales)


# ---------------------------------------------------------
# CHATBOT
# ---------------------------------------------------------

st.header("💬 Ask the Data Analyst")

question = st.text_input(
    "Ask a question about your dataset",
    placeholder=(
        "Examples: What is the average age? "
        "How many rows are there?"
    )
)

if question:

    questions = re.split(
        r"\?| and ",
        question.lower()
    )

    answered_any = False

    for single_question in questions:

        single_question = single_question.strip()

        if not single_question:
            continue

        answered = False

        # ---------------------------------------------
        # ROWS
        # ---------------------------------------------

        if (
            "how many rows" in single_question
            or "number of rows" in single_question
            or "row count" in single_question
        ):
            st.info(
                f"📊 The dataset contains "
                f"**{len(df):,} rows**."
            )
            answered = True

        # ---------------------------------------------
        # COLUMNS
        # ---------------------------------------------

        elif (
            "how many columns" in single_question
            or "number of columns" in single_question
        ):
            st.info(
                f"📊 The dataset contains "
                f"**{len(df.columns)} columns**."
            )
            answered = True

        # ---------------------------------------------
        # MISSING VALUES
        # ---------------------------------------------

        elif (
            "missing" in single_question
            or "null" in single_question
        ):
            st.info(
                f"⚠️ The dataset contains "
                f"**{total_missing:,} missing values**."
            )
            answered = True

        # ---------------------------------------------
        # DUPLICATES
        # ---------------------------------------------

        elif (
            "duplicate" in single_question
            or "duplicates" in single_question
        ):
            st.info(
                f"🔄 The dataset contains "
                f"**{duplicate_rows:,} duplicate rows**."
            )
            answered = True

        # ---------------------------------------------
        # NUMERIC COLUMN ANALYSIS
        # ---------------------------------------------

        else:

            matched_column = find_column(
                single_question,
                numeric_columns
            )

            if matched_column:

                values = df[matched_column].dropna()

                if values.empty:
                    st.warning(
                        f"No usable values found for "
                        f"**{matched_column}**."
                    )
                    answered = True

                elif (
                    "average" in single_question
                    or "mean" in single_question
                ):
                    st.info(
                        f"📈 Average {matched_column}: "
                        f"**{values.mean():,.2f}**"
                    )
                    answered = True

                elif "median" in single_question:

                    st.info(
                        f"📊 Median {matched_column}: "
                        f"**{values.median():,.2f}**"
                    )
                    answered = True

                elif (
                    "maximum" in single_question
                    or "max" in single_question
                    or "highest" in single_question
                ):
                    st.info(
                        f"🔝 Maximum {matched_column}: "
                        f"**{values.max():,.2f}**"
                    )
                    answered = True

                elif (
                    "minimum" in single_question
                    or "min" in single_question
                    or "lowest" in single_question
                ):
                    st.info(
                        f"🔻 Minimum {matched_column}: "
                        f"**{values.min():,.2f}**"
                    )
                    answered = True

                elif (
                    "total" in single_question
                    or "sum" in single_question
                ):
                    st.info(
                        f"➕ Total {matched_column}: "
                        f"**{values.sum():,.2f}**"
                    )
                    answered = True

                elif (
                    "standard deviation" in single_question
                    or "std" in single_question
                ):
                    st.info(
                        f"📐 Standard deviation of "
                        f"{matched_column}: "
                        f"**{values.std():,.2f}**"
                    )
                    answered = True

            # -----------------------------------------
            # CATEGORICAL COLUMN ANALYSIS
            # -----------------------------------------

            if not answered:

                matched_column = find_column(
                    single_question,
                    text_columns
                )

                if matched_column and (
                    "common" in single_question
                    or "most frequent" in single_question
                    or "popular" in single_question
                ):

                    mode = df[matched_column].mode(
                        dropna=True
                    )

                    if not mode.empty:
                        value = mode.iloc[0]
                        count = int(
                            (df[matched_column] == value).sum()
                        )

                        st.info(
                            f"🏷️ Most common "
                            f"{matched_column}: "
                            f"**{value}** "
                            f"({count:,} records)"
                        )
                        answered = True

            # -----------------------------------------
            # COLUMN LIST
            # -----------------------------------------

            if not answered and (
                "what columns" in single_question
                or "list columns" in single_question
                or "column names" in single_question
            ):
                st.info(
                    "📋 Columns: "
                    + ", ".join(df.columns)
                )
                answered = True

        # ---------------------------------------------
        # UNKNOWN QUESTION
        # ---------------------------------------------

        if not answered:
            st.warning(
                f"❓ I couldn't answer: "
                f"'{single_question}'"
            )
        else:
            answered_any = True

    # Helpful fallback
    if not answered_any:

        numeric_examples = ", ".join(
            numeric_columns[:5]
        )

        categorical_examples = ", ".join(
            text_columns[:5]
        )

        st.info(
            "Try asking about rows, columns, "
            "missing values, duplicates, "
            "averages, medians, minimums, "
            "maximums, totals or common values."
        )

        if numeric_examples:
            st.caption(
                f"🔢 Numeric fields: "
                f"{numeric_examples}"
            )

        if categorical_examples:
            st.caption(
                f"🏷️ Categorical fields: "
                f"{categorical_examples}"
            )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "AI Data Quality Analyst | "
    "Python • Pandas • Streamlit"
)