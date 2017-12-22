import csv
from dateutil.parser import parse
import math
import sys

from model import *

K = 45.0

starting_elos = {
    'froyotech': 1500.0,
    'Ascent': 1500.0,
}

def read_season(filename):
    matches = []
    with open(filename) as f:
        reader = csv.DictReader(f)
        for match in reader:
            date = parse(match['Date'])
            if match['Score'] == '':
                m = Match(match['Home'], match['Away'], match['Map'], date)
            else:
                m = Match(match['Home'], match['Away'], match['Map'], date)
                scores = match['Score'].split('-')
                m.set_scores(int(scores[0]), int(scores[1]))
            matches.append(m)
    matches.sort(key = lambda match: match.date)
    teams = {}
    for match in matches:
        if match.team1 not in teams:
            team = Team(match.team1)
            if match.team1 in starting_elos:
                team.elo = starting_elos[match.team1]
            teams[match.team1] = team

    return matches, teams

def dump_elos(teams):
    sorted_teams = sorted(teams.values(), key = lambda team: team.name)
    elos = [str(team.elo) for team in sorted_teams]
    print('\t'.join(elos))

def calculate_elo(matches, teams):
    mse = 0
    dump_elos(teams)
    for match in matches:
        if match.completed:
            team1 = teams[match.team1]
            team2 = teams[match.team2]
            Q1 = math.pow(10.0, team1.elo / 400.0)
            Q2 = math.pow(10.0, team2.elo / 400.0)
            # Calculate expected value
            E1 = Q1 / (Q1 + Q2)
            E2 = Q2 / (Q1 + Q2)

            # Checking
            # print(team1.name, team1.elo, team2.name, team2.elo, E1, E2)
            # if E1 > E2 and match.t1_prob < match.t2_prob:
            #     print(team1.name, team1.elo, team2.name, team2.elo, E1, E2)
            #     print('Error!')

            # Update mse
            mse += math.pow(match.t1_prob - E1, 2)
            mse += math.pow(match.t2_prob - E2, 2)

            # Update elo scores
            t1_elo = team1.elo + K * (match.t1_prob - E1)
            t2_elo = team2.elo + K * (match.t2_prob - E2)
            team1.elo = t1_elo
            team2.elo = t2_elo
            
            dump_elos(teams)
    return mse

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print('Usage: python3 tf2elo.py season_file.csv')
    matches, teams = read_season(sys.argv[1])

    mse = calculate_elo(matches, teams)
    # print(str(K) + '\t' + str(mse))
    # for k in range(10, 500):
    #     for team in teams.values():
    #         team.elo = 1500
    #     K = k
    #     mse = calculate_elo(matches, teams)
    #     print(str(K) + '\t' + str(mse))

    print('=======================')
    elo_sorted = sorted(teams.values(), key = lambda team: team.elo, reverse = True)
    for team in elo_sorted:
        print(team.name, team.elo)