import PyLuaTblParser

PyLuaTblParser = PyLuaTblParser.PyLuaTblParser

def main():
	while True:
		try:
			text = raw_input('lua>')
		except EOFError:
			break
		if not text:
			continue
		a1 = PyLuaTblParser()
		a1.load(text)
		print(a1.dump())

if __name__ == '__main__':
	main()