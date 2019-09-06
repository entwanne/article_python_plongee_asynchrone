* Itérables & générateurs asynchrones

```python
async def gen_words():
    yield 'foo'
    await release()
    yield 'bar'
```

* Gestionnaires de contexte asynchrones

```python
class Foo:
    async def __aenter__(self): pass
    async def __aexit__(self, *args): pass
```
