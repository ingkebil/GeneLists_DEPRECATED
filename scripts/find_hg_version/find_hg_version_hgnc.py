#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
import sys
import pymysql
from pymysql.err import InternalError, ProgrammingError

def main(argv):
    conn = pymysql.connect(host='ensembldb.ensembl.org', port=5306, user='anonymous', db='homo_sapiens_core_75_37')
    cur = conn.cursor()

    # first get the list of available human dbs
    cur.execute("show databases like 'homo_sapiens_core\_%'")
    rs = cur.fetchall()
    dbs = [ db[0] for db in rs ]

    # then based on the coords of one ensid, see which version match
    for db in dbs:
        cur.execute("use %s;" % db)
        try:
            # TODO check with other query for releases 48 - 64
            cur.execute("select g.seq_region_start AS Gene_start, g.seq_region_end AS Gene_stop, x.display_label AS HGNC_ID, g.stable_id AS Ensembl_gene_id, seq_region.name AS Chromosome from gene g join xref x on x.xref_id = g.display_xref_id join seq_region using (seq_region_id) where x.display_label = %s", argv[0])
            rs = cur.fetchall()
            if len(rs) != 0:
                print("%s is the one" % db)
            else:
                print("%s is NOT the one" % db)
        except InternalError as ierrr:
            if ierrr.args[0] != 1054:
                raise
            else:
                print("Skipping %s with %s" % (db, ierrr.args[1]))
        except ProgrammingError as perrr:
            if perrr.args[0] != 1146:
                raise
            else:
                print("Skipping %s with %s" % (db, perrr.args[1]))
    cur.close()
    conn.close()
    pass

if __name__ == '__main__':
    main(sys.argv[1:])
