* Notion de boucle évenementielle
* Remplacement de nos itérations manuelles par un premier prototype de boucle évenementielle (boucle for)

* Gestion parallèle de plusieurs tâches: gather

* Socket: client + serveur

* Notion de priorisation des tâches

Une boucle événementielle est globalement équivalente aux boucles for que nous avons réalisées.

```python
def run_until_complete(task):
    for _ in task.__await__():
        pass
```