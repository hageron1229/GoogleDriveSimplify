# 使い方

## init

driver_option<br>
・ key_file: Googleのサービスアカウントのキー<br>
・ folder_id: データを置きたいGoogle Driveのフォルダのid

## 関数
基本的にadd_fileのみ<br>
・ add_file(フォルダ名,ファイルパス)<br>
...folder_idで指定したフォルダの中のフォルダ名のフォルダにファイルパスで指定したファイルをアップロードする。
（フォルダ名のフォルダがない時は自動で作成する）