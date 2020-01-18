# encoding=utf-8
import requests, sys, os, re, time
from optparse import OptionParser

class wget:
	def __init__(self, config = {}):
		self.config = {
			'block': int(config['block'] if 'block'in config else 1024),
		}
		self.total = 0
		self.size = 0
		self.filename = ''

	def touch(self, filename):
		with open(filename, 'w') as fin:
			pass

	def remove_nonchars(self, name):
		(name, _) = re.subn(r'[\\\/\:\*\?\"\<\>\|]', '', name)
		return name

	def support_continue(self, url):
		headers = {
			'Range': 'bytes=0-4'
		}
		try:
			r = requests.head(url, headers = headers)
			crange = r.headers['content-range']
			self.total = int(re.match(r'^bytes 0-4/(\d+)$', crange).group(1))
			return True
		except:
			pass
		try:
			self.total = int(r.headers['content-length'])
		except:
			self.total = 0
		return False


	def download(self, url, filename, headers = {}):
		finished = False
		block = self.config['block']
		local_filename = self.remove_nonchars(filename)
		tmp_filename = local_filename + '.downtmp'
		size = self.size
		total = self.total
		if self.support_continue(url):  # 支持断点续传
			try:
				with open(tmp_filename, 'rb') as fin:
					self.size = int(fin.read())
					size = self.size + 1
			except:
				self.touch(tmp_filename)
			finally:
				headers['Range'] = "bytes=%d-" % (self.size, )
		else:
			self.touch(tmp_filename)
			self.touch(local_filename)

		r = requests.get(url, stream = True, verify = False, headers = headers)
		if total > 0:
			print("[+] Size: %dKB" % (total / 1024))
		else:
			print("[+] Size: None")
		start_t = time.time()
		with open(local_filename, 'ab+') as f:
			f.seek(self.size)
			f.truncate()
			try:
				for chunk in r.iter_content(chunk_size = block):
					if chunk:
						f.write(chunk)
						size += len(chunk)
						f.flush()
					sys.stdout.write('\b' * 64 + 'Now: %d, Total: %s' % (size, total))
					sys.stdout.flush()
				finished = True
				os.remove(tmp_filename)
				spend = int(time.time() - start_t)
				speed = int((size - self.size) / 1024 / spend)
				sys.stdout.write('\nDownload Finished!\nTotal Time: %ss, Download Speed: %sk/s\n' % (spend, speed))
				sys.stdout.flush()
			except:
				# import traceback
				# print traceback.print_exc()
				print("\nDownload pause.\n")
			finally:
				if not finished:
					with open(tmp_filename, 'wb') as ftmp:
						ftmp.write(str(size))

if __name__ == "__main__":
    url = 'https://github.com/vinta/awesome-python.git'
    wget().download(url,'55')
