# Copyright 2008, 2013 bjweeks, MZMcBride, Tim Landscheidt

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

"""
Report class for unusually long user blocks
"""

import reports

class report(reports.report):
    def get_title(self):
        return 'Unusually long user blocks'

    def get_preamble_template(self):
        return 'Unusually long (more than two years) blocks of users; data as of <onlyinclude>%s</onlyinclude>.'

    def get_table_columns(self):
        return ['User', 'Admin', 'Timestamp', 'Expiry', 'Reason']

    def get_table_rows(self, conn):
        cursor = conn.cursor()
        cursor.execute('''
        /* excessiveusers.py SLOW_OK */
        SELECT
          CONVERT(ipb_address USING utf8),
          CONVERT(actor_user USING utf8),
          ipb_timestamp,
          ipb_expiry,
          CONVERT(comment_text USING utf8)
        FROM ipblocks
        INNER JOIN actor
          ON ipb_by_actor = actor_id
        INNER JOIN comment
          ON ipb_reason_id = comment_id
        WHERE ipb_expiry > DATE_FORMAT(DATE_ADD(NOW(),INTERVAL 2 YEAR),'%Y%m%d%H%i%s')
        AND ipb_expiry != "infinity"
        AND ipb_user != 0;
        ''')

        for ipb_address, actor_user, ipb_timestamp, ipb_expiry, comment_text in cursor:
            ipb_address = u'[[User talk:%s|]]' % ipb_address
            if comment_text:
                comment_text = u'<nowiki>%s</nowiki>' % comment_text
            else:
                comment_text = ''
            yield [ipb_address, actor_user, ipb_timestamp, ipb_expiry, comment_text]

        cursor.close()
