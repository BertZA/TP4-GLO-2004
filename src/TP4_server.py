"""\
GLO-2000 Travail pratique 4 - Serveur
Noms et numéros étudiants:
- Bertrand Awenze : 536 883 612
- Michäel Tremblay : 537 040 140
- Joseph Eli Nyimilongo : 111 261 884
"""

import hashlib
import hmac
import json
import os
import select
import socket
import sys

import glosocket
import gloutils

import re

class Server:
    """Serveur mail @glo2000.ca."""

    def __init__(self) -> None:
        """
        Prépare le socket du serveur `_server_socket`
        et le met en mode écoute.

        Prépare les attributs suivants:
        - `_client_socs` une liste des sockets clients.
        - `_logged_users` un dictionnaire associant chaque
            socket client à un nom d'utilisateur.

        S'assure que les dossiers de données du serveur existent.
        """
        self._server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self._server_socket.bind(("localhost", gloutils.APP_PORT))
            self._server_socket.listen()

        except socket.error as e:
            sys.exit(-1)

        self._client_socs : list[socket.socket] = []
        self._logged_users : dict[socket.socket : str] = {}
        self._client_accounts: dict[str : str] = {}

        if  not os.path.exists(gloutils.SERVER_DATA_DIR):
            os.mkdir(gloutils.SERVER_DATA_DIR)

            if not os.path.exists(os.path.join(
                gloutils.SERVER_DATA_DIR, gloutils.SERVER_LOST_DIR)):
                os.mkdir(os.path.join(
                gloutils.SERVER_DATA_DIR, gloutils.SERVER_LOST_DIR))

    def cleanup(self) -> None:
        """Ferme toutes les connexions résiduelles."""
        for client_soc in self._client_socs:
            client_soc.close()
        self._server_socket.close()

    def _accept_client(self) -> None:
        """Accepte un nouveau client."""
        client, x = self._server_socket.accept()
        self._client_socs.append(client)
        #envoyer un message de bienvenue ici


    def _remove_client(self, client_soc: socket.socket) -> None:
        """Retire le client des structures de données et ferme sa connexion."""
        self._client_socs.remove(client_soc)
        self._logged_users.pop(client_soc)
        client_soc.close()

    def _create_account(self, client_soc: socket.socket,
                        payload: gloutils.AuthPayload
                        ) -> gloutils.GloMessage:
        """
        Crée un compte à partir des données du payload.

        Si les identifiants sont valides, créee le dossier de l'utilisateur,
        associe le socket au nouvel l'utilisateur et retourne un succès,
        sinon retourne un message d'erreur.
        """
        header : int = gloutils.Headers.ERROR
        msg : str = ""
        
        username : str = payload['username'].upper()
        password : str = payload['password']

        if re.search(r"\w", username) is not None:
            #vérifier nom pris ou pas
            if not os.path.exists(os.path.join(gloutils.SERVER_DATA_DIR, username)):
                if len(password) >= 10:
                    reg = re.compile(r'^(?=.*[0-9])(?=.*[A-Z])(?=.*[a-z]).+$')
                    #vérifier mot de passe
                    if reg.match(password):
                        #créer dossier utilisateur
                        os.mkdir(os.path.join(gloutils.SERVER_DATA_DIR, username))

                        pass_hash = hashlib.sha3_512()
                        pass_hash.update(password.encode('utf-8'))
                        password = pass_hash.hexdigest()

                        #écrire dans le fichier dans le dossier
                        with open(os.path.join(gloutils.SERVER_DATA_DIR, username,
                                   gloutils.PASSWORD_FILENAME), 'w') as password_file:
                            password_file.write(password)
                            password_file.close()

                        self._logged_users[client_soc] = username

                        return gloutils.GloMessage(header  = gloutils.Headers.OK,
                                                   payload = "")
                    else:
                        msg = "Mot de passe pas assez fort"
                else:
                    msg = "Mot de passe pas assez long"
            else:
                msg = "Nom d' utilisateur existant"
        else:
            msg = "Le nom d'utilisateur ne doit contenir que de caractères alphanuméques"

        return gloutils.GloMessage(header = header, payload = msg)

    def _login(self, client_soc: socket.socket, payload: gloutils.AuthPayload
               ) -> gloutils.GloMessage:
        """
        Vérifie que les données fournies correspondent à un compte existant.

        Si les identifiants sont valides, associe le socket à l'utilisateur et
        retourne un succès, sinon retourne un message d'erreur.
        """
        message: gloutils.GloMessage = gloutils.GloMessage( 
            header = gloutils.Headers.ERROR,
            payload= "Nom d'utilisateur introuvable"
        )

        username: str = payload['username'].upper()
        pass_hashed = hashlib.sha3_512()
        pass_hashed.update(payload['password'].encode('utf-8'))
        password :str = pass_hashed.hexdigest();

        if os.path.exists(os.path.join(gloutils.SERVER_DATA_DIR, username)):

            with open(os.path.join(gloutils.SERVER_DATA_DIR, username,
                                   gloutils.PASSWORD_FILENAME), 'r') as password_file:
                saved_password : str = password_file.read().strip()
                password_file.close()                

            if saved_password == password:
                self._logged_users[client_soc] = username
                message = gloutils.GloMessage(
                    header = gloutils.Headers.OK,
                    payload = ""
                )
            else:
                message["payload"] = "Mot de passe incorrect"
                
        return message

    def _logout(self, client_soc: socket.socket) -> None:
        """Déconnecte un utilisateur."""
        self._logged_users.pop(client_soc)


    def _get_email_list(self, client_soc: socket.socket
                        ) -> gloutils.GloMessage:
        """
        Récupère la liste des courriels de l'utilisateur associé au socket.
        Les éléments de la liste sont construits à l'aide du gabarit
        SUBJECT_DISPLAY et sont ordonnés du plus récent au plus ancien.

        Une absence de courriel n'est pas une erreur, mais une liste vide.
        """
        return gloutils.GloMessage()

    def _get_email(self, client_soc: socket.socket,
                   payload: gloutils.EmailChoicePayload
                   ) -> gloutils.GloMessage:
        """
        Récupère le contenu de l'email dans le dossier de l'utilisateur associé
        au socket.
        """
        return gloutils.GloMessage()

    def _get_stats(self, client_soc: socket.socket) -> gloutils.GloMessage:
        """
        Récupère le nombre de courriels et la taille du dossier et des fichiers
        de l'utilisateur associé au socket.
        """
        return gloutils.GloMessage()

    def _send_email(self, payload: gloutils.EmailContentPayload
                    ) -> gloutils.GloMessage:
        """
        Détermine si l'envoi est interne ou externe et:
        - Si l'envoi est interne, écris le message tel quel dans le dossier
        du destinataire.
        - Si le destinataire n'existe pas, place le message dans le dossier
        SERVER_LOST_DIR et considère l'envoi comme un échec.
        - Si le destinataire est externe, considère l'envoi comme un échec.

        Retourne un messange indiquant le succès ou l'échec de l'opération.
        """
        message : gloutils.GloMessage = gloutils.GloMessage(
            header = gloutils.Headers.ERROR,
            payload = "Impossible de communiquer avec une adresse externe"
        )

        #Est-ce un mail interne ?
        if payload["destination"].endswith("@" + gloutils.SERVER_DOMAIN):
            destination : str = payload["destination"].removesuffix("@" + gloutils.SERVER_DOMAIN).upper()
            source : str = payload["sender"].upper()
            subject : str = payload["subject"].lower()

            #Est-ce que la destination existe ?
            if os.path.exists(os.path.join(gloutils.SERVER_DATA_DIR, destination)):
                #écrire le mail
                with open(os.path.join(gloutils.SERVER_DATA_DIR, destination, source, subject)) as mail_file:
                    mail_file.write(json.dumps(payload))
                    mail_file.close
                    
                message = {"header" : gloutils.Headers.OK, 
                           "payload": "Mail envoyé avec succès"}
            else:
                message["payload"] = "Adresse de destination introuvable"

        return message

    def run(self):
        """Point d'entrée du serveur."""
        waiters = []
        while True:
            # Select readable sockets
            select_result = select.select([self._server_socket] + self._client_socs, 
                                   [], 
                                   [])
            waiters = select_result[0]

            for waiter in waiters:
                if waiter == self._server_socket:
                    print(type(waiter))
                    print(waiter)
                    self._accept_client()
                    print(self._client_socs)                    
                
                else:
                    try :
                        client_data = glosocket.recv_mesg(waiter)
                    except glosocket.GLOSocketError:
                        self._remove_client(waiter)
                        continue
                    
                    match json.loads(client_data):
                        case {"header" : gloutils.Headers.AUTH_LOGIN,
                              "payload" : payload}:
                            reply = self._login(waiter, payload)
                            glosocket.send_mesg(waiter, json.dumps(reply))
                        
                        case {"header" : gloutils.Headers.AUTH_LOGOUT}:
                            self._logout(waiter)

                        case {"header" : gloutils.Headers.AUTH_REGISTER,
                              "payload": payload}:
                            reply = self._create_account(waiter, payload)
                            glosocket.send_mesg(waiter, json.dumps(reply))
                        
                        case {"header" : gloutils.Headers.INBOX_READING_CHOICE}:
                            pass

                        case {"header" : gloutils.Headers.INBOX_READING_REQUEST}:
                            pass
                        case {"header"  : gloutils.Headers.STATS_REQUEST}:
                            pass
                        case {"header" : gloutils.Headers.EMAIL_SENDING}:
                            pass
                pass


def _main() -> int:
    server = Server()
    try:
        server.run()
    except KeyboardInterrupt:
        server.cleanup()
    return 0


if __name__ == '__main__':
    sys.exit(_main())
