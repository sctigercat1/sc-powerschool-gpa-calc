South Carolina GPA Calculator
============
A small script to determine a student's GPA using the Grade History section in PowerSchool. This is intended to be used by a student's account due to the need for the `/guardian/termgrades.html` page.
NOTE: This doesn't support dual-enrollment or IB classes!

Dependencies
------------
* powerapi (pip install https://github.com/powerapi/powerapi-python/zipball/master)
* beautifulsoup4 (pip install beautifulsoup4)

Usage
------------
`gpa.py https://powerschool.example.com username password`

Example Response
------------
```
$ python gpa.py https://powerschool.greatschool.com horriblestudent plsdonttellthispass
termgrades.html?termid=1000&schoolid=1
termgrades.html?termid=1400&schoolid=2
termgrades.html?termid=1100&schoolid=3
termgrades.html?termid=1200&schoolid=3
termgrades.html?termid=1500&schoolid=2
termgrades.html?termid=1300&schoolid=2
termgrades.html?termid=1600&schoolid=3
4.13027491381
3.0
Your GPR (Weighted GPA) is: 4.13027
Your Unweighted GPA is: 3.00000
$ 
```
