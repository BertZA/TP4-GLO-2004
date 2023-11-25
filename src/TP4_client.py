"""\
GLO-2000 Travail pratique 4 - Client
Noms et numéros étudiants:
- Bertrand Awenze : 536 883 612
- Michäel Tremblay : 537 040 140
- Joseph Eli Nyimilongo : 111 261 884
"""

import argparse
import getpass
import json
import socket
import sys

import glosocket
import gloutils


class Client:
    """Client pour le serveur mail @glo2000.ca."""

    def __init__(self, destination: str) -> None:
        """
        Prépare et connecte le socket du client `_socket`.

        Prépare un attribut `_username` pour stocker le nom d'utilisateur
        courant. Laissé vide quand l'utilisateur n'est pas connecté.
        """
        self._client_socket : socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._client_socket.connect((destination, gloutils.APP_PORT))
        except socket.error :
            sys.exit(-1)    
        self._username : str = ""

    def _register(self) -> None:
        """
        Demande un nom d'utilisateur et un mot de passe et les transmet au
        serveur avec l'entête `AUTH_REGISTER`.

        Si la création du compte s'est effectuée avec succès, l'attribut
        `_username` est mis à jour, sinon l'erreur est affichée.
        """

    def _login(self) -> None:
        """
        Demande un nom d'utilisateur et un mot de passe et les transmet au
        serveur avec l'entête `AUTH_LOGIN`.

        Si la connexion est effectuée avec succès, l'attribut `_username`
        est mis à jour, sinon l'erreur est affichée.
        """
        username : str = str(input("\nNom d'utilisateur\t:>>> "))
        user_password : str = getpass.getpass(f"Mot de passe{' ' * 5}\t:>>> ")

        user_auth : gloutils.AuthPayload = gloutils.AuthPayload(username = username,
                                                                password = user_password)
        login_request : gloutils.GloMessage = gloutils.GloMessage(header = gloutils.Headers.AUTH_LOGIN,
                                                                  payload = user_auth)


        glosocket.send_mesg(self._client_socket, 
                            json.dumps(login_request)
                            )

        response : str = glosocket.recv_mesg(self._client_socket)
        response : gloutils.GloMessage = json.loads(response)

        if response["header"] != gloutils.Headers.OK:
            print(f"\033[1;31m\n{response['payload']}\033[0m")
        

    def _quit(self) -> None:
        """
        Préviens le serveur de la déconnexion avec l'entête `BYE` et ferme le
        socket du client.
        """

    def _read_email(self) -> None:
        """
        Demande au serveur la liste de ses courriels avec l'entête
        `INBOX_READING_REQUEST`.

        Affiche la liste des courriels puis transmet le choix de l'utilisateur
        avec l'entête `INBOX_READING_CHOICE`.

        Affiche le courriel à l'aide du gabarit `EMAIL_DISPLAY`.

        S'il n'y a pas de courriel à lire, l'utilisateur est averti avant de
        retourner au menu principal.
        """

    def _send_email(self) -> None:
        """
        Demande à l'utilisateur respectivement:
        - l'adresse email du destinataire,
        - le sujet du message,
        - le corps du message.

        La saisie du corps se termine par un point seul sur une ligne.

        Transmet ces informations avec l'entête `EMAIL_SENDING`.
        """

    def _check_stats(self) -> None:
        """
        Demande les statistiques au serveur avec l'entête `STATS_REQUEST`.

        Affiche les statistiques à l'aide du gabarit `STATS_DISPLAY`.
        """
    

    def _logout(self) -> None:
        """
        Préviens le serveur avec l'entête `AUTH_LOGOUT`.

        Met à jour l'attribut `_username`.
        """
        msg_logout = gloutils.GloMessage(gloutils.Headers.AUTH_LOGOUT)
        glosocket.send_mesg(msg_logout)
        self._username = None

    def run(self) -> None:
        """Point d'entrée du client."""
        should_quit = False

        while not should_quit:
            if not self._username:

                # Authentication menu
                user_reply: int = None
                while user_reply == None:
                    try: 
                        user_reply = int (input(f"\n{gloutils.CLIENT_AUTH_CHOICE}\n\n:>>> "))
                        if not user_reply >= 1 or not user_reply <= 3:
                            raise ValueError
                    except ValueError : 
                        print("\033[1;31m\nLa valeur que vous avez indiqué est incorrecte\033[0m")
                        user_reply = None

                match user_reply:
                    case 1:
                        self._register()
                        break
                    case 2 :
                        self._login()
                    case 3:
                        sys.exit(0)
                        
    

def _main() -> int:
    #parser = argparse.ArgumentParser()
    #parser.add_argument("-d", "--destination", action="store",
    #                    dest="dest", required=True,
    #                    help="Adresse IP/URL du serveur.")
    #args = parser.parse_args(sys.argv[1:])
    client = Client(
        "127.0.0.1"
    )
    client.run()
    return 0


if __name__ == '__main__':
    sys.exit(_main())
