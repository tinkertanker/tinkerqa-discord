# tinkerqa-discord

A discord bot that manages a QA channel


## Dev setup

If you have envsetup, simply run `envsetup` after cloning the repository.

If not, please install poetry and run `poetry install`


## Deployment

Build the image with
```shell
docker build . -t tinkerqa-discord:latest
```

Deploy it with
```shell
docker run -d -e DISCORD_TOKEN=<TOKEN> tinkerqa-discord:latest
```