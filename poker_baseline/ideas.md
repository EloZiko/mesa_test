# idées poker mesa

## ce qui marche
- 4-6 joueurs avec styles différents (tight, loose, normal)
- pre-flop + flop + turn + river
- blinds, all-in
- datacollector pour tracker les stacks
- visualisation solara basique

## a faire
- meilleure evaluation des mains (pour l'instant c'est un score basique, faudrait faire un vrai ranking)
- side pots quand quelqu'un est all-in
- augmenter les blinds au fil du temps (tournament style)
- historique des actions dans la viz

## intégrer un LLM
l'idée serait de remplacer la méthode decide() d'un agent par un appel à un LLM

genre au lieu de:
```python
def decide(self, to_call):
    strength = hand_strength(self.cards)
    if strength >= 10:
        return ("raise", 4)
```

on ferait:
```python
def decide(self, to_call):
    prompt = f"tu as {self.cards}, pot={self.model.pot}, to_call={to_call}. fold/call/raise?"
    response = llm.complete(prompt)
    return parse_action(response)
```

faudrait:
- un wrapper pour l'api (openai ou claude)
- parser la réponse du LLM (il va pas toujours répondre proprement)
- comparer les performances LLM vs stratégie rule-based
- attention au coût des appels API si on fait tourner beaucoup de mains

## mesa + LLM en général
- un agent mesa pourrait avoir un attribut `use_llm=True`
- on pourrait faire un mixin LLMAgent qui gère le prompt engineering
- intéressant pour tester si un LLM peut apprendre des patterns en jouant plusieurs mains
- possible de faire du few-shot avec les dernières mains jouées comme contexte
