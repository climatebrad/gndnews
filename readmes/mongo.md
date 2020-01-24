## MongoDB

Configure Atlas - create dbUser, whitelist IPs.

export local MongoDB to file, then import to Atlas:
```
mongoimport --uri "mongodb+srv://dbUser:<PASSWORD>@cluster0-lqw4d.mongodb.net/gizmodo?retryWrites=true&w=majority" --collection articles --drop --file ../data/gndnews/<file>.json 
```