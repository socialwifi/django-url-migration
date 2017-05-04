# django-url-migration

A custom 404 handler that uses fixed or regex rules to redirect from old to new urls.

* Fixed URL -> URL rules
* Regex rules
* Usage logging
* Removal of unused url migrations


Configuration
-------------

* Add custom 404 handler to your main urls.py:

```
handler404 = 'url_migration.views.page_not_found'
```
* Add `url_migration` to your `INSTALLED_APPS`.
* Run migrations (`manage.py migrate`)
* Check your Django admin for the url_migration models:
    * Url mappings: fixed url -> url rules
    * Url regexp mappings: regex rules that will generate url mapping for every regex match.

`remove_expired_redirects` management command may be used to remove expired url mappings -
 if the mapping isn't used for given expiry time it will be removed (so you can see which old urls are still used).

Every mapping hit is being logged to `LastUsageLog` model.

You can also check url_migration_demo project in this repository.
