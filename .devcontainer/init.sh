if [ ! -e ./.env ]; then
    cp ./.env.sample ./.env
fi

if [ ! -e ./data/config.yaml ]; then
    mkdir -p ./data
    touch ./data/config.yaml
fi