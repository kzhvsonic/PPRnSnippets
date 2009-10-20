#!/usr/local/bin/perl
#------------------------------------------------------------------
# XREA 提供のログを WEB 上で見やすくする CGI
#------------------------------------------------------------------
$scr_title='XREALOG';
$scr_ver='Ver 1.22.0 2009.10.19';
$author_name='Kazuho/V.Sonic';
#------------------------------------------------------------------
# お約束：
# 　CGI 設置の経験のある方向けです。
# 　「素人」・「初心者」の方はご遠慮ください。
# 　質問・要望・苦情は一切受け付けません。
# 　無断改造大歓迎。無断再配布大歓迎。勝手にどうぞ。
#------------------------------------------------------------------
# 履歴：
# Ver1.22.0 2009.10.19 ログ表示フィルターにをUAだけでなくHOST指定でもできるように
# Ver1.21.2 2009.10.13 ログ表示フィルターにUA追加
# Ver1.21.1 2008.06.22 ログ表示フィルターにUA追加
# Ver1.21.0 2007.10.16 リクエスト文字列にHTMLタグが混ざってる行をエスケープする
# Ver1.20.0 2007.03.27 最後の " がかけている行を上手くパースできなかったのを修正
# Ver1.19.0 2007.03.26 指定のリファラのあるアクセスを非表示にする設定追加
# Ver1.18.0 2007.01.25 バグ修正＆POSTメソッドの時は太字にしてみる
# Ver1.17.5 2006.12.05 ログ表示フィルターにUA追加
# Ver1.17.1 2004.06.01 ログ表示フィルターにUA追加
#                      データの追加だけのバージョンアップは数値を小さくしてみる
# Ver1.17 2004.05.25 ログ加工表示で不成功リクエストが表示されないのを修正
# Ver1.16 2004.05.23 ログ表示フィルターにUA追加
# Ver1.15 2004.05.20 ログ表示フィルターにUA追加
#                    日付選択リストがおかしかったのを修正
# Ver1.14 2004.05.27 ログ表示フィルターにUA追加
# Ver1.13 2004.03.18 除外されたリストのＵＡだけを表示するリンク追加
#                    例のごとくＵＡ増やしてます
# Ver1.12 2004.03.04 ログ表示フィルターの種類をさらに増やした
# Ver1.11 2004.02.20 ログの表示するしないチェックに間違いがあったのを修正
#                    明らかに文法違反なマークアップだけ修正
# Ver1.10 2004.02.18 表示したくないリクエストとかを除外するオプション追加
# Ver1.09 2004.02.14 自サイトからのアクセスを除外するオプション追加
# Ver1.08 2004.02.02 ユーザーエージェント増やしてみた
# Ver1.07 2004.01.30 指定項目が増えたので、メニューをテーブルにした
# Ver1.06 2004.01.14 指定の拡張子だけのログを抽出する機能をつけてみた
# Ver1.05 2003.10.06 なんかログの日本語が全部EUCに変換されてる対策＆過去ログが出来た対策
# Ver1.04 2003.06.26 referを日本語で読めるように表示してみる
# Ver1.03 2003.06.24 生ログ＆認証付きアクセスの表示オプションをつけた
# Ver1.02 2003.05.28 生ログ出力モードをつけた。
# Ver1.01 2003.05.27 アクセスがない除外ＵＡは表示しない。
#                    外部設定を読み込むようにした。
# Ver1.00 2003.05.23 作った。
#
#------------------------------------------------------------------
# ユーザー設定
#------------------------------------------------------------------
# CGI から見たログディレクトリ（相対 or 絶対パス）
$logdir='../../log';
# 戻るリンク
$returl='../index.html';
# ログを一覧に表示したくないサーバーの名前
@hidelog=(
  'test.example.com',
);
# 表示したくないリクエスト（自分しか知らない秘密のＵＲＬとか）
@hidereq=(
#  'cgi-bin/sugoisample.cgi?passwd=samplenapasswd&samplecommand=testnacommand', # 例
#  'favicon.ico', # 最近はページを見に来るだけで取得しようとしやがります
);
# 表示したくないリファラ（自分しか知らない秘密のＵＲＬとか）
@hideref=(
#  'cgi-bin/sugoisample.cgi', # 例
);

# 表示したくないホスト
@hideip=(
  '192.168.1.1', # 例
);
# 一覧で除外しつつ訪問回数をカウントしたいユーザーエージェントを指定。
# うちのサイトのアクセスログに複数回残ってたのしか書いてません。
# ロボットデータベースが目的ではないので、当然抜けはたくさんあります。
# 「うぜぇな、このロボット。一日に何回来たら気がすむんだ」と思う奴を各自追加するように。
# 一部の説明は http://c-moon.jp/robots.shtml を参考にしたです。
%denyua=(
# 'UAに含まれる文字列'  => ['種類','説明','URL（あれば）','フラグ(0:1)'],
  'AppleSyndication'
          => ['R','Safari が RSS 巡回時に名乗ってくる','','1'],
  'almaden.ibm.com'
          => ['Z','IBM Almaden Research Center のロボット','http://www.almaden.ibm.com/cs/crawler','1'],
  'Ask Jeeves/Teoma'
          => ['S','Ask.jp','http://www.ask.jp/','1'],
  'Baiduspider'
          => ['S','百度（中国のサーチエンジン)','http://www.baidu.com/search/spider.htm','1'],
  'BecomeBot'
          => ['S','Become.com ショッピングサイト専用サーチエンジン','http://www.become.com/site_owners.html','1'],
  'BruinBot'
          => ['Z','UCLA のどっかの研究室でやってる WebArchive プロジェクト用','http://webarchive.cs.ucla.edu/bruinbot.html','1'],
  'cococ'
          => ['R','cococ(タスクトレイ常駐型 RSSリーダー)','http://am13.net/wiki/index.php?cococ','1'],
  'Comaneci_bot'
          => ['A','I know.（アンテナ）','http://i-know.jp/','1'],
  'Convera'
          => ['Z','Converaつう会社の実験用クローラーだそうです','http://mail.tawdemo.com/crawl/','1'],
  'Download Ninja'
          => ['D','Download Ninja','http://www.ifour.co.jp/ninja/dln/index.htm','1'],
  'Dumbot'
          => ['D','Dumbfind という検索エンジン（未稼働）のロボット','http://www.dumbfind.com/dumbot.html','1'],
  'EmeraldShield'
          => ['Z','EmeraldWebShieldという、サーバー用のWEBフィルタリングソフトのデータ収集ロボット','http://www.emeraldshield.com/webbot.aspx','1'],
  'FAST-WebCrawler'
          => ['S','AlltheWeb','http://www.alltheweb.com/','1'],
  'Feedpath'
          => ['R','Feerpath オンラインRSSリーダ','http://feedpath.jp/','1'],
  'findlinks'
          => ['Z','findlinks（ドイツ語……）','http://wortschatz.uni-leipzig.de/findlinks/','1'],
  'Gigabot',
          => ['S','Gigablast','http://gigablast.com/','1'],
  'Girafabot',
          => ['S','Girafa(謎)','http://www.girafa.com/','1'],
  'Gaisbot',
          => ['S','Gais（台湾）','http://gais.cs.ccu.edu.tw/','1'],
  'Googlebot'
          => ['S','Google','http://www.google.com/','1'],
  'Feedfetcher-Google'
          => ['S','Google Reader用クローラ','http://www.google.com/feedfetcher.html','1'],
  'Google-Sitemaps'
          => ['S','Google Sitemaps用クローラ','https://www.google.com/webmasters/sitemaps/','1'],
  'Google Wireless Transcoder'
          => ['Z','サイトのデータを携帯閲覧用に変換する Google のロボット','','1'],
  'Hatena Antenna'
          => ['A','はてなアンテナ','http://a.hatena.ne.jp/','1'],
  'Hatena RSS'
          => ['A','はてなRSS','http://r.hatena.ne.jp/','1'],
  'HyperRobot'
          => ['Z','HyperRobot','','1'],
  'ia_archiver'
          => ['S','The Internet Archive','http://www.archive.org/','1'],
  'InternetLinkAgent'
          => ['C','InternetLinkAgent','http://www.osk.3web.ne.jp/~goronyan/winprg/sub.shtml','1'],
  'Jakarta Commons-HttpClient'
          => ['Z','Jakarta(Java の HTTP 通信ライブラリ)を使った何か','http://jakarta.apache.org/commons/httpclient/','1'],
  'livedoorCheckers'
          => ['C','livedoor チェッカーズ','http://checkers.livedoor.com/help/','1'],
  'livedoor FeedFetcher'
          => ['C','livedoor Reader','http://reader.livedoor.com/','1'],
  'livedoor HttpClient'
          => ['C','livedoor のクローラー','http://www.livedoor.com/','1'],
  'libwww-perl'
          => ['C','LWP を使った perl スクリプトのどれか','','1'],
  'Mediapartners-Google'
          => ['S','Google の AdSence 広告用ロボット','','1'],
  'Microsoft-ATL-Native'
          => ['Z','VC++ の ATL Server ライブラリを使ったなにか。 ' # URL長いよ
             ,'http://www.microsoft.com/japan/msdn/library/ja/vclib/html/vclrfatl_http_useragent.asp','1'],
  'moba-crawler'
          => ['S','モバゲータウンの検索用らしい','http://crawler.dena.jp/','1'],
  'Mozilla/3.01 (compatible;)'
          => ['Z','proxy サーバーがよく名乗る（いい加減詐称するのはやめてほしい）','','1'],
  'msnbot'
          => ['S','MSN','http://www.msn.co.jp/','1'],
  'MVAClient'
          => ['Z','台湾あたりから来てるらしいロボット。詳細不明','','1'],
  'Mynifty'
          => ['R','マイニフティのRSSリーダ機能\ ','http://my.nifty.com/','1'],
  'Nandemorss'
          => ['R','なんでもRSS','http://blogwatcher.pi.titech.ac.jp/nandemorss/','1'],
  'NATSU-MICAN'
          => ['A','なつみかん','http://aniki.haun.org/natsu/','1'],
  'Naver'
          => ['S','Naver','http://www.naver.co.jp/','1'],
  'NetNewsWire'
          => ['R','Mac OS X用 RSS リーダ','http://ranchero.com/netnewswire/','1'],
  'NextGenSearchBot'
          => ['Z','極東のどっかの国の非常にお行儀の悪いらしいロボット','','1'],
  'NG'
          => ['S','Exalead(ヨーロッパのサーチエンジン)','http://www.exalead.com/','1'],
  'OmniExplorer'
          => ['S','Internet Categorizer(coming soon だそうで)','http://www.omni-explorer.com','1'],
  'Openbot'
          => ['S','Openfind（台湾のサーチエンジン）','http://www.openfind.com.tw/','1'],
  'PageDown'
          => ['D','PageDown','http://www001.upp.so-net.ne.jp/y_yutaka/','1'],
  'Pathtraq'
          => ['S','Pathtraq (みんなが見ている人気ページや話題ニュースをランキング化する...だそうで)','http://pathtraq.com/about','1'],
  'POE-Component-Client'
          => ['C','Perl用のhttpコンポーネントモジュール','','1'],
  'Program Shareware'
          => ['Z','spam 用のメールアドレス収集ロボット','','1'],
  'RFCrawler'
          => ['S','楽天サーチ','http://www.rfms.rakuten.co.jp/crawler.html','1'],
  'RssBar'
          => ['R','RssBar(IEツールバー型RSSリーダー)','http://darksky.biz/sw/rssbar/','1'],
  'Rumours-Agent'
          => ['Z','Rumours.jp(ドメイン名だけがあってサイトは無いみたい) から来てるらしいロボット','','1'],
  'Sage'
          => ['R','Firefox の RSS 閲覧用拡張 Sage','','1'],
  'SBIder'
          => ['S','Sitesell の巡回ロボット','http://www.sitesell.com/sbider.html','1'],
  'Scooter'
          => ['S','Altavista','http://www.altavista.com/','1'],
  'SideWinder'
          => ['S','Infoseek のロボット','http://www.infoseek.co.jp/','1'],
  'sohu-search'
          => ['S','捜狐（中国のポータルサイト）','http://www.sohu.com/','1'],
  'Steeler'
          => ['Z','東京大学の研究用ロボット','http://www.tkl.iis.u-tokyo.ac.jp/~crawler/','1'],
  'Slurp'
          => ['S','Yahoo Slurp','http://help.yahoo.com/help/us/ysearch/slurp','1'],
  'QuepasaCreep'
          => ['S','QUEPASA(メキシコ?）','http://www.quepasa.com/','1'],
  'TurnitinBot'
          => ['Z','学生がレポートを書くときに、よそのページに書いてある文書のコピペですませてないかをチェックするためにいろんなページを集めるロボット（超意訳）',' http://www.turnitin.com/','1'],
  'Tkensaku'
          => ['S','日本語サイトの検索エンジン',' http://www.tkensaku.com/','1'],
  'WebFetch'
          => ['Z','WebFetch(先読みソフト)','http://hp.vector.co.jp/authors/VA011426/wfetch.html','1'],
  'WebSauger'
          => ['D','WebSauger(ドイツ製のダウンローダ)','','1'],
  'W3C_CSS_Validator'
          => ['V','W3C CSS Validator','http://jigsaw.w3.org/css-validator/','1'],
  'Windows-RSS-Platform'
          => ['R','IE7のRSSリーダー機能\ ','','1'],
  'WWWC'
          => ['C','WWWC','http://www.nakka.com/wwwc/','1'],
  'WWWD'
          => ['C','WWWD','http://www.koizuka.jp/wwwd/','1'],
  'Yahoo-MMCrawler'
          => ['S','Yahoo(?)','http://trd.overture.com/','1'],
  'YahooFeedSeeker'
          => ['R','Yahoo! の RSS リーダー用クローラ','http://publisher.yahoo.com/rssguide','1'],
  'Y!J-BSC'
          => ['R','Yahoo! の blogサーチ用クローラ','http://help.yahoo.co.jp/help/jp/blog-search/','1'],
  'Y!J-BRI'
          => ['R','Yahoo! の クローラ','http://help.yahoo.co.jp/help/jp/search/indexing/indexing-15.html','1'],
  'Y!J-MBS'
          => ['R','Yahoo! の blogサーチ用クローラ','http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html','1'],
  'Y!J-SRD'
          => ['R','Yahoo! の モバイルサーチ用クローラ','http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html','1'],
  'Zao'
          => ['Z','蔵王（言問プロジェクトのロボット）','http://www-tsujii.is.s.u-tokyo.ac.jp/projects-j.html','1'],
  'ZyBorg'
          => ['S','WISEnut','http://www.WISEnutbot.com/','1'],
  );

# 一覧で除外しつつ訪問回数をカウントしたいHOSTを指定。
# UA でクローラーを名乗らない MSNBOT のために新設ｗ
%denyhost=(
# 'HOSTに含まれる文字列'  => ['種類','説明','URL（あれば）','フラグ(0:1)'],
  'search.msn.com'
          => ['S','MSN','','1'],
  );

# ユーザーエージェント種別
%uatype=(
  'A'=>'アンテナ',
  'B'=>'ブラウザ',
  'C'=>'更新チェッカ',
  'D'=>'ダウンロードソフト',
  'R'=>'RSSリーダ',
  'S'=>'サーチエンジン',
  'V'=>'文法チェッカ',
  'Z'=>'その他',
  );

# basic認証してるアクセスの表示
$authlog=0; # 0:非表示 1:表示

# 正常なリザルト
@ok=(
  '200','206','301','302','304'
);

# 生ログ閲覧
# 注意：生ログ表示の時は上にあるフィルター設定はみな無視されますんで、
# これを許可すると全部のログが丸見えですよ。一人だけで楽しみたい時だけどうぞ。
$rawlog=0; # 0:不許可 1:許可

# 表示デフォルト設定 変更したいものだけコメントはずして設定してください。
#$def{'c'}=0; # 1: サイト内での移動は表示しない
#$def{'d'}=0; # 1: 特定のＵＡのアクセスは一覧から除外して訪問回数を表示
#$def{'r'}=0; # 0: 整形ログ 1:完全生ログ 2:整形ログに生ログ行を付け加える
#$def{'s'}=''; # 参照元指定(部分マッチ)
#$def{'u'}=''; # UA指定(部分マッチ)
#$def{'e'}=''; # ファイル指定（末尾からマッチ）
#$def{'h'}=''; # UA指定（部分マッチ）
$def{'cs'}=1; # 指定参照元だけ（０：除外　１：表示）
$def{'cu'}=1; # 指定UAだけ（０：除外　１：表示）
$def{'ce'}=1; # 指定のファイルだけ（０：除外　１：表示）
$def{'ch'}=1; # 指定ホストだけ（０：除外　１：表示）
#$def{'z'}=0; # 1:ユニークアクセスのみ
#$def{'f'}='sample.s1.xrea.com'; # サーバー指定
# ↑これを指定するとサーバー選択メニューはでない
# 一つの場所で複数のドメイン管理してない人はこれを有効にすると便利。


#------------------------------------------------------------------
# 以上の設定を変更した外部ファイル（使う人だけ）
$usetfile='xrealogset.cgi';
#--------------------------------------------------------------------
# ここからは改造したい人だけ
#------------------------------------------------------------------
BEGIN{
  $| = 1;
  print "Content-type: text/html; charset=Shift_JIS\n\n";
print <<__EOM__;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang="ja">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS">
	<meta name="ROBOTS" content="NOINDEX,NOFOLLOW,NOARCHIVE">
	<meta http-equiv="Content-Script-Type" content="text/javascript">
	<meta http-equiv="Content-Style-Type" content="text/css">
	<style type="text/css">
	</style>
__EOM__
  open(STDERR, ">&STDOUT");
}

#--------------------------------------------------------------------
require $usetfile if(-f $usetfile);
$cgi=substr($0,rindex($0,'/')+1);
foreach(keys(%denyua2)){
  $denyua{$_}=$denyua2{$_} if($_);
}
foreach(sort(keys(%uatype))){
  $uacomm.=$_.':'.$uatype{$_}.' ' if($_);
}
foreach(@ok){
  $ok{$_}++;
}
foreach(@hidelog){
  $hidelog{$_}++;
}
my $ret=eval('require Jcode');
if ($ret) { # Jcode.pm 使用
  $jcodever = "Jcode.pm $Jcode::VERSION";
  *Jgetcode = \&Jcode::getcode;
  *Jconvert = \&Jcode::convert;
}

if($ENV{'REQUEST_METHOD'} eq 'GET'){ # GET以外シカト
  my $query=$ENV{'QUERY_STRING'};
  my @query=split(/&/, $query); # 引数分解
  foreach (@query){ # ハッシュにほうり込む
    tr/+/ /;
    my($key, $val)=split(/=/,$_,2); # = の手前と後で分ける
    $key=~tr/\W//d; # キーに余計なものはなし
    $val =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;  # デコード
    $val=~tr/\0\x0D\x0A//d; # NULL文字&改行コード削除
    if($jcodever){
      my $chkstr=$key.$val;
      my $code=&Jgetcode(\$chkstr); # 日本語コードチェック
      &Jconvert(\$key, 'sjis', $code) if($key && $code ne 'sjis'); # 日本語コード変換
      &Jconvert(\$val, 'sjis', $code) if($val && $code ne 'sjis'); # 日本語コード変換
    }
    $in{$key}=$val;
  }
}

foreach my $key (keys(%def)){
  $in{$key}=$def{$key} unless(exists($in{$key}));
}

if($in{'r'} ==1 and !$rawlog){
  $in{'r'}=2;
}
if(exists($in{'f'})){
  if($in{'r'}==1){
    &RawView;
  }
  else{
    &LogView;
  }
}
else{
  &LogList;
}

print "<br><a href='$returl'>戻る</a>\n";
print "<hr><address>$scr_title $scr_ver</address>\n";
print "</body>\n</html>\n";

#--------------------------------------------------------------------
sub LogList{
	print "<title>アクセスログ一覧</title></head><body>\n";
  print "<h1>アクセスログ一覧</h1>\n";
  my ($menu,$form)=&Menu();
  print $menu,$form;
}

#--------------------------------------------------------------------
sub Menu {
  my $selhost=shift;
  my $menu="<hr>\n";
  my $form="";
  my %hosts;
  unless(opendir(DIR,$logdir)){
    &Error("$logdir がオープンできません",$!);
    return;
  }
  while(my $ent=readdir(DIR)){
    if($ent=~/(.*?)\.log$/){
      my $host=$1;
      my $cnt=0;
      if($host=~/(.*?)\.(\d+)$/){
        $host=$1;
        $cnt=$2;
      }
      next if($hidelog{$host});
      my @st=stat($logdir.'/'.$ent);
      $hosts{$host}=[] unless(ref($hosts{$host}) eq 'ARRAY');
      $hosts{$host}->[$cnt]=&GetTime($st[9],'d');
    }
  }
  closedir(DIR);

  my $cu1=" checked" if($in{'cu'}==0);
  my $cu2=" checked" if($in{'cu'}==1);
  my $ce1=" checked" if($in{'ce'}==0);
  my $ce2=" checked" if($in{'ce'}==1);
  my $cs1=" checked" if($in{'cs'}==0);
  my $cs2=" checked" if($in{'cs'}==1);
  my $ch1=" checked" if($in{'ch'}==0);
  my $ch2=" checked" if($in{'ch'}==1);
  my $r1=" checked" if($in{'r'}==1);
  my $r2=" checked" if($in{'r'}==0);
  my $r3=" checked" if($in{'r'}==2);
  my $c=" checked" if($in{'c'});
  my $h=" checked" if($in{'h'});
  my $z=" checked" if($in{'z'});
  my $d=" checked" if($in{'d'});
  foreach my $host (sort(keys(%hosts))){
    next if($selhost && $selhost ne $host);
    my $host2=$host;
    $host2=~tr/\./_/;
    $menu.=" [<a href='#$host2'>$host</a>]\n";
    $form.="<form action='$cgi' method='get'>\n<table border='1'>\n";
    if($selhost ne $host){
      $form.="<tr><th colspan='2' bgcolor='#ddddff'><a name='$host2'>$host</a></th></tr>\n";
    }
    $form.="<tr><th>表\示ログ</th><td>";
    $form.="<select name='i'>\n";
    for($i=0; $i<scalar(@{$hosts{$host}});$i++){
      $form.="<option value='$i'";
      $form.=" selected" if($in{'i'} == $i);
      $form.=">${$hosts{$host}}[$i]</option>\n";
    }
    $form.="</select>\n";
    $form.="<input type='submit' value='表\示'>\n";
    $form.="<input type='hidden' name='f' value='$host'>\n";
    $form.="<input type='radio' name='r' value='1'$r1>生ログ\n" if($rawlog);
    $form.="<input type='radio' name='r' value='0'$r2>整形ログ\n";
    $form.="<input type='radio' name='r' value='2'$r3>整形ログ+生ログ\n";
    $form.="</td></tr>\n";
    $form.="<tr><th>オプション<br>※整形ログ時に有効</th><td>";
    $form.="<input type='checkbox' name='z' value='1'$z>ユニークアクセスのみ<br>\n";
    $form.="<input type='checkbox' name='c' value='1'$c>$host からの参照は除外<br>\n";
    $form.="<input type='checkbox' name='d' value='1'$d>特定のＵＡは一覧から除外\n";
    $form.="</td></tr>\n";
    $form.="<tr><th>フィルター<br>※整形ログ時に有効</th><td>";
    $form.="ブラウザ <input type='text' name='u' size='30' value='$in{'u'}'>（一部マッチ）\n";
    $form.=" <input type='radio' name='cu' size='20' value='0'$cu1>除外\n";
    $form.=" <input type='radio' name='cu' size='20' value='1'$cu2>表\示<br>\n";
    $form.="ホスト <input type='text' name='h' size='30' value='$in{'h'}'>（一部マッチ）\n";
    $form.=" <input type='radio' name='ch' size='20' value='0'$ch1>除外\n";
    $form.=" <input type='radio' name='ch' size='20' value='1'$ch2>表\示<br>\n";
    $form.="ファイル <input type='text' name='e' size='30' value=$in{'e'}>（末尾マッチ）\n";
    $form.=" <input type='radio' name='ce' size='20' value='0'$ce1>除外\n";
    $form.=" <input type='radio' name='ce' size='20' value='1'$ce2>表\示<br>\n";
    $form.="参照元 <input type='text' name='s' size='30' value=$in{'s'}>（一部マッチ）";
    $form.=" <input type='radio' name='cs' size='20' value='0'$cs1>除外\n";
    $form.=" <input type='radio' name='cs' size='20' value='1'$cs2>表\示<br>\n";
    $form.="(参照元がないログを指定する時は「-（半角ハイフン）」を入力)\n";
    $form.="</td></tr></table></form>\n";
  }
  $menu.="<hr>\n";
  unless($selhost){
    return ($menu,$form);
  }
  else{
    return $form;
  }
}

#--------------------------------------------------------------------
sub Title {
  my($date,$form)=@_;
  my $title.="アクセスログ";
  my($stitle,$ret);
  if($in{'f'}){
    $title.="- $in{'f'}";
    $title.="($date)" if($date);
    $stitle.="[生ログ]" if($in{'r'});
    $stitle.="[特定ＵＡの除外]" if($in{'d'});
    $stitle.="[ユニークアクセスのみ]" if($in{'z'});
    $stitle.="[$in{'f'} からでないアクセス]" if($in{'c'});
    $stitle.="[フィルター(ファイル) &lt;$in{'e'}&gt;]" if($in{'e'});
    $stitle.="[フィルター(ホスト) &lt;$in{'h'}&gt;]" if($in{'h'});
    $stitle.="[フィルター(ブラウザ) &lt;$in{'u'}&gt;]" if($in{'u'});
    $stitle.="[フィルター(参照元) &lt;$in{'s'}&gt;]" if($in{'s'});
    $stitle="<p>$stitle</p>\n" if($stitle);
    $ret="<a href='$cgi?'>一覧に戻る</a>\n";
  }
  return "<title>$title</title></head><body>$ret<h1>$title</h1>$form$stitle";
}

#--------------------------------------------------------------------
# 表示するログなら true
sub ChkLog {
  my($host,$user,$req,$result,$ref,$ua)=@_;

  # 初期設定での除外指定
  # 指定ホストのアクセスは除外
  foreach my $h (@hideip){
    return 0 if(index($host,$h)>=0);
  }
  
  # 指定リクエスト文字列のアクセスは除外
  foreach my $h (@hidereq){
    return 0 if(index($req,$h)>=0);
  }

  # 指定リファラ文字列のアクセスは除外
  foreach my $h (@hideref){
    return 0 if(index($ref,$h)>=0);
  }

  # 同じサーバーからの参照アクセスは除外
  return 0 if($in{'c'} and $ref=~/$in{'f'}/);

  # フィルター指定
  # 指定のファイル(末尾マッチ)
  my $file=$req;
  my $length=index($req,'?');
  if($length>0){
    $file=substr($req,0,index($req,'?'));
  }
  if($in{'e'}){
    if($in{'ce'}){ # 指定のファイル以外を除外
      return 0 unless($file=~/$in{'e'}$/);
    }
    else{ # 指定のファイルを除外
      return 0 if($file=~/$in{'e'}$/);
    }
  }

  # 指定のIP(一部マッチ)
  if($in{'h'}){
    if($in{'ch'}){ # 指定のＵＡ以外を除外
      return 0 unless($host=~/$in{'h'}/);
#      print "$in{'ch'} $in{'h'} $host<br>\n";
    }
    else{ # 指定のＵＡを除外
      return 0 if($host=~/$in{'h'}/);
#      print "$in{'ch'} $in{'h'} $host<br>\n";
    }
  }

  # 指定のUA(一部マッチ)
  if($in{'u'}){
    if($in{'cu'}){ # 指定のＵＡ以外を除外
      return 0 unless($ua=~/$in{'u'}/);
#      print "$in{'cu'} $in{'u'} $ua<br>\n";
    }
    else{ # 指定のＵＡを除外
      return 0 if($ua=~/$in{'u'}/);
#      print "$in{'cu'} $in{'u'} $ua<br>\n";
    }
  }

  # 指定の参照元
  if($in{'s'}){
    if($in{'cs'}){ # 指定の参照元以外を除外
      if($in{'s'} eq '-' ){
        return 0  unless($ref eq '-');
      }
      else{
        return 0 unless($ref=~/$in{'s'}/);
      }
    }
    else{ # 指定の参照元を除外
      if($in{'s'} eq '-' ){
        return 0  if($ref eq '-');
      }
      else{
        return 0 if($ref=~/$in{'s'}/);
      }
    }
  }
  
  # 認証付ログのチェック
  return 0 if(!$authlog and $user ne '-');

  return 1;
}
#--------------------------------------------------------------------
sub LogView{
  my $log=$logdir.'/'.$in{'f'};
  $log.=".$in{'i'}" if($in{'i'});
  $log.='.log';
  my(%das,%ip);
  my @stat=stat($log);
  my $date=&GetTime($stat[9],'d');
  unless(open(LOG,$log)){
    &Error("$log がオープンできません",$!);
    return;
  }
  my %host=(); # 訪問したホストと回数
  my $form=&Menu($in{'f'});
  print &Title($date,$form);
  print "<dl>\n";
  my $count=0;
  while(my $str=<LOG>){
    if($jcodever){
      my $code=&Jgetcode(\$str); # ユーザーエージェント
      &Jconvert(\$str, 'sjis', $code) if($str && $code ne 'sjis'); # 日本語コード変換
    }
    my($host,$l,$user,$time,$method,$req,$http,$result,$size,$ref,$ua)=
      $str=~/^(.+?) (.+?) (.+?) (\[.+?\]) "(GET|HEAD|POST) (.+?) (HTTP.+?)" (.+?) (.+?) "(.+?)" "(.+)/; #";
    $ua =~tr/"$//d; #";
    next unless($host);
    if($jcodever && $ref && $ref ne'-'){
      # 勝手にログファイルの中の日本語コード変換しくさりおって・・・。
      if(index($ref,'\\x')){
        $ref =~ s/\\x/%/g;
        $ref =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;  # デコード
        $ref=~tr/\0\x0D\x0A//d; # NULL文字&改行コード削除
        #if($ref=~/ie=UTF\-8/){
        #  $code='utf8';
        #}
        #else{
        $code=&Jgetcode(\$ref);
        #}
        &Jconvert(\$ref, 'sjis', $code) if($ref && $code ne 'sjis'); # 日本語コード変換
      }
    }
    # 表示するログをチェック
    next unless(&ChkLog($host,$user,$req,$result,$ref,$ua));

    # ユニークアクセスのチェック
    next if($ok{$result} and $in{'z'} and $ip{$host});

    # 指定ＵＡのチェック
    my $deny=0;
    if($in{'d'}){
      foreach my $da (keys(%denyua)){
        if(index($ua,$da)>-1){
          $das{$da}++;
          $deny=1;
          last;
        }
      }
      foreach my $dh (keys(%denyhost)){
        if(index($host,$dh)>-1){
          $das{$dh}++;
          $deny=1;
          last;
        }
      }
      next if($deny);
    }

    # ホストのカウント
    $ip{$host}++;
    # ログ整形
    $count++;
    &DisTag(\$user);
    &DisTag(\$host);
    &DisTag(\$req);
    &DisTag(\$method);
    &DisTag(\$ua);
    &DisTag(\$ref);
    $method = '<b>'.$method.'</b>' if($method eq 'POST');
    if(!$ok{$result}){
      print "<dt>$count <font style='color:#ff0000'> $time </font>　";
      print "<font style='color:#cc6633;font-weight:bold'> $host </font></dt>\n";
      print "<dd><font style='color:#ff0000'> $method $req $http </font> ";
      print "<font style='color:#ff0000;font-weight:bold'> $result </font></dd>\n";
      print "<dd><font style='color:#3333cc'> $ref </font></dd>\n";
      print "<dd><font style='color:#336633'> $ua </font></dd>\n";
    }
    else{
      print "<dt>$count $time　";
      print "<font style='color:#cc6633;font-weight:bold'> $host </font></dt>\n";
      print "<dd><font style='color:#6633cc'> $method $req $http $result </font></dd>\n";
      print "<dd><font style='color:#3333cc'> $ref </font></dd>\n";
      print "<dd><font style='color:#336633'> $ua </font></dd>\n";
    }
    if($in{'r'}==2){
			&DisTag(\$str);
      print "<dd><font style='color:#999999;font-size:8pt'> $str </font></dd>\n";
    }
  }
  print "</dl>\n";
  if($in{'d'} && %das){
    print "<h2>除外されたユーザーエージェントの訪問回数</h2>\n";
    print "<table border='1' summary='除外されたユーザーエージェントの訪問回数'>\n";
    print "<tr><th>順位</th><th>UA名</th><th>回数</th><th>説明</th></tr>\n";
    my @keys=sort{$das{$b}<=>$das{$a}} keys(%das);
    my($no,$last,$no2);
    foreach my $da (@keys){
      $no++;
      if($last != $das{$da}){
        $no2=$no;
      }
      my $ualink="$cgi?f=$in{'f'}&amp;c=0&amp;i=$in{'i'}&amp;r=$in{'r'}&amp;u=$da&amp;cu=1";
			my($type,$comm,$url) = ('','','');
			if(defined($denyua{$da})){
				$type=${$denyua{$da}}[0];
				$comm=${$denyua{$da}}[1];
				$url=${$denyua{$da}}[2];
			}
			elsif(defined($denyhost{$da})){
				$type=${$denyhost{$da}}[0];
				$comm=${$denyhost{$da}}[1];
				$url=${$denyhost{$da}}[2];
			}
      print "<tr><th>$no2</th><th align='left'><a href='$ualink'>$da</a></th>";
      print "<td>$das{$da}</td><td>[$uatype{$type}] $comm";
      print " (<a href='$url'>参考 URL</a>)" if($url);
      print "</td></tr>\n";
      $last=$das{$da};
    }
    print "</table>\n<p>$uacomm</p>\n";
  }
  print "<a href='$cgi?'>一覧</a><br>\n";
}

#--------------------------------------------------------------------
sub RawView{
  my $log=$logdir.'/'.$in{'f'}.'.log';
  unless(open(LOG,$log)){
    &Error("$log がオープンできません",$!);
    return;
  }
  print &Title;
  print '<pre>';
  while(my $str=<LOG>){
    if($jcodever){
      my $code=&Jgetcode(\$str);
      &Jconvert(\$str, 'sjis', $code) if($str && $code ne 'sjis');
    }
    $str=&DisTag($str);
    print $str;
  }
  print "</pre><hr>\n";
  print "<a href='$cgi?'>一覧</a><br>\n";
}
#--------------------------------------------------------------------
sub Error{
  my($msg1,$msg2)=@_;
  print "<h1>エラー</h1>\n";
  print "<dl><dt>$msg1</dt><dd>$msg2</dd></dl>\n";
}
#----------------------------------------------------------
# DisTag; タグを無効にする
sub DisTag{
  my @tr=(['&','&amp;'],['<','&lt;'],['>','&gt;'],
    ['"','&#34;'],["'",'&#39;']);
  if(ref($_[0]) eq 'SCALAR'){
    foreach my $tr (@tr){
      ${$_[0]}=~s/${$tr}[0]/${$tr}[1]/g;
    }
  }
  else{
    my $str=$_[0];
    foreach my $tr (@tr){
      $str=~s/${$tr}[0]/${$tr}[1]/g;
    }
    return $str;
  }
}
#--------------------------------------------------------------------
# GetTime;localtime 時間文字列を返す
sub GetTime {
	my($tm,$mode)=@_;
	my($sec, $min, $hour, $day, $mon, $year, $wday, $yday, $isdst) = localtime($tm);
	$mon++;
	$year+=1900;
	if(wantarray){
		return ($sec, $min, $hour, $day, $mon, $year);
	}
	else{
    if($mode eq 'd'){
      return sprintf("%04d/%02d/%02d",$year,$mon,$day);
    }
    if($mode eq 't'){
      return sprintf("%02d:%02d",$hour,$min);
    }
    else{
      return sprintf("%04d/%02d/%02d %02d:%02d",$year,$mon,$day,$hour,$min);
    }
  }
}
#----------------------------------------------------------

1;
