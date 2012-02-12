#!/usr/bin/env python2.5
 
# Copyright 2009-2011 bjweeks, MZMcBride, svick
 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
 
import datetime
import MySQLdb
import wikitools
import settings
 
report_title = 'User:Svick/WikiProjects by changes'
 
report_template = u'''
List of WikiProjects by number of changes to all its pages in the last 365 days; \
data as of <onlyinclude>%s</onlyinclude>.
 
{| class="wikitable sortable plainlinks"
|-
! No.
! WikiProject
! Edits
! excl. bots
|-
%s
|}

[[en:Wikipedia:Database reports/WikiProjects by changes]]
'''
 
wiki = wikitools.Wiki('http://pl.wikipedia.org/w/api.php')
wiki.login(settings.username, settings.password)
 
conn = MySQLdb.connect(host='plwiki-p.rrdb.toolserver.org', db='plwiki_p', read_default_file='~/.my.cnf')
cursor = conn.cursor()
cursor.execute('''
/* pl_project_changes.py */
SELECT SUBSTRING_INDEX(page_title, '/', 1) AS project,
       SUM((
         SELECT COUNT(*)
         FROM revision
         WHERE page_id = rev_page
         AND DATEDIFF(NOW(), rev_timestamp) <= 365
       )) AS count,
       SUM((
         SELECT COUNT(*)
         FROM revision
         WHERE page_id = rev_page
         AND DATEDIFF(NOW(), rev_timestamp) <= 365
         AND rev_user NOT IN
          (SELECT ug_user
          FROM user_groups
          WHERE ug_group = 'bot')
       )) AS no_bots_count,
       (SELECT page_is_redirect
       FROM page
       WHERE page_namespace = 102
       AND page_title = project) AS redirect
FROM page
WHERE page_namespace BETWEEN 102 AND 103
AND page_is_redirect = 0
GROUP BY project
ORDER BY count DESC
''')
 
i = 1
output = []
for row in cursor.fetchall():
    page_title = '[[Wikiprojekt:%s]]' % unicode(row[0], 'utf-8').replace('_', ' ')
    edits = row[1]
    no_bots_edits = row[2]
    is_redirect = row[3]
    if is_redirect:
        page_title = "''" + page_title + "''"
    table_row = u'''| %d
| %s
| %d
| %d
|-''' % (i, page_title, edits, no_bots_edits)
    output.append(table_row)
    i += 1
 
cursor.execute('SELECT UNIX_TIMESTAMP() - UNIX_TIMESTAMP(rc_timestamp) FROM recentchanges ORDER BY rc_timestamp DESC LIMIT 1;')
rep_lag = cursor.fetchone()[0]
current_of = (datetime.datetime.utcnow() - datetime.timedelta(seconds=rep_lag)).strftime('%H:%M, %d %B %Y (UTC)')
 
report = wikitools.Page(wiki, report_title)
report_text = report_template % (current_of, '\n'.join(output))
report_text = report_text.encode('utf-8')
report.edit(report_text, summary=settings.editsumm, bot=1)
 
cursor.close()
conn.close()
