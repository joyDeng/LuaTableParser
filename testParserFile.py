import ast
import PyLuaTblParser

PyLuaTblParser = PyLuaTblParser.PyLuaTblParser

def main():
	while True:
		try:
			luatext = raw_input('lua_filename>')
		except EOFError:
			break
		if not luatext:
			continue
		a1 = PyLuaTblParser()
		print(luatext)
		a1.loadLuaTable(luatext)
		print(a1.dump())
		try:
			wtext = raw_input('wirte_to_filename>')
		except EOFError:
			break
		if not wtext:
			continue
		a1.dumpLuaTable(wtext)

		try:
			dictext = raw_input('dict_filename>')
		except EOFError:
			break
		if not dictext:
			continue
		a2 = PyLuaTblParser()
		with open(dictext, 'r') as file:
			d = file.read()
			dic = ast.literal_eval(d)
		a2.loadDict(dic)
		print(a2.dumpDict())
		print(a2.dump())

if __name__ == '__main__':
	main()