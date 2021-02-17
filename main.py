import os
import re
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials

class GoogleDrive:
	def __init__(self,key_file,folder_id):
		scope = ['https://www.googleapis.com/auth/drive.file']
		credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file, scopes=scope)
		self.service = build("drive", "v3", credentials=credentials, cache_discovery=False)
		self.parents = folder_id
		self.folder_info = {}

	def add_info(self,folder_name,folder_id):
		if folder_name in self.folder_info:
			raise Exception("既に登録されています。")
		else:
			self.folder_info[folder_name] = folder_id

	def get_link(self,f_id):
		return f"https://drive.google.com/drive/folders/{f_id}"

	def get_meta(self,name,folder_id=False,mimeType=False):
		if folder_id:
			data = {"name": name, "parents": [folder_id]}
		else:
			data = {"name": name, "parents": [self.parents]}
		if mimeType:
			data["mimeType"] = mimeType
		return data

	def upload(self,file_path,folder_id=False,mimeType=False):
		#ファイルの存在チェック
		if not os.path.isfile(file_path) and mimeType==False:
			raise Exception(f"{file_path}が存在しません。")
		params = {"name": os.path.basename(file_path)}
		if folder_id:
			params["folder_id"] = folder_id
		if mimeType:
			params["mimeType"] = mimeType
		meta = self.get_meta(**params)
		media = MediaFileUpload(file_path, resumable=True)
		file = self.service.files().create(body=meta, media_body=media, fields='id,kind').execute()
		return file["id"]

	def create_folder(self,name):
		meta = self.get_meta(name,mimeType="application/vnd.google-apps.folder")
		file = self.service.files().create(body=meta, fields='id,kind').execute()
		self.add_info(name,file["id"])
		return file["id"]

	def exist_folder(self,folder_name):
		query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and '{self.parents}' in parents and trashed = false"
		res = self.service.files().list(fields="files(id,name)",q=query).execute()
		if len(res["files"])==0:
			return False
		elif len(res["files"])==1:
			file_id = res["files"][0]["id"]
			self.add_info(folder_name,file_id)
			return file_id
		else:
			raise Exception("複数のフォルダーが存在します。")

	def exist_folder2(self, folder_name):
		if folder_name in self.folder_info:
			return self.folder_info[folder_name]
		else:
			return self.exist_folder(folder_name)

	def delete(self,folder_id):
		res = self.service.files().delete(fileId = folder_id).execute()

	def delete_all(self):
		res = self.service.files().list(fields="files(id,name)",q="").execute()
		for item in res["files"]:
			self.delete(item["id"])

	def add_file(self,folder_name, file_path):
		folder_id = self.exist_folder2(folder_name)
		if folder_id==False:
			folder_id = self.create_folder(folder_name)
		file_id = self.upload(file_path=file_path,folder_id=folder_id)
		data = {"folder_url":self.get_link(folder_id)}
		return data

