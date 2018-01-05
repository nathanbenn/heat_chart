# import the Flask class from the flask module
from flask import Flask, render_template
from pprint import pprint
import goldsberry
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.patches import Circle, Rectangle, Arc
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as patches

# # create the application object
# app = Flask(__name__)

#This part grabs all of the unique player identifiers for the current NBA season
#Do not modify this section
players = goldsberry.PlayerList(Season='2016-17')
players = pd.DataFrame(players.players())
players = players['PERSON_ID'].tolist()
players = [str(i) for i in players]

# pprint ((players._data_tables['resultSets'][0]))

# # use decorators to link the function to a url
# @app.route('/')
# def home():
#     return "Hello, World!"  # return a string

# @app.route('/welcome')
# def welcome():
#     return render_template('welcome.html')  # render a template

def customFunc(x, y):
    print("This is x: ", x)
    return 16

def setHexagonSize(count):
    if count > 4:
        return 0.8
    elif count >= 2 and count <= 3:
        return 0.5
    elif count >= 1 and count < 2:
        return 0.3
    else:
        return 0

def getShotDifference(x, y, player_average):
    location = shot_zone(x, y)
    shot_range = player_average.loc[player_average['SHOT_ZONE_RANGE'] == location[0]] 
    shot_range = shot_range.loc[player_average['SHOT_ZONE_AREA'] == location[1]]
    shot_average = shot_range['difference']
    shot_difference = shot_average.iloc[0]
    return shot_difference

def buildSizeKey(ax):
    colors = ['#d10240', '#f4aa42', '#fff7bc', '#bdfcd6', '#ccfffc']
    x =  -21
    y = -7
    color = 2
    size = 0.8
    offset = 0.4
    change = 0.3

    for num in range(3):
        hexagon = patches.RegularPolygon((x, y), 6, size, fill=True)
        hexagon.set_facecolor(colors[color])
        hexagon.set_edgecolor('black')
        ax.add_patch(hexagon)
        x = x + 1.6 + offset
        size = size - change
        change -= 0.1
        offset -= 0.2

    plt.text(-17, -8.5,'Less',horizontalalignment='center',verticalalignment='center')
    plt.text(-21, -8.5,'More',horizontalalignment='center',verticalalignment='center')

def buildKey(ax):
    colors = ['#d10240', '#f4aa42', '#fff7bc', '#bdfcd6', '#ccfffc']
    x =  21
    y = -7
    color = 4
    size = 0.8

    for num in range(5):
        hexagon = patches.RegularPolygon((x, y), 6, size, fill=True)
        hexagon.set_facecolor(colors[color])
        hexagon.set_edgecolor('black')
        ax.add_patch(hexagon)
        x =  x - 1.4
        color -= 1

    plt.text(21,-8.5,'Cold',horizontalalignment='center',verticalalignment='center')
    plt.text(15.4,-8.5,'Hot',horizontalalignment='center',verticalalignment='center')

def getColor(average):
    colors = ['#d10240', '#f4aa42', '#fff7bc', '#bdfcd6', '#ccfffc']

    if average >= 0.05:
        return colors[0]
    elif average >= 0.02:
        return colors[1]
    elif average >= -0.02:
        return colors[2]
    elif average >= -0.04:
        return colors[3]
    else:
        return colors[4]

def buildHexagon(x, y, ax, count, player_average):
    size = setHexagonSize(count)
    shot_difference = getShotDifference(x, y, player_average)
    color = getColor(shot_difference)

    hexagon = patches.RegularPolygon((x, y), 6, size, fill=True)
    hexagon.set_facecolor(color)
    hexagon.set_edgecolor('black')
    ax.add_patch(hexagon)

def buildCourt(ax):
    color = 'black'
    lw = 4
    transparency = .7

    # Create court lines
    # citation: https://github.com/eyalshafran/NBAapi
    hoop = Circle((0, 0), radius=0.75, linewidth=lw/2, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-3, -0.75), 6, -0.1, linewidth=lw, color=color)

    # The paint
    # Create the outer box of the paint, width=16ft, height=19ft
    outer_box = Rectangle((-8, -5.25), 16, 19, linewidth=lw, color=color,
                          fill=False)

    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-6, -5.25), 12, 19, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 13.75), 12, 12, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 13.75), 12, 12, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 8, 8, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    corner_three_a = Rectangle((-22, -5.25), 0, np.sqrt(23.75**2-22.0**2)+5.25, linewidth=lw,
                                   color=color)

    corner_three_b = Rectangle((22, -5.25), 0, np.sqrt(23.75**2-22.0**2)+5.25, linewidth=lw, color=color)

    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    three_arc = Arc((0, 0), 47.5, 47.5, theta1=np.arccos(22/23.75)*180/np.pi, theta2=180.0-np.arccos(22/23.75)*180/np.pi, linewidth=lw,
                    color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, top_free_throw, bottom_free_throw, restricted, corner_three_a, corner_three_b, three_arc]

    for element in court_elements:
        element.set_alpha(transparency)
        ax.add_patch(element)

# Get shot location
# Citation: http://www.eyalshafran.com/grantland_shotchart.html
def shot_zone(X,Y):
    '''
    Uses shot coordinates x and y (in feet - divide by 10 if using the shotchart units)
    and returns a tuple with the zone location
    '''
    r = np.sqrt(X**2+Y**2)
    a = np.arctan2(Y,X)*180.0/np.pi
    if (Y<0) & (X > 0):
        a = 0
    elif (Y<0) & (X < 0):
        a = 180
    if r<=8:
        z = ('Less Than 8 ft.','Center(C)')
    elif (r>8) & (r<=16):
        if a < 60:
            z = ('8-16 ft.','Right Side(R)')
        elif (a>=60) & (a<=120):
            z = ('8-16 ft.','Center(C)')
        else:
            z = ('8-16 ft.','Left Side(L)')
    elif (r>16) & (r<=23.75):
        if a < 36:
            z = ('16-24 ft.','Right Side(R)')
        elif (a>=36) & (a<72):
            z = ('16-24 ft.','Right Side Center(RC)')
        elif (a>=72) & (a<=108):
            z = ('16-24 ft.','Center(C)')
        elif (a>108) & (a<144):
            z = ('16-24 ft.','Left Side Center(LC)')
        else:
            z = ('16-24 ft.','Left Side(L)')
    elif r>23.75:
        if a < 72:
            z = ('24+ ft.','Right Side Center(RC)')
        elif (a>=72) & (a<=108):
            z = ('24+ ft.','Center(C)')
        else:
            z = ('24+ ft.','Left Side Center(LC)')
    if (np.abs(X)>=22):
        if (X > 0) & (np.abs(Y)<8.75):
            z = ('24+ ft.','Right Side(R)')
        elif (X < 0) & (np.abs(Y)<8.75):
            z = ('24+ ft.','Left Side(L)')
        elif (X > 0) & (np.abs(Y)>=8.75):
            z = ('24+ ft.','Right Side Center(RC)')
        elif (X < 0) & (np.abs(Y)>=8.75):
            z = ('24+ ft.','Left Side Center(LC)')
    if Y >= 40:
        z = ('Back Court Shot', 'Back Court(BC)')
    return z

def getAverage(z):
    if (len(z) > 0):
        average = sum(z)/float(len(z))
        return average
    else:
        return 0

# Citation: http://www.eyalshafran.com/grantland_shotchart.html
def getShotChart(playerId, season):

    print("Hey this thing works")

    url = 'http://stats.nba.com/stats/shotchartdetail?Period=0&VsConference=&LeagueID=00&LastNGames=0&TeamID=0&Position=&Location=&Outcome=&ContextMeasure=FGA&DateFrom=&StartPeriod=&DateTo=&OpponentTeamID=0&ContextFilter=&RangeType=&Season=2017-18&AheadBehind=&PlayerID=' + playerId + '&EndRange=&VsDivision=&PointDiff=&RookieYear=&GameSegment=&Month=0&ClutchTime=&StartRange=&EndPeriod=&SeasonType=Regular+Season&SeasonSegment=&GameID=&PlayerPosition='

    u_a = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36"

    # scrapping
    response = requests.get(url, headers={"USER-AGENT":u_a})
    data = response.json()

    # Get league averages
    averages = pd.DataFrame(data['resultSets'][1]['rowSet'], columns=data['resultSets'][1]['headers'])

    # Get player shots
    shots = pd.DataFrame(data['resultSets'][0]['rowSet'], columns=data['resultSets'][0]['headers'])

    # Reduce league averages
    l_average = averages.loc[:,'SHOT_ZONE_AREA':'FGM'].groupby(['SHOT_ZONE_RANGE','SHOT_ZONE_AREA']).sum()
    l_average['FGP'] = 1.0*l_average['FGM']/l_average['FGA'] # create new column with FG%
    l_zone = l_average.index.get_level_values('SHOT_ZONE_AREA').tolist()
    l_range = l_average.index.get_level_values('SHOT_ZONE_RANGE').tolist()
    l_average['SHOT_ZONE_AREA'] = l_zone 
    l_average['SHOT_ZONE_RANGE'] = l_range 

    # return only appropriate columns for player
    player_info = shots[['SHOT_ZONE_AREA', 'SHOT_ZONE_RANGE', 'SHOT_MADE_FLAG']].copy()

    # Reduce Player
    player_zones = player_info.groupby(['SHOT_ZONE_AREA', 'SHOT_ZONE_RANGE']).aggregate(np.average)
    court_zone = player_zones.index.get_level_values('SHOT_ZONE_AREA').tolist()
    court_range = player_zones.index.get_level_values('SHOT_ZONE_RANGE').tolist()
    player_zones['SHOT_ZONE_AREA'] = court_zone 
    player_zones['SHOT_ZONE_RANGE'] = court_range 
    player_average = player_zones[['SHOT_ZONE_AREA', 'SHOT_ZONE_RANGE', 'SHOT_MADE_FLAG']].copy()
    player_average = player_average.merge(l_average, how = 'left', on = ['SHOT_ZONE_RANGE', 'SHOT_ZONE_AREA'])
    player_average['difference'] = player_average['SHOT_MADE_FLAG'] - player_average['FGP']

    print("Averages")
    print(l_average)

    print("Player Averages")
    print(player_average)

    x = 0.1 * shots.LOC_X
    y = 0.1 * shots.LOC_Y
    z = shots.SHOT_MADE_FLAG

    # Get averages for hexbins
    poly = plt.hexbin(x, y, C=z, gridsize=35, extent=[-25,25,-6.25,50-6.25], reduce_C_function=getAverage, mincnt=0)
    averages = poly.get_array()

    # Get count for hexbins
    poly = plt.hexbin(x, y, gridsize=35, extent=[-25,25,-6.25,50-6.25], mincnt=1)
    verts = poly.get_offsets()
    paths = poly.get_paths()
    counts = poly.get_array()

    fig = plt.figure(figsize=(12,10),facecolor='white') 
    ax = plt.gca(xlim=[30,-30], ylim = [-10,40], aspect=1.0)
    
    # counts_test = np.zeros_like(counts)
    
    for offc in xrange(verts.shape[0]):
        binx,biny = verts[offc][0],verts[offc][1]
        if counts[offc]:
            shot_count = counts[offc]
            buildHexagon(binx, biny, ax, shot_count, player_average)

    # Build court
    buildCourt(ax)
    buildKey(ax)
    buildSizeKey(ax)
    ax.axis('off')
    plt.savefig('testplot.png')

    # print(shots)
    

# start the server with the 'run()' method
# if __name__ == '__main__':
#     app.run(debug=True)

# Citation: http://www.eyalshafran.com/grantland_shotchart.html
def commonallplayers(currentseason=0,leagueid='00',season='2015-16'):
    url = 'http://stats.nba.com/stats/commonallplayers?'
    api_param = {
        'IsOnlyCurrentSeason' : currentseason,
        'LeagueID' : leagueid,
        'Season' : season,             
    }
    u_a = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36"
    response = requests.get(url,params=api_param,headers={"USER-AGENT":u_a})
    data = response.json()
    return pd.DataFrame(data['resultSets'][0]['rowSet'],columns=data['resultSets'][0]['headers'])

def getPlayerId(name):
    player_list = commonallplayers(currentseason=0)

    player = player_list.loc[player_list['DISPLAY_FIRST_LAST'] == name]

    print("Player:", player)

    playerId = player['PERSON_ID']
    playerId = playerId.iloc[0]
    print("Player Id:", playerId)
    playerId = str(playerId)
    return playerId


# playerId = '1628384'
# getShotChart(playerId, '2017-2018') 

playerId = getPlayerId('Damian Lillard')
getShotChart(playerId, '2017-2018') 

# pprint (shotchart)
