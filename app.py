import sys
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as patches

def setHexagonSize(count):
    if count > 4:
        return 0.8
    elif count >= 2 and count <= 4:
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

    # Error check for empty dataframe
    if shot_range.empty:
        return None

    shot_difference = shot_average.iloc[0]
    return shot_difference

def buildText(name, year, textColor):
    textSize = 20 

    plt.text(0,-7.5, (name + "   " + year), horizontalalignment='center', verticalalignment='center', fontsize=textSize, color=textColor)
    plt.text(-17.3, -8.5,'Less',horizontalalignment='center',verticalalignment='center', fontsize=textSize, color=textColor)
    plt.text(-21, -8.5,'More',horizontalalignment='center',verticalalignment='center', fontsize=textSize, color=textColor)
    plt.text(21,-8.5,'Cold',horizontalalignment='center',verticalalignment='center', fontsize=textSize, color=textColor)
    plt.text(15.4,-8.5,'Hot',horizontalalignment='center',verticalalignment='center', fontsize=textSize, color=textColor)

def getColors():
    colors = ['#d10240', '#f97306', '#ffb375', '#fff7bc', '#ccfffc']
    return colors

def buildSizeKey(ax):
    colors = getColors()
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

def buildKey(ax):
    colors = getColors()
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

def getHexagonColor(average):
    colors = getColors()

    if average >= 0.07:
        return colors[0]
    elif average >= 0.03:
        return colors[1]
    elif average >= -0.03:
        return colors[2]
    elif average >= -0.07:
        return colors[3]
    else:
        return colors[4]

def buildHexagon(x, y, ax, count, player_average):
    size = setHexagonSize(count)
    shot_difference = getShotDifference(x, y, player_average)

    # Error check
    if shot_difference == None:
        return 0

    color = getHexagonColor(shot_difference)

    hexagon = patches.RegularPolygon((x, y), 6, size, fill=True)
    hexagon.set_facecolor(color)
    hexagon.set_edgecolor('black')
    ax.add_patch(hexagon)

def getFromNBA(playerId, season):
    url = 'http://stats.nba.com/stats/shotchartdetail?Period=0&VsConference=&LeagueID=00&LastNGames=0&TeamID=0&Position=&Location=&Outcome=&ContextMeasure=FGA&DateFrom=&StartPeriod=&DateTo=&OpponentTeamID=0&ContextFilter=&RangeType=&Season=' + season + '&AheadBehind=&PlayerID=' + playerId + '&EndRange=&VsDivision=&PointDiff=&RookieYear=&GameSegment=&Month=0&ClutchTime=&StartRange=&EndPeriod=&SeasonType=Regular+Season&SeasonSegment=&GameID=&PlayerPosition='

    u_a = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36"

    # scrapping
    response = requests.get(url, headers={"USER-AGENT":u_a})
    data = response.json()
    return data

def buildCourt(ax, color):
    lw = 4
    transparency = .5

    # Create court lines
    # citation: https://github.com/eyalshafran/NBAapi
    hoop = patches.Circle((0, 0), radius=0.75, linewidth=lw/2, color=color, fill=False)

    # Create backboard
    backboard = patches.Rectangle((-3, -0.75), 6, -0.1, linewidth=lw, color=color)

    # The paint

    # Create the outer box of the paint, width=16ft, height=19ft
    outer_box = patches.Rectangle((-8, -5.25), 16, 19, linewidth=lw, color=color,
                          fill=False)

    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = patches.Rectangle((-6, -5.25), 12, 19, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = patches.Arc((0, 13.75), 12, 12, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = patches.Arc((0, 13.75), 12, 12, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = patches.Arc((0, 0), 8, 8, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    corner_three_a = patches.Rectangle((-22, -5.25), 0, np.sqrt(23.75**2-22.0**2)+5.25, linewidth=lw,
                                   color=color)

    corner_three_b = patches.Rectangle((22, -5.25), 0, np.sqrt(23.75**2-22.0**2)+5.25, linewidth=lw, color=color)

    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    three_arc = patches.Arc((0, 0), 47.5, 47.5, theta1=np.arccos(22/23.75)*180/np.pi, theta2=180.0-np.arccos(22/23.75)*180/np.pi, linewidth=lw,
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
def getShotChart(playerName, year, data, fileName, limit):
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
    player_info = shots[['LOC_X', 'LOC_Y', 'SHOT_ZONE_AREA', 'SHOT_ZONE_RANGE', 'SHOT_MADE_FLAG', 'GAME_DATE']].copy()

    # Shot attempt range
    player_info = player_info.loc[0 : limit]
    print(player_info)

    # Reduce Player
    player_zones = player_info.groupby(['SHOT_ZONE_AREA', 'SHOT_ZONE_RANGE']).aggregate(np.average)
    court_zone = player_zones.index.get_level_values('SHOT_ZONE_AREA').tolist()
    court_range = player_zones.index.get_level_values('SHOT_ZONE_RANGE').tolist()
    player_zones['SHOT_ZONE_AREA'] = court_zone 
    player_zones['SHOT_ZONE_RANGE'] = court_range 
    player_average = player_zones[['SHOT_ZONE_AREA', 'SHOT_ZONE_RANGE', 'SHOT_MADE_FLAG']].copy()
    player_average = player_average.merge(l_average, how = 'left', on = ['SHOT_ZONE_RANGE', 'SHOT_ZONE_AREA'])
    player_average['difference'] = player_average['SHOT_MADE_FLAG'] - player_average['FGP']

    x = 0.1 * player_info.LOC_X
    y = 0.1 * player_info.LOC_Y
    z = player_info.SHOT_MADE_FLAG
    
    # Get averages for hexbins
    poly = plt.hexbin(x, y, C=z, gridsize=35, extent=[-25,25,-6.25,50-6.25], reduce_C_function=getAverage)
    averages = poly.get_array()

    # Get count for hexbins
    poly = plt.hexbin(x, y, gridsize=35, extent=[-25,25,-6.25,50-6.25])
    verts = poly.get_offsets()
    paths = poly.get_paths()
    counts = poly.get_array()

    fig = plt.figure(figsize=(26.8, 24)) 
    # fig.set_facecolor("black")
    ax = plt.gca(xlim=[30,-30], ylim = [-10,40], aspect=1.0)

    for offc in range(verts.shape[0]):
        binx,biny = verts[offc][0],verts[offc][1]
        if counts[offc] != 0:
            shot_count = counts[offc]
            buildHexagon(binx, biny, ax, shot_count, player_average)

    buildCourt(ax, 'white')
    buildKey(ax)
    buildSizeKey(ax)
    buildText(playerName, year, 'white')

    # Hide axes
    ax.axis('off')
    
    # Save file
    plt.savefig((fileName), bbox_inches='tight', facecolor='black', transparent=False)

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

    if player.empty:
        print("Player does not exist.")
        sys.exit(2)

    playerId = player['PERSON_ID']
    playerId = playerId.iloc[0]
    playerId = str(playerId)
    return playerId

def getShotVolume(data):
    # Get player shots
    shots = pd.DataFrame(data['resultSets'][0]['rowSet'], columns=data['resultSets'][0]['headers'])
    volume = len(shots.index)
    return volume

def createSeries(playerName, year):
    playerId = getPlayerId(playerName)
    data = getFromNBA(playerId, year)
    size = getShotVolume(data)

    for index in range(0, size):
        fileName = str(index)
        getShotChart(" ", " ", data, fileName, index) 

def shotChart(playerName, year):
    playerId = getPlayerId(playerName)
    print("Player id")
    print(playerId)
    data = getFromNBA(playerId, year)
    size = getShotVolume(data)

    fileName = playerName + "_" + year
    getShotChart(playerName, year, data, fileName, size) 


def main():
    print(sys.argv[1])

    if len(sys.argv) < 3:
        print ("usage: %s <firstname> <lastname> <year>" % (sys.argv[0]))
        print ("example: %s Damian Lillard 2017-18" sys.argv[0]))
        sys.exit(2)

    playerName = sys.argv[1] + " " + sys.argv[2]

    print(playerName)

    shotChart(playerName, '2017-18')

main()
