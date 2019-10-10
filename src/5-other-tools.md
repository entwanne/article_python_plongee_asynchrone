# Quelques autres outils

* Itérables & générateurs asynchrones

```python
async def gen_words():
    yield 'foo'
    await release()
    yield 'bar'
```

Méthodes `__aiter__` et `__anext__` similaires à `__iter__`/`__next__` (mais coroutines à la place de fonctions classiques).

* Gestionnaires de contexte asynchrones

```python
class Foo:
    async def __aenter__(self): pass
    async def __aexit__(self, *args): pass
```

Idem, `__aenter__`/`__aexit__` strictement équivalentes à `__enter__`/`__exit__` mais coroutines.
