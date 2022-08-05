from flexlate_dev.config import FlexlateDevConfig


def create_config_schema() -> str:
    return FlexlateDevConfig.schema_json(indent=2)


def main():
    print(create_config_schema())


if __name__ == "__main__":
    main()
