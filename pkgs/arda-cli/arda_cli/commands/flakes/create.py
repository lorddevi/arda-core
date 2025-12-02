"""Create new Arda world using flakes."""

import shlex
import subprocess
import sys
from pathlib import Path
from shutil import copytree

import click
import rich_click as rclick
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from arda_cli.lib.output import get_output_manager


@click.command()
@click.argument("name")
@click.option(
    "--template",
    default="default",
    help="Template to use for the new world",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force creation even if directory exists",
)
@click.pass_context
def create(ctx: click.Context, name: str, template: str, force: bool) -> None:
    """Create a new Arda world.

    This creates a new flake-based Arda installation in a new directory.

    NAME is the name of the world to create.
    """
    output = get_output_manager(ctx)

    # Validate world name
    if not name.replace("-", "").replace("_", "").isalnum():
        output.error(
            f"Invalid world name '{name}'. "
            "Use only letters, numbers, hyphens, and underscores."
        )
        sys.exit(1)

    # Determine target directory
    target_dir = Path(name).absolute()

    # Check if directory exists
    if target_dir.exists() and not force:
        output.error(
            f"Directory '{target_dir}' already exists. "
            f"Use --force to overwrite or choose a different name."
        )
        sys.exit(1)

    # Get template path - templates are in arda-core/templates/arda/
    # Following clan-core's pattern: templates are copied into the package
    # at arda_core_templates/arda during the Nix build process

    # Try development path first (running from source)
    arda_core_root = Path(__file__).parent.parent.parent.parent.parent.parent
    dev_templates_dir = arda_core_root / "templates" / "arda"

    # Try installed package path (templates copied into package)
    # Use site.getsitepackages() to find the correct site-packages location
    import site

    site_packages = site.getsitepackages()[0]
    installed_templates_dir = (
        Path(site_packages) / "arda_cli" / "arda_core_templates" / "arda"
    )

    # Choose the right templates directory
    if dev_templates_dir.exists():
        templates_dir = dev_templates_dir
    elif installed_templates_dir.exists():
        templates_dir = installed_templates_dir
    else:
        output.error(
            f"Template directory not found. "
            f"Checked: {dev_templates_dir} and {installed_templates_dir}"
        )
        sys.exit(1)

    template_path = templates_dir / template

    if not template_path.exists():
        output.error(f"Template '{template}' not found at {template_path}")
        output.info("Available templates: default")
        sys.exit(1)

    console = Console()

    # Confirm creation
    if not force:
        if not Confirm.ask(
            f"Create new Arda world '{name}' at {target_dir}?",
            default=True,
            console=console,
        ):
            output.info("World creation cancelled.")
            sys.exit(0)

    # Create the world
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating world...", total=None)

            # 1. Remove directory if it exists
            if target_dir.exists():
                import shutil

                shutil.rmtree(target_dir)

            # 2. Copy template
            progress.update(task, description="Copying template files...")
            copytree(str(template_path), str(target_dir))

            # 3. Initialize git
            progress.update(task, description="Initializing git repository...")
            subprocess.run(
                ["git", "init"],
                cwd=target_dir,
                check=True,
                capture_output=True,
                shell=False,
            )
            subprocess.run(
                ["git", "add", "."],
                cwd=target_dir,
                check=True,
                capture_output=True,
                shell=False,
            )

            # 4. Update flake
            progress.update(task, description="Updating flake...")
            result = subprocess.run(
                ["nix", "flake", "update"],
                cwd=target_dir,
                capture_output=True,
                text=True,
                shell=False,
            )
            if result.returncode != 0:
                output.warning(
                    "Flake update had warnings (this is normal for first run)"
                )

            # 5. Create initial commit
            progress.update(task, description="Creating initial commit...")
            subprocess.run(
                ["git", "add", "."],
                cwd=target_dir,
                check=True,
                capture_output=True,
                shell=False,
            )
            # Use shlex.quote to safely escape the world name
            safe_name = shlex.quote(name)
            subprocess.run(  # noqa: S603
                ["git", "commit", "-m", f"Initial {safe_name} world"],
                cwd=target_dir,
                check=True,
                capture_output=True,
                shell=False,
            )

            # 6. Generate age keys if needed
            progress.update(task, description="Setting up secrets...")
            age_key_path = target_dir / ".sops" / "age" / "keys.txt"
            if not age_key_path.exists():
                (target_dir / ".sops" / "age").mkdir(parents=True, exist_ok=True)
                try:
                    # Validate that the path is within the target directory
                    age_key_path_str = str(age_key_path)
                    if not age_key_path_str.startswith(str(target_dir)):
                        raise ValueError("Invalid age key path")
                    subprocess.run(  # noqa: S603
                        ["age-keygen", "-o", age_key_path_str],
                        check=True,
                        capture_output=True,
                        text=True,
                        shell=False,
                    )
                    output.info(f"Generated age key at {age_key_path}")
                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    output.warning(
                        f"Failed to generate age key: {e}. "
                        "You can install 'age' package if you plan to use "
                        "secrets management."
                    )

            progress.update(task, description="Done!")

        # Success message
        success_panel = Panel(
            f"Successfully created Arda world: [bold]{name}[/bold]\n\n"
            f"Location: [cyan]{target_dir}[/cyan]\n\n"
            f"Next steps:\n"
            f"  • cd {name}\n"
            f"  • nix develop\n"
            f"  • arda help\n\n"
            f"[dim]See README.md in the world directory for more information.[/dim]",
            title="✅ World Created",
            border_style="green",
        )
        console.print(success_panel)

    except subprocess.CalledProcessError as e:
        output.error(f"Command failed: {e.cmd[0]}")
        if e.output:
            output.debug(f"Output: {e.output.decode()}")
        if e.stderr:
            output.debug(f"Error: {e.stderr.decode()}")
        sys.exit(1)
    except Exception as e:
        output.error(f"Failed to create world: {e}")
        import traceback

        output.debug("Full traceback:")
        output.debug(traceback.format_exc())
        sys.exit(1)
