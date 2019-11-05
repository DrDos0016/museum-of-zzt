try:
    from museum_site.patron_secrets import PASSWORD2DOLLARS, PASSWORD5DOLLARS
except ModuleNotFoundError:
    print("PATRON_SECRETS.PY NOT FOUND. USING DEV VALUES")
    PASSWORD2DOLLARS = "test2dollars"
    PASSWORD5DOLLARS = "test5dollars"

# Article publish states
PUBLISHED_ARTICLE = 1
UPCOMING_ARTICLE = 2
UNPUBLISHED_ARTICLE = 3
REMOVED_ARTICLE = 0
