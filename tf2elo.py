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

def update_elos(t1_elo, t2_elo, t1_prob, t2_prob):
    Q1 = math.pow(10.0, t1_elo / 400.0)
    Q2 = math.pow(10.0, t2_elo / 400.0)
    # Calculate expected value
    E1 = Q1 / (Q1 + Q2)
    E2 = Q2 / (Q1 + Q2)

    t1_elo = t1_elo + K * (t1_prob - E1)
    t2_elo = t2_elo + K * (t2_prob - E2)
    
    return t1_elo, t2_elo

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
    
    for match in matches:
        if not match.completed: continue
        team1 = teams[match.team1]
        team2 = teams[match.team2]
        if match.winner == match.team1:
            team1.matches_for += 1
            team2.matches_against += 1
        else:
            team2.matches_for += 1
            team1.matches_against += 1

    return matches, teams

def dump_elos(teams):
    sorted_teams = sorted(teams.values(), key = lambda team: team.name)
    elos = [str(team.elo) for team in sorted_teams]
    print('\t'.join(elos))

def calculate_elo(matches, teams, print_changes = False):
    if print_changes: dump_elos(teams)
    for match in matches:
        if match.completed:
            team1 = teams[match.team1]
            team2 = teams[match.team2]

            # Update elo scores
            t1_elo, t2_elo = update_elos(team1.elo, team2.elo, match.t1_prob, match.t2_prob)
            team1.elo = t1_elo
            team2.elo = t2_elo
            
            if print_changes: dump_elos(teams)

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print('Usage: python3 tf2elo.py season_file.csv')
    matches, teams = read_season(sys.argv[1])

    calculate_elo(matches, teams)

    print('=======================')
    elo_sorted = sorted(teams.values(), key = lambda team: team.elo, reverse = True)
    for team in elo_sorted:
        print(team.name, team.elo, team.matches_for, team.matches_against)
    
    print('=======================')