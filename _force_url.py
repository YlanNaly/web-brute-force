import asyncio
import uuid
import aiohttp
import math
import multiprocessing
import random
import os
import aiofiles


TARGET_URL = "http://127.0.0.1:5000"


async def write_to_file(directory, filename, content):
    async with aiofiles.open(os.path.join(directory, filename), "w") as file:  # Ouvrir le fichier de manière asynchrone
        await file.write(content)  # Écrire le contenu dans le fichier


# Fonction pour récupérer le contenu d'un fichier
def retrieve_file_content(file_path):
    data = None
    with open(file_path, 'r') as file:  # Ouvrir le fichier en mode lecture
        data = file.read()  # Lire le contenu du fichier
    return data


# Fonction asynchrone pour trouver les routes existantes
async def find_existing_routes(routes, workers_count):
    available_routes = ""
    async with aiohttp.ClientSession() as session:
        for route in routes:
            print("processing... %s/%s" % (TARGET_URL, route))  # Afficher un message de traitement en cours avec les valeurs de route et TARGET_URL
            async with session.get(f"{TARGET_URL}/{route}") as res:  # Effectuer une requête HTTP GET
                if res.status != 404:  # Vérifier si la réponse est différente de 404 (non trouvé)
                    random_value = random.randint(0, 1000)  # Générer une valeur aléatoire
                    available_routes += route + "\n"  # Ajouter la route disponible à la chaîne
                    async with session.get(f"{TARGET_URL}/{route}/{random_value}") as path:  # Requête pour un chemin spécifique
                        if path.status != 404:  # Vérifier si le chemin existe
                            available_routes += f"{route}/:id \n"  # Ajouter le chemin à la chaîne
                    for r in routes:  # Parcourir les routes
                        async with session.get(f"{TARGET_URL}/{route}?{r}={random_value}") as query:  # Requête pour une requête spécifique
                            if query.status != 404:  # Vérifier si la requête est valide
                                available_routes += f"{route}?{r}=? \n"  # Ajouter la requête à la chaîne

    print("proc number: %s" % workers_count)
    filename = str(uuid.uuid4()) + ".txt"  # Générer un nom de fichier unique
    directory = "routes_availables"  # Chemin du répertoire
    if not os.path.exists(directory):  # Vérifier si le répertoire n'existe pas
        os.makedirs(directory)  # Créer le répertoire s'il n'existe pas
    await write_to_file(directory, filename, available_routes)


async def main():
    random_routes = retrieve_file_content("dir_list.txt").split("\n")  # Lire les routes à partir d'un fichier
    workers_count = multiprocessing.cpu_count()  # Obtenir le nombre de processeurs

    length = len(random_routes)  # Obtenir la longueur des routes
    quota = math.floor(length / workers_count)  # Calculer le quota de routes par processus
    index_from = 0  # Index de départ

    tasks = []  # Liste pour stocker les tâches
    for i in range(0, workers_count):  # Boucler sur le nombre de processus
        batch = random_routes[index_from:index_from+quota]  # Diviser les routes en lots pour chaque processus
        tasks.append(find_existing_routes(batch, workers_count))  # Ajouter la tâche à la liste
        index_from = index_from + quota  # Mettre à jour l'index de départ

    await asyncio.gather(*tasks)  # Exécuter toutes les tâches en parallèle


if __name__ == "__main__":
    asyncio.run(main())  # Exécuter la fonction principale de manière asynchrone
