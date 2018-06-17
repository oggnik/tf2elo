import datetime
import sys

def write_week(matches, teams, num_simulations, week_number, template_name, outfile_name):
    elo_table = ''
    elo_sorted = sorted(teams.values(), key = lambda team: team.elo, reverse = True)
    for team in elo_sorted:
        # Don't round up to 100% or down to 0%
        if team.num_playoffs * 100.0 / num_simulations > 99.5 and team.num_playoffs * 100.0 / num_simulations < 99.9999:
            elo_table += '<tr><td>%s</td><td>%.0f</td><td>&gt; 99%%</td></tr>' % (team.name, team.elo)
        elif team.num_playoffs * 100.0 / num_simulations < 0.5 and team.num_playoffs * 100.0 / num_simulations > 0.0001:
            elo_table += '<tr><td>%s</td><td>%.0f</td><td>&lt; 1%%</td></tr>' % (team.name, team.elo)
        else:
            elo_table += '<tr><td>%s</td><td>%.0f</td><td>%.0f%%</td></tr>' % (team.name, team.elo, team.num_playoffs * 100.0 / num_simulations)

    match_html = ''
    end_week = datetime.datetime.today()
    end_week += datetime.timedelta(days=7)
    for match in matches:
        if match.orig_completed: continue
        if match.date > end_week: continue
        match_html += '<div class="match pure-u-1">'
        match_html += '<div class="match-date pure-g">'
        match_html += '<div class="pure-u-1">%s</div>' % ('{0:%B} {0:%d}'.format(match.date))
        match_html += '</div>'
        match_html += '<div class="match-text pure-g">'
        match_html += '<div class="team1 pure-u-1-4 pure-u-sm-1-12">%.0f%%</div>' % (match.t1_prob * 100)
        match_html += '<div class="team1 pure-u-3-4 pure-u-sm-1-3">%s</div>' % (match.team1)
        match_html += '<div class="pure-u-sm-1-6"></div>'
        match_html += '<div class="team2 pure-u-3-4 pure-u-sm-1-3">%s</div>' % (match.team2)
        match_html += '<div class="team2 pure-u-1-4 pure-u-sm-1-12">%.0f%%</div>' % (match.t2_prob * 100)
        match_html += '</div>'
        match_html += '<div class="prob pure-g">'
        match_html += '<div class="team1-prob" style="width: %.0f%%"></div>' % (match.t1_prob * 100)
        match_html += '<div class="team2-prob" style="width: %.0f%%"></div>' % (match.t2_prob * 100)
        match_html += '</div>'
        match_html += '</div>'
    
    with open(template_name, 'r') as template_file:
        template = template_file.read()
    with open(outfile_name, 'w') as outfile:
        contents = template.replace('WEEK_NUMBER', week_number)
        contents = contents.replace('ELO_TABLE', elo_table)
        contents = contents.replace('MATCH_LISTING', match_html)
        outfile.write(contents)