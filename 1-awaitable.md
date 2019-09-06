* Objets qui peuvent être utilisés après un `await` pour être attendus par une autre tâche asynchrone (ou être exécutés dans une boucle évenementielle)
* Méthode spéciale `__await__` qui renvoie un itérateur

* Implémentation d'awaitables simples (release + producers)
* Itération sur une tâche asynchrone (`for _ in aw.__await__(): ...`)
* Liaison avec les générateurs (utilisation d'un `yield from` dans une méthode `__await__`)
