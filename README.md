doyoulikeit
===========


```shell
atlas migrate diff --dir "file://migrations" --to "file://db/schema.sql" --dev-url "docker://postgres/17"
atlas migrate apply --url "$DATABASE_URL" --dir file://migrations
```
