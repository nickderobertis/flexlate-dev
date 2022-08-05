from pathlib import Path

import multivenv


def main():
    config_path = Path("mvenv.yaml")
    config_class = multivenv.info.model_cls  # type: ignore
    config = config_class.load(config_path)
    venvs = config.venvs
    targets = config.targets

    info = multivenv.info.invoke(venv_names=None, venvs=venvs, targets=targets, quiet=True)
    # Find the correct extension by comparing the possible extensions for the system
    # to the default output extensions from the config
    for system_extension in info.system.file_extensions.all:
        for venv_info in info.venv_info:
            for target in venv_info.targets:
                if target.file_extensions.default == system_extension:
                    print(system_extension)
                    return
    raise ValueError("No matching extension found")


if __name__ == "__main__":
    main()
