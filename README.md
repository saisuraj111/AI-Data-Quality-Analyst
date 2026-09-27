# 📊 AI Data Quality Analyst

A beginner-friendly data analysis and data quality application built with **Python, Pandas and Streamlit**.

The application allows users to upload a CSV dataset and automatically analyse its structure, data quality and basic statistical insights through an interactive web interface.

## 🚀 Features

* Upload CSV datasets
* Automatically detect numeric and categorical columns
* Detect date columns
* Display dataset size and structure
* Check missing values
* Detect duplicate rows
* Generate numeric data statistics
* Analyse categorical fields
* Detect potential numerical anomalies using the IQR method
* Generate automatic dataset insights
* Display business metrics when relevant fields are available
* Ask natural-language questions about the uploaded dataset

## 🛠️ Technologies Used

* Python
* Pandas
* Streamlit
* Git
* GitHub

## 📂 Project Structure

```text
AI Data Quality Analyst/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
└── sample_data/
    ├── Iris.csv
    └── samplesuperstore.csv
```

## ▶️ How to Run

### 1. Clone the repository

Open PowerShell or Command Prompt and run:

```bash
git clone https://github.com/saisuraj111/AI-Data-Quality-Analyst.git
```

### 2. Open the project folder

```bash
cd AI-Data-Quality-Analyst
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 5. Install the required packages

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 📊 Data Quality Checks

The application automatically checks uploaded datasets for:

* Missing values
* Duplicate rows
* Data types
* Unique values
* Potential numerical anomalies

Anomaly detection uses the **Interquartile Range (IQR)** method.

An anomaly represents a statistically unusual value and does not necessarily mean the data is incorrect.

## 📈 Dataset Analysis

The application automatically generates:

* Dataset dimensions
* Numeric column statistics
* Categorical column summaries
* Most common categorical values
* Numeric anomaly counts
* Missing-value information
* Duplicate-row information

For datasets containing relevant business fields such as `Sales`, `Profit` and `Quantity`, the application also displays business metrics and charts.

## 💬 Example Questions

Users can ask questions about the uploaded dataset, such as:

* How many rows are there?
* How many columns are there?
* What is the average Sales?
* What is the maximum Profit?
* What is the minimum Age?
* What is the most common Species?
* Are there any missing values?
* Are there any duplicate rows?

## 🧪 Example Datasets

The application has been tested with different CSV datasets, including:

* Sample Superstore
* Iris

This demonstrates that the application can perform basic profiling and analysis across different dataset structures.

## 📸 Application Screenshots


![Dataset Overview](Screenshots/Screenshot%202026-09-27%20155426.png)

![Data Quality Analysis](Screenshots/Screenshot%202026-09-27%20155614.png)

![Natural-Language Query](Screenshots/Screenshot%202026-09-27%20155848.png)

## 🎯 Project Purpose

This project was developed to demonstrate practical experience with:

* Data quality analysis
* Exploratory data analysis
* Python and Pandas
* Data profiling
* Basic statistical analysis
* Data validation
* Interactive data applications
* Natural-language data querying

## 🔍 Data Quality Approach

The application combines automated profiling with rule-based analysis.

The workflow is:

```text
CSV Upload
     ↓
Dataset Profiling
     ↓
Data Quality Checks
     ↓
Statistical Analysis
     ↓
Anomaly Detection
     ↓
Dataset Insights
     ↓
Natural-Language Questions
```

## 👨‍💻 Author

**Sai Suraj Durgumahanti**

MSc Computer Science (Data Science)
TU Dublin
