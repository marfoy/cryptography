#!/usr/bin/python3
exec(open("/home/mrt/.startup.py").read())
from openssl import *
import os
import ast
import base64
import json
import urllib.request
import urllib.parse
import urllib.error
import time

# Ceci est du code Python v3.x (la version >= 3.4 est conseillée pour une
# compatibilité optimale).
# --- les admins

class ServerError(Exception):
    """
    Exception déclenchée en cas de problème côté serveur (URL incorrecte,
    accès interdit, requête mal formée, etc.)
    """
    def __init__(self, code=None, msg=None):
        self.code = code
        self.msg = msg


class Connection:
    """
    Cette classe sert à ouvrir et à maintenir une connection avec le système
    UGLIX. Voir les exemples ci-dessous.

    Pour créer une instance de la classe, il faut spécifier une ``adresse de 
    base''. Les requêtes se font à partir de là, ce qui est bien pratique.
    L'adresse de base est typiquement l'adresse du système UGLIX.

    Cet objet Connection() s'utilise surtout via ses méthodes get(), post()...

    Il est conçu pour pouvoir être étendu facilement. En dériver une sous-classe
    capable de gérer des connexions chiffrées ne nécessite que 20 lignes de
    code supplémentaires.

    Exemple :
    >>> c = Connection("http://pac.fil.cool/uglix")
    >>> c.get('/bin/echo')
    'usage: echo [arguments]'
    """
    def __init__(self, base_url):
        self.base = base_url
        # au départ nous n'avons pas d'identifiant de session
        self.session = None

    def _post_processing(self, result, http_headers):
        """
        Effectue post-traitement sur le résultat "brut" de la requête. En
        particulier, on décode les dictionnaires JSON, et on convertit le texte
        (encodé en UTF-8) en chaine de charactère Unicode. On peut étendre cette
        méthode pour gérer d'autres types de contenu si besoin.
        """
        if http_headers['Content-Type'] == "application/json":
            return json.loads(result.decode())
        if http_headers['Content-Type'].startswith("text/plain"):
            return result.decode()
        # on ne sait pas ce que c'est : on laisse tel quel
        return result

    def _query(self, url, request, data=None):
        """
        Cette fonction à usage interne est appelée par get(), post(), put(),
        etc. Elle reçoit en argument une url et un objet Request() du module
        standard urllib.request.
        """
        try:
            # si on a un identifiant de session, on le renvoie au serveur
            if self.session:
                request.add_header('Cookie', self.session)
            # lance la requête. Si data n'est pas None, la requête aura un
            # corps non-vide, avec data dedans.
            with urllib.request.urlopen(request, data) as connexion:
                # récupère les en-têtes HTTP et le corps de la réponse, puis
                # ferme la connection
                headers = dict(connexion.info())
                result = connexion.read()
            
            # si on reçoit un identifiant de session, on le stocke
            if 'Set-Cookie' in headers:
                self.session = headers['Set-Cookie']

            # on effectue le post-processing, puis on renvoie les données.
            # c'est fini.
            return self._post_processing(result, headers)

        except urllib.error.HTTPError as e:
            # On arrive ici si le serveur a renvoyé un code d'erreur HTTP
            # (genre 400, 403, 404, etc.). On récupère le corps de la réponse
            # car il y a peut-être des explications dedans. On a besoin des
            # en-tête pour le post-processing.
            headers = dict(e.headers)
            message = e.read()
            raise ServerError(e.code, self._post_processing(message, headers)) from None
          
    
    def get(self, url):
        """
        Charge l'url demandée. Une requête HTTP GET est envoyée.

        >>> c = Connection("http://pac.fil.cool/uglix")
        >>> c.get('/bin/echo')
        'usage: echo [arguments]'

        En cas d'erreur côté serveur, on récupère une exception.
        >>> c.get('/bin/foobar') # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        client.ServerError: (404, ...)
        """
        # prépare la requête
        request = urllib.request.Request(self.base + url, method='GET')
        return self._query(url, request)


    def post(self, url, **kwds):
        """
        Charge l'URL demandée. Une requête HTTP POST est envoyée. Il est 
        possible d'envoyer un nombre arbitraire d'arguments supplémentaires
        sous la forme de paires clef-valeur. Ces paires sont encodées sous la
        forme d'un dictionnaire JSON qui constitue le corps de la requête.

        Python permet de spécifier ces paires clef-valeurs comme des arguments
        nommés de la méthode post(). On peut envoyer des valeurs de n'importe
        quel type sérialisable en JSON.

        Par exemple, pour envoyer un paramètre nommé "string_example" de valeur
        "toto et un paramètre nommé "list_example" de valeur [True, 42, {'foo': 'bar'}],
        il faut invoquer :

        >>> c = Connection("http://pac.fil.cool/uglix")
        >>> c.post('/bin/echo', string_example="toto", list_example=[True, 42, {'foo': 'bar'}])
        {'content_found': {'string_example': 'toto', 'list_example': [True, 42, {'foo': 'bar'}]}}

        L'idée est que la méthode post() convertit ceci en un dictionnaire JSON, qui 
        ici ressemblerait à :

        {'string_example': 'toto', 'list_example': [True, 42, {'foo': 'bar'}]},

        puis l'envoie au serveur.
        """
        # prépare la requête
        request = urllib.request.Request(self.base + url, method='POST')
        data = None
        # kwds est un dictionnaire qui contient les arguments nommés. S'il
        # n'est pas vide, on l'encode en JSON et on l'ajoute au corps de la
        # requête.
        if kwds:     
            request.add_header('Content-type', 'application/json')
            data = json.dumps(kwds).encode()
        return self._query(url, request, data)


    def put(self, url, content):
        """
        Charge l'URL demandée avec une requête HTTP PUT. L'argument content
        forme le corps de la requête. Si content est de type str(), il est
        automatiquement encodé en UTF-8. cf /doc/strings pour plus de détails
        sur la question.
        """
        request = urllib.request.Request(self.base + url, method='PUT')
        if isinstance(content, str):
            content = content.encode()
        return self._query(url, request, data=content)


    def post_raw(self, url, data, content_type='application/octet-stream'):
        """
        Charge l'url demandée avec une requête HTTP POST. L'argument data
        forme le corps de la requête. Il doit s'agir d'un objet de type 
        bytes(). Cette méthode est d'un usage plus rare, et sert à envoyer des
        données qui n'ont pas vocation à être serialisées en JSON (comme des
        données binaires chiffrées, par exemple).

        Principalement utilisé pour étendre le client et lui ajouter des
        fonctionnalité.
        """
        request = urllib.request.Request(self.base + url, method='POST')
        request.add_header('Content-type', content_type)
        return self._query(url, request, data)

    def close_session(self):
        """
        Oublie la session actuelle. En principe, personne n'a besoin de ceci.
        """
        self.session = None


def check_trans(c):
	cert_CA = c.get("/bin/banks/CA")
	sample = c.get("/bin/banks/forensics")
	id_lot = sample['identifier']
	card_numbers = sample['card-numbers']
	#card_numbers = ["6230-8700-4679-2413"] #FIXME
	trans = [c.get("/bin/banks/card-data/"+i) for i in card_numbers]
	valid_trans = []
	for t in trans:
		card_id = t['card-number']
		bank_name = t['bank-name']
		cert_card = t['card-certificate']
		cert_bank = t['bank-certificate']
		sign = t['signature']
		chal = t['challenge']
		chal = chal.strip()
		valid_trans.append(verify_sign(chal,cert_card,sign) and verify_cert(cert_card,cert_bank,cert_CA,bank_name,card_id))
		#valid_trans.append(verify_cert(cert_card,cert_bank,cert_CA,bank_name,card_id))
	return (id_lot,valid_trans)


def write(data,filename,byte):
	if(byte):
		f = open(filename,"wb")
	else:
		f = open(filename,"w")
	f.write(data)
	f.close()

env_var = {'security_level':'normal','session_key':'debug-me','gateway':'/bin/test-gateway'}

def cmd():
	c = Connection("http://pac.fil.cool/uglix")
	while 1:
		instruction = input(">> ")
		if(instruction in ["END","end","End"]):
			exit(0)
		command = parse_cmd(instruction)
		if(command[0] in globals()):
			#print(*filter(lambda x : x !={},command[1:]))
			res = globals()[command[0].lower()](c,*filter(lambda x : x !={},command[1:]))
			if(res != None):
				print(res)
		elif(command[0] in env_var.keys()):
			env_var[command[0]] = command[1]

def parse_cmd(command):
	command = command.split()
	http_request = command[0]
	if( http_request.lower() in ["get_crypt","post_crypt","put_crypt","get","post","put"]):
		command_name = command[1]
		arguments = command[2:]
		arg_dic = {}
		for arg in arguments:
			key_value = arg.split(':')
			arg_dic[key_value[0]] = eval(key_value[1])
		return [http_request,command_name,arg_dic]
	else:
		arguments = command[1:]
		arg_dic = {}
		for arg in arguments:
			key_value = arg.split(':')
			arg_dic[key_value[0]] = key_value[1]
		return [http_request,arg_dic]
def clear(client,args=None):
	os.system('tput reset')
def write(client,args):
	if(args['byte'] in ["True","true","TRUE","t"]):
		f = open(args['filename'],'wb')
	elif(args['byte'] in ["False","false","FALSE","f"]):
		f = open(args['filename'],'w')
	method = args['method']
	url = args['url']
	del args['filename']
	del args['method']
	del args['url']
	f.write(str(globals()[method](client,url,args)))
	f.close()
def get(client,command_name,args=None):
	return client.get(command_name)
def wait(client,args=None):
	time.sleep(2)
def get_crypt(client,command_name,args=None):
	dic_to_crypt = {}
	dic_to_crypt['method'] = "GET"
	dic_to_crypt['url'] = command_name
	response  = client.post_raw(env_var['gateway'],base64.b64decode(encrypt(json.dumps(dic_to_crypt),env_var['session_key'])))
	return decrypt(response,env_var['session_key'],base64=False).decode('utf-8')

def post(client,command_name,args):
	return client.post(command_name,**args)

def post_crypt(client,command_name,args=None):
	dic_to_crypt = {}
	dic_to_crypt['method'] = "POST"
	if(args != None):
		dic_to_crypt['args'] = args
	dic_to_crypt['url'] = command_name
	print("COMMAND" + command_name)
	response  = client.post_raw(env_var['gateway'],base64.b64decode(encrypt(json.dumps(dic_to_crypt),env_var['session_key'])))
	return decrypt(response,env_var['session_key'],base64=False).decode('utf-8')
def put(client,command_name,args):
	f = open(args['filename'],'rb')
	data = f.read()
	return client.put(command_name,data)
def put_crypt(client,command_name,args):
	dic_to_crypt = {}
	dic_to_crypt['method'] = "PUT"
	dic_to_crypt['data'] = base64.b64encode(args['data'].encode('utf-8')).decode('utf-8')
	dic_to_crypt['url'] = command_name
	response  = client.post_raw(env_var['gateway'],base64.b64decode(encrypt(json.dumps(dic_to_crypt),env_var['session_key'])))
	return decrypt(response,env_var['session_key'],base64=False)


def chap(client, args):
	chal = client.get("/bin/login/CHAP")["challenge"]
	env_var['username'] = args['user']
	env_var['password'] = args['password']
	plaintxt = encrypt(args['user'] + "-" + chal,args['password'])
	return client.post("/bin/login/CHAP",user=args['user'],response=plaintxt)
def stp(client, args):
	env_var['gateway'] = "/bin/stp/gateway"
	env_var['username'] = args['username']
	env_var['password'] = args['password']
	post_args = {"username": args['username']}
	nonce = post(client,"/bin/stp",post_args)
	env_var['session_key'] = args['password']+'-'+nonce
	print(env_var['session_key'])
	return get_crypt(client,"/bin/stp/handshake")
def stp_off(client,args=None):
	env_var['security_level'] = 'normal'
	env_var['session_key'] = 'debug-m'
	env_var['gateway'] = '/bin/test-gateway'
def authenticator(key):
	auth = {'username': env_var['username'],'timestamp': time.time()}
	return encrypt(json.dumps(auth), key)
def kerberos(client,args=None):
	tgt_dic = client.get("/bin/kerberos/authentication-service/{0}".format(env_var['username']))
	tgt = tgt_dic['TGT']
	key = decrypt(tgt_dic['Client-TGS-session-key'],env_var['password']).decode('utf-8')
	auth=authenticator(key)
	cst_dic = client.post('/bin/kerberos/ticket-granting-service',TGT=tgt,vm_name=args["vm"],authenticator=auth)
	key2 = decrypt(cst_dic["Client-Server-session-key"],key).decode('utf-8')
	auth2=authenticator(key2)
	env_var['session_key'] = key2
	env_var['gateway'] = '/bin/uVM/{0}/gateway'.format(args['vm'])
	cst = client.post("/bin/uVM/{0}/hello".format(args['vm']),ticket=cst_dic["Client-Server-ticket"],authenticator=auth2)
	return cst

cmd()
