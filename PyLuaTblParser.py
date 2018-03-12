"""
Created by Deng,Xi on 2017.02.26
Parser of LuaTable

#expr:    LBR term (COMMA term)* RBR
#term:    factor | key EQUAL factor 
#factor:  NUMBER | STRING | BOOL | NULL | expr | COMMENTS
#key:     NUMBER | STRING

"""

NUMBER, STRING, COMMA, EOF, BOOL, LBR, RBR, NULL, EQUAL, EMPTY, EMPTYLIST  = 'NUMBER','STRING','COMMA','EOF','BOOL','LBR','RBR','NULL','EQUAL', 'EMPTY', 'EMPTYLIST'


class Token(object):
	# token type: NUMBER, STRING, COMMA, EOF, BOOL, LBR, RBR, NULL, EQUAL
	# token value: 0-9 ascI , { }  NONE or =
	def __init__(self, type, value):
		self.type = type;
		self.value = value;

	def __str__(self):
		""" string representation """
		return 'Token: {type}, {value}'.format(
			 type  = self.type,
			 value = repr(self.value)
			)

	def __repr__(self):
		return self.__str__()

#######################################################
########				Lexer    			 ##########
#######################################################
class Lexer(object):
	def __init__(self, text):
		self.text = text
		self.pos = 0
		self.pre_char = ''
		self.current_char = self.text[self.pos]

	def error(self):
		raise Exception('Invalid character')

	def advance(self):
		""" move the pos pointer one step forward and set to the current_char """
		self.pos += 1;
		if self.pos > len(self.text) - 1:
			self.current_char = None #input end
		else:
			self.pre_char = self.current_char
			self.current_char = self.text[self.pos]
			

	def is_space(self,c):
		if ' ' == c or '\t' == c or '\n' == c or '\r' == c:
			return True
		return False

	def skip_space(self):
		while self.current_char is not None and self.is_space(self.current_char):
			self.advance()

	def mutiline(self):
		"""
			prase the braket of comments
		"""
		if self.current_char != '[':
			return ''
		else:
			braket = []
			braket.append('[')
			self.advance()
			while self.current_char is not None and self.current_char == '=':
				braket.append('=')
				self.advance()
			if self.current_char is not None and self.current_char == '[':
				braket.append('[')
				self.advance()
				return ''.join(braket)
			return ''

	def invert_braket(self,braket):
		rb = braket[:].replace('[', ']')
		return rb

	def parse_comments(self): 
		"""
			skipcomments in input
			singleline: -- 
				multiline: --[(=)*[  
				multilines
			](=)*]
		"""
		braket = self.mutiline()
  		if braket == '':
			while self.current_char is not None and self.current_char != '\n' and self.current_char != '\r':
					self.advance()
		else:
			rb = self.invert_braket(braket)
			while self.current_char is not None and self.pos < len(self.text) - len(braket) and rb != self.text[self.pos : self.pos + len(braket)]:
					self.advance()
			for t in braket:
				self.advance()
		if self.is_space(self.current_char):
			self.skip_space()


	def is_otherend(self, slash_count):
		"""
		Check if this is the end of _LeOther factor
		"""
		if (self.current_char == ',' or self.current_char == '}' or self.current_char == '=' or self.current_char == ']') and slash_count == 0:
			return True
		return False

	def is_strend(self, slash_count, begin_char):
		"""
		Check if this is end of a string input
		"""
		if (self.current_char == begin_char) and slash_count == 0:
			return True
		return False

	def is_number(self, s):
		"""
		Check wether the string is a number 
		Return: True or False
		"""
		try:
			float(s)
			return True
		except ValueError:
			pass
		return False

	def is_int(self, s):
		try:
			int(s)
			return True
		except ValueError:
			pass
		return False

	def __LeString(self, begin_char):
		"""return a string """
		slash = 0
		ret = []
		while self.current_char is not None and False == self.is_strend(slash, begin_char):
			if self.current_char == '\\':
				if slash == 0:
					slash = 1
				else:
					slash = 0
			elif slash == 1:
				slash = 0
			if self.current_char != '\t' and self.current_char != '\n':
				ret.append(self.current_char)
			self.advance()
		self.advance()
		return ''.join(ret)

	def __LeOther(self):
		"""return a string that represent a factor which could be: number, string, nil, boolean"""
		slash = 0
		ret = []
		while self.current_char is not None and False == self.is_otherend(slash):
			if self.current_char == '\\':
				if slash == 0:
					slash = 1
				else:
					slash = 0
			elif slash == 1:
				slash = 0
			if False == self.is_space(self.current_char):
				ret.append(self.current_char)
			self.advance()
		return ''.join(ret)

	def __LeKey(self):
		"""return a key factor that could only be number or a string"""
		ret = ''
		self.skip_space()
		if self.current_char == '\'' or self.current_char == '\"':
			begin_char = self.current_char
			self.advance()
			ret = Token(STRING, self.__LeString(begin_char))

		else:
			s = self.__LeOther()
			if self.is_number(s):
				if self.is_int(s):
					ret =  Token(NUMBER, int(s))
				else:
					ret =  Token(NUMBER, float(s))
			else:
				self.error()
		self.skip_space()
		self.advance()
		return ret


	def tokenizer(self):
		""" this break the input into tokens, return one token at a time """
		while self.current_char is not None:
			if self.is_space(self.current_char):
				self.skip_space()
				continue

			# skipcomments
			if self.pos < len(self.text) - 2 and "--" == self.text[self.pos:self.pos+2]:
				self.advance()
				self.advance()
				self.parse_comments()
				continue


			if self.current_char == '{' and self.pre_char != '\\':
				self.advance()
				return Token(LBR, '{')

			if self.current_char == '}' and self.pre_char != '\\':
				self.advance()
				return Token(RBR, '}')

			if self.current_char == ',' or self.current_char == ';' and self.pre_char != '\\':
				self.advance()
				return Token(COMMA, self.current_char)

			if self.current_char == '=' and self.pre_char != '\\':
				self.advance()
				return Token(EQUAL, '=')

			# Lexer 'string' and "string"
			if self.current_char == '\'' or self.current_char == '"':
				begin_char = self.current_char
				self.advance()
				return Token(STRING, self.__LeString(begin_char))

			# Lexer key in the braket []
			if self.current_char == '[':
				self.advance()
				return self.__LeKey()

			# Lexer factors: bool, int, float, 
			cur_str = self.__LeOther()
			s = cur_str
			if self.is_number(s):
				if self.is_int(cur_str):
					return Token(NUMBER, int(cur_str))
				else:
					return Token(NUMBER, float(cur_str))
			elif cur_str == "false":
				return Token(BOOL, False)
			elif cur_str == "true":
				return Token(BOOL, True)
			elif cur_str == "nil":
				return Token(NULL, cur_str)
			elif cur_str == '':
				return Token(EMPTY, cur_str)
			else:
				return Token(STRING, cur_str)


		return Token(EOF, None)

#######################################################
########				Parser				 ##########
#######################################################

class AST(object):
	pass

class Leaf(AST):
	def __init__(self, token):
		self.token = token
		self.value = token.value

class Node(AST):
	def __init__(self, token, child):
		self.token = token
		self.child = child


class Link(AST):
	def __init__(self, left,token, right):
		self.left = left
		self.token = token
		self.right = right
		self.pretoken = token


class Parser(object):
	def __init__(self, text):
		self.lexer = Lexer(text)
		self.tokenlist = []
		self.current_token = self.lexer.tokenizer()
		self.index = 0

	def error(self):
		raise Exception('Invalid syntax')

	def eat(self, token_type):
		if self.current_token.type == token_type:
			self.pretoken = self.current_token
			self.tokenlist.append(self.current_token)
			self.current_token = self.lexer.tokenizer()
		else:
			self.error()

	def factor(self):
		"""factor:  NUMBER | STRING | BOOL | NULL | expr """
		token = self.current_token

		if token.type == NUMBER or token.type == STRING or token.type == NULL:
			self.eat(token.type)
			if self.current_token.type == EQUAL:
				self.eat(EQUAL)
				if self.current_token.type == LBR:
					return Link(Leaf(token), Token(EQUAL,'='), self.expr())
				else:
					return Link(Leaf(token), Token(EQUAL,'='), self.factor())
			else:
			    return Leaf(token)

		if token.type == LBR:
			node = self.expr()
			return node

		if token.type == COMMA:
			self.eat(COMMA)
			return Leaf(Token(EMPTY,[]))

		if token.type == RBR:
			pretoken = self.pretoken
			if pretoken.type is LBR:
				return Leaf(Token(EMPTYLIST, []))
			else:
				return Leaf(Token(EMPTY,[]))

		if token.type == BOOL:
			self.eat(BOOL)
			return Leaf(Token(BOOL, token.value))

		else:
			self.error()



	def expr(self):
		""" #expr:    LBR term (COMMA term)* RBR """
		self.eat(LBR)
		node = self.factor()
		while self.current_token.type is COMMA:
			self.eat(COMMA)
			
			node = Link(node, Token(COMMA, ','), self.factor())

		self.eat(RBR)
		node = Node(Token(LBR, '{'), node)
		return node

#######################################################
########			Interpreter              ##########
#######################################################
 
class VisitNode(object):
	def visit(self, node):
		func = 'visit_' + type(node).__name__
		visitor = getattr(self, func, self.visit_error)
		return visitor(node)

	def visit_error(self, node):
		raise Exception('No {} node function'.format(type(node).__name__))


class Interpreter(VisitNode):
	def __init__(self, parser):
		self.parser = parser
		self.key = 1

	def error(self,error_info):
		raise Exception('Invalid character'+ error_info)

	def isinkey(self, key, keys):
		if key in keys:
			return True
		else:
			return False

	def isfactor(self, cur_str):
		if isinstance(cur_str,str) or isinstance(cur_str, float) or isinstance(cur_str, int) or isinstance(cur_str, bool) or cur_str is None:
			return True
		return False

	def combine_Factor(self, left, right):
		if self.isfactor(left) and self.isfactor(right):
			re = []
			re.append(left)
			re.append(right)
			return re
		elif isinstance(left, list) and self.isfactor(right):
			left.append(right)
			return left
		elif isinstance(right, list) and self.isfactor(left):
			ret = []
			ret.append(left)
			ret.append(right)
			return ret
		elif isinstance(left, list) and isinstance(right, list):
			return sum([left, right],[])
		elif isinstance(left, dict) and isinstance(right, dict):
			left.update(right)
			return left
		elif isinstance(left, dict) and self.isfactor(right):
			if right is not None:
				keys= left.keys()
				while self.isinkey(self.key, keys):
					self.key += 1
				left[self.key] = right
				self.key += 1
			return left
		elif isinstance(right, dict) and self.isfactor(left):
			if left is not None:
				keys = right.keys()
				while self.isinkey(self.key, keys):
					self.key += 1
				ret = {}
				ret[self.key] = left
				self.key += 1
				ret.update(right)
			return ret
		elif isinstance(left, dict) and isinstance(right, list):
			rdict = {}
			keys = left.keys()
			for r in right:
				if r is None:
					continue
				else:
					while self.isinkey(self.key, keys):
						self.key += 1
					rdict[self.key] = r
					self.key+=1
			left.update(rdict)
			return left
		elif isinstance(right, dict) and isinstance(left, list):
			ldict = {}
			keys = right.keys()
			for l in left:
				if l is None:
					continue
				else:
					while self.isinkey(self.key, keys):
						self.key += 1
					ldict[self.key] = l
					self.key+=1
			ldict.update(right)
			return ldict
		else:
			li = []
			li.append(left)
			li.append(right)
			return li

	def brace(self,item):
		if isinstance(item, dict):
			ret = {}
			ret[self.key] = item
			self.key += 1
			return ret
		else:
			ret = []
			ret.append(item)
			return ret

	def visit_Node(self, node):
		return self.visit(node.child)

	def visit_Link(self, node):
		if node.token.type == COMMA:
			if node.left.token.type is EMPTY:
				return right
			left = self.visit(node.left)
			right = self.visit(node.right)

			if node.left.token.type == LBR:
				left = self.brace(left)
			if node.right.token.type == LBR:
				right = self.brace(right)
			if node.right.token.type is EMPTY:
				return left
			return self.combine_Factor(left,right)


		if node.token.type == EQUAL:
			dic = {}
			key = self.visit(node.left)
			if self.is_LegalKey(key):
				dic[key] = self.visit(node.right)
				return dic
			else:
				self.error(' invalid dict key type')

	def visit_Leaf(self, node):
		if node.token.type == NULL:
		 	return None
		return node.value

		# check whether the key has legal value
	def is_LegalKey(self,key):
		if isinstance(key, str) or isinstance(key, int) or isinstance(key, float):
			return True
		return False

	def interpret(self):
		ast = self.parser.expr()
		return self.visit(ast)


#######################################################
########			PyLuaTblParser			###########
#######################################################
class PyLuaTblParser(object):
	def __init__(self):
		self.data = {}


	def load(self, s):
		"""
		Input string s satisfy lua table defination
		no return value
		raise error when syntax error happen
		"""
		self.lua_str = s
		parse = Parser(s)
		interpret = Interpreter(parse)
		self.data = interpret.interpret()

	def dump(self):
		"""
		Return: lua table string according to the data in class
		"""
		if isinstance(self.data, dict):
			return self.__Dict2String(self.data)
		else:
			return self.__List2String(self.data)

	def loadLuaTable(self, f):
		"""
		Read lua string from file, 
		Param: f is the path of file
		raise error when syntax error happen
		"""
		with open(f,'r') as file:
			lua_str = file.read()
			self.load(lua_str)
		file.close()

	def dumpLuaTable(self, f):
		"""	Write content as Lua table format to file, f is the path 
		"""
		with open(f,'w') as file:
			file = open(f, 'w')
			file.write(self.dump())
		file.close()


	def loadDict(self,d):
		"""
		Read data in d and save it to the class
		Param: d is a dict or list
		the key of dict is num, string ortherwise, ignore it
		"""
		if isinstance(d, dict):
			self.data= self.__TraceDict(d)
		elif isinstance(d, list):
			self.data = []
			for val in d:
				self.data.append(val)
		else:
			self.__error('Invalid format of dictionary')


	def dumpDict(self):
		"""Return: a dict that contain information of class"""
		if isinstance(self.data, dict):
			ret = {}
			for key,value in self.data.items():
				ret[key] = value
		else:
			ret = []
			for value in self.data:
				ret.append(value)
		return ret

	def update(self, d):
		"""
		Update self.data with dictionary
		Param: d dictionary used to update
		"""
		if isinstance(d, dict) and isinstance(self.data, dict):
			dic = self.__TraceDict(d)
			self.data.update(dic)
		else:
			self.error("Wrong Format")


	def __error(self, error_info):
		raise Exception('Error: '+ error_info)

	def __TraceDict(self, d):
		dic = {}
		for key, value in d.items():
			if (isinstance(key, float) or isinstance(key, int) or isinstance(key, str)) and value is not None:
				if isinstance(value, dict):
					dic[key] = self.__TraceDict(value)
				else:
					dic[key] = value
		return dic


	def __Value2Luastr(self,value):
		if value is False:
			return 'false'
		elif value is True:
			return 'true'
		elif value is None:
			return 'nil'
		elif isinstance(value, str):
			value = value[:].replace('\'','\\\'')
			ret = '"' + value[:].replace('\"','\\\"') + '"'
			return ret
		return str(value)


	def __Dict2String(self, dic):
		ret = []
		ret.append('{')
		for key, value in dic.items():
			ret.append('[')
			ret.append(self.__Value2Luastr(key))
			ret.append(']')
			ret.append('=')
			if isinstance(value, list):
				ret.append(self.__List2String(value))
			elif isinstance(value, dict):
				ret.append(self.__Dict2String(value))
			else:
				ret.append(self.__Value2Luastr(value))
			ret.append(',')
		if ret[-1] == ',':
			ret = ret[:-1]
		ret.append('}')
		return ''.join(ret)

	def __List2String(self,lis):
		ret = []
		ret.append('{')
		for value in lis:
			if isinstance(value, list):
				ret.append(self.__List2String(value))
			else:
				ret.append(self.__Value2Luastr(value))
			ret.append(',')
		if ret[-1] == ',':
			ret = ret[:-1]
		ret.append('}')
		return ''.join(ret)


