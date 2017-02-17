import re
import unicodedata

carlos_dict = {}
postalcodes = {}
count_diap = count_comarca = count_appeal = 0


csv_output = True

# from 'carlos' file read the cities, their comarcas and their diaps
def read_carlos():
	filename = "carlos-file-small.csv"

	with open(filename, "r") as f:
		data = f.readlines()

	for i in range(1,len(data)):
		line = data[i].strip()
		words = line.split(",")
		# print words[0]
		carlos_dict[words[0].strip()]=[words[1].strip(), words[2].strip()]


#read postal codes from what was exported from Atlas
def read_postalcodes():
	filename = "portugal-localities-pc.csv"

	with open(filename, "r") as f:
		data = f.readlines()

	current_city = ""
	current_pc = ""
	for i in range(1, len(data)):
		line = data[i].strip()
		words = line.split(",")
		city =  words[0]
		words = words[1].split("-")
		pc = words[0]
		if current_city != city or pc != current_pc:
			postalcodes.setdefault(city,[]).append(pc)
		current_city = city
		current_pc = pc

#read postal codes from wikipedia page
def read_postalcodes_2():
	filename = "all_pc_loc.txt"

	with open(filename, "r") as f:
		data = f.readlines()

	for line in data:
		line = line.strip();
		words = line.split(" - ");
		if words[1]:
			city=words[1]
			pc=words[0]
			postalcodes.setdefault(city, []).append(pc)

# make strings ready for comparison
def normalize_string(word):
	return unicodedata.normalize('NFC', word.decode('utf-8')).lower()

#find postal code is city
def find_pc(city, root_pc):
	if city in postalcodes:
		if len(postalcodes[city])==1:
			return postalcodes[city][0]
		for pc in postalcodes[city]:
			if root_pc[:2]==pc[:2]:
				return pc
		for pc in postalcodes[city]:
			if root_pc[:1]==pc[:1]:
				return pc
		return postalcodes[city][0]+' ##'
	return "####"

# finding DIAP
def find_diap(match_city):
	match_city = normalize_string(match_city)
	for city in carlos_dict:
		test = normalize_string(city)
		if test==match_city:
			return carlos_dict[city][1]
	return "####"

# from 'silvia' files read all localities
def read_silvia(filename):
	global count_appeal, count_comarca, count_diap
	count_appeal += 1
	with open(filename, "r") as f:
		data = f.readlines()

	diap = freguesia = city = comarca = postalcode_city =  ""
	tribunal = re.sub(r"TRIBUNAL DA RELA.*O D.+ ", "", data[0].strip())

	for i in range(1,len(data)):
		line = data[i].strip()
		s1 = re.search(r".*COMARCA D[EOAS]+ (.*)", line, re.M|re.I)
		s2 = re.search(r".*- (.*) -.*([0-9]{4,4}).*", line, re.M|re.I)
		freguesia =   ""
		if s1:
			comarca = s1.group(1)
			count_comarca += 1
			# print "%s\n  --COMARCA: %s" % (line,s1.group(1))
		elif s2:
			city = s2.group(1)
			postalcode_city = s2.group(2)
			diap = find_diap(city)
			count_diap += 1
			freguesia = city
			postalcode_fregusia = postalcode_city
			# if diap == '????':
				# print tribunal, comarca,city, postalcode_city, diap
		else:
			freguesia = line
			postalcode_fregusia = find_pc(freguesia, postalcode_city)
			# print "       |          fr.: %s" % line
			if freguesia == city:
				continue  # skip city itself, already taken care of!

		if freguesia!="" :
			if not csv_output:
				print "%-35s%-6s%-22s%-22s%-35s%s" % (freguesia, postalcode_fregusia, "tr:"+tribunal, "com:"+comarca, "diap:"+diap, city+" ("+postalcode_city+")")
			else:
				flag = ""
				if "#" in postalcode_fregusia:
					flag = "CHECK"
				print "%s,%s,%s,%s,%s,%s,%s" % (freguesia, postalcode_fregusia, flag, city, diap, comarca,  tribunal)


read_postalcodes()
read_postalcodes_2()

read_carlos()
if not csv_output:
	print "%-35s%-6s%-22s%-22s%-35s%s" % ("FREGUSIA", "PC", "TRIBUNAL", "COMARCA", "DIAP", "CITY" )
	print "==============================================================================================================================================="
else:
	print "locality,pc_locality,flag,city,diap,comarca,tribunal"

read_silvia("coimbra.txt")
read_silvia("evora.txt")
read_silvia("guimaraes.txt")
read_silvia("lisbon.txt")
read_silvia("porto.txt")

# for city in postalcodes:
# 	print city, postalcodes[city]

# print ("Found courts of appeal: %d\nFound comarcas: %d\nFound diaps: %d" % (count_appeal, count_comarca, count_diap))
