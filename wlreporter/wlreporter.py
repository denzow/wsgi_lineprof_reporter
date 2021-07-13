#!/usr/bin/env python
# coding:utf-8
"""
this script is creating more useful report for ISUCON from line profiler log bia **wsgi_lineprof**.

"""


import argparse
import re
import sqlite3 as sqlite

__VERSION__ = "0.3.0"


class DbClass(object):
    """
    init sqlite for analyze.
    """

    def __init__(self, db_name):
        """

        :param str db_name:
        """
        self.db_name = db_name
        self.conn = sqlite.connect(self.db_name)
        self.conn.row_factory = sqlite.Row
        self.conn.execute("""
        create table profile_data(
            id  integer PRIMARY KEY AUTOINCREMENT,
            file_name text,
            func_name text,
            total_time float
        )
        """)
        self.conn.execute("""
        create table profile_line_data(
            id  INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id integer,
            file_name text,
            func_name text,
            line integer,
            hits integer,
            time integer,
            code text
        )
        """)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()

    def create_indexes(self):
        """
        add indexes
        :return:
        """
        self.execute("create index idx_profile_data_file_name on profile_data(file_name)")
        self.execute("create index idx_profile_data_func_name on profile_data(func_name)")

        self.execute("create index idx_profile_line_data_file_name on profile_line_data(file_name)")
        self.execute("create index idx_profile_line_data_func_name on profile_line_data(func_name)")
        self.execute("create index idx_profile_line_data_line on profile_line_data(line)")

    def commit(self):
        self.conn.commit()

    def execute(self, sql, params=None):
        """
        execute sql

        :param str sql:
        :param tuple params:
        :return cursor:
        """
        if params:
            return self.cursor.execute(sql, params)
        else:
            return self.cursor.execute(sql)

    def save_profile_data(self, file_name, func_name, total_time):
        """
        save function based profile data.

        :param str file_name: python script name
        :param str func_name: function name
        :param str total_time: total time
        :return int: sequence for profile data.
        """
        self.execute("""
        insert into profile_data(file_name, func_name, total_time)
        values(?,?,?)
        """, (file_name, func_name, total_time))

        return self.cursor.lastrowid

    def save_line_data(self, profile_id, file_name, func_name, line, hits, time, code):
        """
        save line based profile data.

        :param int profile_id: from save_profile_data()
        :param str file_name: python script name
        :param str func_name: function name
        :param str line: line no
        :param str hits: hits num
        :param str time: time
        :param str code: code string
        :return:
        """
        self.execute("""
            insert into profile_line_data(profile_id, file_name, func_name, line, hits, time, code)
            values(?,?,?,?,?,?,?)
        """, (profile_id, file_name, func_name, line, hits, time, code))

    # debug
    def _dump(self):
        for row in self.execute("select * from profile_data"):
            print(list(row))

    # debug
    def _dump_line(self):
        for row in self.execute("select * from profile_line_data"):
            print(list(row))


def init():
    """
    script initialize. get arguments
    :return:
    """
    parser = argparse.ArgumentParser(description='This script is parsing wsgi_lineprof result')
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="wlreporter Version:{}".format(__VERSION__)
    )

    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        dest="is_verbose",
        action="store_true",
        help="get verbose line data report."
    )

    parser.add_argument(
        "-f",
        "--file",
        required=True,
        dest="target_file",
        help="target line profiler log file"
    )
    parser.add_argument(
        "-d",
        "--db-name",
        dest="db_name",
        default=":memory:",
        help="db name for persistence. if not set, use :memory:. :memory: is temporary database."
    )

    parser.add_argument(
        "-r",
        "--report-name-prefix",
        dest="report_name_prefix",
        help="report name prefix. if not set, use profile log name."
    )

    parser.add_argument(
        "-e",
        "--exclude",
        nargs="*",
        dest="exclude_patterns",
        help="exclude patterns for line_data. ie.) app.py:120. -> app.py 120 row's total time is ignore."
    )

    args = parser.parse_args()

    return args.target_file, args.db_name, args.report_name_prefix, args.exclude_patterns, args.is_verbose


def parse(profiler_log_name):
    """
    parse line profile report.
    :param str profiler_log_name:
    :return:
    """


    """
    File: /home/ishocon/webapp/python/app.py
    Name: get_mypage
    Total time: 0.172644 [sec]
      Line      Hits         Time  Code
    ===================================
       221                         @app.route('/users/<int:user_id>')
       222                         def get_mypage(user_id):
       223         1        12230      cur = db().cursor()
       224         1            1      cur.execute(""
       225                         SELECT p.id, p.name, p.description, p.image_path, ifnull(p.price,0) as price , h.created_at
       226                         FROM histories as h
    :
       249         1        23970                                            total_pay=total_pay, current_user=current_user())
    
    File:
    """
    empty_pattern = re.compile("^\s*$")
    file_pattern = re.compile("^File: (.+)")
    name_pattern = re.compile("^Name: (.+)")
    time_pattern = re.compile("^Total time: (.+) \[sec\]")
    # code have indent, so get another way.
    line_pattern = re.compile("^\s+(\d+)\s+(\d+)?\s+(\d+)?\s+(.+)")

    is_data = False
    is_line_found = False
    # code column start point , because code is not start with space.
    code_index = 0
    buf = {
        "file_name": None,
        "func_name": None,
        "total_time": None,
        "lines": [],
    }

    profile_data_list = []
    with open(profiler_log_name) as raw_log_file:
        for line in raw_log_file:
            # not need \n
            line = line.rstrip("\n")

            # start data block
            if file_pattern.match(line):
                is_data = True

            # end data block and clear.
            if is_data and empty_pattern.match(line):
                is_data = False
                is_line_found = False
                profile_data_list.append(buf)
                buf = {
                    "file_name": None,
                    "func_name": None,
                    "total_time": None,
                    "lines": [],
                }
            if is_data:
                if file_pattern.match(line):
                    buf["file_name"] = file_pattern.match(line).groups()[0]
                if name_pattern.match(line):
                    buf["func_name"] = name_pattern.match(line).groups()[0]
                if time_pattern.match(line):
                    buf["total_time"] = time_pattern.match(line).groups()[0]

                # get line profile data
                if line_pattern.match(line):
                    if not is_line_found:
                        code = line_pattern.match(line).groups()[-1]
                        # save start point of code column. because python code have many space.
                        code_index = line.find(code)
                        is_line_found = True
                    matcher = line_pattern.match(line).groups()
                    line_data = {
                        "line": matcher[0],
                        "hits": matcher[1] if matcher[1] else 0,
                        "time": matcher[2] if matcher[2] else 0,
                        "code": line[code_index:],
                    }
                    buf["lines"].append(line_data)
        # least
        if buf:
            profile_data_list.append(buf)

    return profile_data_list


def persist(db, profile_data):
    """
    persistence to sqlite database
    :param DbClass db:
    :param list profile_data:
    :return:
    """
    for data in profile_data:
        # invalid format remove.
        if not data["func_name"]:
            continue
        data_id = db.save_profile_data(
            file_name=data["file_name"],
            func_name=data["func_name"],
            total_time=data["total_time"]
        )
        for line in data["lines"]:
            db.save_line_data(
                profile_id=data_id,
                file_name=data["file_name"],
                func_name=data["func_name"],
                line=line["line"],
                hits=line["hits"],
                time=line["time"],
                code=line["code"],
            )
        db.commit()
    db.create_indexes()
    db.commit()


def get_max_str_length(raw_list_dict_data, column_name):
    """
    max length for specified column.
    It's useful for pretify report.
    :param list[dict] raw_list_dict_data:
    :param str column_name:
    :return:
    """
    max_length = max([len(str(dict_[column_name])) for dict_ in raw_list_dict_data])
    # I need prettify format. not real max length of data
    if len(column_name) > max_length:
        return len(column_name)
    return max_length


def create_report(base_data, columns, report_name):
    """
    write report file.
    :param list[dict] base_data:
    :param list[str] columns:
    :param str report_name:
    :return:
    """
    with open(report_name, "w") as f:
        # get max_length of columns for prettify report.
        max_length_dict = {x: get_max_str_length(base_data, x) for x in columns}

        # write header
        header_str = "  ".join([x.rjust(max_length_dict[x]) for x in columns])
        header_line = "  ".join(["-".rjust(max_length_dict[x], "-") for x in columns])
        f.write("{}\n".format(header_str))
        f.write("{}\n".format(header_line))

        # write data
        for row_data in base_data:
            row_data_list = []
            for col in columns:
                col_data = row_data[col]
                # str is ljust, digit is rjust
                if hasattr(col_data, "ljust"):
                    if col_data:
                        row_data_list.append(col_data.ljust(max_length_dict[col]))
                    else:
                        row_data_list.append("".ljust(max_length_dict[col]))
                else:
                    if col_data:
                        row_data_list.append(str(col_data).rjust(max_length_dict[col]))
                    else:
                        row_data_list.append(str(0).rjust(max_length_dict[col]))

            f.write("{}\n".format("  ".join(row_data_list).rstrip()))


def parse_exclude_patterns(raw_pattern_list):
    """

    :param list[str] raw_pattern_list:
    :return:
    """
    if not raw_pattern_list:
        return []
    # line no cast to int. because comparing easily.
    return [(x.split(":")[0], "*" if x.split(":")[1] == "*" else int(x.split(":")[1])) for x in raw_pattern_list]


def report(db, report_file_name_prefix, exclude_pattern_list, is_verbose):
    """
    一般的な観点でのレポートを出力する。現時点では以下の2種類

    * 関数ごとの時間
    * 行ごとの時間

    :param DbClass db: temporary database
    :param str report_file_name_prefix: report name prefix
    :param list exclude_pattern_list:
    :param bool is_verbose: 行データレポートでmin, maxを含めるか
    :return:
    """
    # 関数ごとに経過時間や平均などを集計
    summary_columns = ["file_name", "func_name", "total_time", "avg_time", "min_time", "max_time", "call_count"]
    func_list_with_time_sql = """
    select
        file_name,
        func_name,
        round(sum(total_time),5) as total_time,
        round(avg(total_time),5) as avg_time,
        round(min(total_time),5) as min_time,
        round(max(total_time),5) as max_time,
        count(*) as call_count
    from
        profile_data
    group by
        file_name,
        func_name
    order by
        total_time desc ,1,2
    """

    # すべての行単位で集計
    line_data_columns = ["file_name", "line", "avg_per_time", "hits", "total_time", "graph", "code"]
    whole_line_with_time_sql = """
    select
        file_name,
        line,
        sum(hits) as hits,
        round(sum(cast(time as float))/ sum(hits), 3) as avg_per_time,
        sum(time) as total_time,
        (
            select
                code
            from
                profile_line_data
            where
                file_name = d.file_name
            and line = d.line
            limit 1
        ) as code
    from
        profile_line_data d
    group by
        file_name, line
    order by
        1, 2
    """
    if is_verbose:
        line_data_columns = ["file_name", "line", "min_time", "max_time",
                             "avg_per_time", "hits", "total_time", "graph","code"]
        whole_line_with_time_sql = """
        select
            file_name,
            line,
            sum(hits) as hits,
            round(min(cast(time as float) / hits), 3) as min_time,
            round(max(cast(time as float) / hits), 3) as max_time,
            round(sum(cast(time as float))/ sum(hits), 3) as avg_per_time,
            sum(time) as total_time,
            (
                select
                    code
                from
                    profile_line_data
                where
                    file_name = d.file_name
                and line = d.line
                limit 1
            ) as code
        from
            profile_line_data d
        group by
            file_name, line
        order by
            1, 2
        """

    # sqlite.Row is better, but i need dict.(ie. add custom column data)
    summary_data = [dict(row) for row in db.execute(func_list_with_time_sql).fetchall()]  # type: list[dict]
    # add graph column
    line_data = [dict(row) for row in db.execute(whole_line_with_time_sql).fetchall()]  # type: list[dict]

    # add graph column
    exclude_pattern_data = parse_exclude_patterns(exclude_pattern_list)
    if exclude_pattern_data:
        max_time = max([row["total_time"] for row in line_data
                        if (row["file_name"], "*") not in exclude_pattern_data and (row["file_name"], row["line"]) not in exclude_pattern_data])
    else:
        max_time = max([row["total_time"] for row in line_data])

    for row in line_data:
        # max time line add ! to found easily.
        if row["total_time"] == max_time:
            row.update(graph="!" + round(row["total_time"] * 9 / max_time) * "*")
        # if max_time exceeded, the lines must be ignore.
        elif row["total_time"] > max_time:
            row.update(graph="@IGNORE@")
        else:
            row.update(graph=round(row["total_time"] * 10 / max_time)*"*")

    # create summary report.
    create_report(
        base_data=summary_data,
        columns=summary_columns,
        report_name="{}_summary_data.log".format(report_file_name_prefix)
    )
    # create line report.
    create_report(
        base_data=line_data,
        columns=line_data_columns,
        report_name="{}_line_data.log".format(report_file_name_prefix)
    )


def main():
    target_file_name, target_db_name, report_name_prefix, exclude_patterns, is_verbose = init()
    # テキスト形式のプロファイルログをDictに変換
    parsed_profile_data = parse(target_file_name)
    # 一旦SQLiteに格納し、各種集計・分析後にレポート出力
    with DbClass(target_db_name) as tmp_db:
        persist(tmp_db, parsed_profile_data)
        prefix = target_file_name
        if report_name_prefix:
            prefix = report_name_prefix
        report(tmp_db, prefix, exclude_patterns, is_verbose)


if __name__ == "__main__":
    main()


