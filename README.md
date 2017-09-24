wsgi_lineprof_reporter
============================

このスクリプトは[wsgi_lineprof](https://github.com/ymyzk/wsgi_lineprof)で出力した複数の結果を統合し、サマリー的なレポートを出力します。
[wsgi_lineprof](https://github.com/ymyzk/wsgi_lineprof)では1リクエストごとにログが出力されますので、大量にアクセスしたあとでは確認量が多く時間がかかっていました。
そのためすべての結果を集計してシンプルなレポートを出力します。


前提
------------

本スクリプトはPython3.xの標準ライブラリのみで作成しているので依存ライブラリはありません。(おそらく)Python3が入った全ての環境で動作します。



インストール
------------

まだ**PyPi**には登録できていません。リポジトリをそのままコピーされるか以下の様にスクリプトをそのまま取得してください。

```
$ curl https://raw.githubusercontent.com/denzow/wsgi_lineprof_reporter/master/wlreporter.py > wlreporter.py
```

使い方
-----------



[wsgi_lineprof](https://github.com/ymyzk/wsgi_lineprof)で対象のアプリケーションのプロファイルログを取得します。。
取得したファイルに対して以下のように実行します。

```bash
$ python wlreporter.py -f /target/file/name.log
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
                         file_name  line  hits  total_time       graph                                                                                                         code
----------------------------------  ----  ----  ----------  ----------  -----------------------------------------------------------------------------------------------------------
/home/XXXXXXXXXXXXXX/python/app.py   192     0           0              @app.route('/')                                                                                            
/home/XXXXXXXXXXXXXX/python/app.py   193     0           0              def get_index():                                                                                           
/home/XXXXXXXXXXXXXX/python/app.py   194     1         191                  page = int(request.args.get('page', 0))                                                                
/home/XXXXXXXXXXXXXX/python/app.py   195     1        2333                  cur = db().cursor()                                                                                    
/home/XXXXXXXXXXXXXX/python/app.py   196     1           1                  cur.execute("""                                                                                        
/home/XXXXXXXXXXXXXX/python/app.py   197     0           0                  SELECT                                                                                                 
/home/XXXXXXXXXXXXXX/python/app.py   198     0           0                  id,                                                                                                    
/home/XXXXXXXXXXXXXX/python/app.py   199     0           0                  name,                                                                                                  
/home/XXXXXXXXXXXXXX/python/app.py   200     0           0                  image_path,                                                                                            
/home/XXXXXXXXXXXXXX/python/app.py   201     0           0                  price,                                                                                                 
/home/XXXXXXXXXXXXXX/python/app.py   202     0           0                  description,                                                                                           
/home/XXXXXXXXXXXXXX/python/app.py   203     0           0                  created_at                                                                                             
/home/XXXXXXXXXXXXXX/python/app.py   204     0           0                  FROM                                                                                                   
/home/XXXXXXXXXXXXXX/python/app.py   205     0           0                      products p                                                                                         
/home/XXXXXXXXXXXXXX/python/app.py   206     0           0                  ORDER BY  id DESC LIMIT 50 OFFSET {}                                                                   
/home/XXXXXXXXXXXXXX/python/app.py   207     1        2580                  """.format(page * 50))                                                                                 
/home/XXXXXXXXXXXXXX/python/app.py   208     1           9                  products = cur.fetchall()                                                                              
/home/XXXXXXXXXXXXXX/python/app.py   209     1          54                  product_id_list = [str(x["id"]) for x in products]                                                     
/home/XXXXXXXXXXXXXX/python/app.py   210     1       29017  **              comment_data = get_all_comments(product_id_list)                                                       
/home/XXXXXXXXXXXXXX/python/app.py   212    51          27                  for product in products:                                                                               
/home/XXXXXXXXXXXXXX/python/app.py   213    50          64                      product['description'] = product['description'][:70]                                               
/home/XXXXXXXXXXXXXX/python/app.py   214    50         183                      product['created_at'] = to_jst(product['created_at'])                                              
/home/XXXXXXXXXXXXXX/python/app.py   215    50          50                      product['comments'] = comment_data.get(product['id'])[:5]#get_comments(product['id'])              
/home/XXXXXXXXXXXXXX/python/app.py   216    50          42                      product['comments_count'] = len(comment_data.get(product['id'])) #get_comments_count(product['id'])
/home/XXXXXXXXXXXXXX/python/app.py   218     1      143940  **********      return render_template('index.html', products=products, current_user=current_user())                   
/home/XXXXXXXXXXXXXX/python/app.py   278     0           0              @app.route('/initialize')                                                                                  
/home/XXXXXXXXXXXXXX/python/app.py   279     0           0              def get_initialize():                                                                                      
/home/XXXXXXXXXXXXXX/python/app.py   280     1        9837  *               cur = db().cursor()                                                                                    
/home/XXXXXXXXXXXXXX/python/app.py   281     1         284                  cur.execute('DELETE FROM users WHERE id > 5000')                                                       
/home/XXXXXXXXXXXXXX/python/app.py   282     1         225                  cur.execute('DELETE FROM products WHERE id > 10000')                                                   
/home/XXXXXXXXXXXXXX/python/app.py   283     1        3487                  cur.execute('DELETE FROM comments WHERE id > 200000')                                                  
/home/XXXXXXXXXXXXXX/python/app.py   284     1        4803                  cur.execute('DELETE FROM histories WHERE id > 500000')                                                 
/home/XXXXXXXXXXXXXX/python/app.py   285     1           0                  return ("Finish")       

```

graph列はレポート内の最大時間との比率を`*`で表現しています。`*`が多い行にチューニングポイントがあります。


#### その他オプション


幾つかオプションがあります。

```
denzownoMacBook-Pro:wsgi_lineprof_reporter denzow$ python wlreporter.py --help
usage: wlreporter.py [-h] -f TARGET_FILE [-d DB_NAME] [-r REPORT_NAME_PREFIX]

This script is parsing wsgi_lineprof result

optional arguments:
  -h, --help            show this help message and exit
  -f TARGET_FILE, --file TARGET_FILE
                        target line profiler log file
  -d DB_NAME, --db-name DB_NAME
                        db name for persistence. if not set, use :memory:.
                        :memory: is temporary database.
  -r REPORT_NAME_PREFIX, --report-name-prefix REPORT_NAME_PREFIX
                        report name prefix. if not set, use profile log name.
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

* PyPIへの登録
* 複数レポートの差分比較
* HTML でのグラフィカルレポートの追加