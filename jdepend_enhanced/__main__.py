import click
import subprocess
import logging
import re
import questionary


class Package:
    def __init__(self, name, description, package_filter='.*'):
        self.name = name
        titles = ['Stats:', '\nAbstract Classes:',
                  '\nConcrete Classes:', '\nDepends Upon:', '\nUsed By:']
        pattern = '|'.join(titles)
        sections = re.split(pattern, description)
        if len(sections) == 1:
            self.is_empty = True
            return
        self.is_empty = False
        self.stats = sections[1].strip()
        self.abstract_classes = [c.strip()
                                 for c in sections[2].strip().split('\n')]
        self.concrete_classes = [c.strip()
                                 for c in sections[3].strip().split('\n')]
        self.depends_upon = [c.strip()
                             for c in sections[4].strip().split('\n') if re.search(package_filter, c)]
        self.used_by = [c.strip() for c in sections[5].strip().split('\n')
                        if re.search(package_filter, c)]

    def __str__(self):
        if self.is_empty:
            return f'Package: {self.name}\nempty package'
        new_line = '\n'
        return f'''Package: {self.name}
Stats:
{self.stats}

Abstract Classes:
{new_line.join(self.abstract_classes)}

Concrete Classes:
{new_line.join(self.concrete_classes)}

Depends Upon:
{new_line.join(self.depends_upon)}

Used By:
{new_line.join(self.used_by)}
'''


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')


@cli.command()
@click.argument("path", type=click.Path(exists=True), default="/data")
@click.argument("report_path", type=click.Path(), default="/data/report.txt")
def report(path, report_path):
    command = ["java", "-cp", "/app/jdepend-2.10.jar",
               "jdepend.textui.JDepend", path]
    result = subprocess.run(command, capture_output=True, text=True)
    with open(report_path, "w") as f:
        f.write(result.stdout)


@cli.command()
@click.argument("report_path", type=click.Path(), default="/data/report.txt")
def dive(report_path):
    with open(report_path, "r") as f:
        data = f.read()
    package_filter = questionary.text("Package filter").ask()
    packages, package_dependency_cycles, summary = parse(data, package_filter)
    entry_package_name = questionary.text("Entry package").ask()
    last_package_name = entry_package_name
    last_last_package_name = entry_package_name
    while True:
        if entry_package_name == "/":
            entry_package_name = questionary.text("Entry package").ask()
        if entry_package_name == "..":
            entry_package_name = last_last_package_name
            logging.info(f'back to "{entry_package_name}"')
        if entry_package_name not in packages:
            if entry_package_name is None:
                logging.info('exit')
                break
            candidates = [package_name for package_name in packages.keys()
                          if re.search(entry_package_name, package_name)]
            if len(candidates) == 1:
                logging.info(f'dive into "{candidates[0]}"')
                entry_package_name = candidates[0]
            elif len(candidates) > 36:
                entry_package_name = questionary.select(
                    "which package?",
                    choices=candidates,
                ).ask()
            elif len(candidates) > 0:
                entry_package_name = questionary.rawselect(
                    "which package?",
                    choices=candidates,
                ).ask()
            else:
                logging.info(f'package "{entry_package_name}" not found')
                break
        last_last_package_name = last_package_name
        last_package_name = entry_package_name
        entry_package = packages[entry_package_name]
        if entry_package.is_empty:
            logging.info(f'package "{entry_package_name}" is empty')
            break
        next_package_name = \
            ["/", "..", "=== Depends Upon:"] + entry_package.depends_upon + \
            ["", "=== Used By:"] + entry_package.used_by
        if len(next_package_name) > 36:
            entry_package_name = questionary.select(
                "dive",
                choices=next_package_name,
            ).ask()
        else:
            entry_package_name = questionary.rawselect(
                "dive",
                choices=next_package_name,
            ).ask()


def parse(data, package_filter) -> tuple[dict[str, Package], list[str], str]:
    sections = data.split('--------------------------------------------------')
    sections = [section.strip() for section in sections]

    packages = {}
    package_dependency_cycles = []
    summary = ''
    for idx, (head, body) in enumerate(zip(sections[1:], sections[2:])):
        if idx % 2 == 1:
            continue
        if re.match(r'- Package: ', head):
            name = head.split('Package: ')[1]
            if re.search(package_filter, name) is None:
                continue
            description = body
            package = Package(name, description, package_filter)
            packages[name] = package
            logging.debug(f'package: {package}')
        elif re.match(r'- Package Dependency Cycles:', head):
            package_dependency_cycles.append(body)
        elif re.match(r'- Summary:', head):
            summary = body
        else:
            logging.info(f'\nhead: \n{head}\n')
            # logging.info(f'\nbody: \n{body}\n')
    return packages, package_dependency_cycles, summary


if __name__ == "__main__":
    cli()
