import re           # helps us search for patterns in text
import time         # lets us pause the program (sleep)
import random       # lets us pick random numbers
import requests     # lets us download web pages
from datetime import datetime        # lets us track time
from urllib.parse import urlparse    # breaks a URL into parts
from urllib.robotparser import RobotFileParser  # reads robots.txt rules

# =============================================================================
# STEP 1 — DATA
# These are the words and phrases we look for in Indian medical text
# =============================================================================

# Famous Indian hospitals
HOSPITALS = [
    "AIIMS",
    "PGIMER",
    "JIPMER",
    "Apollo Hospital",
    "Fortis Hospital"
]

# Short forms used by Indian doctors
ABBREVIATIONS = [
    "s/o",    # son of
    "d/o",    # daughter of
    "c/o",    # complains of
    "h/o",    # history of
    "k/c/o",  # known case of
    "NAD",    # no abnormality detected
    "MLC",    # medico legal case
    "DAMA"    # discharged against medical advice
]

# Common phrases in Indian medical notes
PHRASES = [
    "came with complaints of",
    "known case of",
    "advised to",
    "per abdomen"
]

# Regex patterns — flexible text matching rules
PATTERNS = [
    r"\b(s/o|d/o|w/o)\s+\w+",       # matches "s/o Ramesh" style
    r"\bcame with complaints of\b",   # matches exact phrase
    r"\bper\s+(abdomen|speculum)\b",  # matches "per abdomen" style
    r"\b(DAMA|LAMA)\b"               # matches discharge codes
]


# =============================================================================
# STEP 2 — INDIAN TEXT DETECTOR
# This function reads text and gives it a score.
# Higher score = more likely to be Indian medical text.
# Score 2 or above = classified as Indian.
# =============================================================================

def is_indian(text):
    # Convert to lowercase so matching is easier
    text_lower = text.lower()

    # Start score at zero
    score = 0

    # Add 2 points for every hospital name found
    score = score + sum(2 for h in HOSPITALS if h.lower() in text_lower)

    # Add 1 point for every abbreviation found
    score = score + sum(
        1 for a in ABBREVIATIONS
        if re.search(r"\b" + re.escape(a) + r"\b", text, re.IGNORECASE)
    )

    # Add 2 points for every phrase found
    score = score + sum(2 for p in PHRASES if p in text_lower)

    # Add 3 points for every pattern matched
    score = score + sum(3 for p in PATTERNS if re.search(p, text_lower))

    # Return True if score is 2 or more, plus the score itself
    return score >= 2, score


# =============================================================================
# STEP 3 — TOKEN BUCKET
# Think of this like a jar of tokens (tickets).
# The jar holds 6 tokens. One token = one allowed request.
# Tokens refill slowly over time (1 every 10 seconds).
# If jar is empty, we wait until a token appears.
# This makes sure we never send more than 6 requests per minute.
# =============================================================================

class TokenBucket:

    def __init__(self):
        self.tokens = 6.0              # start with full jar
        self.last_checked = datetime.now()  # track when we last refilled

    def take_one_token(self):
        # Keep trying until we get a token
        while True:
            # How many seconds have passed since last check?
            now = datetime.now()
            seconds_passed = (now - self.last_checked).total_seconds()

            # Add new tokens based on time passed (1 token per 10 seconds)
            self.tokens = min(6, self.tokens + seconds_passed / 10)
            self.last_checked = now

            # If we have at least 1 token, take it and leave
            if self.tokens >= 1:
                self.tokens = self.tokens - 1
                return

            # No token yet — wait a tiny bit and try again
            time.sleep(0.1)


# =============================================================================
# STEP 4 — POLITE CRAWLER
# This class downloads web pages politely:
#   1. Checks robots.txt before crawling
#   2. Waits between visits to the same website
#   3. Retries if something goes wrong
# =============================================================================

class Crawler:

    def __init__(self):
        self.bucket = TokenBucket()   # our token jar from Step 3
        self.last_visit = {}          # remembers when we last visited each site
        self.robots_rules = {}        # stores robots.txt rules per site

        # Set up HTTP session with a clear bot name
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "Indian-Clinical-Bot/2.0"

    # ── Check if crawling is allowed ──────────────────────────────────────

    def is_allowed(self, url):
        # Get just the domain part, e.g. "https://example.com"
        parts = urlparse(url)
        domain = parts.scheme + "://" + parts.netloc

        # Only fetch robots.txt if we haven't seen this domain before
        if domain not in self.robots_rules:
            parser = RobotFileParser()
            try:
                response = self.session.get(domain + "/robots.txt", timeout=10)
                if response.ok:
                    parser.parse(response.text.splitlines())
                else:
                    # Could not find robots.txt — block everything to be safe
                    parser.parse(["User-agent: *", "Disallow: /"])
            except Exception:
                # Network error — block everything to be safe
                parser.parse(["User-agent: *", "Disallow: /"])

            # Save the rules for this domain
            self.robots_rules[domain] = parser

        # Ask the parser: can our bot visit this URL?
        return self.robots_rules[domain].can_fetch("Indian-Clinical-Bot/2.0", url)

    # ── Wait politely before visiting ────────────────────────────────────

    def wait_before_visit(self, url):
        # Use token bucket for global rate limiting
        self.bucket.take_one_token()

        # Also enforce per-site delay
        domain = urlparse(url).netloc

        if domain in self.last_visit:
            # How many seconds since we last visited this site?
            seconds_since_last = (datetime.now() - self.last_visit[domain]).total_seconds()

            # We want to wait 7 to 10 seconds between visits
            minimum_wait = 5 + random.uniform(2, 5)

            # If not enough time has passed, sleep the rest
            if seconds_since_last < minimum_wait:
                time.sleep(minimum_wait - seconds_since_last)

        # Record that we are visiting now
        self.last_visit[domain] = datetime.now()

    # ── Fetch a page with retries ─────────────────────────────────────────

    def fetch(self, url):
        # Try up to 3 times
        for attempt in range(3):
            try:
                self.wait_before_visit(url)
                response = self.session.get(url, timeout=30)

                # Website said "too many requests" — wait and retry
                if response.status_code == 429:
                    wait_time = int(response.headers.get("Retry-After", 60))
                    print("Rate limited. Waiting", wait_time, "seconds...")
                    time.sleep(wait_time)
                    continue

                # Server error — wait longer each time (60s, 120s, 240s)
                if response.status_code >= 500:
                    wait_time = 60 * (2 ** attempt)
                    print("Server error. Waiting", wait_time, "seconds...")
                    time.sleep(wait_time)
                    continue

                # Success — return the response
                return response

            except Exception as error:
                print("Something went wrong:", error)
                time.sleep(60 * (2 ** attempt))

        # All 3 attempts failed
        print("Could not fetch:", url)
        return None


# =============================================================================
# STEP 5 — MAIN PIPELINE
# Ties everything together:
#   1. Check if allowed
#   2. Fetch page
#   3. Score it
#   4. Save if Indian
# =============================================================================

def run(urls, max_samples=100, output_file="results.txt"):
    crawler = Crawler()
    collected = 0

    for url in urls:
        # Stop if we have enough samples
        if collected >= max_samples:
            break

        print("\nVisiting:", url)

        # Skip if robots.txt blocks us
        if crawler.is_allowed(url) == False:
            print("Blocked by robots.txt — skipping")
            continue

        # Download the page
        response = crawler.fetch(url)

        # Skip if download failed
        if response is None or response.ok == False:
            print("Could not download page — skipping")
            continue

        # Check if it is Indian medical text
        indian, score = is_indian(response.text)
        print("Score:", score, "| Indian:", indian)

        # Save to file if Indian
        if indian:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write("# score=" + str(score) + "\n")
                f.write(response.text[:500])   # save first 500 characters
                f.write("\n\n")
            print("Saved!")

        collected = collected + 1

    print("\nFinished. Total collected:", collected)


# =============================================================================
# RUN THE PROGRAM
# =============================================================================

if __name__ == "__main__":
    my_urls = [
    "https://www.iqvia.com", "https://www.iconplc.com", "https://www.parexel.com",
    "https://www.ppd.com", "https://www.syneoshealth.com", "https://www.fortrea.com",
    "https://www.medpace.com", "https://www.criver.com", "https://www.wuxiapptec.com",
    "https://www.labcorp.com", "https://www.novartis.com/clinicaltrials",
    "https://www.pfizer.com/science/clinical-trials", "https://www.merck.com/research/clinical-trials",
    "https://www.gsk-studyregister.com", "https://www.roche.com/innovation/clinical-trials",
    "https://www.sanofi.com/en/science-and-innovation/clinical-trials",
    "https://www.janssen.com/clinical-trials", "https://www.astrazenecaclinicaltrials.com",
    "https://www.lillytrialguide.com", "https://clinicaltrials.bayer.com", "https://www.tigermed.net",
    "https://www.sgs.com/en/health-science", "https://www.eurofins.com", "https://www.psi-cro.com",
    "https://www.clinchoice.com", "https://www.worldwide.com", "https://www.ctifacts.com",
    "https://www.caidya.com", "https://premier-research.com", "https://veranex.com",
    "https://qservecro.com", "https://www.mcra.com", "https://velocityclinical.com",
    "https://clinexel.com", "https://www.accutestglobal.com", "https://www.lambdarc.com",
    "https://www.aragen.com", "https://www.veedacr.com", "https://www.siroclinpharm.com",
    "https://www.jssresearch.com", "https://www.navitaslifesciences.com", "https://www.syncorphealth.com",
    "https://www.celerion.com", "https://www.biopharmaservices.com", "https://www.frontagelab.com",
    "https://www.pharmaron.com", "https://www.altasciences.com", "https://www.propharmagroup.com",
    "https://www.clinilabs.com", "https://www.linical.com", "https://aptusclinical.com",
    "https://www.lotuscr.com", "https://www.advancedclinical.com", "https://www.criteriuminc.com",
    "https://ctri.nic.in", "https://clinicaltrials.gov", "https://www.clinicaltrialsregister.eu",
    "https://trialsearch.who.int", "https://kcrcro.com", "https://www.ergomedplc.com",
    "https://medelis.com", "https://www.syntactx.com", "https://www.georgeclinical.com",
    "https://novotech-cro.com", "https://www.asco.org", "https://www.dana-farber.org/research",
    "https://www.mayo.edu/research/clinical-trials", "https://www.cerexa.com",
    "https://www.cognizant.com/life-sciences-technology-solutions",
    "https://www.accenture.com/in-en/industries/life-sciences-index",
    "https://www.wipro.com/life-sciences", "https://www.tcs.com/life-sciences",
    "https://www.zyduslife.com", "https://sunpharma.com", "https://www.drreddys.com",
    "https://www.lupin.com", "https://www.cipla.com", "https://www.biocon.com",
    "https://www.aurobindo.com", "https://www.torrentpharma.com", "https://www.alkemlabs.com",
    "https://www.glenmarkpharma.com", "https://www.clinven.com", "https://www.sandoz.com",
    "https://www.boehringer-ingelheim.com", "https://clinicaltrials.takeda.com", "https://www.amgen.com",
    "https://www.gilead.com", "https://www.bms.com", "https://www.abbvieclinicaltrials.com",
    "https://www.biogen.com", "https://www.vrtx.com", "https://www.regeneron.com",
    "https://www.modernatx.com/research/clinical-trials", "https://biontech.com",
    "https://www.clinigengroup.com", "https://www.advarra.com", "https://www.wcgclinical.com",
    "https://www.medidata.com", "https://www.veeva.com", "https://www.oracle.com/industries/life-sciences",
    "https://www.arisglobal.com", "https://www.viedoc.com", "https://www.castoredc.com",
    "https://www.clincapture.com"
    ]
    run(my_urls)