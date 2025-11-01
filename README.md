## Prompt

```
boiler chicken:
 serve: 0.4 KG
 ingreds:
    - masino pyaj: 0.5
    - lasun-adhuwa paste
    - tamatar[masino]
    - khursani
    - masala:
        - mix masala: 1 spoon
        - garam masala: 1 spoon
        - besar: 0.5 spoon
        - meat masala: 1 spoon
    - salt: 2 spoon
 steps:    
    - tel, 2, l
    - masino pyaj
    - khursani[vutne], 2
    - masu, 5
    - xopne, 3
    - lasun-adhuwa, 2
    - masala, 1, m
    - tamatar
    - salt
    - tamatar galunjel xopne, 2
    - jhol
    - xopne, 2, h
```

following this format, write recipe for daal or Lentils in nepali roman. for two servings.
- in serve, it can be 2 person or 20 gm or 2 meal or any quantity followed by unit. it should represent what this recipe is for.
- ingredients format is: `ingredient [optional note]: optional quantity `. again quantity can be any number followed by unit and unit it is optional.
- as in example, the ingredients could be nested. many ingredients under on ingredient.
- step's format is: `step[optional note], optional time, optional flame`. the format is flexible, it can be: `step, time` or `step, flame`. or just `step`. if no flame is mentioned, it will automatically use the flame last mentioned in earlier steps. so if sequentially 4 steps use low flame, we can mention low flame in only the first step. 
point to remember is, if the step name is exact same as ingredient, my system can also display ingredient's quantity and notes when displaying that particular step. if ingredient is 'salt' and step is 'add salt', this won't work.
the time is in minute. but if decimal is provided, the minute and seconds are calculated as below:
```
            const minutes = Math.floor(time/ 60); 
            const seconds = time % 60; 
```

the flame is defined as follow and it can be altered if required. the l,m,h are short ids so that it would be easy to represent flames when writing steps. first item inside flame is human readable name. second is angle. it represent how much angle shall typical stove be tuned to get that temperature. third is degree. useful when cooking in inductions.

```
flames:
  l:
    - low
    - 180
    - 500
  m:
    - medium
    - 100
    - 800
  h:
    - high
    - 90
    - 1200
```
