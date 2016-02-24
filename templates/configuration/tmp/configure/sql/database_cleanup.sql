delete from mysql.user where User='root' AND Host not in ('localhost', '127.0.0.1', '::1');
delete from mysql.user where User='';
delete from mysql.db where Db='test' or Db='test\_%';
flush privileges;