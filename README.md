# awa-scraper

## Develop
```console
$ python setup.py develop
$ python -m awa
2021-08-24T00:38:28.130Z INFO:root:Doing something
```

## Scrape 

You can run the scraper, 

```
python -m awa.sources 
```

There are five enumerated data sources supported at the moment.  This will retrieve each one, a build a master set of links in `links/master-links.csv`.  

This also creates a caching directory, in `cache` (you can change the location by setting the environment variable `CACHE_DIR`).  The _first_ time you run the scraper, all the pages will be retrieved from the web but also cached locally.  

The _second_ and subsequent times (unless you clear the cache, which you can do at the moment by manually deleting the `cache` folder) a web page is read from the cache, if present.  

## Test

Run the tests using 

```
pytest
```

At the moment, (see `pytest.ini`) the only tests that are run is that every Python file is checked to make sure there are no `black`-detected linting errors. 

## Lint
Run `black` against everything

```console
$ pip install black
$ find . -iname "*.py" -exec black {} \;
All done! ✨ 🍰 ✨
```
