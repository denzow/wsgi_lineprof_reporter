wsgi_lineprof_reporter
============================

このスクリプトは[wsgi_lineprof](https://github.com/ymyzk/wsgi_lineprof)で出力した複数の結果を統合し、サマリー的なレポートを出力します。
[wsgi_lineprof](https://github.com/ymyzk/wsgi_lineprof)では1リクエストごとにログが出力されますので、大量にアクセスしたあとでは確認量が多く時間がかかっていました。
そのためすべての結果を集計してシンプルなレポートを出力します。


前提
------------

本スクリプトはPython3.xの標準ライブラリのみで作成しているので依存ライブラリはありません。

インストール
------------

### PyPi

以下のコマンドで簡単にインストールできます。インストールに成功すれば`wlreporter`コマンドが利用可能になります。

```
$ pip install wlreporter
$ wlreporter -v
```

### 手動

単一のスクリプトで動作します。以下を実行し、任意のディレクトリに配置して利用可能です。

```
$ curl https://raw.githubusercontent.com/denzow/wsgi_lineprof_reporter/master/wlreporter/wlreporter.py > wlreporter.py
```

使い方
-----------



[wsgi_lineprof](https://github.com/ymyzk/wsgi_lineprof)で対象のアプリケーションのプロファイルログを取得します。。
取得したファイルに対して以下のように実行します。

```bash
$ wlreporter -f /target/file/name.log
```

実行すると以下の2つのファイルが元ファイルと同じディレクトリに生成されます。

* `xxxx_summary_data.log`
* `xxxx_line_data.log`

それぞれ以下のような内容です。


#### `xxxx_summary_data.log`

関数単位での実行時間順に集計した結果です。上位の関数にチューニングポイントがあります。

```
                         file_name       func_name  total_time  avg_time  call_count
----------------------------------  --------------  ----------  --------  ----------
/home/XXXXXXXXXXXXXX/python/app.py  get_index          0.17849   0.17849           1
/home/XXXXXXXXXXXXXX/python/app.py  get_initialize         0.0       0.0           1

```

#### `xxxx_line_data.log`

スクリプト内の各行ごとにかかった時間やHit等を集計しています。


```
                         file_name  line  min_time  max_time  avg_per_time  hits  total_time       graph                                                                                                         code
----------------------------------  ----  --------  --------  ------------  ----  ----------  ----------  -----------------------------------------------------------------------------------------------------------
/home/XXXXXXXXXXXXXX/python/app.py   192         0         0             0     0           0              @app.route('/')                                                                                            
/home/XXXXXXXXXXXXXX/python/app.py   193         0         0             0     0           0              def get_index():                                                                                           
/home/XXXXXXXXXXXXXX/python/app.py   194     191.0     191.0         191.0     1         191                  page = int(request.args.get('page', 0))                                                                
/home/XXXXXXXXXXXXXX/python/app.py   195    2333.0    2333.0        2333.0     1        2333                  cur = db().cursor()                                                                                    
/home/XXXXXXXXXXXXXX/python/app.py   196       1.0       1.0           1.0     1           1                  cur.execute("""                                                                                        
/home/XXXXXXXXXXXXXX/python/app.py   197         0         0             0     0           0                  SELECT                                                                                                 
/home/XXXXXXXXXXXXXX/python/app.py   198         0         0             0     0           0                  id,                                                                                                    
/home/XXXXXXXXXXXXXX/python/app.py   199         0         0             0     0           0                  name,                                                                                                  
/home/XXXXXXXXXXXXXX/python/app.py   200         0         0             0     0           0                  image_path,                                                                                            
/home/XXXXXXXXXXXXXX/python/app.py   201         0         0             0     0           0                  price,                                                                                                 
/home/XXXXXXXXXXXXXX/python/app.py   202         0         0             0     0           0                  description,                                                                                           
/home/XXXXXXXXXXXXXX/python/app.py   203         0         0             0     0           0                  created_at                                                                                             
/home/XXXXXXXXXXXXXX/python/app.py   204         0         0             0     0           0                  FROM                                                                                                   
/home/XXXXXXXXXXXXXX/python/app.py   205         0         0             0     0           0                      products p                                                                                         
/home/XXXXXXXXXXXXXX/python/app.py   206         0         0             0     0           0                  ORDER BY  id DESC LIMIT 50 OFFSET {}                                                                   
/home/XXXXXXXXXXXXXX/python/app.py   207    2580.0    2580.0        2580.0     1        2580                  """.format(page * 50))                                                                                 
/home/XXXXXXXXXXXXXX/python/app.py   208       9.0       9.0           9.0     1           9                  products = cur.fetchall()                                                                              
/home/XXXXXXXXXXXXXX/python/app.py   209      54.0      54.0          54.0     1          54                  product_id_list = [str(x["id"]) for x in products]                                                     
/home/XXXXXXXXXXXXXX/python/app.py   210   29017.0   29017.0       29017.0     1       29017  **              comment_data = get_all_comments(product_id_list)                                                       
/home/XXXXXXXXXXXXXX/python/app.py   212     0.529     0.529         0.529    51          27                  for product in products:                                                                               
/home/XXXXXXXXXXXXXX/python/app.py   213      1.28      1.28          1.28    50          64                      product['description'] = product['description'][:70]                                               
/home/XXXXXXXXXXXXXX/python/app.py   214      3.66      3.66          3.66    50         183                      product['created_at'] = to_jst(product['created_at'])                                              
/home/XXXXXXXXXXXXXX/python/app.py   215       1.0       1.0           1.0    50          50                      product['comments'] = comment_data.get(product['id'])[:5]#get_comments(product['id'])              
/home/XXXXXXXXXXXXXX/python/app.py   216      0.84      0.84          0.84    50          42                      product['comments_count'] = len(comment_data.get(product['id'])) #get_comments_count(product['id'])
/home/XXXXXXXXXXXXXX/python/app.py   218  143940.0  143940.0      143940.0     1      143940  !*********      return render_template('index.html', products=products, current_user=current_user())                   
/home/XXXXXXXXXXXXXX/python/app.py   278         0         0             0     0           0              @app.route('/initialize')                                                                                  
/home/XXXXXXXXXXXXXX/python/app.py   279         0         0             0     0           0              def get_initialize():                                                                                      
/home/XXXXXXXXXXXXXX/python/app.py   280    9837.0    9837.0        9837.0     1        9837  *               cur = db().cursor()                                                                                    
/home/XXXXXXXXXXXXXX/python/app.py   281     284.0     284.0         284.0     1         284                  cur.execute('DELETE FROM users WHERE id > 5000')                                                       
/home/XXXXXXXXXXXXXX/python/app.py   282     225.0     225.0         225.0     1         225                  cur.execute('DELETE FROM products WHERE id > 10000')                                                   
/home/XXXXXXXXXXXXXX/python/app.py   283    3487.0    3487.0        3487.0     1        3487                  cur.execute('DELETE FROM comments WHERE id > 200000')                                                  
/home/XXXXXXXXXXXXXX/python/app.py   284    4803.0    4803.0        4803.0     1        4803                  cur.execute('DELETE FROM histories WHERE id > 500000')                                                 
/home/XXXXXXXXXXXXXX/python/app.py   285         0         0             0     1           0                  return ("Finish")                                                                                      

```

graph列はレポート内の最大時間との比率を`*`で表現しています。`*`が多い行にチューニングポイントがあります。最も時間を要している行には`!`がついているのでまずはその行が改善できないかを検討します。

各列の意味は以下です。

|column|mean|
|--------|------|
|file_name|File Name|
|line|Line Number |
|min_time|Min Time(per One hit)for the line |
|max_time|Max Time(per One hit)for the line |
|avg_per_time|Avg Time(per One hit)for the line |
|hits| hit count the line |
|total_time| Avg * Hits |

なお、min_time,max_timeは`--verbose`を指定した場合のみ出力されます。

#### excludeオプション

最も時間がかかっている箇所をチューニングするのが原則ですが、そのポイントを諦める場合に使用します。

```sh
$ wlreporter -f sample/small.log  -e /home/XXXXXXXXXXXXXX/python/app.py:218
```

本例の場合、`/home/XXXXXXXXXXXXXX/python/app.py`の218行目はGraph列の計算に含まれなくなります。

```
                         file_name  line  min_time  max_time  avg_per_time  hits  total_time       graph                                                                                                         code
----------------------------------  ----  --------  --------  ------------  ----  ----------  ----------  -----------------------------------------------------------------------------------------------------------
:
/home/XXXXXXXXXXXXXX/python/app.py   209      54.0      54.0          54.0     1          54                  product_id_list = [str(x["id"]) for x in products]                                                     
/home/XXXXXXXXXXXXXX/python/app.py   210   29017.0   29017.0       29017.0     1       29017  !*********      comment_data = get_all_comments(product_id_list)                                                       
/home/XXXXXXXXXXXXXX/python/app.py   212     0.529     0.529         0.529    51          27                  for product in products:                                                                               
/home/XXXXXXXXXXXXXX/python/app.py   213      1.28      1.28          1.28    50          64                      product['description'] = product['description'][:70]                                               
/home/XXXXXXXXXXXXXX/python/app.py   214      3.66      3.66          3.66    50         183                      product['created_at'] = to_jst(product['created_at'])                                              
/home/XXXXXXXXXXXXXX/python/app.py   215       1.0       1.0           1.0    50          50                      product['comments'] = comment_data.get(product['id'])[:5]#get_comments(product['id'])              
/home/XXXXXXXXXXXXXX/python/app.py   216      0.84      0.84          0.84    50          42                      product['comments_count'] = len(comment_data.get(product['id'])) #get_comments_count(product['id'])
/home/XXXXXXXXXXXXXX/python/app.py   218  143940.0  143940.0      143940.0     1      143940  @IGNORE@        return render_template('index.html', products=products, current_user=current_user())                   
/home/XXXXXXXXXXXXXX/python/app.py   278         0         0             0     0           0              @app.route('/initialize')   

```

最も時間がかかっているのは218行目ですが、Graph列は`@IGNORE@`と表示されています。次に時間がかかっている210行目を最大時間としてGraph列が計算されるため、突出して時間がかかっている行のチューニングを諦めた場合の次のチューニングポイントが探しやすくなります。

#### その他オプション


幾つかオプションがあります。

```
$ wlreporter -h
usage: wlreporter [-h] [-V] [-v] -f TARGET_FILE [-d DB_NAME]
                  [-r REPORT_NAME_PREFIX]
                  [-e [EXCLUDE_PATTERNS [EXCLUDE_PATTERNS ...]]]

This script is parsing wsgi_lineprof result

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -v, --verbose         get verbose line data report.
  -f TARGET_FILE, --file TARGET_FILE
                        target line profiler log file
  -d DB_NAME, --db-name DB_NAME
                        db name for persistence. if not set, use :memory:.
                        :memory: is temporary database.
  -r REPORT_NAME_PREFIX, --report-name-prefix REPORT_NAME_PREFIX
                        report name prefix. if not set, use profile log name.
  -e [EXCLUDE_PATTERNS [EXCLUDE_PATTERNS ...]], --exclude [EXCLUDE_PATTERNS [EXCLUDE_PATTERNS ...]]
                        exclude patterns for line_data. ie.) app.py:120. ->
                        app.py 120 row's total time is ignore.
```

内部では一旦オンメモリのSQLiteに格納してからレポートティングしています。そのためレポート後は自動で
DBは破棄されますが`-d`でファイル名を指定することで分析結果を格納したDBをスクリプト終了後も保持することができます。

通常のレポート以上の分析を実施する場合はこちらのDBをSQLiteに対応したクライアントで分析してください。

謝辞
---------

本スクリプトは[wsgi_lineprof](https://github.com/ymyzk/wsgi_lineprof)を前提としています。[wsgi_lineprof](https://github.com/ymyzk/wsgi_lineprof)の作者のymyzk様の
お陰でWEBアプリのパフォーマンスチェックが快適になりました。

TODO
------------

* 複数レポートの差分比較
* HTML でのグラフィカルレポートの追加
* パフォーマンス改善