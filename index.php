<?php
   class MyDB extends SQLite3
   {
      function __construct()
      {
         $this->open('Bing.db');
      }
   }
   $db = new MyDB();
   if(!$db){
      echo $db->lastErrorMsg();echo "Operation done successfully\n";
   } else {
      echo "Opened database successfully\n";
   }
   $sql ="SELECT * FROM sqlite_sequence WHERE name='Bing_info'";
   $ret = $db->query($sql);
   while($row = $ret->fetchArray(SQLITE3_ASSOC) ){
    $max_row = $row['seq'];  # 获取最大id值
   }
   $i = rand(1,$max_row);  # 生成随机数
   $sql ="SELECT * FROM Bing_info WHERE id='$i'";
   $ret = $db->query($sql);
   while($row = $ret->fetchArray(SQLITE3_ASSOC) ){
    $URL_1920X1080_via_COS = $row['URL_1920x1080_via_COS'];
   }
   echo "Operation done successfully\n";
   $db->close();
   header("Location: $URL_1920X1080_via_COS");
?>