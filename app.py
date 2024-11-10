import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Function to scrape jobs from a given company's job page
def scrape_jobs(company_url, keywords):
    jobs = []
    
    try:
        response = requests.get(company_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Example placeholder selectors; replace these with the real ones from the target websites
        job_elements = soup.find_all('div', class_='job-listing')  # Adjust class name based on actual site structure
        
        for job_elem in job_elements:
            title = job_elem.find('h2').text.strip() if job_elem.find('h2') else 'No Title'
            description = job_elem.find('p').text.strip() if job_elem.find('p') else 'No Description'
            
            # Keyword filtering
            if any(keyword.lower() in description.lower() for keyword in keywords):
                jobs.append({
                    'Title': title,
                    'Description': description,
                    'URL': company_url  # Add job-specific URL if available
                })
    except Exception as e:
        st.error(f"Error scraping {company_url}: {e}")
    
    return jobs

# Streamlit UI
st.title("Corporate Job Scraper")
st.write("Scrape jobs from specific corporate websites by keyword.")

# Inputs
company_url = st.text_input("Enter company career page URL", "https://example.com/careers")  # Replace with actual example
keywords = st.text_input("Enter keywords for job search (comma-separated)", "data analyst, pricing, marketing").split(',')

# Start scraping
if st.button("Start Scraping"):
    st.write("Scraping jobs, please wait...")
    job_data = scrape_jobs(company_url, keywords)
    
    # Display results
    if job_data:
        df = pd.DataFrame(job_data)
        st.write(f"Found {len(df)} jobs matching criteria.")
        st.dataframe(df)
        
        # CSV download
        csv = df.to_csv(index=False)
        st.download_button("Download as CSV", data=csv, file_name="jobs.csv", mime="text/csv")
    else:
        st.write("No jobs found matching criteria.")

# Rate limiter to avoid IP blocking
time.sleep(1)  # Adjust delay as needed for actual use