from typing import *
from pathlib import Path
from argparse import ArgumentParser
from dataclasses import dataclass
import tomllib
import shutil

def main():
    parser = ArgumentParser('sf-backup', description='Satisfactory SaveGame backup tool')
    parser.add_argument('config', type=Path, default='config.toml', nargs='?', help='config TOML file path')
    args = parser.parse_args()

    config = load_config(args.config)
    if not config:
        return

    backed_up_saves = {}
    for save_name in config.SaveGameNames:
        save_backup_dir = config.BackupDirectory / save_name
        save_backup_dir.mkdir(parents=True, exist_ok=True)
        backed_up_saves[save_name] = list(save_backup_dir.iterdir())
    new_backups = {}
    all_saves = config.SaveGamesDirectory.iterdir()
    for save in sorted(all_saves, key=lambda f: f.stat().st_mtime, reverse=True):
        for savegame_name in config.SaveGameNames:
            if savegame_name not in new_backups and save.name.startswith(savegame_name):
                new_backups[savegame_name] = save

    for savegame_name, save in new_backups.items():
        backup_dir = config.BackupDirectory / savegame_name
        if save.name not in (backup.name for backup in backup_dir.iterdir()):
            print(f'Copying: [{save.name}] to [{backup_dir}]')
            shutil.copy(save, backup_dir, follow_symlinks=True)

@dataclass
class Config:
    SaveGamesDirectory: Path
    BackupDirectory: Path
    SaveGameNames: list[str]

def load_config(filename: Path) -> Optional[Config]:
    if not filename.is_file():
        print(f'Error: config: {filename} does not exist')
        return None
    else:
        with filename.open('rb') as f:
            try:
                config = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                print(f'Error reading config file: {e}')
                return None

    if 'SaveGamesDirectory' not in config:
        print('Error: config missing SaveGamesDirectory')
        return None
    else:
        savegames_dir = Path(config['SaveGamesDirectory'])
        if not savegames_dir.is_dir():
            print('Error: invalid SaveGamesDirectory')
            return None

    if 'BackupDirectory' not in config:
        print('Error: config missing BackupDirectory')
        return None
    else:
        backup_dir = Path(config['BackupDirectory'])
        if backup_dir.exists() and not backup_dir.is_dir():
            print('Error: invalid BackupDirectory')
            return None

    if 'SaveGameNames' not in config:
        print('Error: config missing SaveGameNames')
        return None
    else:
        savegame_names = list(config['SaveGameNames'])
    if not savegame_names:
        print('Error: no SaveGameNames provided')
        return None

    return Config(savegames_dir, backup_dir, savegame_names)

if __name__ == '__main__':
    main()
