# Ride Online Auth
Auth server for ride online's project

Deploy
---

Pull the image latest version
```shell
docker pull ghcr.io/jadjer/rideonline_auth:latest
```

Keys
---

Get the generator script
```shell
wget https://raw.githubusercontent.com/jadjer/rideonline_auth/main/generate_keys.sh
```

Make script as executable
```shell
chmod +x ./generate_keys.sh
```

Generate keys pair
```shell
./generate_keys.sh ./keys
```

Run
---

```shell
docker run -d --restart always --name auth -e DATABASE_HOST= -e DATABASE_USER= -e DATABASE_PASS= -e SMS_SERVICE= -v $PWD/keys:/app/keys -p 8000:8000 ghcr.io/jadjer/rideonline_auth:latest
```
`DATABASE_HOST - host ip for neo4j database`

`DATABASE_USER - user in neo4j database`

`DATABASE_PASS - user's password in neo4j database`

`SMS_SERVICE - http link for sms service (for send verification codes)`

Use It
---

```http request
http://localhost:8000/docs
```
