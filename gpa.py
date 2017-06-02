# Version: 1.0.0
# sctigercat1

# Dependencies:
# powerapi (pip install https://github.com/powerapi/powerapi-python/zipball/master)
# beautifulsoup4 (pip install beautifulsoup4)

# Usage:
# gpa.py https://powerschool.example.com username password

# Intended for usage in South Carolina high schools to determine weighted and unweighted GPAs for students.
# This script currently does not support dual-enrollment or IB classes!

import powerapi
import base64, hashlib, hmac, re, time, urlparse, sys

from bs4 import BeautifulSoup

addr = sys.argv[1]
if not addr.endswith('/'):
    addr += '/'
uid = sys.argv[2]
pw = sys.argv[3]

ps = powerapi.core(addr)

success = False

while success is False:
    try:
        user = ps.auth(uid, pw)
        success = True
    except Exception, err:
        print "Whoops! Something went wrong with PowerAPI:", err
        print "Trying again..."
        time.sleep(4)

core = user.core
termtext = core.session.get(addr + "guardian/termgrades.html").text
matches = re.findall('<a href="termgrades.html(.*?)">(.*?)</a>', termtext)
terms = {}
# Get all history URLs
for match in matches:
    urldata = urlparse.parse_qs(match[0])
    terms[match[1]] = {k.lstrip('?'):v for k, v in urldata.iteritems()}

# Only account for the last 6 years of data: max - 6
mm = max([int(term[:2]) for term in terms.keys()])
latest = []
for k, v in terms.iteritems(): # todo shorten this?
    if k.startswith(str(mm)):
        latest.extend([k, v])
oldest = int(latest[1]['termid'][0][:2]) - 6 # back 6 years
urls = {}

for tid in range(oldest, oldest+7):
    atid = str(tid) + '00'
    ftdata = None

    for term, data in terms.iteritems():
        if data['termid'][0] == atid:
            ftdata = data

    if ftdata is not None:
        urls['termgrades.html?termid=%s&schoolid=%s' % (ftdata['termid'][0], ftdata['schoolid'][0])] = [ftdata['termid'][0], ftdata['schoolid'][0]]

grades = {'full': {'AP': {'old': [], 'new': []}, 'Honors': {'old': [], 'new': []}, 'Theory': {'old': [], 'new': []}},
    'half': {'AP': {'old': [], 'new': []}, 'Honors': {'old': [], 'new': []}, 'Theory': {'old': [], 'new': []}}
}

# get grades for each history URL
for url, data in urls.iteritems():
    print url
    time.sleep(3)
    ud = core.session.get(addr + 'guardian/' + url).text
    soup = BeautifulSoup(ud, 'html.parser')
    for elem in soup.find_all('tr'):
        if '1.00' in elem.get_text():
            weight = 'full'
        elif '0.50' in elem.get_text():
            weight = 'half'
        else:
            # Probably implies 0.00, which we can't count
            continue

        grade = elem.get_text().split('\n')[2]
        aclass = elem.get_text().split('\n')[1]
        # These are the likely cases for class identification
        if 'ap' in aclass.lower() and 'hn' not in aclass.lower() and 'honors' not in aclass.lower():
            classtype = 'AP'
        elif 'hn' in aclass.lower() or 'honors' in aclass.lower():
            classtype = 'Honors'
        else:
            # Assume theory
            classtype = 'Theory'

        if int(data[0]) >= 2600:
            # In the 2016-2017 school year, the SC uniform grading system became based on a 6.0 scale instead of 5.875
            # This was due to the change from 93-100 as an A to 90-100 as an A.
            grades[weight][classtype]['new'].append(grade)
        else:
            grades[weight][classtype]['old'].append(grade)

# Sort the data
#print grades
weightedGrades = ()
unweightedGrades = ()

for weight in grades:
    if weight == 'full':
        nweight = 1.00
    elif weight == 'half':
        nweight = 0.50
    for classtype in grades[weight]:
        for time in grades[weight][classtype]:
            for grade in grades[weight][classtype][time]:
                if time == 'old':
                    cgpr = 4.875 - ((100.0-float(grade)) * 0.125)
                elif time == 'new':
                    cgpr = 5.000 - ((100.0-float(grade)) * 0.100)
                if cgpr > 0.00:
                    if classtype == 'AP':
                        cgpr += 1.00
                    elif classtype == 'Honors':
                        cgpr += 0.50
                else:
                    cgpr = 0.00 # can't have negative gpa

                weightedGrades += (cgpr, nweight),

                # Unweighted logic
                # At least this is how I assume it works \_(:-))_/
                fgrade = float(grade)
                if time == 'old':
                    if fgrade >= 93.0: unweightedGrades += (4.0, nweight), # A
                    elif fgrade >= 85.0 and fgrade < 93.0: unweightedGrades += (3.0, nweight), # B
                    elif fgrade >= 76.0 and fgrade < 85.0: unweightedGrades += (2.0, nweight), # C
                    elif fgrade >= 70.0 and fgrade < 76.0: unweightedGrades += (1.0, nweight), # D
                    else: unweightedGrades += (0.0, nweight), # < 70.0, F
                elif time == 'new':
                    if fgrade >= 90.0: unweightedGrades += (4.0, nweight), # A
                    elif fgrade >= 80.0 and fgrade < 90.0: unweightedGrades += (3.0, nweight), # B
                    elif fgrade >= 70.0 and fgrade < 80.0: unweightedGrades += (2.0, nweight), # C
                    elif fgrade >= 60.0 and fgrade < 70.0: unweightedGrades += (1.0, nweight), # D
                    else: unweightedGrades += (0.0, nweight), # < 60.0, F

# Calculate the GPR
wGPR = 0.00
wGPR_sum = 0.00
for cgpr, weight in weightedGrades:
    wGPR += cgpr * weight
    wGPR_sum += weight

wGPR_final = wGPR / wGPR_sum

print wGPR_final

uwGPR = 0.00
uwGPR_sum = 0.00
# Unweighted GPA
for cgpr, weight in unweightedGrades:
    uwGPR += cgpr * weight
    uwGPR_sum += weight

uwGPR_final = uwGPR / uwGPR_sum

print uwGPR_final

# %.5f == float & truncate to 5 decimal places
print 'Your GPR (Weighted GPA) is: %.5f' % wGPR_final
print 'Your Unweighted GPA is: %.5f' % uwGPR_final
