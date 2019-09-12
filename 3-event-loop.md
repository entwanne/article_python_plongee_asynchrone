* Notion de boucle évenementielle
* Notion de rendre la main à la boucle (asyncio.sleep(0) = yield)
* Définition d'un awaitable release

* Remplacement de nos itérations manuelles par un premier prototype de boucle évenementielle (boucle for)

* Gestion parallèle de plusieurs tâches: gather

* Socket: client + serveur

* Notion de priorisation des tâches
* Rappel sur les futures (consacrer une partie complète ?)

Une boucle événementielle est globalement équivalente aux boucles for que nous avons réalisées.

```python
def run_until_complete(task):
    for _ in task.__await__():
        pass
```
