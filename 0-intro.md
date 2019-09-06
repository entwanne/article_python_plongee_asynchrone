Si vous vous êtes déjà intéressé de près aux mécanismes de Python, vous savez qu'ils reposent sur des interfaces et méthodes spéciales, telles que `__iter__` pour les itérables, `__getitem__` pour les conteneurs ou `__call__` pour les appelables.

Nous verrons ici qu'il en est de même pour les tâches asynchrones, avec la méthode `__await__`.

Cet article présuppose une version de Python ≥ 3.5, intégrant les mot-clés `async` et `await`.
