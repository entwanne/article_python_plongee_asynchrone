# Futures

* Point sur les futures: traiter le résultat d'un asyncio.sleep
* Réécriture de la boucle événementielle avec futures & events

Notre implémentation actuelle du `sleep` est assez inefficace : la coroutine est appelée à chaque itération alors que le temps n'est pas écoulé.
Il en est de même pour la tâche `Waiter` qui n'a normalement pas besoin d'être programmée tant que son compteur n'est pas terminé.

C'est là qu'interviennent les _futures_, permettant à la boucle de programmer les tâches quand des conditions sont atteintes.
