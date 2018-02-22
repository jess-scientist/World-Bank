# Python 3.6
import requests
import pandas as pd
import simplejson as json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_style("darkgrid")
import pdfkit

# Load JSON data: SH.STA.ACSN, all countries, from 1960 to present (307 pages)
urlstart = "http://api.worldbank.org/v2/countries/all/indicators/SH.STA.ACSN?date=1960:2018&format=json&page="
alldata = []
for i in range(1,308):
    r = requests.get(urlstart+str(i))
    data = json.loads(r.content)
    alldata.extend(data[1])

# Convert dictionary to pandas dataframe
df2 = pd.DataFrame.from_dict(alldata)

# Important columns: country, date, value
# Country column is in dict format, unpack first
countries = pd.DataFrame(df2['country'].to_dict()).T
countries = countries.rename(index=int,columns={'id':'country_id','value':'country_name'})
# Then combine with date and value columns
df3 = pd.concat([countries,df2.loc[:,['date','value']]],axis=1)

# Calculate the change in % value from first date to last date
f = np.zeros(15312)
l = np.zeros(15312)
for i in range(0,264):  # loop over each country
    myseries = df3.iloc[i*58:(i+1)*58]['value']   # 58 years of date
    first_index = myseries.last_valid_index()
    if first_index != None:
        first = myseries[first_index]
    else:
        first = float('nan')
    last_index = myseries.first_valid_index()
    if last_index != None:
        last = myseries[last_index]
    else:
        last = float('nan')
    f[i*58:(i+1)*58] = first*np.ones(58)
    l[i*58:(i+1)*58] = last*np.ones(58)
df_idk = df3.assign(first = f,last = l, change = l-f)

# Print the change for income groups
dfmean = df_idk.groupby('country_name').mean().reset_index()
high = dfmean.loc[dfmean['country_name']=='High income']['change']
middle = dfmean.loc[dfmean['country_name']=='Middle income']['change']
low = dfmean.loc[dfmean['country_name']=='Low income']['change']

print("""High income change: %2.1f\nMiddle income change: %2.1f\nLow income change: %2.1f""" % (high,middle,low))

# Plot the % access over time by income group
fig = plt.figure()
plt.plot(df_idk.loc[df_idk['country_name']=='High income']['date'],
         df_idk.loc[df_idk['country_name']=='High income']['value'],label="High income")
plt.plot(df_idk.loc[df_idk['country_name']=='Upper middle income']['date'],
         df_idk.loc[df_idk['country_name']=='Upper middle income']['value'],label = "Upper middle income")
plt.plot(df_idk.loc[df_idk['country_name']=='Lower middle income']['date'],
         df_idk.loc[df_idk['country_name']=='Lower middle income']['value'],label = "Lower middle income")
plt.plot(df_idk.loc[df_idk['country_name']=='Low income']['date'],
         df_idk.loc[df_idk['country_name']=='Low income']['value'],label="Low income")
plt.axis([1990,2015,0,100])
plt.legend(loc=4)
plt.title('Access to Improved Sanitation Facilities by Income Group')
plt.xlabel('Date (year)')
plt.ylabel('Access Percentage (%)')
fig.savefig('income.png')

# Save the info as a html file
myfile = open('income.html','w')
html_text = """<html><body><h1>Improved Sanitation Facilities (% of population with access)</h1>
                <p><img src="income.png"></p>
                <p><font size="+2">The figure above shows the evolution of access to improved sanitation facilties over time
                by income group. The overall trend shows that access to improved sanitation facilities increases
                over time over all income groups. The high income group did not change much over 25 years because
                it started at nearly 100%. But the middle income group increases in access at a faster rate than
                the low income group (+21% over 25 years for the middle income group vs. +15% for the low income
                group).</font>
                </p></body></html>"""
myfile.write(html_text)
myfile.close()

# Convert html to pdf
# Configured for my computer, change wkhtmltopdf path
config = pdfkit.configuration(wkhtmltopdf="/usr/local/bin/wkhtmltopdf")
pdfkit.from_file('income.html','part1.pdf',configuration=config)
