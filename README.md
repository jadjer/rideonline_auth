# rideonline_auth
Auth server

Deploy
---
```shell
docker pull jadjer/ride2online_auth
```

Run
---
```shell
docker run -d --restart always --name auth -e DATABASE_HOST= -e DATABASE_USER= -e DATABASE_PASS= -e SMS_SERVICE= -p 8000:8000 jadjer/ride2online_auth
```
`DATABASE_HOST - host ip for neo4j database`

`DATABASE_USER - user in neo4j database`

`DATABASE_PASS - user's password in neo4j database`

`SMS_SERVICE - http link for sms service (for send verification codes)`

Key
---
```shell
docker cp auth:/app/keys/public_key.pem public_key.pem
```

`public_key.pem used for verification JWT tokens`