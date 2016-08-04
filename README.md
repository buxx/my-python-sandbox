TODO:

* Comparer les performances entre l'usage de sharedmem et processing.Manager
* Que fait le GIL si il y a un dict par thread ?
* sharedmem et processing.Manager peuvent t-il porter des données complexes ?

NOTES:
multiprocessing.Value --> shared memory avec des types issus de ctype, donc pas n'importe quoi, c'est relou
multiprocessing.Manager --> moins performant, mais supporte n'importe quel type, donc simple à utilisé
