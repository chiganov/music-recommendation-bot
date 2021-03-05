# MUSIC RECOMENDATION BOT

Bot get music posts from VK groups/clubs, serch it in Spotify and post in Telegram Chanel.

# RUN

1. prepare
```
touch env
mkdir data
```

2. variables and keys
```
cat env
VK_KEY=111111111111111111111111111111111111111111111111111111111111111111111
VC_CLUBS=club1,club2,club3

SP_KEY=11111111111111111111111111111111
SP_CLIENT_ID=1111111111111111111111111111111

TG_KEY=11111111111111:11111111111111111111111111111111
TG_CHAT=-111111111111

DB_NAME=/data/bot.db
```

3. build docker
```
docker build . -t music-recommendation-bot
```

4. run docker 
```
docker run -d -v $(pwd)/data:/data --env-file=env --name=music-recommendation-bot  music-recommendation-bot
```

5. see logs
```
docker logs music-recommendation-bot -f
```
