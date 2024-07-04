# TimeConstraints

The source code for the KR'24 submission : *Explainable Temporal Knowledge Graph Validation Through Complex Temporal Constraints Discovery*.

## Usage

* Install requirements:
  ```shell
  pip3 install -r ./requirements.txt
  ```

* Run all:

  ```shell
  # Property P31 (default, i.e. instance of)
  # Type Q3624078 (i.e. sovereign state)
  python3 0.0.RunAllGlobal.py -type Q3624078
  ```

### Details

Quintuplet format (example):

```
http://www.wikidata.org/entity/Q1006	http://www.wikidata.org/prop/P1313	http://www.wikidata.org/entity/Q14917303	1996-07-09	None
http://www.wikidata.org/entity/Q1006	http://www.wikidata.org/prop/P31	http://www.wikidata.org/entity/Q3624078	1958-01-01	None
http://www.wikidata.org/entity/Q1006	http://www.wikidata.org/prop/P35	http://www.wikidata.org/entity/Q108418519	2021-10-01	None
http://www.wikidata.org/entity/Q1006	http://www.wikidata.org/prop/P35	http://www.wikidata.org/entity/Q4413	2010-12-21	2021-09-05
http://www.wikidata.org/entity/Q1006	http://www.wikidata.org/prop/P38	http://www.wikidata.org/entity/Q496938	1971-01-01	1985-01-01
http://www.wikidata.org/entity/Q1006	http://www.wikidata.org/prop/P38	http://www.wikidata.org/entity/Q213311	1985-01-01	None
http://www.wikidata.org/entity/Q1006	http://www.wikidata.org/prop/P395	RG	1972-01-01	None
http://www.wikidata.org/entity/Q1006	http://www.wikidata.org/prop/P3984	GuineaRepublic	2020-05-11	None
```

## Copyright

Copyright (c) 2024, *TBD*. All rights reserved.

## License

* *TBD*.

## Maintainer

* *TBD*.