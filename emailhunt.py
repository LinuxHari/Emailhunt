#Importing Modules
import sys
import requests
import re
from urllib.parse import urlparse
import tldextract

#This method sends request to the passed url
def req_url(url):
	try:
		res = requests.get(url).text #Content of given url page will be stored in res in string format
		return res
	except requests.exceptions.RequestException as e:
		print(f"Error fetching URL: {url}")
		print(e)
		sys.exit(1) #This line refers that the program stopped in an abnormal way 

#This method searches and fetches url that are related to given url domain and types of files that user desire to fetch
def fetch_links_files(url, regexs):
    try:
        res = req_url(url)
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while making the request: {str(e)}")
        return ([], [])
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt: Program terminated by user")
        sys.exit(0) #This line refers that the program has executed in normal way
    files = []
    urls = []

    for regex in regexs:
        try:
            files += rem_dup(re.findall(regex, res))
        except Exception as e:
            print(f"Error occurred while finding files with regex {regex}: {str(e)}")
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt: Program terminated by user")
            sys.exit(0)
    try:
        urls = rem_dup(re.findall(f'http[s]?://(?:[A-z0-9]+.)?{domain}/(?:[A-z0-9?=#%./]+)?', res))
    except Exception as e:
        print(f"Error occurred while finding URLs: {str(e)}")
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt: Program terminated by user")
        sys.exit(0)
    return (files,urls)
#This method fetches emails using regex by fetch contents of files and urls found in webpage 
def fetch_emails(url, files, urls):
    try:
        res = req_url(url)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt: Program terminated by user")
        sys.exit(0)
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', res)
#Below for loop fetches emails from all fetched url contents
    for file in files:
        try:
            file_url = f'{url}/{file}'
            res = req_url(file_url)
            emails += re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', res)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {file_url}: {e}")
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt: Program terminated by user")
            sys.exit(0)
#Below for loop fetches emails from all fetched file contents
    for url in urls:
        try:
            res = req_url(url)
            emails += re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', res)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt: Program terminated by user")
            sys.exit(0)
    return rem_dup(emails)

#This function returns top level domain of the url so that we can search for urls that belong to same domain from given url
def find_domain(url):
	try:
		domain_extract = urlparse(url)
		domain = domain_extract.netloc
		tld_extract = tldextract.extract(domain)
		tld = tld_extract.domain+'.'+tld_extract.suffix
		return tld
	except:
		print("Error: Invalid URL or unable to extract domain from URL")
		return None

#This method returns regular expressions from which types of files user want to fetch emails
def regex_list(regexs):
	regex_list = []
	for regex in regexs:
		match regex:
			case 'html':
				regex_list += ['[A-z0-9\-\._]*?\.[hH][tT][mM][lL]','[A-z0-9\-\._]*?\.[hH][tT][mM][^"lL\']']
			case 'php':
				regex_list += ['[A-z0-9\-\._]*?\.[pP][hH][pP]']
			case 'css':
				regex_list += ['[A-z0-9\-\._]*?\.[cC][sS]{2}']
			case 'js':
				regex_list += ['[A-z0-9\-\._]*?\.[jJ][sS]']
			case 'json':
				regex_list += ['[A-z0-9\-\._]*?\.[jJ][sS][oO][nN]']
			case 'jsp':
				regex_list += ['[A-z0-9\-\._]*?\.[jJ][sS][pP]']
			case 'asp':
				regex_list += ['[A-z0-9\-\._]*?\.[aA][sS][pP]']
			case 'aspx':
				regex_list += ['[A-z0-9\-\._]*?\.[aA][sS][pP][xX]']
			case 'xml':
				regex_list += ['[A-z0-9\-\._]*?\.[xX][mM][lL]']
			case 'txt':
				regex_list += ['[A-z0-9\-\._]*?\.[tT][xX][tT]']
			case _:
				print("Invalid file type",regex)
				sys.exit(1)
	return regex_list

#This function removes duplicate values as set datatype does not contain any duplicate values
def rem_dup(items):
        item_set = set(items)
        return list(item_set)

url=''
file_type=[]
try:
	url = sys.argv[1]
	file_type=sys.argv[2]
except:
	print("Missing arguments:")
	print("Command should be:")
	print("script.py <url> <file type(s)>")
	print("\n")
	print("File types can be html,php,asp,aspx,txt,json,xml,jsp,css,js")
	sys.exit(1)
	
	
	
url_pattern = re.compile(r'^(http|https)://[^\s/$.?#].[^\s]*$')
if not url_pattern.match(url):
    print("Error: Invalid URL format. Please provide a valid URL.")
    sys.exit(1)
domain = find_domain(url)
regexs = regex_list((file_type).split(','))
files,urls = fetch_links_files(url,regexs)
emails = fetch_emails(url,files,urls)
print("*********************************")
print("*\tDomain:{}\t*".format(domain))
print("*********************************")

print("*********************************")
print("*\tFILE(s) FOUND\t\t*")
print("*********************************")
for file in files:
	print(file)

print("*********************************")
print("*\tURL(s) FOUND\t\t*")
print("*********************************")
for url in urls:
	print(url)

print("*********************************")
print("*\tEMAIL(s) FOUND\t\t*")
print("*********************************")
for email in emails:
	print(email)
