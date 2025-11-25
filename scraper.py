#!/usr/bin/env python3
"""
Singapore Government Email Domain Scraper

This script scrapes https://www.sgdi.gov.sg/search-results?term=.gov.sg
to extract all unique @*.gov.sg email domains.

The scraper progressively loads data by calling the JavaScript LoadData(n) function
and extracts email domains from the SearchResult element.
"""

import json
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import JavascriptException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def setup_driver():
    """Set up and return a Selenium WebDriver with appropriate options."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        raise RuntimeError(
            "Failed to initialize Chrome WebDriver. "
            "Please ensure Chrome/Chromium and ChromeDriver are installed and in your PATH. "
            f"Error: {e}"
        )


def extract_email_domains(html_content):
    """
    Extract unique @*.gov.sg email domains from HTML content.

    Args:
        html_content: HTML string to parse

    Returns:
        set: Set of unique email domains found
    """
    soup = BeautifulSoup(html_content, "lxml")

    # Pattern to match email addresses with .gov.sg domain
    email_pattern = r"@[\w\.\-]+\.gov\.sg"

    # Extract all text and find email domains
    text = soup.get_text()
    matches = re.findall(email_pattern, text, re.IGNORECASE)

    # Return unique domains (normalized to lowercase)
    return set(domain.lower() for domain in matches)


def scrape_govt_email_domains(
    url="https://www.sgdi.gov.sg/search-results?term=.gov.sg", max_iterations=10_000
):
    """
    Scrape Singapore government email domains from the SGDI website.

    Args:
        url: URL to scrape (default: SGDI search results for .gov.sg)
        max_iterations: Maximum number of LoadData iterations to prevent infinite loops

    Returns:
        set: Set of unique email domains found
    """
    driver = setup_driver()
    all_domains = set()

    try:
        print(f"Loading initial page: {url}")
        driver.get(url)

        # CSS selector for TotalResult elements
        CSS_SELECTOR = "*[id*='TotalResult']"

        # Maximum time to wait (in seconds)
        WAIT_TIME_SECONDS = 15

        # Initialize the WebDriverWait object once
        wait = WebDriverWait(driver, WAIT_TIME_SECONDS)

        iteration = 1
        consecutive_no_new_data = 0
        max_no_new_data = 1000  # Stop if no new data for 1000 consecutive iterations

        while iteration <= max_iterations:
            print(f"\nIteration {iteration}:")

            try:
                # Execute LoadData(n) JavaScript function
                print(f"  Calling LoadData({iteration})...")
                driver.execute_script(f"LoadData({iteration});")

                # Wait until the element matching the CSS selector is VISIBLE on the page
                wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, CSS_SELECTOR))
                )

                # Get the page source and look for elements with ID containing SearchResult
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, "lxml")

                # Find elements with ID containing "SearchResult" or similar
                search_result_elements = soup.find_all(
                    id=re.compile(r"SearchResult", re.IGNORECASE)
                )

                # If no specific SearchResult elements found, look for common result containers
                if not search_result_elements:
                    # Try alternative selectors for search results
                    search_result_elements = soup.find_all(
                        class_=re.compile(r"result|search", re.IGNORECASE)
                    )

                # Extract domains from the search results
                iteration_domains = set()
                if search_result_elements:
                    for element in search_result_elements:
                        domains = extract_email_domains(str(element))
                        iteration_domains.update(domains)
                else:
                    # Last resort: parse entire page but this may include irrelevant domains
                    print(
                        "  Warning: No specific search result elements found, parsing entire page"
                    )
                    iteration_domains = extract_email_domains(page_source)

                # Check for new domains
                new_domains = iteration_domains - all_domains

                if new_domains:
                    print(f"  Found {len(new_domains)} new domain(s)")
                    for domain in sorted(new_domains):
                        print(f"    {domain}")
                    all_domains.update(new_domains)
                    consecutive_no_new_data = 0
                else:
                    print(f"  No new domains found")
                    consecutive_no_new_data += 1

                    if consecutive_no_new_data >= max_no_new_data:
                        print(
                            f"\nNo new data for {max_no_new_data} consecutive iterations. Stopping."
                        )
                        break

                iteration += 1

            except JavascriptException as e:
                print(f"  JavaScript error: {e}")
                print("  LoadData function might not be available. Stopping.")
                break
            except TimeoutException:
                print(f"  Timeout waiting for content to load")
                consecutive_no_new_data += 1
                if consecutive_no_new_data >= max_no_new_data:
                    print(f"\nTimeout threshold reached. Stopping.")
                    break
                iteration += 1
            except Exception as e:
                print(f"  Error during iteration: {e}")
                break

        print(f"\n{'='*60}")
        print(f"Scraping complete!")
        print(f"Total unique email domains found: {len(all_domains)}")
        print(f"{'='*60}")

        return all_domains

    finally:
        driver.quit()


def save_results(domains, output_file="email_domains.txt"):
    """
    Save the scraped email domains to a file.

    Args:
        domains: Set of email domains
        output_file: Output filename
    """
    with open(output_file, "w") as f:
        for domain in sorted(domains):
            f.write(f"{domain}\n")

    print(f"\nResults saved to: {output_file}")


def main():
    """Main entry point for the scraper."""
    print("Singapore Government Email Domain Scraper")
    print("=" * 60)

    # Run the scraper
    domains = scrape_govt_email_domains()

    # Display results
    if domains:
        print("\nAll unique email domains:")
        for domain in sorted(domains):
            print(f"  {domain}")

        # Save to file
        save_results(domains)

        # Also save as JSON for programmatic use
        with open("email_domains.json", "w") as f:
            json.dump(sorted(list(domains)), f, indent=2)
        print("Results also saved to: email_domains.json")
    else:
        print("\nNo email domains found.")


if __name__ == "__main__":
    main()
