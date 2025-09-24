from setuptools import setup, find_packages

setup(
    name="impact_predictor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy==1.26.3",
        "pandas==2.1.4",
        "scikit-learn==1.3.2",
        "spacy==3.7.2",
        "textblob==0.17.1",
        "yfinance==0.2.36",
        "plotly==5.18.0",
        "joblib==1.3.2",
        "reportlab==4.0.8",
        "requests==2.31.0",
        "python-dateutil==2.8.2",
        "pytz==2023.3.post1"
    ],
    python_requires=">=3.8",
) 