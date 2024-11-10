import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import openai

# Set up OpenAI API Key (use environment variables for production)
openai.api_key = "YOUR_OPENAI_API_KEY"

def get_top_companies(industry, country):
    # Use OpenAI API to get a list of leading companies
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"List the top companies in the {industry} industry in {country}, and provide their career page URLs.",
        max_tokens=150
    )
    # Extract company names and URLs from response
    companies = response['choices'][0]['text'].strip().split("\n")
    return companies

def scrape_jobs(company_url, keywords):
    jobs = []
    try:
        response = requests.get(company_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        job_elements = soup.find_all('div', class_='job-listing')  # Adjust selector as needed
        for job_elem in job_elements:
            title = job_elem.find('h2').text.strip() if job_elem.find('h2') else 'No Title'
            description = job_elem.find('p').text.strip() if job_elem.find('p') else 'No Description'
            
            if any(keyword.lower() in description.lower() for keyword in keywords):
                jobs.append({'Title': title, 'Description': description, 'URL': company_url})
    except Exception as e:
        st.error(f"Error scraping {company_url}: {e}")
    return jobs

# Streamlit UI
st.title("Corporate Job Scraper")

# User Inputs for Industry, Country, and Keywords
industry = st.text_input("Enter Industry", "Technology")
country = st.text_input("Enter Country", "USA")
keywords = st.text_input("Enter keywords for job search (comma-separated)", "data analyst, pricing, marketing").split(',')

if st.button("Fetch Top Companies and Start Scraping"):
    companies = get_top_companies(industry, country)
    st.write(f"Top companies in {industry} in {country}:")
    for company in companies:
        st.write(company)
    
    # Scraping each company's career page
    all_jobs = []
    for company in companies:
        company_name, career_url = company.split(",")  # Adjust based on API response format
        st.write(f"Scraping {company_name}...")
        jobs = scrape_jobs(career_url, keywords)
        all_jobs.extend(jobs)
    
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        st.write(f"Found {len(df)} jobs matching criteria.")
        st.dataframe(df)
        csv = df.to_csv(index=False)
        st.download_button("Download as CSV", data=csv, file_name="jobs.csv", mime="text/csv")
    else:
        st.write("No jobs found matching criteria.")