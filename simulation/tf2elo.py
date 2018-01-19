import copy
import csv
from dateutil.parser import parse
import math
import numpy as np
import sys
from tqdm import tqdm

from model import *
from printer import *

K = 35.0
num_simulations = 10000

starting_elos = {
    'froyotech': 1637.883823,
    'Ascent': 1595.387592,
    'SVIFT NA': 1533.208293,
    'Velocity eSports TF2': 1525.354096,
    'woodpig quantum': 1522.659128,
    'Feint Gaming': 1459.309800,
    'black swan': 1440.162811,
    'TFCrew': 1405.528499,
    'Cat Noises': 1380.505958,
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
                m.orig_completed = True
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
    for match in tqdm(matches, desc = 'Calculating elos'):
        if match.completed:
            team1 = teams[match.team1]
            team2 = teams[match.team2]

            # Update elo scores
            t1_elo, t2_elo = update_elos(team1.elo, team2.elo, match.t1_prob, match.t2_prob)
            team1.elo = t1_elo
            team2.elo = t2_elo
            
            if print_changes: dump_elos(teams)

def simulate_season(orig_matches, orig_teams):
    for i in tqdm(range(0, num_simulations), desc = 'Simulating season'):
        # We don't want to modify originals
        teams = copy.deepcopy(orig_teams)

        for match in matches:
            if match.orig_completed: continue
            team1 = teams[match.team1]
            team2 = teams[match.team2]

            Q1 = math.pow(10.0, team1.elo / 400.0)
            Q2 = math.pow(10.0, team2.elo / 400.0)
            # Calculate expected value
            E1 = Q1 / (Q1 + Q2)
            E2 = Q2 / (Q1 + Q2)

            r = np.random.uniform()
            if r < E1:
                # Team 1 won
                match.set_scores(5, 0)
                team1.matches_for += 1
                team2.matches_against += 1
            else:
                # Team 2 won
                match.set_scores(0, 5)
                team2.matches_for += 1
                team1.matches_against += 1
        
        # Slightly perturb the matches for to prevent perfect ties from happening.
        # This takes ties and effectively picks a random winner.
        for team in teams:
            teams[team].matches_for += np.random.uniform(0, 0.01)
        
        teams_sorted = sorted(teams.values(), key = lambda team: team.matches_for, reverse = True)
        for team in teams_sorted[:4]:
            orig_teams[team.name].num_playoffs += 1

def set_match_probs(matches, teams):
    for match in matches:
        if match.orig_completed: continue
        team1 = teams[match.team1]
        team2 = teams[match.team2]

        Q1 = math.pow(10.0, team1.elo / 400.0)
        Q2 = math.pow(10.0, team2.elo / 400.0)
        # Calculate expected value
        E1 = Q1 / (Q1 + Q2)
        E2 = Q2 / (Q1 + Q2)

        match.t1_prob = E1
        match.t2_prob = E2

def calculate_next_season_start_elos(teams):
    for team in teams.values():
       team.next_season_elo = (team.elo - 1500) * .66 + 1500

if __name__ == "__main__":
    if (len(sys.argv) != 3):
        print('Usage: python3 tf2elo.py season_file.csv week_number')
        exit(1)
    matches, teams = read_season(sys.argv[1])

    calculate_elo(matches, teams)
    simulate_season(matches, teams)
    set_match_probs(matches, teams)
    calculate_next_season_start_elos(teams)

    # Write the html output
    write_week(matches, teams, num_simulations, sys.argv[2], 'week_template.html', 'out.html')

    print('\n======Current Elos======')
    elo_sorted = sorted(teams.values(), key = lambda team: team.elo, reverse = True)
    for team in elo_sorted:
        print('%s %.0f %d %d' % (team.name, team.elo, team.matches_for, team.matches_against))

    print('\n===Playoff Percentage===')
    playoffs_sorted = sorted(teams.values(), key = lambda team: team.num_playoffs, reverse = True)
    for team in playoffs_sorted:
        print(team.name, team.num_playoffs * 100.0 / num_simulations)

    # print('\n====Next Season Elo====')
    # nelo_sorted = sorted(teams.values(), key = lambda team: team.next_season_elo, reverse = True)
    # for team in nelo_sorted:
    #     print('\'%s\': %f,' % (team.name, team.next_season_elo))

    # print('\n==Match Probabilities==')
    # for match in matches:
    #     print(match.date, match.team1, match.t1_prob, match.team2, match.t2_prob)
