# scrape-sg-govt-email-domains

Scraper to pull all Singapore government email domains from https://www.sgdi.gov.sg contacts list

## Overview

This Python web scraper uses Selenium and BeautifulSoup to extract all unique `@*.gov.sg` email domains from the Singapore Government Developer Portal (SGDI).

The scraper works by:
1. Loading the search results page at https://www.sgdi.gov.sg/search-results?term=.gov.sg
2. Progressively calling the JavaScript function `LoadData(n)` where `n` is the iteration number
3. Extracting email domains from the element with ID containing "SearchResult" after each load
4. Collecting unique domains until no new data is found

## Requirements

- Python 3.7+
- Chrome browser (for Selenium WebDriver)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/WHKcoderox/scrape-sg-govt-email-domains.git
cd scrape-sg-govt-email-domains
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:
```bash
python scraper.py
```

The scraper will:
- Display progress as it loads each batch of data
- Show newly discovered email domains
- Save results to `email_domains.txt` (one domain per line)
- Save results to `email_domains.json` (JSON array format)

## Output

The scraper generates two output files:

- `email_domains.txt`: Plain text file with one email domain per line
- `email_domains.json`: JSON array of email domains for programmatic use

## How it Works

The scraper uses:
- **Selenium WebDriver**: To execute JavaScript and interact with the dynamic webpage
- **BeautifulSoup**: To parse HTML and extract email addresses
- **Regular Expressions**: To identify and extract `@*.gov.sg` email domains

The infinite loop automatically terminates when:
- No new domains are found for 3 consecutive iterations
- The maximum iteration limit is reached (default: 1000)
- A JavaScript error occurs (e.g., `LoadData` function not available)

## Customization

You can modify the scraper behavior by editing `scraper.py`:

- Change `max_iterations` parameter to adjust the maximum number of loads
- Modify the email pattern in `extract_email_domains()` to match different formats
- Adjust wait times if the page loads slowly

## License

MIT
