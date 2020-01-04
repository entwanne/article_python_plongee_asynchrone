# Introduction

Le modèle asynchrone a pris beaucoup d'ampleur dans les dernières versions de Python.
La bibliothèque *asyncio* a été ajoutée en Python 3.4, ont suivi les mots-clés `async` et `await`en Python 3.5, et d'autres nouveautés dans les versions suivantes.

Grâce à nohar vous savez déjà comment fonctionnent [les coroutines](https://zestedesavoir.com/articles/152/la-puissance-cachee-des-coroutines/) et [la programmasion asynchrone en Python](https://zestedesavoir.com/articles/1568/decouvrons-la-programmation-asynchrone-en-python/).
Mais vous êtes-vous déjà demandé comment Python gérait cela ?

Dans ce tutoriel, j'aimerais vous faire découvrir ce qui se cache derrière les mots-clés `async` et `await`, comment ils s'interfacent avec *asyncio*.
Mais aussi de quoi est faite cette bibliothèque et comment on pourrait la réécrire.

Cet article présuppose une version de Python supérieure ou égale à 3.5.
Une connaissance minimale du modèle asynchrone de Python et de la bibliothèque *asyncio* sont préférables.
