pgloader mysql://bomzheg:petrochi@localhost/curchange postgresql://postgres:postgres@localhost/curchange
pg_dump -f ~/dumps/curchange -F d --no-owner --no-privileges postgresql://postgres:postgres@localhost/curchange
pg_restore -F d --no-owner --no-privileges -U postgres -d postgresql://postgres:postgres@localhost/curchange ~/dumps/curchange
