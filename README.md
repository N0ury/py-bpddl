# py-bpddl
Utilisation d'un tensiomètre Microlife BP A200 sous MacOs

<sub>*Version du 13 février 2020*</sup>

Ce programme permet l'utilisation d'un tensiomètre Microlife BP A200 sous MacOs.

Ce matériel est commercialisé avec un logiciel fonctionnant uniquement sous Windows.
Un projet permettant son utilisation sous Linux existe. Il a été réalisé par Hervé Quillévéré, et porte le nom de **bpddl**. Ce projet est visible sur cette [page](http://www.rvq.fr/linux/bpddl.php)

Sous Linux le matériel est détecté comme périphérique USB ayant comme vendor id et product id: 0x04b4 et 0x5500. Le module **cypress_m8** est automatiquement chargé, et un port /dev/ttyUSBx est créé.  
Cypress semiconductor est le fabriquant du composant permettant la communication avec l'extérieur.  
Le module cypress_m8 est un driver qui permet la communication usb-série.  
Malheureusement, il n'y a pas d'équivalent sous MacOs. Le tensiomètre est bien reconnu comme dispositif USB avec les bons vendor id et product id, mais on ne va pas plus loin. Aucun port n'est créé dans /dev, contrairement à ce qui se passe avec  les autres dispositifs usb-série (ftdi par exemple)    

Heureusement, on peut utiliser l'api `hidapi` pour communiquer.  
J'ai donc écrit un programme en Python utilisant cette possibilité.  
Je me suis essentiellement basé sur le travail d'Hervé qui est parfaitement détaillé sur sa page.  
Le seul point sur lequel j'ai quelques doutes sur mon code, concerne la gestion de l'ID utilisateur. Je n'ai pu faire des tests que sur mon appareil. J'aimerais avoir des retours concernant d'autres appareils.  
Pour le reste, je dois reconnaître que le plus gros du travail concerne le reverse engineering, et qu'Hervé a déjà tout fait.    

# Prérequis:

On utilise la bibliothèque Python "python-easyhid" qui est constituée d'un
unique fichier Python récupérable [ici](https://github.com/ahtn/python-easyhid/blob/master/easyhid/easyhid.py)


On peut également la récupérer à l'aide de la commande:  
`wget https://raw.githubusercontent.com/ahtn/python-easyhid/master/easyhid/easyhid.py`

Le paquet `hidapi` est également indispensable. C'est une bibliothèque de communication
avec les appareils USB HID.
Chacun récupèrera ce paquet selon la méthode de son choix.
Pour ma part, utilisant Homebrew, ce paquet est récupéré par `brew install hidapi` sur Mac.


# Syntaxe de la commande:

```
microlife.py [-r] [-d] [-t] [-n] [-g] [-s id] [-h]  
-r   : read mode. Permet d'afficher tout les mesures du tensiomètre.  
-d   : delete mode. Efface toutes les mesures, mais pas l'ID.  
-t   : set time. Mise à jour de la date et heure à partir de celle du Mac.  
-n   : serial number. Lit le numéro de série (un doute existe sur le résultat).  
-g   : get id. Lecture de l'ID enregistré sur le tensiomètre.  
-s id: set id. Enregistre une nouvelle valeur de l'ID sur le tensiomètre.  
               Les mesures ne sont pas effacées.  
-h   : help. Affiche cette aide.
```

En cas de question, ou de différence de fonctionnement avec un autre appareil, il ne faut pas hésiter à ouvrir une `issue`.

