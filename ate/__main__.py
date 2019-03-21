import logging

import click
from ate import __version__


@click.command()
@click.option('--version', '-v', is_flag=True)
def main(version):
    logger = logging.getLogger('ATE')

    if version:
        print(f'Automated Test Environment, version {__version__}')
        print('Jason R. Jones')
        print('MIT License')
        return


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
