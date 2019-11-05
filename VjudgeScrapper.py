# Arnab Sen Sharma (arnab-api)
# Lecturer, Department of CSE
# Shahjalal University of Science and Technology

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
import re

def initialize():
    browser = webdriver.Chrome()
    browser.implicitly_wait(5)
    browser.get('https://vjudge.net')

    return browser


def insertValue2TextField(browser, value, element):
    jexe = "arguments[0].setAttribute('value','"+value+"');"
    browser.execute_script(jexe, element)


def login2vjudge(browser, username, password):
    login = browser.find_element_by_link_text("Login")
    login.click()
    browser.implicitly_wait(5)

    name_div = browser.find_element_by_id("login-username")
    pass_div = browser.find_element_by_id("login-password")

    insertValue2TextField(browser, username, name_div)
    insertValue2TextField(browser, password, pass_div)
    browser.implicitly_wait(5)
    print("clicking submit")

    btn_submit = browser.find_element_by_id("btn-login")
    jexe = "arguments[0].click();"
    browser.execute_script(jexe, btn_submit)

    return True

def getContestListInPage(driver):
    con_json = []
    contest_entry = driver.find_elements_by_class_name("contest_entry")
    for contest in contest_entry:
        print(contest.get_attribute('href'), contest.get_attribute('text'))
        obj = {
            "link": contest.get_attribute('href'),
            "name": contest.get_attribute('text')
        }
        con_json.append(obj)
    return con_json

def getNextPage(driver):
    page_links = driver.find_elements_by_class_name("page-link")
    for elem in page_links:
        # print(elem.get_attribute('text'))
        if(elem.get_attribute('text') == "Next"):
            return elem


def parseProblemList(page_soup):
    ### PARSE PROBLEM LINKS ###
    problinkelements = page_soup.findAll("td", {
        "class": "prob-origin text-xs-center"
    })

    problinks = []
    for link in problinkelements:
        sublink = link.findAll("a")[0]
        problinks.append(sublink['href'])

    ### PARSE PROBLEM LINK ###
    probtitleelements = page_soup.findAll("td", {
        "class": "prob-title"
    })

    probtitles = []
    for link in probtitleelements:
        sublink = link.findAll("a")[0]
        # print(sublink.contents[0].strip())
        probtitles.append(sublink.contents[0].strip())
    
    return probtitles, problinks


def parseOneTeam(team):
    try:
    # if(True):
        # print(team.prettify())

        team_rank = team.find("td", { 'class': "rank meta" })
        if(team_rank == None):
            team_rank = team.find("td", { 'class': "rank meta same" })
        # print(team_rank.contents)

        team_solved = team.find("td", { 'class': "solved meta" })
        if(team_solved == None):
            team_solved = team.find("td", { 'class': "solved meta same" })
        # print(team_solved.contents[0].contents)

        try:
            team_name = team.find("td", { 'class': "team meta" }).contents[0].contents[0]
        except:
            team_name = team.find("td", { 'class': "team meta same" }).contents[0].contents[0]

        # print(team_name.contents)
        # print(team_name['href'])
        team_type = "current"
        if(len(team_name) > 1):
            team_type = "previous"

        # print(style)
        try:
            team_penalty = team.find("td", { 'class': "penalty meta" }).contents[1].contents
        except:
            team_penalty = team.find("td", { 'class': "penalty meta same" }).contents[1].contents
        # print(team_penalty)
        
        href = None
        try:
            href = team_name['href']
        except:
            pass

        team_json = {
            "rank": int(team_rank.contents[0]),
            "name": str(team_name.contents[0]),
            "href": href,
            "type": team_type,
            "score": int(team_solved.contents[0].contents[0]),
            "penalty": int(team_penalty[0])
        }
    except:
        return None

    return team_json


def parseOneContest(driver, contest):
    print("")
    print("")

    contest_link = contest["link"]
    print("collecting data from : <" + contest_link + "> " + contest["name"])
    id = contest_link.split('/')[-1]

    driver.get(contest_link)
    page_soup = BeautifulSoup(driver.page_source, 'html.parser')


    probtitles, problinks = parseProblemList(page_soup)
    problems = []
    for i in range(len(problinks)):
        print("name: {}    ||   link:{}".format(probtitles[i], problinks[i]))
        info = {
            "name": probtitles[i],
            "link": problinks[i]
        }
        problems.append(info)


    rank_elem = driver.find_element_by_xpath('//*[@id="contest-tabs"]/li[4]/a')
    rank_elem.click()

    print("waiting")
    driver.implicitly_wait(3)
    time.sleep(5)

    print("check")
    rank_table = driver.find_element_by_id('contest_rank')
    # print(rank_table)
    rank_table = rank_table.find_element_by_id('contest-rank-table')
    # print(rank_table)

    try:
        full_rank = rank_table.find_element_by_id("show-all-teams")
        full_rank.click()
        time.sleep(1)
    except:
        pass

    html = rank_table.get_attribute('innerHTML')
    rank_soup = BeautifulSoup(html, 'html.parser')
    rank_soup = rank_soup.find('tbody')

    try:
        team_info = rank_soup.findAll("tr")
    except:
        print("Could not parse ranklist")
        return "!! ERROR: Could not parse ranklist !!"

    participants = []
    for team in team_info:
        team_json = parseOneTeam(team)
        print(team_json)
        if(team_json != None):
            participants.append(team_json)
        # print("######################################################################")

    contest_info = {
        "problems": problems,
        "participants": participants
    }

    contest["name"] = re.sub(r'[^a-zA-Z0-9]', '_', contest["name"])
    print(contest_info)
    file_name = id + "____" + contest["name"]
    print("saving "+id)
    with open("Output/"+file_name+".json", "w") as f:
        json.dump(contest_info, f)

    print("{} saved successfully".format(file_name))


def getArrangedContestList(driver):
    #### Contest list ######
    driver.get('https://vjudge.net/contest')
    driver.implicitly_wait(3)

    arrangement = driver.find_element_by_xpath('//*[@id="my-contest-panel"]/a[4]')
    # print(arrangement)
    arrangement.click()

    contest_info = []
    page_cnt = 1
    while(True):
        print("      page: ", page_cnt)
        con_arr = getContestListInPage(driver)
        if(len(con_arr) == 0):
            break
        contest_info += con_arr
        nxt_page = getNextPage(driver)
        nxt_page.click()
        time.sleep(1)
        page_cnt += 1

    return contest_info

###################################################################################################################



print("\n\n############### LOG IN #############################\n\n")
driver = initialize()
check = login2vjudge(driver, "********", "********")

if(check == True):
    print("logged in successfully")



print("\n\n############### Getting Contest List #############################\n\n")
contest_info = getArrangedContestList(driver)
for contest in contest_info:
    print(contest)

with open("Output/00_all_contests.json", "w") as f:
    json.dump(contest_info, f)
print("all contests ids saved")




print("\n\n############### Now Starting Parsing #############################\n\n")
for contest in contest_info:
    # contest_link = "https://vjudge.net/contest/339684"
    parseOneContest(driver, contest)



# parseOneContest(driver,
#     {
#         "link": "https://vjudge.net/contest/297804",
#         "name": "Individual Contest (26/04/2019)"
#     })