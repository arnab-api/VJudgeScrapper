import pandas as pd

df = pd.read_excel (r'350-Presentation.xlsx')
serial      = df['Serial No']
member_1    = df['Member 01']
member_2    = df['Member 02']
title       = df['Project Title']

for i in range(len(member_2)):
    if(member_2[i]!=member_2[i]):
        member_2[i] = 0

for i in range(1, 32):
    print("{}. ({}, {}), Title: {}".format(int(serial[i]), int(member_1[i]), int(member_2[i]), title[i]))
