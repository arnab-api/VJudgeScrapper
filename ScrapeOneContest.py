import re

contest_link = "____Individual Contest (26/04/2019)"

contest_link = re.sub(r'[^a-zA-Z0-9]', '_', contest_link)
print(contest_link)
