import json
import requests
from bs4 import BeautifulSoup

# 1. DOWNLOADER
#THE VISIT: Go to the website
def downloader(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
             return None
    except:
        return None
# 2 & 3. SCRAPER & EXTRACTOR
def extractor(html):
    soup = BeautifulSoup(html, 'html.parser')
    name = 'Unknown Agent'
    # Example: Extracting the title of the research page
    if soup.h1:
        name = soup.h1.get_text().strip()
    elif soup.title :
        name = soup.title.string.strip()
    else:
        print("Unknown Agent")
    return {"name": name}

# 4. FILTER
def filter_data(data):
    # If name is not "Unknown Agent", return the data. Otherwise, return nothing.
    if data['name'] != "Unknown Agent":
        return data
# 5. STORAGE
def storage(data_list):
    with open('clinical_agents.json', 'w') as f:
        json.dump(data_list, f, indent=4)

# --- MAIN EXECUTION ---
urls = [
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
] # Add your 100 URLs here

final_results = []
for link in urls:
    # 1. Get the website code
    raw_html = downloader(link)
    # 2. If the website opens successfully:
    if raw_html:
        extracted = extractor(raw_html)
        filtered = filter_data(extracted)
        # 3. If the data is valid, add to list and SHOW IT NOW
        if filtered:
            final_results.append(filtered)
            # THIS LINE SHOWS THE OUTPUT YOU WANT:
            print(f"LINK: {link} ---> NAME: {filtered['name']}")

storage(final_results)
print(f"Successfully processed {len(final_results)} agents!")
print("All done! Check your results.json file.")
