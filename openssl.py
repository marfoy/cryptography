#!/usr/bin/python3

import base64
from subprocess import Popen, PIPE
# en cas de problème, cette exception est déclenchée
class OpensslError(Exception):
    pass

def ca(cert):
	args = ['openssl', 'x509', '-purpose', '-noout']
	pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

	if isinstance(cert, str):
		cert = cert.encode('utf-8')

	stdout, stderr = pipeline.communicate(cert)
	return b"CRL signing CA : Yes" in stdout

def subject(cert):
	args = ['openssl', 'x509', '-subject', '-noout']
	pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

	if isinstance(cert, str):
		cert = cert.encode('utf-8')

	stdout, stderr = pipeline.communicate(cert)
	return stdout.decode('utf-8')
def pubkey(cert):
	args = ['openssl', 'x509', '-pubkey', '-noout']
	pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

	if isinstance(cert, str):
		cert = cert.encode('utf-8')

	stdout, stderr = pipeline.communicate(cert)
	return stdout.decode('utf-8')
def verify_sign(chal,cert,sign):
	f = open("cert.pub","w")
	f.write(pubkey(cert))
	f.close()
	f = open("sign.bin","wb")
	f.write(base64.b64decode(sign))
	f.close()

	if isinstance(chal, str):
		chal = chal.encode('utf-8')

	args = ['openssl', 'dgst', '-sha256','-verify','cert.pub','-signature','sign.bin']

	pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
	stdout, stderr = pipeline.communicate(chal)

	return stderr == b'' and b"Failure" not in stdout



def verify_cert(card_cert,untrusted_cert,trusted_cert,bank_name,card_id):
	file_cert_untrusted = open("cert_untrusted","w")
	file_cert_untrusted.write(untrusted_cert)
	file_cert_untrusted.close()

	file_trusted = open("cert_trusted","w")
	file_trusted.write(trusted_cert)
	file_trusted.close()
	args = ['openssl', 'verify', '-trusted', 'cert_trusted','-untrusted','cert_untrusted']

	# l'encoder en bytes() pour pouvoir l'envoyer dans le pipeline vers 
	# openssl
	if isinstance(card_cert, str):
	    card_cert = card_cert.encode('utf-8')
	
	# ouvre le pipeline vers openssl. Redirige stdin, stdout et stderr
	#    affiche la commande invoquée
	#    print('debug : {0}'.format(' '.join(args)))
	pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
	
	# envoie plaintext sur le stdin de openssl, récupère stdout et stderr
	stdout, stderr = pipeline.communicate(card_cert)
	
	# si un message d'erreur est présent sur stderr, on arrête tout
	# attention, sur stderr on récupère des bytes(), donc on convertit
	error_message = stderr.decode()
	#print(subject(untrusted_cert), bank_name)
	return b"error" not in stdout and error_message == '' and bank_name in subject(untrusted_cert) and card_id in subject(card_cert) and ca(untrusted_cert)
	    #raise OpensslError(error_message)
def encrypt(plaintext, passphrase, cipher='aes-128-cbc',base64=True):
	"""invoke the OpenSSL library (though the openssl executable which must be
	   present on your system) to encrypt content using a symmetric cipher.

	   The passphrase is an str object (a unicode string)
	   The plaintext is str() or bytes()
	   The output is bytes()

	   # encryption use
	   >>> message = "texte avec caractères accentués"
	   >>> c = encrypt(message, 'foobar')
	"""
	# prépare les arguments à envoyer à openssl
	pass_arg = 'pass:{0}'.format(passphrase)
	if(base64):
		args = ['openssl', 'enc', '-' + cipher, '-base64', '-pass', pass_arg]
	else:
		args = ['openssl', 'enc', '-' + cipher, '-pass', pass_arg]
	# si le message clair est une chaine unicode, on est obligé de
	# l'encoder en bytes() pour pouvoir l'envoyer dans le pipeline vers 
	# openssl
	if isinstance(plaintext, str):
		plaintext = plaintext.encode('utf-8')
	# ouvre le pipeline vers openssl. Redirige stdin, stdout et stderr
	#    affiche la commande invoquée
	#    print('debug : {0}'.format(' '.join(args)))
	pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

	# envoie plaintext sur le stdin de openssl, récupère stdout et stderr
	stdout, stderr = pipeline.communicate(plaintext)

	# si un message d'erreur est présent sur stderr, on arrête tout
	# attention, sur stderr on récupère des bytes(), donc on convertit
	error_message = stderr.decode()
	if error_message != '':
		raise OpensslError(error_message)

	# OK, openssl a envoyé le chiffré sur stdout, en base64.
	# On récupère des bytes, donc on en fait une chaine unicode
	return stdout.decode()
def decrypt(crypted_msg, passphrase, cipher='aes-128-cbc', base64=True):
	pass_arg = 'pass:{0}'.format(passphrase)
	if(base64):
		args = ['openssl', 'enc','-d','-' + cipher, '-base64', '-pass', pass_arg]
	else:
		args = ['openssl', 'enc','-d','-' + cipher, '-pass', pass_arg]

	if isinstance(crypted_msg, str):
		crypted_msg = crypted_msg.encode('utf-8')

	pipeline = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

	stdout, stderr = pipeline.communicate(crypted_msg)

	error_message = stderr.decode()
	if error_message != '':
		print(error_message)
		raise OpensslError(error_message)

	return stdout

passwd = "coucou"
text = "jean est bon"
enc = encrypt(text,passwd)
#print(decrypt(enc,passwd).decode("utf-8"))
